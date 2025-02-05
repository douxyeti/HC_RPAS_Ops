from firebase_admin import initialize_app, credentials
from .auth_service import AuthService
from .config_service import ConfigService
from .roles_tasks_service import RolesTasksService
import os

class AppService:
    """Service principal de l'application"""
    
    def __init__(self):
        # Chemin vers le fichier de configuration Firebase
        cred_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'firebase-credentials.json')
        self.cred = credentials.Certificate(cred_path)
        self.firebase_app = initialize_app(self.cred, {
            'databaseURL': 'https://hc-rpas-ops-default-rtdb.firebaseio.com'
        })
        
        # Initialiser les services
        self.auth_service = AuthService()
        self.config_service = ConfigService()
        self.roles_tasks_service = RolesTasksService()
        
    def initialize(self):
        """Initialise tous les services de l'application"""
        # Initialiser les services dans l'ordre approprié
        self.auth_service.initialize()
        self.config_service.initialize()
        print("Services initialisés avec succès")
