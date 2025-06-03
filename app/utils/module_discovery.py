"""
Utilitaire pour découvrir et interagir avec les modules installés dans l'application.
Permet de récupérer la liste des modules et leurs écrans indexés dans Firebase.
"""
from typing import Dict, List, Any, Optional
import importlib
import os
import logging
from pathlib import Path

class ModuleDiscovery:
    """Utilitaire pour découvrir et interagir avec les modules installés"""
    
    def __init__(self, firebase_service):
        """
        Initialise l'utilitaire de découverte de modules
        
        Args:
            firebase_service: Instance du service Firebase
        """
        self.firebase_service = firebase_service
        self.modules_cache = {}
        self.screens_cache = {}
        self.logger = logging.getLogger('hc_rpas.module_discovery')
    
    def get_installed_modules(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste des modules installés depuis Firebase
        
        Returns:
            List[Dict[str, Any]]: Liste des modules installés
        """
        try:
            # Chercher dans Firebase
            collection_name = "module_indexes_modules"
            modules_list = self.firebase_service.get_collection(collection_name)
            
            # Si rien dans Firebase, chercher dans le système de fichiers
            if not modules_list:
                self.logger.info("Aucun module indexé trouvé dans Firebase, recherche dans le système de fichiers")
                modules_list = self._discover_modules_from_filesystem()
                
            # Mettre en cache
            self.modules_cache = {module.get('id'): module for module in modules_list if 'id' in module}
            
            return modules_list
        except Exception as e:
            self.logger.error(f"Erreur lors de la découverte des modules: {str(e)}")
            return []
    
    def get_module_screens(self, module_id: str) -> List[Dict[str, Any]]:
        """
        Récupère les écrans d'un module spécifique
        
        Args:
            module_id (str): Identifiant du module
            
        Returns:
            List[Dict[str, Any]]: Liste des écrans du module
        """
        try:
            collection_name = f"module_indexes_screens_{module_id}"
            self.logger.debug(f"Récupération des écrans pour le module {module_id} dans la collection {collection_name}")
            
            screens_list = self.firebase_service.get_collection(collection_name)
            self.logger.debug(f"Nombre d'écrans récupérés: {len(screens_list) if screens_list else 0}")
            
            # Détails de chaque écran pour le débogage
            if screens_list:
                for idx, screen in enumerate(screens_list):
                    self.logger.debug(f"Écran {idx+1}: ID={screen.get('id', 'N/A')}, Nom={screen.get('name', 'N/A')}")
            
            # Mettre en cache
            if module_id not in self.screens_cache:
                self.screens_cache[module_id] = {}
                
            self.screens_cache[module_id] = {
                screen.get('id'): screen for screen in screens_list if 'id' in screen
            }
            
            return screens_list
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des écrans du module {module_id}: {str(e)}")
            return []
    
    def get_screen_details(self, module_id: str, screen_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les détails d'un écran spécifique
        
        Args:
            module_id (str): Identifiant du module
            screen_id (str): Identifiant de l'écran
            
        Returns:
            Optional[Dict[str, Any]]: Détails de l'écran ou None si non trouvé
        """
        try:
            # Si déjà en cache, utiliser le cache
            if module_id in self.screens_cache and screen_id in self.screens_cache[module_id]:
                return self.screens_cache[module_id][screen_id]
            
            # Sinon, charger depuis Firebase
            collection_name = f"module_indexes_screens_{module_id}"
            screen_path = f"{collection_name}/{screen_id}"
            screen_data = self.firebase_service.get_document(collection_name, screen_id)
            
            # Mettre en cache
            if module_id not in self.screens_cache:
                self.screens_cache[module_id] = {}
            
            if screen_data:
                self.screens_cache[module_id][screen_id] = screen_data
                
            return screen_data
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des détails de l'écran {module_id}.{screen_id}: {str(e)}")
            return None
    
    def _discover_modules_from_filesystem(self) -> List[Dict[str, Any]]:
        """
        Découvre les modules installés en parcourant le système de fichiers
        
        Returns:
            List[Dict[str, Any]]: Liste des modules découverts
        """
        modules = []
        services_dir = Path("services")
        
        if not services_dir.exists():
            return []
            
        # Chercher tous les répertoires commençant par "module_"
        for module_dir in services_dir.glob("module_*"):
            if not module_dir.is_dir():
                continue
                
            manifest_path = module_dir / "manifest.json"
            if manifest_path.exists():
                try:
                    import json
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                        
                    module_id = manifest.get('module_id') or module_dir.name.replace('module_', '')
                    modules.append({
                        'id': module_id,
                        'name': manifest.get('name', module_id),
                        'version': manifest.get('version', '1.0.0'),
                        'description': manifest.get('description', '')
                    })
                except Exception as e:
                    self.logger.error(f"Erreur lors de la lecture du manifest {manifest_path}: {str(e)}")
        
        return modules
        
    def navigate_to_module_screen(self, app_instance, module_id: str, screen_id: str, 
                                field_id: Optional[str] = None, **kwargs):
        """
        Navigue vers un écran spécifique d'un module
        
        Args:
            app_instance: Instance de l'application Kivy
            module_id (str): Identifiant du module
            screen_id (str): Identifiant de l'écran
            field_id (Optional[str]): Identifiant du champ (optionnel)
            **kwargs: Arguments supplémentaires à passer à l'écran
        
        Returns:
            bool: True si la navigation a réussi, False sinon
        """
        try:
            # Construire le chemin du module
            module_path = f"services.module_{module_id}"
            
            # Tenter d'importer le module
            try:
                module = importlib.import_module(module_path)
                # Vérifier si le module a un registre
                if hasattr(module, 'get_registry'):
                    registry = module.get_registry()
                    # Naviguer vers l'écran
                    return registry.navigate_to_screen(
                        screen_id=screen_id,
                        field_id=field_id,
                        app=app_instance,
                        **kwargs
                    )
                else:
                    self.logger.error(f"Le module {module_id} n'a pas de méthode get_registry")
            except ImportError as e:
                self.logger.error(f"Impossible d'importer le module {module_path}: {str(e)}")
            
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la navigation vers l'écran {module_id}.{screen_id}: {str(e)}")
            return False
