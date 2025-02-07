from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import SlideTransition
from kivy.lang import Builder
from dotenv import load_dotenv
import os

# Import des services
from app.services import ConfigService, FirebaseService, RolesManagerService
from app.services.mqtt_service import MQTTService

# Import des écrans
from app.views.screens.splash_screen import SplashScreen
from app.views.screens.login_screen import LoginScreen
from app.views.screens.dashboard_screen import DashboardScreen
from app.views.screens.specialized_dashboard_screen import SpecializedDashboardScreen
from app.views.screens.roles_manager_screen import RolesManagerScreen
from app.views.screens.role_edit_screen import RoleEditScreen
from app.views.screens.task_manager_screen import TaskManagerScreen

class MainScreenManager(MDScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition()
        # Ajouter les écrans dans l'ordre
        self.add_widget(SplashScreen(name="splash"))
        self.add_widget(LoginScreen(name="login"))
        self.add_widget(DashboardScreen(name="dashboard"))
        self.add_widget(SpecializedDashboardScreen(name="specialized_dashboard"))
        self.add_widget(RolesManagerScreen(name="roles_manager"))
        self.add_widget(RoleEditScreen(name="role_edit"))
        self.add_widget(TaskManagerScreen(name="task_manager"))

class HighCloudRPASApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = None
        self.config_service = None
        self.firebase_service = None
        self.mqtt_service = None
        self.roles_manager_service = None
        self.current_role = None
        self.available_roles = []  # Sera chargé depuis Firebase
        
    def build(self):
        # Charge les variables d'environnement
        load_dotenv()
        
        # Définir le thème clair par défaut
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"  # Couleur principale
        self.theme_cls.accent_palette = "Amber"  # Couleur d'accent
        
        # Initialisation des services
        try:
            # Initialise le service de configuration
            self.config_service = ConfigService()
            
            # Initialise le service MQTT
            self.mqtt_service = MQTTService()
            
            # Utilise les variables d'environnement pour MQTT
            broker = os.getenv('MQTT_BROKER', 'localhost')
            port = int(os.getenv('MQTT_PORT', 1883))
            
            if self.mqtt_service.connect(broker, port):
                print("Service MQTT initialisé avec succès")
            else:
                print("Erreur lors de l'initialisation du service MQTT")
            
            # Initialise le service Firebase
            self.firebase_service = FirebaseService()
            
            # Initialise le service de gestion des rôles
            self.roles_manager_service = RolesManagerService()
            
            # Charge les rôles depuis Firebase
            roles_data = self.roles_manager_service.get_all_roles()
            self.available_roles = [role.get('name') for role in roles_data.values()]
            self.available_roles.sort()  # Trie les rôles par ordre alphabétique
            
            print("Services initialisés avec succès")
        except Exception as e:
            print(f"Erreur lors de l'initialisation des services: {str(e)}")
            raise
        
        # Charge les fichiers KV
        self._load_kv_files()
        
        # Crée le gestionnaire d'écrans
        self.screen_manager = MainScreenManager()
        
        # Définit l'écran initial
        self.screen_manager.current = "splash"
        
        return self.screen_manager
        
    def _load_kv_files(self):
        """Charge tous les fichiers KV"""
        kv_files = [
            'app/views/kv/splash_screen.kv',
            'app/views/kv/login_screen.kv',
            'app/views/kv/dashboard_screen.kv',
            'app/views/kv/roles_manager_screen.kv',
            'app/views/kv/role_edit_screen.kv',  # Ajout du fichier KV pour l'édition des rôles
            'app/views/kv/task_manager_screen.kv'  # Ajout du fichier KV pour la gestion des tâches
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
