"""
Registre du module de contrôle des vols.
Permet l'indexation et l'accès aux écrans et champs.
"""

import json
import importlib
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional, Callable
from .index_storage import FirebaseIndexStorage

class ModuleRegistry:
    """
    Registre pour le module de contrôle des vols.
    Permet l'indexation et l'accès aux écrans et champs.
    """
    
    _instance = None
    _initialized = False
    
    @classmethod
    def get_instance(cls):
        """Retourne l'instance unique du registre (singleton)"""
        if cls._instance is None:
            cls._instance = ModuleRegistry()
        return cls._instance
    
    def __init__(self):
        """Initialise le registre"""
        if not ModuleRegistry._initialized:
            self.logger = logging.getLogger('hc_rpas.module_registry')
            self.firebase_service = None
            self.index_storage = None
            self.module_id = "operations"
            self.manifest_data = {}
            self.screens = {}
            self._screen_instances = {}
            ModuleRegistry._initialized = True
    
    def initialize(self, firebase_service, module_id="operations"):
        """
        Initialise le registre avec le service Firebase
        
        Args:
            firebase_service: Service Firebase à utiliser
            module_id: Identifiant du module
        """
        self.firebase_service = firebase_service
        self.module_id = module_id
        self.index_storage = FirebaseIndexStorage(firebase_service)
        
        # Charger le manifest
        self._load_manifest()
        
        # Enregistrer le module et ses écrans dans Firebase
        self.index_storage.register_from_manifest(self.module_id, self.manifest_data)
        
        self.logger.info(f"ModuleRegistry initialisé pour le module '{module_id}'")
        return True
    
    def _load_manifest(self):
        """Charge les données du manifest depuis le fichier JSON"""
        try:
            manifest_path = Path(f"services/module_controle_vols/manifest.json")
            if manifest_path.exists():
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    self.manifest_data = json.load(f)
                    
                # Précharger les écrans
                self.screens = {}
                for screen in self.manifest_data.get("screens", []):
                    screen_id = screen.get("id")
                    if screen_id:
                        self.screens[screen_id] = screen
                
                self.logger.info(f"Manifest chargé: {len(self.screens)} écrans trouvés")
            else:
                self.logger.warning(f"Fichier manifest introuvable: {manifest_path}")
                self.manifest_data = {
                    "module_id": self.module_id,
                    "name": "Contrôle Opérationnel des Vols",
                    "version": "1.0.0",
                    "screens": []
                }
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du manifest: {str(e)}")
            self.manifest_data = {}
    
    def get_all_screens(self):
        """Retourne tous les écrans disponibles dans ce module"""
        return self.screens
    
    def get_screen_info(self, screen_id):
        """Retourne les informations d'un écran par son ID"""
        return self.screens.get(screen_id)
    
    def get_field_info(self, screen_id, field_id):
        """Retourne les informations d'un champ par son ID"""
        screen = self.screens.get(screen_id)
        if not screen:
            return None
            
        for field in screen.get("fields", []):
            if field.get("id") == field_id:
                return field
        return None
    
    def navigate_to_screen(self, screen_id, field_id=None, app=None, **kwargs):
        """
        Navigue vers un écran spécifique du module
        
        Args:
            screen_id: Identifiant de l'écran
            field_id: Identifiant du champ à mettre en focus (optionnel)
            app: Instance de l'application (si appelé depuis l'app principale)
            kwargs: Paramètres supplémentaires pour l'écran
            
        Returns:
            L'instance de l'écran ou None si erreur
        """
        try:
            # Vérifier que l'écran existe
            screen_info = self.screens.get(screen_id)
            if not screen_info:
                self.logger.error(f"Écran '{screen_id}' non trouvé")
                return None
                
            # Récupérer la classe d'écran
            screen_class_name = screen_info.get("class")
            if not screen_class_name:
                self.logger.error(f"Classe non spécifiée pour l'écran '{screen_id}'")
                return None
                
            # Si l'écran est déjà instancié, le réutiliser
            screen_key = f"{screen_id}_{hash(str(kwargs))}"
            if screen_key in self._screen_instances:
                screen = self._screen_instances[screen_key]
                
                # Mettre le focus sur le champ si demandé
                if field_id and hasattr(screen, 'focus_field'):
                    screen.focus_field(field_id)
                    
                # Naviguer vers l'écran
                if app:
                    app.switch_screen(screen.name)
                return screen
                
            # Créer une nouvelle instance de l'écran
            try:
                # Importer le module contenant la classe (utiliser les écrans existants)
                try:
                    # D'abord, essayer de charger depuis l'application existante
                    module_path = f"app.views.screens.{screen_id}_screen"
                    screen_module = importlib.import_module(module_path)
                except ImportError:
                    # Si ça échoue, essayer le chemin dans le module
                    module_path = f"services.module_controle_vols.views.screens.{screen_id}_screen"
                    screen_module = importlib.import_module(module_path)
                
                # Obtenir la classe
                screen_class = getattr(screen_module, screen_class_name)
                
                # Créer l'instance
                screen_name = f"module_controle_vols_{screen_id}"
                screen = screen_class(name=screen_name, **kwargs)
                
                # Mettre le focus sur le champ si demandé
                if field_id and hasattr(screen, 'focus_field'):
                    screen.focus_field(field_id)
                
                # Ajouter à l'écran manager si app est fourni
                if app and hasattr(app, 'screen_manager'):
                    app.screen_manager.add_widget(screen)
                    app.switch_screen(screen_name)
                
                # Mettre en cache
                self._screen_instances[screen_key] = screen
                
                self.logger.info(f"Écran '{screen_id}' créé avec succès")
                return screen
            except Exception as e:
                self.logger.error(f"Erreur lors de la création de l'écran '{screen_id}': {str(e)}", exc_info=True)
                return None
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la navigation vers l'écran '{screen_id}': {str(e)}")
            return None
