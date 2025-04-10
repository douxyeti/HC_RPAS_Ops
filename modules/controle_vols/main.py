from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import SlideTransition
from kivy.lang import Builder
from dotenv import load_dotenv
import os

# Import des services
from services.firebase_service import FirebaseService
from services.mqtt_service import MQTTService

# Import des écrans
from views.screens.splash_screen import SplashScreen
from views.screens.login_screen import LoginScreen
from views.screens.dashboard_screen import DashboardScreen
from views.screens.specialized_dashboard_screen import SpecializedDashboardScreen

# Import du container
from core.container import Container

class MainScreenManager(MDScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition()
        # Ajouter les écrans dans l'ordre
        self.add_widget(SplashScreen(name="splash"))
        self.add_widget(LoginScreen(name="login"))
        self.add_widget(DashboardScreen(name="dashboard"))
        self.add_widget(SpecializedDashboardScreen(name="specialized_dashboard"))

class ControleVolsApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = None
        self.config_service = None
        self.firebase_service = None
        self.mqtt_service = None
        self.roles_manager_service = None
        self.current_role = None
        self.available_roles = []  # Sera chargé depuis Firebase
        self.container = Container()

    def build(self):
        # Charger les variables d'environnement
        load_dotenv()
        
        # Charger les fichiers KV
        Builder.load_file(os.path.join(os.path.dirname(__file__), 'views', 'kv', 'splash_screen.kv'))
        Builder.load_file(os.path.join(os.path.dirname(__file__), 'views', 'kv', 'login_screen.kv'))
        
        # Initialiser les services
        self.firebase_service = FirebaseService()
        self.mqtt_service = MQTTService()
        
        # Enregistrer les services dans le container
        self.container.register_service('firebase', self.firebase_service)
        self.container.register_service('mqtt', self.mqtt_service)
        
        # Créer le gestionnaire d'écrans
        self.screen_manager = MainScreenManager()
        
        return self.screen_manager

    def on_start(self):
        """Appelé quand l'application démarre."""
        # Initialiser les services si nécessaire
        pass

    def on_stop(self):
        """Appelé quand l'application s'arrête."""
        # Nettoyer les ressources si nécessaire
        if self.mqtt_service:
            self.mqtt_service.disconnect()
