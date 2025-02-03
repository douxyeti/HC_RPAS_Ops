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
        self.current_role = None
        self.available_roles = [
            "Commandant de bord",
            "Pilote",
            "Observateur",
            "Technicien maintenance",
            "Gestionnaire opérations",
            "Responsable formation"
        ]
        
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
        kv_files = [
            'app/views/kv/splash_screen.kv',
            'app/views/kv/login_screen.kv',
            'app/views/kv/dashboard_screen.kv'
        ]
        for kv_file in kv_files:
            Builder.load_file(kv_file)

    def toggle_theme(self):
        """Bascule entre le thème clair et sombre"""
        self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        print(f"Theme changed to: {self.theme_cls.theme_style}")

    def switch_screen(self, screen_name, direction='left'):
        """Change l'écran courant avec une transition"""
        if screen_name in self.screen_manager.screen_names:
            self.screen_manager.transition.direction = direction
            self.screen_manager.current = screen_name

    def set_role(self, role):
        """Définit le rôle actuel de l'utilisateur"""
        if role in self.available_roles:
            self.current_role = role
            # Met à jour le tableau de bord avec les informations du rôle
            dashboard_screen = self.screen_manager.get_screen('dashboard')
            if dashboard_screen:
                dashboard_screen.title.text = f"Tableau de bord - {role}"

if __name__ == "__main__":
    HighCloudRPASApp().run()
