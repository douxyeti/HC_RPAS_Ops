from kivymd.uix.screen import MDScreen
import os

class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "login"
        
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        if os.getenv('DEBUG_MODE') == 'True':
            self.ids.email.text = os.getenv('DEV_EMAIL', '')
            self.ids.password.text = os.getenv('DEV_PASSWORD', '')
        
    def on_login(self, email, password):
        """Gère la connexion de l'utilisateur"""
        try:
            print("Connexion réussie !")
            self.manager.current = "dashboard"  # Redirection vers le dashboard
        except Exception as e:
            print(f"Erreur de connexion : {e}")
            
    def on_forgot_password(self, email):
        """Gère la réinitialisation du mot de passe"""
        try:
            print("Email de réinitialisation envoyé !")
        except Exception as e:
            print(f"Erreur d'envoi : {e}")
