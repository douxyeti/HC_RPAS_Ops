"""
Module de contrôle opérationnel des vols pour HighCloud RPAS Ops.
Ce module peut être utilisé de manière autonome ou intégré à l'application principale.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional
from .module_registry import ModuleRegistry

logger = logging.getLogger("hc_rpas.operations")

class Module:
    """Classe de base pour le module de contrôle des vols"""
    
    def __init__(self):
        self.id = "operations"
        self.name = "Contrôle Opérationnel des Vols"
        self.version = "1.0.1"
        self.initialized = False
        self.services = {}
        self.settings = {}
        self.mqtt_topics = []
        self.registry = ModuleRegistry.get_instance()
        
        # Charger la configuration du module
        self._load_config()
    
    def _load_config(self):
        """Charge la configuration du module depuis manifest.json"""
        try:
            module_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(module_dir, 'manifest.json')
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Mise à jour des attributs
                if 'module_id' in config:
                    self.id = config['module_id']
                if 'name' in config:
                    self.name = config['name']
                if 'version' in config:
                    self.version = config['version']
                
                logger.info(f"Configuration chargée pour le module {self.name}")
            else:
                logger.warning(f"Fichier de configuration introuvable: {config_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {str(e)}")
    
    def initialize(self, firebase_service=None) -> bool:
        """Initialise le module"""
        try:
            logger.info(f"Initialisation du module {self.name}")
            
            # Initialiser le registre du module
            self.registry.initialize(firebase_service)
            
            # Initialiser les services du module
            self._init_services()
            
            # S'abonner aux topics MQTT si nécessaire
            self._subscribe_mqtt_topics()
            
            self.initialized = True
            logger.info(f"Module {self.name} initialisé avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du module {self.name}: {str(e)}")
            return False
    
    def _init_services(self):
        """Initialise les services du module"""
        # À implémenter si nécessaire
        pass
    
    def _subscribe_mqtt_topics(self):
        """S'abonne aux topics MQTT définis pour ce module"""
        # À implémenter si nécessaire
        pass
    
    def cleanup(self) -> bool:
        """Nettoie les ressources du module"""
        try:
            logger.info(f"Nettoyage du module {self.name}")
            
            # Se désabonner des topics MQTT
            self._unsubscribe_mqtt_topics()
            
            # Nettoyer les services
            for service_id, service in self.services.items():
                if hasattr(service, 'cleanup'):
                    service.cleanup()
            
            self.initialized = False
            logger.info(f"Module {self.name} nettoyé avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du module {self.name}: {str(e)}")
            return False
    
    def _unsubscribe_mqtt_topics(self):
        """Se désabonne des topics MQTT"""
        # À implémenter si nécessaire
        pass
    
    def get_screens(self) -> List[Dict[str, str]]:
        """Retourne la liste des écrans disponibles"""
        try:
            screens = []
            module_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(module_dir, 'manifest.json')
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if 'screens' in config:
                    for screen in config['screens']:
                        screens.append({
                            'id': screen.get('id', ''),
                            'name': screen.get('name', ''),
                            'class': screen.get('class', ''),
                            'description': screen.get('description', '')
                        })
            
            logger.info(f"Récupération de {len(screens)} écrans pour le module {self.name}")
            return screens
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des écrans: {str(e)}")
            return []
    
    def get_service(self, service_id: str) -> Optional[Any]:
        """Récupère un service du module"""
        return self.services.get(service_id)
    
    def register_service(self, service_id: str, service: Any) -> None:
        """Enregistre un service fourni par le module"""
        self.services[service_id] = service
        logger.info(f"Service {service_id} enregistré pour le module {self.name}")
    
    def handle_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Gère un événement envoyé au module"""
        # À implémenter si nécessaire
        pass
    
    def __str__(self):
        return f"{self.name} (v{self.version})"

# Fonctions de compatibilité pour l'ancienne interface
def initialize(firebase_service):
    """Compatibilité avec l'ancienne interface"""
    module = Module()
    return module.initialize(firebase_service)

def get_registry():
    """Compatibilité avec l'ancienne interface"""
    return ModuleRegistry.get_instance()
