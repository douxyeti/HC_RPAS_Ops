from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.app import MDApp
from kivy.uix.screenmanager import SlideTransition
from dotenv import load_dotenv

# Import des services
from app.services.config_service import ConfigService
from app.services.firebase_service import FirebaseService

# Import des écrans
from app.views.screens.splash_screen import SplashScreen
from app.views.screens.login_screen import LoginScreen
from app.views.screens.main_screen import MainScreen

class MainScreenManager(MDScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition()
        # Ajouter les écrans dans l'ordre
        self.add_widget(SplashScreen())
        self.add_widget(LoginScreen())
        self.add_widget(MainScreen())

class HCApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_service = None
        self.firebase_service = None
        
    def build(self):
        # Charge les variables d'environnement
        load_dotenv()
        
        # Configure le thème
        self.theme_cls.material_style = "M3"
        
        # Initialise les services
        self._init_services()
        
        # Charge les fichiers KV
        self._load_kv_files()
        
        return MainScreenManager()
        
    def _init_services(self):
        """Initialise les services de l'application"""
        try:
            # Initialise le service de configuration
            self.config_service = ConfigService()
            
            # Initialise Firebase
            self.firebase_service = FirebaseService()
            
            print("Services initialisés avec succès")
        except Exception as e:
            print(f"Erreur lors de l'initialisation des services: {str(e)}")
            raise
        
    def _load_kv_files(self):
        """Charge tous les fichiers KV"""
        Builder.load_file("app/views/kv/splash_screen.kv")
        Builder.load_file("app/views/kv/login_screen.kv")
        Builder.load_file("app/views/kv/main_screen.kv")

if __name__ == "__main__":
    HCApp().run()
