from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from app.services.firebase_service import FirebaseService

class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "login"
        self.firebase = FirebaseService()
        
    def on_login(self, email, password):
        """Gère la connexion de l'utilisateur"""
        try:
            user = self.firebase.sign_in_with_email_password(email, password)
            print("Connexion réussie !")
            self.manager.current = "dashboard"  # Redirection vers le dashboard
        except Exception as e:
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
