from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.snackbar.snackbar import MDSnackbarText
from app.services.firebase_service import FirebaseService
import os

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
        
    def validate_input(self, email, password):
        """Valide les champs de saisie"""
        if not email:
            self.show_error("Veuillez entrer votre email")
            return False
        if not password:
            self.show_error("Veuillez entrer votre mot de passe")
            return False
        return True
        
    def show_error(self, message):
        """Affiche un message d'erreur"""
        snackbar = MDSnackbar(
            MDSnackbarText(
                text=message,
            ),
            y=24,
            pos_hint={"center_x": 0.5},
            duration=3
        )
        snackbar.open()
        
    def show_success(self, message):
        """Affiche un message de succès"""
        snackbar = MDSnackbar(
            MDSnackbarText(
                text=message,
            ),
            y=24,
            pos_hint={"center_x": 0.5},
            duration=2
        )
        snackbar.open()
            
    def on_login(self, email, password):
        """Gère la connexion de l'utilisateur"""
        if not self.validate_input(email, password):
            return
            
        try:
            user = self.firebase.sign_in_with_email_password(email, password)
            self.show_success("Connexion réussie !")
            self.manager.current = "main"
        except Exception as e:
            error_message = str(e)
            if "INVALID_LOGIN_CREDENTIALS" in error_message:
                self.show_error("Email ou mot de passe incorrect")
            else:
                self.show_error(f"Erreur de connexion : {str(e)}")
            
    def on_register(self, email, password):
        """Gère l'inscription d'un nouvel utilisateur"""
        if not self.validate_input(email, password):
            return
            
        try:
            user = self.firebase.create_user_with_email_password(email, password)
            self.show_success("Inscription réussie ! Vous pouvez maintenant vous connecter.")
        except Exception as e:
            error_message = str(e)
            if "EMAIL_EXISTS" in error_message:
                self.show_error("Cet email est déjà utilisé")
            elif "WEAK_PASSWORD" in error_message:
                self.show_error("Le mot de passe doit contenir au moins 6 caractères")
            else:
                self.show_error(f"Erreur d'inscription : {str(e)}")
            
    def on_forgot_password(self, email):
        """Gère la réinitialisation du mot de passe"""
        if not email:
            self.show_error("Veuillez entrer votre email")
            return
            
        try:
            self.firebase.send_password_reset_email(email)
            self.show_success("Un email de réinitialisation a été envoyé !")
        except Exception as e:
            error_message = str(e)
            if "EMAIL_NOT_FOUND" in error_message:
                self.show_error("Cet email n'existe pas")
            else:
                self.show_error(f"Erreur d'envoi : {str(e)}")
