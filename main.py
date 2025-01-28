# Imports principaux
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from pathlib import Path
import os
from dotenv import load_dotenv
from app.services import ConfigService, FirebaseService
from app.views.screens.splash_screen import SplashScreen

# Chargement des variables d'environnement
load_dotenv()

class HighCloudRPASApp(MDApp):
    # Properties pour MVVM
    screen_manager = ObjectProperty(None)
    view_model = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Configuration du thème
        self.theme_cls.theme_style = "Light"  # Majuscule pour la nouvelle version
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.material_style = "M3"  # Utiliser Material Design 3
        
        # Services principaux
        self.config_service = None
        self.firebase = None
        
        # État de l'application
        self.current_user = None
        self.current_role = None
        self.is_authenticated = False
        
    def build(self):
        """Construction de l'interface principale"""
        # Initialisation des services
        self._initialize_services()
        
        # Configuration de l'application
        self._configure_app()
        
        # Chargement des fichiers KV d'abord
        self._load_kv_files()
        
        # Puis chargement des écrans
        self._load_screens()
        
        return self.screen_manager
        
    def _initialize_services(self):
        """Initialisation des services principaux"""
        try:
            # Initialisation du service de configuration
            self.config_service = ConfigService()
            
            # Temporairement commenté pour tester le splashscreen
            # self.firebase = FirebaseService()
            
            print("Services initialisés avec succès")
        except Exception as e:
            print(f"Erreur lors de l'initialisation des services: {str(e)}")
            raise
        
    def _configure_app(self):
        """Configuration de l'application"""
        # Configuration de base de l'application
        app_config = self.config_service.get_app_config()
        self.title = app_config['name']
        
        # Configuration de la fenêtre
        Window.size = (1280, 720)
        Window.minimum_width, Window.minimum_height = 1024, 600
        
        # Initialisation du screen manager
        self.screen_manager = MDScreenManager()
        
    def _load_screens(self):
        """Chargement des écrans de l'application"""
        # Chargement du SplashScreen
        splash_screen = SplashScreen(name='splash')
        self.screen_manager.add_widget(splash_screen)
        self.screen_manager.current = 'splash'
        
    def _load_kv_files(self):
        """Chargement des fichiers KV"""
        kv_files_dir = Path(__file__).parent / "app" / "views" / "kv"
        if kv_files_dir.exists():
            for kv_file in kv_files_dir.glob("*.kv"):
                Builder.load_file(str(kv_file))
                print(f"Fichier KV chargé : {kv_file}")  # Debug
        
    def on_start(self):
        """Actions au démarrage de l'application"""
        # Vérification de l'authentification
        if not self.is_authenticated:
            # Redirection vers l'écran de connexion
            # self.screen_manager.current = 'login'  # À implémenter
            pass
        
    def on_stop(self):
        """Actions à l'arrêt de l'application"""
        # Nettoyage des ressources
        # Sauvegarde de l'état si nécessaire
        pass

if __name__ == "__main__":
    HighCloudRPASApp().run()
