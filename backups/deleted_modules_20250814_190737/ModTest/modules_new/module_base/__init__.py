"""
Module de base (template) pour l'architecture modulaire HC_RPAS_Ops
Ce module sert de template pour la création de nouveaux modules
"""

import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("hc_rpas.module_base")

class Module:
    """Classe de base pour tous les modules"""
    
    def __init__(self):
        self.id = "module_base"
        self.name = "Module de Base"
        self.version = "1.0.0"
        self.initialized = False
        self.services = {}
        self.settings = {}
        self.mqtt_topics = []
        
        # Charger la configuration du module
        self._load_config()
    
    def _load_config(self):
        """Charge la configuration du module depuis module_info.json"""
        try:
            import json
            module_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(module_dir, 'module_info.json')
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Mise à jour des attributs
                for key, value in config.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                
                logger.info(f"Configuration chargée pour le module {self.name}")
            else:
                logger.warning(f"Fichier de configuration introuvable: {config_path}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {str(e)}")
    
    def initialize(self) -> bool:
        """Initialise le module"""
        try:
            logger.info(f"Initialisation du module {self.name}")
            
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
        # À implémenter dans les classes dérivées
        pass
    
    def _subscribe_mqtt_topics(self):
        """S'abonne aux topics MQTT définis pour ce module"""
        # Cette méthode sera remplacée par l'implémentation réelle
        # lorsque le module sera utilisé avec l'application principale
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
        # Cette méthode sera remplacée par l'implémentation réelle
        pass
    
    def get_screens(self) -> List[Dict[str, str]]:
        """Retourne la liste des écrans disponibles"""
        try:
            screens = []
            screens_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screens')
            
            if os.path.exists(screens_dir) and os.path.isdir(screens_dir):
                for file in os.listdir(screens_dir):
                    if file.endswith('_screen.py'):
                        screen_id = file.replace('_screen.py', '')
                        screen_class = ''.join(word.capitalize() for word in screen_id.split('_')) + 'Screen'
                        
                        screens.append({
                            'id': screen_id,
                            'name': screen_id.replace('_', ' ').title(),
                            'class': screen_class,
                            'file': file
                        })
            
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
        # À implémenter dans les classes dérivées
        pass
    
    def __str__(self):
        return f"{self.name} (v{self.version})"
