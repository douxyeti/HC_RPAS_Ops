import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
import pyrebase
from .config_service import ConfigService

class FirebaseService:
    _instance = None

    def __init__(self):
        config = ConfigService().get_firebase_config()
        
        # Initialisation de Pyrebase pour l'authentification
        self.firebase = pyrebase.initialize_app(config['firebase'])
        self.auth_client = self.firebase.auth()
        
        # Initialisation de l'Admin SDK avec les permissions par défaut
        if not firebase_admin._apps:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': config['firebase']['projectId'],
                'storageBucket': config['firebase']['storageBucket']
            })
        
        self.auth = auth
        self.db = firestore.client()
        self.storage = storage

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = FirebaseService()
        return cls._instance

    def sign_in_with_email_password(self, email, password):
        """Authentifie un utilisateur avec email/mot de passe"""
        try:
            user = self.auth_client.sign_in_with_email_and_password(email, password)
            return user
        except Exception as e:
            print(f"Erreur d'authentification: {str(e)}")
            raise

    def create_user_with_email_password(self, email, password):
        """Crée un nouvel utilisateur"""
        try:
            user = self.auth_client.create_user_with_email_and_password(email, password)
            return user
        except Exception as e:
            print(f"Erreur lors de la création de l'utilisateur: {str(e)}")
            raise

    def get_data(self, path):
        """Récupère des données de la base de données temps réel"""
        try:
            return self.db.collection(path).get()
        except Exception as e:
            print(f"Erreur lors de la récupération des données: {str(e)}")
            raise

    def set_data(self, path, data):
        """Définit des données dans la base de données temps réel"""
        try:
            self.db.collection(path).document().set(data)
        except Exception as e:
            print(f"Erreur lors de l'écriture des données: {str(e)}")
            raise

    def update_data(self, path, data):
        """Met à jour des données dans la base de données temps réel"""
        try:
            self.db.collection(path).document().update(data)
        except Exception as e:
            print(f"Erreur lors de la mise à jour des données: {str(e)}")
            raise

    def delete_data(self, path):
        """Supprime des données de la base de données temps réel"""
        try:
            self.db.collection(path).document().delete()
        except Exception as e:
            print(f"Erreur lors de la suppression des données: {str(e)}")
            raise

    def upload_file(self, file_path, storage_path):
        """Upload un fichier vers Firebase Storage"""
        try:
            self.storage.bucket().blob(storage_path).upload_from_filename(file_path)
        except Exception as e:
            print(f"Erreur lors de l'upload du fichier: {str(e)}")
            raise

    def get_file_url(self, storage_path):
        """Récupère l'URL de téléchargement d'un fichier"""
        try:
            return self.storage.bucket().blob(storage_path).public_url
        except Exception as e:
            print(f"Erreur lors de la récupération de l'URL: {str(e)}")
            raise
