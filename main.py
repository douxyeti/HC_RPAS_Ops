from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import SlideTransition
from kivy.lang import Builder
from dotenv import load_dotenv

# Import des services
from app.services import ConfigService, FirebaseService

# Import des écrans
from app.views.screens.splash_screen import SplashScreen
from app.views.screens.login_screen import LoginScreen
from app.views.screens.dashboard_screen import DashboardScreen

class MainScreenManager(MDScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition()
        # Ajouter les écrans dans l'ordre
        self.add_widget(SplashScreen(name="splash"))
        self.add_widget(LoginScreen(name="login"))
        self.add_widget(DashboardScreen(name="dashboard"))

class HighCloudRPASApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = None
        self.config_service = None
        self.firebase_service = None
        
    def build(self):
        # Charge les variables d'environnement
        load_dotenv()
        
        # Configure le thème
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_palette = "Blue"  # Couleur principale
        self.theme_cls.accent_palette = "Amber"  # Couleur d'accent
        self.theme_cls.theme_style = "Light"     # Thème clair
        
        # Initialise les services
        self._init_services()
        
        # Charge les fichiers KV
        self._load_kv_files()
        
        # Crée le gestionnaire d'écrans
        self.screen_manager = MainScreenManager()
        
        # Définit l'écran initial
        self.screen_manager.current = "splash"
        
        return self.screen_manager
        
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
        Builder.load_file("app/views/kv/dashboard_screen.kv")

    def toggle_theme(self):
        """Bascule entre le thème clair et sombre"""
        self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        print(f"Theme changed to: {self.theme_cls.theme_style}")

if __name__ == "__main__":
    HighCloudRPASApp().run()
