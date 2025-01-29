import pyrebase
from .config_service import ConfigService

class FirebaseService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialise la connexion Firebase"""
        try:
            # Obtient la configuration Firebase
            config = ConfigService().get_firebase_config()
            
            # Initialise Firebase
            self.firebase = pyrebase.initialize_app(config)
            
            # Initialise les services
            self.auth = self.firebase.auth()
            self.db = self.firebase.database()
            self.storage = self.firebase.storage()
            
            print("Firebase initialisé avec succès")

        except Exception as e:
            print(f"Erreur lors de l'initialisation de Firebase: {str(e)}")
            raise

    def sign_in_with_email_password(self, email, password):
        """Authentifie un utilisateur avec email/mot de passe"""
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            return user
        except Exception as e:
            print(f"Erreur d'authentification: {str(e)}")
            raise

    def create_user_with_email_password(self, email, password):
        """Crée un nouvel utilisateur"""
        try:
            user = self.auth.create_user_with_email_and_password(email, password)
            return user
        except Exception as e:
            print(f"Erreur lors de la création de l'utilisateur: {str(e)}")
            raise

    def get_data(self, path):
        """Récupère des données de la base de données temps réel"""
        try:
            return self.db.child(path).get().val()
        except Exception as e:
            print(f"Erreur lors de la récupération des données: {str(e)}")
            raise

    def set_data(self, path, data):
        """Définit des données dans la base de données temps réel"""
        try:
            self.db.child(path).set(data)
        except Exception as e:
            print(f"Erreur lors de l'écriture des données: {str(e)}")
            raise

    def update_data(self, path, data):
        """Met à jour des données dans la base de données temps réel"""
        try:
            self.db.child(path).update(data)
        except Exception as e:
            print(f"Erreur lors de la mise à jour des données: {str(e)}")
            raise

    def delete_data(self, path):
        """Supprime des données de la base de données temps réel"""
        try:
            self.db.child(path).remove()
        except Exception as e:
            print(f"Erreur lors de la suppression des données: {str(e)}")
            raise

    def upload_file(self, file_path, storage_path):
        """Upload un fichier vers Firebase Storage"""
        try:
            self.storage.child(storage_path).put(file_path)
        except Exception as e:
            print(f"Erreur lors de l'upload du fichier: {str(e)}")
            raise

    def get_file_url(self, storage_path):
        """Récupère l'URL de téléchargement d'un fichier"""
        try:
            return self.storage.child(storage_path).get_url(None)
        except Exception as e:
            print(f"Erreur lors de la récupération de l'URL: {str(e)}")
            raise
