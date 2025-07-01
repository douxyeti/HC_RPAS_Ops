from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import SlideTransition
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.logger import Logger
from app.utils.device_utils import get_or_create_device_id
from kivy.clock import Clock
from dotenv import load_dotenv
import os
import logging
from threading import Event
import json
import base64

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
        self.sso_check_finished = Event()
        self.device_id = None
        self.session_topic = None  # Le topic unique pour le dictionnaire des sessions
        self.sso_sessions = {}     # Le dictionnaire des sessions actives
        self.config_service = None
        self.firebase_service = None
        self.mqtt_service = None
        self.encryption_service = None
        self.roles_manager_service = None
        self.current_role = None
        self.available_roles = []  # Sera chargé depuis Firebase
        self.is_primary_instance = False  # Indicateur pour la session SSO
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
        
        # La vérification SSO est maintenant déclenchée par l'écran de démarrage.

        return self.screen_manager

    def on_start(self):
        """Méthode appelée au démarrage de l'application."""
        self.logger.info("L'application a démarré.")
        # Initialisation de l'ID de l'appareil et du topic de session SSO
        self.device_id = get_or_create_device_id(self)
        self.session_topic = self.config_service.get_config('sso').get('session_topic')
        if not self.session_topic:
            self.logger.error("Le topic de session SSO n'est pas défini dans la configuration.")
        else:
            self.logger.info(f"Device ID: {self.device_id}")
            self.logger.info(f"SSO Session Topic: {self.session_topic}")

            # Lance la vérification SSO au démarrage pour la connexion automatique
            self._check_for_sso_session()
        
    def on_stop(self):
        """Méthode appelée à la fermeture de l'application."""
        self.logger.info("on_stop: Début de la procédure de fermeture.")

        # 1. Nettoyage de la session SSO de cet appareil
        self.logger.info("on_stop: Tentative de nettoyage de la session SSO.")
        if self.mqtt_service and self.mqtt_service.connection_state == 'connected' and self.session_topic and self.device_id in self.sso_sessions:
            self.logger.info(f"on_stop: Nettoyage de la session SSO pour l'appareil {self.device_id}.")
            try:
                # NOTE: La logique de publication d'un dictionnaire mis à jour est désactivée
                # pour éviter les conditions de course où une instance qui se ferme
                # avec un état obsolète pourrait écraser la session partagée.
                # La session de cet appareil expirera d'elle-même.
                self.logger.info("on_stop: La logique de mise à jour de la session partagée est désactivée pour des raisons de sécurité.")
                # del self.sso_sessions[self.device_id]
                
                # # Publier le dictionnaire mis à jour
                # payload = json.dumps(self.sso_sessions)
                # self.mqtt_service.client.publish(self.session_topic, payload, qos=1, retain=True)
                # self.logger.info("on_stop: Dictionnaire des sessions mis à jour publié sur MQTT.")
            except Exception as e:
                self.logger.error(f"on_stop: Erreur lors du nettoyage de la session SSO: {e}", exc_info=True)
        else:
            self.logger.warning("on_stop: Conditions non remplies pour le nettoyage de la session SSO.")

        # 2. Déconnexion propre du client MQTT
        self.logger.info("on_stop: Tentative de déconnexion de MQTT...")
        if self.mqtt_service:
            self.mqtt_service.disconnect()
            self.logger.info("on_stop: Appel à mqtt_service.disconnect() effectué.")
        else:
            self.logger.warning("on_stop: mqtt_service non disponible, déconnexion impossible.")

        # 3. Déconnexion propre de Firebase pour éviter les erreurs gRPC
        self.logger.info("on_stop: Tentative de déconnexion de Firebase...")
        if self.firebase_service:
            self.firebase_service.disconnect()
            self.logger.info("on_stop: Appel à firebase_service.disconnect() effectué.")
        else:
            self.logger.warning("on_stop: firebase_service non disponible, déconnexion impossible.")
        
        self.logger.info("on_stop: Procédure de fermeture terminée.")

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
        """S'abonne au topic des sessions SSO et vérifie la présence d'une session pour cet appareil."""
        if not self.mqtt_service or self.mqtt_service.connection_state != 'connected' or not self.session_topic:
            self.logger.warning("SSO Check: Prérequis non remplis (MQTT non connecté ou topic non configuré). La vérification est annulée.")
            self.sso_check_finished.set()
            Clock.schedule_once(lambda dt: self.switch_screen("login"), 2)
            return

        self.logger.info(f"SSO Check: Abonnement au topic des sessions '{self.session_topic}'.")
        self.mqtt_service.client.subscribe(self.session_topic)
        self.mqtt_service.register_callback(self.session_topic, self._on_sso_message)
        
        # Laisse un peu de temps pour recevoir le message retenu
        Clock.schedule_once(self._sso_timeout, 2)

    def _on_sso_message(self, dt, topic, payload):
        """Callback pour la réception du dictionnaire des sessions SSO."""
        try:
            if not payload: # Message vide, le dictionnaire est vide
                self.sso_sessions = {}
                self.logger.info("SSO Check: Dictionnaire des sessions vide reçu.")
            elif isinstance(payload, dict):
                self.sso_sessions = payload
                self.logger.info(f"SSO Check: Dictionnaire des sessions reçu avec {len(self.sso_sessions)} session(s).")
            else:
                self.logger.warning(f"SSO Check: Payload inattendu de type {type(payload)}.")
                return
            
            # Vérifier si notre appareil a une session active
            if self.device_id in self.sso_sessions:
                self.logger.info("SSO Check: Session trouvée pour cet appareil. Tentative de connexion automatique.")
                encoded_token = self.sso_sessions.get(self.device_id)
                if encoded_token:
                    self._sso_login(encoded_token)
            else:
                self.logger.info("SSO Check: Aucune session active pour cet appareil.")

        except Exception as e:
            self.logger.error(f"SSO Check: Erreur inattendue lors du traitement du message SSO: {e}", exc_info=True)
        finally:
            # Indiquer que la vérification initiale est terminée
            if not self.sso_check_finished.is_set():
                self.sso_check_finished.set()

    def _sso_timeout(self, dt):
        """Gère le timeout de la vérification SSO."""
        if not self.sso_check_finished.is_set():
            self.logger.info("SSO Check: Timeout. Aucune session trouvée pour cet appareil.")
        self.sso_check_finished.set()

    def _sso_login(self, encoded_token):
        """Tente de se connecter en utilisant un token SSO."""
        try:
            # Décoder la chaîne Base64 en bytes avant le déchiffrement
            encrypted_token_bytes = base64.b64decode(encoded_token)
            decrypted_token = self.encryption_service.decrypt(encrypted_token_bytes)
            user_tokens = self.firebase_service.sign_in_with_custom_token(decrypted_token)
            
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
            pilot_doc = self.firebase_service.get_document('pilots', user_id)

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
        """Initialise tous les services dans le bon ordre."""
        try:
            # 1. Service de configuration
            self.config_service = ConfigService()
            self.logger.info("Service de configuration initialisé")

            # 2. Service MQTT (optionnel)
            if self.config_service.get_config('mqtt.enabled', False):
                self.logger.info("Initialisation du service MQTT...")
                self.mqtt_service = MQTTService()
                broker = self.config_service.get_config('mqtt.broker', 'localhost')
                port = int(self.config_service.get_config('mqtt.port', 1883))
                self.mqtt_service.connect(broker, port)
                self.logger.info(f"Service MQTT connecté à {broker}:{port}")
            else:
                self.logger.info("Service MQTT désactivé dans la configuration")

            # 3. Service Firebase
            self.logger.info("Initialisation du service Firebase...")
            self.firebase_service = FirebaseService.get_instance()
            self.logger.info("Service Firebase initialisé")

            # 4. Vider le cache et lancer l'indexation des modules
            self.logger.info("Préparation de l'indexation des modules...")
            try:
                # Vider le cache pour forcer la relecture depuis Firebase
                self.logger.debug("Nettoyage du cache des modules...")
                self.firebase_service.clear_cache(prefix="module_indexes")
                
                # Lancer l'indexation
                self.logger.info("Lancement de l'indexation...")
                module_initializer = get_module_initializer()
                module_initializer.initialize_with_services(self.firebase_service)
                self.logger.info("Indexation des modules terminée.")
            except Exception as e:
                self.logger.error(f"Erreur critique lors de l'indexation des modules: {e}", exc_info=True)
            
            # 5. Service de gestion des rôles
            self.logger.info("Initialisation du service de gestion des rôles...")
            self.roles_manager_service = RolesManagerService()
            
            # 6. Chargement des rôles
            self.logger.info("Chargement des rôles depuis Firebase...")
            roles_data = self.roles_manager_service.get_all_roles()
            self.available_roles = [role.get('name') for role in roles_data if role.get('name')]
            self.available_roles.sort()
            self.logger.info(f"{len(self.available_roles)} rôles chargés")

            # Initialise le service de chiffrement
            self.logger.info("Initialisation du service de chiffrement...")
            self.encryption_service = EncryptionService()
            self.logger.info("Service de chiffrement initialisé")

        except Exception as e:
            self.logger.error(f"Échec de l'initialisation d'un service critique: {e}", exc_info=True)
            raise




if __name__ == "__main__":
    HighCloudRPASApp().run()
