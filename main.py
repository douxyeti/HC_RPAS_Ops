from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import SlideTransition
from kivy.lang import Builder
from kivy.clock import Clock
from dotenv import load_dotenv
import os
import logging

# Import des services
from app.services import ConfigService, FirebaseService, RolesManagerService
from app.services.mqtt_service import MQTTService
from app.services.encryption_service import EncryptionService

# Import de l'initialisation des modules
from app.utils.module_initializer import get_module_initializer

# Import des écrans
from app.views.screens.splash_screen import SplashScreen
from app.views.screens.login_screen import LoginScreen
from app.views.screens.dashboard_screen import DashboardScreen
from app.views.screens.specialized_dashboard_screen import SpecializedDashboardScreen
from app.views.screens.roles_manager_screen import RolesManagerScreen
from app.views.screens.role_edit_screen import RoleEditScreen
from app.views.screens.task_manager_screen import TaskManagerScreen
from app.views.screens.procedures_manager_screen import ProceduresManagerScreen
from app.views.screens.modules_admin_screen import ModulesAdminScreen
from app.views.screens.sso_management_screen import SsoManagementScreen

# Import du modèle
from app.models.application_model import ApplicationModel

# Import du container
from app.core.container import Container

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
        self.add_widget(ModulesAdminScreen(name="modules_admin"))
        self.add_widget(SsoManagementScreen(name="sso_management"))

class HighCloudRPASApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = None
        self.config_service = None
        self.firebase_service = None
        self.mqtt_service = None
        self.encryption_service = None
        self.roles_manager_service = None
        self.current_role = None
        self.available_roles = []  # Sera chargé depuis Firebase
        self.model = ApplicationModel()
        
        # Initialiser le container
        self.container = Container()
        self.container.config.from_dict({
            'firebase': {
                'config_path': os.path.join(os.path.dirname(__file__), 'app', 'config', 'firebase_config.json')
            }
        })
        
    def build(self):
        # Charge les variables d'environnement
        load_dotenv()
        
        # Définir le thème clair par défaut
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"  # Couleur principale
        self.theme_cls.accent_palette = "Amber"  # Couleur d'accent
        
        # Récupérer le logger depuis le container
        self.logger = self.container.logger()
        
        try:
            # Initialiser les services (y compris l'initialisation du module)
            self.init_services()
            self.logger.info("Services initialisés avec succès")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation des services: {str(e)}", exc_info=True)
            raise
        
        # Charge les fichiers KV
        self._load_kv_files()
        
        # Crée le gestionnaire d'écrans
        self.screen_manager = MainScreenManager()
        
        # Ajoute l'écran de gestion des procédures avec son service
        procedures_manager_screen = ProceduresManagerScreen(
            name="procedures_manager",
            procedures_manager_service=self.container.procedures_manager()
        )
        self.screen_manager.add_widget(procedures_manager_screen)
        
        # Définit l'écran initial sur le splash screen
        self.screen_manager.current = "splash"
        
        # Tente une connexion SSO après un court instant, pour laisser le splash screen s'afficher
        Clock.schedule_once(lambda dt: self._check_for_sso_session(), 1)

        return self.screen_manager
        
    def _load_kv_files(self):
        """Charge tous les fichiers KV dynamiquement"""
        from pathlib import Path
        
        # Répertoire contenant les fichiers KV
        kv_directory = Path("app/views/kv")
        
        # Vérifier que le répertoire existe
        if not kv_directory.exists():
            self.logger.error(f"Le répertoire {kv_directory} n'existe pas")
            return
        
        # Liste des fichiers qui doivent être chargés en premier (ordre spécifique si nécessaire)
        # Par exemple, si certains fichiers définissent des widgets utilisés par d'autres
        priority_files = [
            "splash_screen.kv"  # Exemple : charger d'abord l'écran de démarrage
        ]
        
        # Charger d'abord les fichiers prioritaires
        for filename in priority_files:
            kv_file = kv_directory / filename
            if kv_file.exists():
                self.logger.debug(f"Chargement prioritaire du fichier KV: {kv_file}")
                Builder.load_file(str(kv_file))
        
        # Charger tous les autres fichiers .kv
        for kv_file in kv_directory.glob("*.kv"):
            # Ne pas recharger les fichiers prioritaires déjà chargés
            if kv_file.name not in priority_files:
                self.logger.debug(f"Chargement du fichier KV: {kv_file}")
                Builder.load_file(str(kv_file))

    def toggle_theme(self):
        """Bascule entre le thème clair et sombre"""
        self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        self.logger.info(f"Theme changed to: {self.theme_cls.theme_style}")

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

    def load_configuration(self):
        # Code pour charger la configuration
        pass

    def _check_for_sso_session(self):
        """Vérifie la présence d'un token SSO sur MQTT au démarrage."""
        if not self.mqtt_service or self.mqtt_service.connection_state != 'connected':
            self.logger.warning("SSO Check: MQTT non connecté, passage à l'écran de connexion.")
            self.switch_screen("login")
            return

        sso_config = self.config_service.get_config('sso')
        token_topic = sso_config.get('token_topic')

        # Définir un timeout pour passer à l'écran de login si aucun token n'est reçu
        self._login_timeout = Clock.schedule_once(
            lambda dt: self.switch_screen("login"), 2
        )

        # S'abonner au topic et définir le callback
        self.mqtt_service.subscribe(token_topic, self._on_sso_token_received)
        self.logger.info(f"SSO Check: Abonné au topic '{token_topic}' avec un timeout de 2s.")

    def _on_sso_token_received(self, client, userdata, message):
        """Callback exécuté à la réception d'un token SSO."""
        if hasattr(self, '_login_timeout'):
            self._login_timeout.cancel()
        
        encrypted_token = message.payload
        if not encrypted_token:
            self.logger.warning("SSO Login: Message reçu mais payload vide. Passage à l'écran de connexion.")
            self.switch_screen("login")
            return

        try:
            self.logger.info("SSO Login: Token reçu, tentative de déchiffrement et connexion.")
            custom_token = self.encryption_service.decrypt(encrypted_token)
            user_tokens = self.firebase_service.sign_in_with_custom_token(custom_token)
            
            if user_tokens:
                self.logger.info("SSO Login: Connexion automatique réussie.")
                self.load_user_roles()  # Les détails de l'utilisateur sont maintenant dans firebase_service.current_user
                self.switch_screen("dashboard")
            else:
                self.logger.error("SSO Login: Échec de la connexion avec le token personnalisé.")
                self.switch_screen("login")
        except Exception as e:
            self.logger.error(f"SSO Login: Échec du processus de connexion SSO : {e}", exc_info=True)
            self.switch_screen("login")

    def load_user_roles(self):
        """Charge les rôles de l'utilisateur depuis Firebase en utilisant l'utilisateur actuellement connecté."""
        if not self.firebase_service.current_user:
            logging.warning("Load Roles: Attempting to load roles without a logged-in user.")
            return

        try:
            user_id = self.firebase_service.current_user['localId']
            logging.info(f"Load Roles: Loading roles for user {user_id}.")

            # New logic: Fetch the pilot document using the user_id
            pilot_doc = self.firebase_service.get_document(f'pilots/{user_id}')

            if not pilot_doc:
                logging.warning(f"Load Roles: No pilot document found for user ID '{user_id}'.")
                self.user_roles = []
                return

            role_name = pilot_doc.get('role_name')
            if not role_name:
                logging.warning(f"Load Roles: 'role_name' not found in pilot document for user '{user_id}'.")
                self.user_roles = []
                return

            logging.info(f"User '{user_id}' has role '{role_name}'. Assigning to user_roles.")
            # For now, we just assign the role name. The dropdown menu will be populated with this.
            self.user_roles = [role_name]
            logging.info(f"Roles loaded for {user_id}: {self.user_roles}")

        except KeyError:
            logging.error("Load Roles: 'localId' not found in self.firebase_service.current_user.")
            self.user_roles = []
        except Exception as e:
            logging.error(f"Load Roles: An unexpected error occurred: {e}")
            self.user_roles = []

    def init_services(self):
        """Initialise tous les services"""
        try:
            # Initialise le service de configuration (toujours en premier)
            self.config_service = ConfigService()
            self.logger.info("Service de configuration initialisé")
            
            # On initialise d'abord la connexion MQTT si le service est activé
            mqtt_enabled = self.config_service.get_config('mqtt.enabled', False)
            if mqtt_enabled:
                self.logger.info("Initialisation du service MQTT...")
                self.mqtt_service = MQTTService()
                # Connexion au broker MQTT
                broker = self.config_service.get_config('mqtt.broker', 'localhost')
                port = int(self.config_service.get_config('mqtt.port', 1883))
                self.mqtt_service.connect(broker, port)
                self.logger.info(f"Service MQTT connecté à {broker}:{port}")
            else:
                self.logger.info("Service MQTT désactivé dans la configuration")
            
            # Initialise ensuite le service Firebase
            self.logger.info("Initialisation du service Firebase...")
            self.firebase_service = FirebaseService.get_instance()
            self.logger.info("Service Firebase initialisé")
            
            # Initialise le service de gestion des rôles
            self.logger.info("Initialisation du service de gestion des rôles...")
            self.roles_manager_service = RolesManagerService()
            
            # Charge les rôles depuis Firebase
            self.logger.info("Chargement des rôles depuis Firebase...")
            roles_data = self.roles_manager_service.get_all_roles()
            self.available_roles = []
            for role in roles_data:
                if role.get('name'):
                    self.available_roles.append(role.get('name'))
            self.logger.info(f"{len(self.available_roles)} rôles chargés")

            # Initialise le service de chiffrement
            self.logger.info("Initialisation du service de chiffrement...")
            self.encryption_service = EncryptionService()
            self.logger.info("Service de chiffrement initialisé")

            # Initialise le service de chiffrement
            self.logger.info("Initialisation du service de chiffrement...")
            self.encryption_service = EncryptionService()
            self.logger.info("Service de chiffrement initialisé")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation des services: {e}")
            raise
        self.available_roles.sort()  # Trie les rôles par ordre alphabétique
        
        # Initialiser le module pour cette branche si nécessaire
        try:
            module_initializer = get_module_initializer()
            module_initializer.initialize_with_services(self.firebase_service)
            if module_initializer.is_module_initialized():
                logging.info("Module correctement initialisé et indexé pour la branche actuelle.")
            else:
                logging.info("Le module était déjà indexé pour la branche actuelle.")
        except Exception as e:
            logging.error(f"Erreur lors de l'initialisation du module: {e}")
            # Ne pas bloquer le démarrage de l'application en cas d'erreur

    def on_stop(self):
        """Méthode exécutée à la fermeture de l'application."""
        self.logger.info("Fermeture de l'application. Nettoyage de la session SSO.")
        try:
            if self.mqtt_service and self.mqtt_service.connection_state == 'connected':
                # Récupérer le topic du token SSO
                sso_config = self.config_service.get_config('sso')
                token_topic = sso_config.get('token_topic')
                
                if token_topic:
                    # Publier un message vide pour effacer le token retenu sur le broker
                    self.logger.info(f"Nettoyage du token SSO sur le topic '{token_topic}'.")
                    self.mqtt_service.publish(topic=token_topic, message="", retain=True)
                
                # Déconnexion propre du service MQTT
                self.mqtt_service.disconnect()
                self.logger.info("Service MQTT déconnecté proprement.")
        except Exception as e:
            self.logger.error(f"Erreur lors du nettoyage à la fermeture : {e}", exc_info=True)


if __name__ == "__main__":
    HighCloudRPASApp().run()
