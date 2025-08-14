"""
Module de contrôle des vols pour HighCloud RPAS Operations Manager.
Gère les opérations liées aux vols de drones, incluant la planification,
l'exécution et le suivi des missions.
"""

import os
import json
import logging

# Configuration du logger
logger = logging.getLogger('hc_rpas.module.controle_vols')

# Simuler les importations pour l'environnement satellite
# Note: Dans un environnement réel, ces classes seraient réellement importées
class Task:
    def __init__(self, title, description, module=None, icon=None, status=None):
        self.title = title
        self.description = description
        self.module = module
        self.icon = icon
        self.status = status
        self.screen_id = None
        self.screen_path = None
        self.target_module_id = None
        self.target_screen_id = None

# Métadonnées du module - utilisées par l'application principale pour l'intégration
MODULE_METADATA = {
    "id": "controle_vols",
    "name": "Contrôle Opérationnel des Vols",
    "version": "1.0.1",
    "description": "Module de gestion et contrôle des opérations de vol pour drones",
    "main_screen": "pilot_dashboard",
    "screens": [
        "pilot_dashboard", 
        "flight_planning", 
        "flight_log", 
        "training_records", 
        "procedures_manager", 
        "chief_pilot_dashboard"
    ],
    "author": "mario@domotiflex.com"
}

# API standard pour l'intégration avec l'application principale
def initialize(app_instance=None, services=None):
    """
    Initialise le module avec une référence à l'application et aux services
    Cette fonction est appelée par l'application principale lors de l'intégration
    
    Args:
        app_instance: Instance de l'application principale
        services: Dictionnaire des services fournis par l'application principale
        
    Returns:
        Instance du module initialisé
    """
    logger.info(f"Initialisation du module controle_vols: app_instance={app_instance}, services={list(services.keys()) if services else None}")
    
    # Simulation du container pour l'environnement satellite
    class MockContainer:
        def __init__(self):
            self.app = app_instance
            self.services = services
            
        def register_screen(self, screen_id, screen_class):
            logger.info(f"Enregistrement de l'écran {screen_id}")
            
    container = MockContainer()
        
    return container

def get_screens():
    """
    Retourne les définitions des écrans du module
    Cette fonction est appelée par l'application principale pour charger les écrans
    
    Returns:
        Dictionnaire des définitions d'écrans
    """
    try:
        # Charger les métadonnées du module depuis le fichier manifest.json
        manifest_path = os.path.join(os.path.dirname(__file__), 'manifest.json')
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
            
        # Extraire les définitions d'écrans
        screens = manifest_data.get('screens', {})
        logger.info(f"Récupération des écrans: {len(screens)} écran(s) trouvé(s)")
        return screens
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des définitions d'écrans: {str(e)}", exc_info=True)
        return {}

def run_standalone():
    """
    Lance le module en mode autonome
    Cette fonction est appelée lorsque le module est exécuté directement
    """
    logger.info("Démarrage du module en mode autonome")
    print("Module controle_vols - Ce module est conçu pour être intégré à l'application principale HC RPAS Ops")
    print("Pour l'exécuter en mode autonome, utilisez: python -m modules.controle_vols")

# Point d'entrée pour l'exécution en tant que module Python indépendant
if __name__ == "__main__":
    run_standalone()

# Définition d'exemple pour démonstration
def get_task_list():
    """
    Retourne une liste de tâches pour ce module
    Cette fonction est utilisée pour peupler l'interface de gestion des tâches
    
    Returns:
        list: Liste des tâches disponibles
    """
    return [
        Task(
            title="Planification de vol",
            description="Planifier un nouveau vol de drone",
            module="controle_vols",
            icon="airplane",
            status="active"
        ),
        Task(
            title="Enregistrement de logs",
            description="Enregistrer les logs d'un vol complété",
            module="controle_vols",
            icon="note-text", 
            status="active"
        ),
        Task(
            title="Validation procédure",
            description="Vérifier la conformité des procédures avant vol",
            module="controle_vols",
            icon="check-circle",
            status="active"
        ),
        Task(
            title="Tableau de bord chef pilote",
            description="Accéder au tableau de bord du chef pilote",
            module="controle_vols",
            icon="view-dashboard",
            status="active"
        )
    ]
