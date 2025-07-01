from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.app import MDApp
from app.services.firebase_service import FirebaseService
import os
import json
import base64

class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "login"
        self.firebase = FirebaseService()
        
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        if os.getenv('DEBUG_MODE') == 'True':
            self.ids.email.text = os.getenv('DEV_EMAIL', '')
            self.ids.password.text = os.getenv('DEV_PASSWORD', '')
        
    def on_login(self, email, password):
        """Gère la connexion de l'utilisateur et met à jour le dictionnaire de sessions SSO."""
        try:
            user = self.firebase.sign_in_with_email_password(email, password)
            app = MDApp.get_running_app()
            app.logger.info("Connexion réussie !")

            # Marquer cette instance comme la source de la connexion SSO
            app.is_primary_instance = True
            
            # Tenter de mettre à jour le dictionnaire des sessions SSO
            try:
                uid = user.get('localId')
                # Utiliser la nouvelle clé de configuration pour le topic des sessions
                session_topic = app.config_service.get_config('sso.session_topic')
                device_id = app.device_id
                
                if uid and session_topic and device_id and app.mqtt_service and app.encryption_service:
                    # Créer un jeton personnalisé pour le SSO
                    custom_token_bytes = self.firebase.create_custom_token(uid)
                    custom_token_str = custom_token_bytes.decode('utf-8')
                    
                    encrypted_token = app.encryption_service.encrypt(custom_token_str)
                    
                    # Encoder le token chiffré (bytes) en une chaîne Base64 pour la sérialisation JSON
                    encoded_token = base64.b64encode(encrypted_token).decode('utf-8')
                    
                    # Mettre à jour le dictionnaire des sessions
                    # app.sso_sessions contient déjà le dictionnaire actuel
                    app.sso_sessions[device_id] = encoded_token
                    
                    # Sérialiser et publier le dictionnaire mis à jour
                    sessions_payload = json.dumps(app.sso_sessions)
                    
                    app.mqtt_service.publish(
                        topic=session_topic,
                        message=sessions_payload,
                        qos=1,
                        retain=True
                    )
                    app.logger.info(f"Dictionnaire des sessions SSO mis à jour et publié sur '{session_topic}'.")
                else:
                    app.logger.warning("Publication SSO annulée: informations ou service manquant.")
            except Exception as e:
                app.logger.error(f"Erreur lors de la mise à jour du dictionnaire SSO: {e}", exc_info=True)

            # Quoi qu'il arrive, on redirige vers le dashboard après une connexion réussie
            self.manager.current = "dashboard"
            
        except Exception as e:
            app = MDApp.get_running_app()
            if app:
                app.logger.error(f"Erreur de connexion : {e}", exc_info=True)
            else:
                print(f"Erreur de connexion : {e}")
            
    def on_register(self, email, password):
        """Gère l'inscription d'un nouvel utilisateur"""
        try:
            user = self.firebase.create_user_with_email_password(email, password)
            print("Inscription réussie !")
            self.manager.current = "dashboard"  # Redirection vers le dashboard
        except Exception as e:
            print(f"Erreur d'inscription : {e}")
            
    def on_forgot_password(self, email):
        """Gère la réinitialisation du mot de passe"""
        try:
            self.firebase.auth.send_password_reset_email(email)
            print("Email de réinitialisation envoyé !")
        except Exception as e:
            print(f"Erreur d'envoi : {e}")
