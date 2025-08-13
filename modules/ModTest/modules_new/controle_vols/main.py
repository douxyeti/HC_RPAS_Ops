"""Point d'entrée pour l'exécution autonome du module de contrôle des vols.
Ce fichier permet d'utiliser le module comme une application indépendante.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ajouter le répertoire parent au path pour les imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

# Charger les variables d'environnement
load_dotenv(os.path.join(project_root, '.env'))

# Import de l'application principale avec aliasing pour éviter les conflits
from main import HighCloudRPASApp as BaseApp
from .module_registry import ModuleRegistry
from app.utils.logger import setup_logger

class ControleVolsApp(BaseApp):
    """
    Version autonome du module de contrôle des vols.
    Hérite de l'application principale mais configure le registre de module.
    """
    
    def __init__(self, **kwargs):
        # Configuration du logger dédié au module
        self.module_logger = setup_logger(name="controle_vols", level=logging.INFO, log_to_file=True)
        self.module_logger.info("Démarrage du module de contrôle des vols en mode autonome")
        
        # Initialisation de l'application de base
        super().__init__(**kwargs)
        
        # Remplacer le titre pour le mode autonome
        self.title = "Contrôle Opérationnel des Vols - HighCloud RPAS"
        
        # Référence au registre de module
        self.module_registry = None

    def on_start(self):
        """Appelé après le build, avant le démarrage effectif"""
        # Appeler la méthode de base
        super().on_start()
        
        # Initialiser le registre de module et enregistrer les écrans
        try:
            self.module_logger.info("Initialisation du registre de module...")
            self.module_registry = ModuleRegistry.get_instance()
            self.module_registry.initialize(self.firebase_service)
            self.module_logger.info("Module de contrôle des vols initialisé avec succès")
            
            # Enregistrer ce module dans Firebase pour l'indexation
            self.module_registry.index_storage.register_from_manifest(
                "controle_vols", 
                self.module_registry.manifest_data
            )
        except Exception as e:
            self.module_logger.error(f"Erreur lors de l'initialisation du module: {str(e)}", exc_info=True)

    def navigate_to_module_screen(self, screen_id, field_id=None, **kwargs):
        """Méthode d'accès aux écrans du module"""
        if self.module_registry:
            return self.module_registry.navigate_to_screen(screen_id, field_id, app=self, **kwargs)
        return None

if __name__ == "__main__":
    try:
        # Exécuter l'application en mode autonome
        ControleVolsApp().run()
    except Exception as e:
        logging.error(f"Erreur fatale: {str(e)}", exc_info=True)
        sys.exit(1)
