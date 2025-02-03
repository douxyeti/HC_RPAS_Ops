import os
import pyrebase
from dotenv import load_dotenv

class FirebaseService:
    def __init__(self):
        """Initialise le service Firebase avec les configurations depuis .env"""
        load_dotenv()
        
        # Configuration Firebase
        self.config = {
            "apiKey": os.getenv('FIREBASE_API_KEY'),
            "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
            "databaseURL": os.getenv('FIREBASE_DATABASE_URL'),
            "projectId": os.getenv('FIREBASE_PROJECT_ID'),
            "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
            "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
            "appId": os.getenv('FIREBASE_APP_ID'),
            "measurementId": os.getenv('FIREBASE_MEASUREMENT_ID')
        }
        
        # Initialise Firebase
        self.firebase = pyrebase.initialize_app(self.config)
        self.auth = self.firebase.auth()
        self.db = self.firebase.database()
        
    def sign_in_with_email_password(self, email, password):
        """Connecte un utilisateur avec email/mot de passe"""
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            return user
        except Exception as e:
            print(f"Erreur de connexion : {str(e)}")
            raise
            
    def create_user_with_email_password(self, email, password):
        """Crée un nouvel utilisateur avec email/mot de passe"""
        try:
            user = self.auth.create_user_with_email_and_password(email, password)
            return user
        except Exception as e:
            print(f"Erreur de création d'utilisateur : {str(e)}")
            raise
            
    def send_password_reset_email(self, email):
        """Envoie un email de réinitialisation de mot de passe"""
        try:
            self.auth.send_password_reset_email(email)
        except Exception as e:
            print(f"Erreur d'envoi d'email : {str(e)}")
            raise
