"""
Gestionnaire de modules pour l'architecture modulaire HC_RPAS_Ops
Ce gestionnaire permet d'intégrer des modules indépendants sans perturber l'application existante
"""

import os
import sys
import importlib
import importlib.util
import json
import logging
import inspect
from typing import Dict, List, Any, Optional, Type, Callable

logger = logging.getLogger("hc_rpas.module_manager")

class ModuleManager:
    """
    Gestionnaire de modules permettant la découverte, le chargement et l'intégration
    des modules indépendants dans l'application HC_RPAS_Ops
    """
    
    def __init__(self):
        self.modules = {}  # modules chargés (id -> instance de module)
        self.module_info = {}  # métadonnées des modules (id -> info)
        self.screens_registry = {}  # écrans disponibles (id -> info)
        self.event_handlers = {}  # gestionnaires d'événements (type -> [handlers])
        
        # Dossiers de modules (priorité aux nouveaux modules)
        self.module_dirs = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules_new')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules'))
        ]
        
        # Valider les chemins de modules
        self.module_dirs = [d for d in self.module_dirs if os.path.exists(d) and os.path.isdir(d)]
        
        if not self.module_dirs:
            logger.warning("Aucun répertoire de modules valide n'a été trouvé!")
    
    def discover_modules(self) -> List[Dict[str, Any]]:
        """
        Découvre tous les modules disponibles dans les chemins de modules
        """
        modules_info = []
        
        for module_dir in self.module_dirs:
            logger.info(f"Recherche de modules dans {module_dir}")
            
            try:
                # Parcourir les sous-dossiers (potentiels modules)
                for item in os.listdir(module_dir):
                    item_path = os.path.join(module_dir, item)
                    
                    # Vérifier si c'est un dossier et s'il contient module_info.json
                    if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, 'module_info.json')):
                        try:
                            # Charger les infos du module
                            with open(os.path.join(item_path, 'module_info.json'), 'r', encoding='utf-8') as f:
                                module_info = json.load(f)
                            
                            # Ajouter les métadonnées du chemin
                            module_info['path'] = item_path
                            module_info['directory'] = module_dir
                            
                            # Vérifier si le module a déjà été découvert (priorité aux premiers trouvés)
                            if module_info.get('id') not in [m.get('id') for m in modules_info]:
                                modules_info.append(module_info)
                                
                                # Stocker les informations pour référence future
                                self.module_info[module_info.get('id')] = module_info
                                
                                logger.info(f"Module découvert: {module_info.get('name', item)} ({module_info.get('id')})")
                        except Exception as e:
                            logger.warning(f"Erreur lors du chargement du module {item}: {str(e)}")
            except Exception as e:
                logger.error(f"Erreur lors de la découverte des modules dans {module_dir}: {str(e)}")
        
        return modules_info
    
    def load_module(self, module_id: str) -> bool:
        """
        Charge un module spécifique dans la mémoire
        """
        # Vérifier si le module est déjà chargé
        if module_id in self.modules:
            logger.info(f"Module {module_id} déjà chargé")
            return True
        
        # Vérifier si les informations du module sont disponibles
        if module_id not in self.module_info:
            logger.error(f"Module {module_id} non découvert")
            return False
        
        module_info = self.module_info[module_id]
        module_path = module_info.get('path')
        
        try:
            # Dynamiquement importer le module
            logger.debug(f"Importation du module depuis {module_path}")
            
            # Détecter le sous-module principale (généralement __init__.py)
            init_file = os.path.join(module_path, '__init__.py')
            if not os.path.exists(init_file):
                logger.error(f"Fichier __init__.py introuvable pour le module {module_id}")
                return False
            
            # Charger le module
            spec = importlib.util.spec_from_file_location(f"hc_rpas.modules.{module_id}", init_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Trouver la classe Module
            module_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and name == 'Module':
                    module_class = obj
                    break
            
            if not module_class:
                logger.error(f"Classe Module introuvable dans {module_id}")
                return False
            
            # Instancier le module
            logger.info(f"Instanciation du module {module_id}")
            module_instance = module_class()
            
            # Stocker l'instance
            self.modules[module_id] = module_instance
            
            # Charger les écrans du module
            self._register_module_screens(module_id, module_instance)
            
            logger.info(f"Module {module_id} chargé avec succès")
            return True
        except Exception as e:
            import traceback
            logger.error(f"Erreur lors du chargement du module {module_id}: {str(e)}")
            logger.debug(traceback.format_exc())
            return False
    
    def _register_module_screens(self, module_id: str, module_instance: Any) -> None:
        """Enregistre les écrans fournis par un module"""
        try:
            # Demander au module ses écrans disponibles
            if hasattr(module_instance, 'get_screens'):
                screens = module_instance.get_screens()
                
                for screen in screens:
                    screen_id = screen.get('id')
                    # Ajouter l'identifiant du module
                    screen['module_id'] = module_id
                    
                    # Générer un ID unique pour l'écran
                    unique_id = f"{module_id}.{screen_id}"
                    self.screens_registry[unique_id] = screen
                    
                    logger.debug(f"Écran enregistré: {unique_id}")
                
                logger.info(f"{len(screens)} écrans enregistrés pour le module {module_id}")
            else:
                logger.warning(f"Le module {module_id} ne fournit pas de méthode get_screens()")
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des écrans du module {module_id}: {str(e)}")
    
    def initialize_module(self, module_id: str) -> bool:
        """
        Initialise un module précédemment chargé
        """
        if module_id not in self.modules:
            logger.error(f"Module {module_id} non chargé, impossible d'initialiser")
            return False
        
        module = self.modules[module_id]
        
        try:
            if hasattr(module, 'initialize'):
                logger.info(f"Initialisation du module {module_id}")
                result = module.initialize()
                
                if result:
                    logger.info(f"Module {module_id} initialisé avec succès")
                else:
                    logger.error(f"Échec de l'initialisation du module {module_id}")
                
                return result
            else:
                logger.warning(f"Le module {module_id} ne fournit pas de méthode initialize()")
                return False
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du module {module_id}: {str(e)}")
            return False
    
    def cleanup_module(self, module_id: str) -> bool:
        """
        Nettoie les ressources d'un module
        """
        if module_id not in self.modules:
            logger.warning(f"Module {module_id} non chargé, aucun nettoyage nécessaire")
            return True
        
        module = self.modules[module_id]
        
        try:
            if hasattr(module, 'cleanup'):
                logger.info(f"Nettoyage du module {module_id}")
                result = module.cleanup()
                
                if result:
                    logger.info(f"Module {module_id} nettoyé avec succès")
                else:
                    logger.error(f"Échec du nettoyage du module {module_id}")
                
                return result
            else:
                logger.warning(f"Le module {module_id} ne fournit pas de méthode cleanup()")
                return True
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du module {module_id}: {str(e)}")
            return False
    
    def unload_module(self, module_id: str) -> bool:
        """
        Décharge un module de la mémoire après nettoyage
        """
        # D'abord nettoyer
        if not self.cleanup_module(module_id):
            logger.warning(f"Le nettoyage du module {module_id} a échoué, déchargement forcé")
        
        # Supprimer les écrans associés
        screens_to_remove = []
        for screen_id in self.screens_registry:
            if screen_id.startswith(f"{module_id}."):
                screens_to_remove.append(screen_id)
        
        for screen_id in screens_to_remove:
            self.screens_registry.pop(screen_id, None)
        
        # Supprimer l'instance du module
        if module_id in self.modules:
            self.modules.pop(module_id)
            logger.info(f"Module {module_id} déchargé")
            return True
        
        return False
    
    def get_module_screens(self, module_id: str) -> List[Dict[str, Any]]:
        """
        Récupère la liste des écrans fournis par un module
        """
        screens = []
        
        # Vérifier d'abord si le module est chargé
        if module_id not in self.modules:
            logger.warning(f"Le module {module_id} n'est pas chargé, chargement automatique...")
            if not self.load_module(module_id):
                logger.error(f"Impossible de charger le module {module_id}")
                return []
        
        # Collecter les écrans enregistrés pour ce module
        for screen_id, screen_info in self.screens_registry.items():
            if screen_info.get('module_id') == module_id:
                screens.append(screen_info)
        
        logger.info(f"Récupération de {len(screens)} écrans pour le module {module_id}")
        return screens
    
    def load_screen(self, screen_id: str) -> Optional[Type]:
        """
        Charge la classe d'un écran spécifique
        
        Args:
            screen_id: Format "module_id.screen_id"
        
        Returns:
            La classe de l'écran ou None si non trouvée
        """
        parts = screen_id.split('.')
        if len(parts) != 2:
            logger.error(f"Format d'ID d'écran invalide: {screen_id} (doit être module_id.screen_id)")
            return None
        
        module_id, local_screen_id = parts
        
        # Vérifier si le module est chargé
        if module_id not in self.modules:
            logger.warning(f"Le module {module_id} n'est pas chargé, chargement automatique...")
            if not self.load_module(module_id):
                logger.error(f"Impossible de charger le module {module_id}")
                return None
        
        # Vérifier si l'écran est enregistré
        if screen_id not in self.screens_registry:
            logger.error(f"Écran inconnu: {screen_id}")
            return None
        
        screen_info = self.screens_registry[screen_id]
        module_path = self.module_info[module_id].get('path')
        
        # Déterminer le chemin du fichier de l'écran
        if 'file' in screen_info:
            screen_file = os.path.join(module_path, 'screens', screen_info['file'])
        else:
            screen_file = os.path.join(module_path, 'screens', f"{local_screen_id}_screen.py")
        
        if not os.path.exists(screen_file):
            logger.error(f"Fichier d'écran introuvable: {screen_file}")
            return None
        
        try:
            # Charger dynamiquement le module contenant l'écran
            logger.debug(f"Chargement de l'écran depuis {screen_file}")
            
            # Importer le module
            spec = importlib.util.spec_from_file_location(f"hc_rpas.modules.{module_id}.screens.{local_screen_id}", screen_file)
            screen_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(screen_module)
            
            # Trouver la classe d'écran
            class_name = screen_info.get('class', '')
            if not class_name:
                # Deviner le nom de la classe à partir du nom du fichier
                class_name = ''.join(word.capitalize() for word in local_screen_id.split('_')) + 'Screen'
            
            # Récupérer la classe
            screen_class = getattr(screen_module, class_name, None)
            
            if not screen_class:
                logger.error(f"Classe d'écran {class_name} introuvable dans {screen_file}")
                return None
            
            logger.info(f"Écran {screen_id} chargé avec succès (classe {class_name})")
            return screen_class
        except Exception as e:
            import traceback
            logger.error(f"Erreur lors du chargement de l'écran {screen_id}: {str(e)}")
            logger.debug(traceback.format_exc())
            return None
    
    def register_event_handler(self, event_type: str, handler: Callable, module_id: Optional[str] = None) -> bool:
        """
        Enregistre un gestionnaire d'événements pour un type d'événement
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        # Stocker le gestionnaire avec l'ID du module (pour nettoyage)
        self.event_handlers[event_type].append({
            'handler': handler,
            'module_id': module_id
        })
        
        logger.debug(f"Gestionnaire d'événements enregistré pour {event_type}" + 
                    (f" (module {module_id})" if module_id else ""))
        return True
    
    def unregister_event_handlers(self, module_id: str) -> int:
        """
        Supprime tous les gestionnaires d'événements associés à un module
        """
        count = 0
        
        for event_type in self.event_handlers:
            # Filtrer les gestionnaires associés au module
            handlers = self.event_handlers[event_type]
            self.event_handlers[event_type] = [h for h in handlers if h.get('module_id') != module_id]
            
            # Compter les suppressions
            count += len(handlers) - len(self.event_handlers[event_type])
        
        logger.info(f"{count} gestionnaires d'événements supprimés pour le module {module_id}")
        return count
    
    def trigger_event(self, event_type: str, data: Dict[str, Any]) -> int:
        """
        Déclenche un événement et notifie tous les gestionnaires enregistrés
        """
        if event_type not in self.event_handlers:
            logger.debug(f"Aucun gestionnaire pour l'événement {event_type}")
            return 0
        
        handlers = self.event_handlers[event_type]
        count = 0
        
        for handler_info in handlers:
            try:
                handler = handler_info['handler']
                handler(event_type, data)
                count += 1
            except Exception as e:
                module_id = handler_info.get('module_id', 'inconnu')
                logger.error(f"Erreur dans le gestionnaire d'événements de {module_id} pour {event_type}: {str(e)}")
        
        logger.debug(f"Événement {event_type} traité par {count} gestionnaires")
        return count
    
    def get_all_screens(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Récupère tous les écrans disponibles, groupés par module
        """
        result = {}
        
        # Découvrir tous les modules disponibles
        self.discover_modules()
        
        # Pour chaque module, charger et récupérer les écrans
        for module_id in self.module_info:
            # Tenter de charger le module si pas déjà fait
            if module_id not in self.modules:
                self.load_module(module_id)
            
            # Récupérer les écrans de ce module
            if module_id in self.modules:
                screens = self.get_module_screens(module_id)
                result[module_id] = screens
        
        return result
    
    def load_all_modules(self) -> Dict[str, bool]:
        """
        Charge et initialise tous les modules disponibles
        """
        results = {}
        
        # Découvrir les modules
        self.discover_modules()
        
        # Charger et initialiser chaque module
        for module_id in self.module_info:
            load_success = self.load_module(module_id)
            
            if load_success:
                init_success = self.initialize_module(module_id)
                results[module_id] = init_success
            else:
                results[module_id] = False
        
        return results
    
    def unload_all_modules(self) -> None:
        """
        Décharge tous les modules chargés
        """
        # Copier la liste des IDs car on va modifier le dictionnaire
        module_ids = list(self.modules.keys())
        
        for module_id in module_ids:
            self.unload_module(module_id)

# Instance singleton pour l'application
_instance = None

def get_module_manager() -> ModuleManager:
    """
    Récupère l'instance unique du gestionnaire de modules
    """
    global _instance
    if _instance is None:
        _instance = ModuleManager()
    return _instance
