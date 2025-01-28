import firebase_admin
from firebase_admin import credentials, firestore
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
            
            # Initialise Firebase avec les credentials
            cred = credentials.Certificate(config)
            firebase_admin.initialize_app(cred)
            
            # Initialise Firestore
            self.db = firestore.client()
            print("Firebase initialisé avec succès")

        except Exception as e:
            print(f"Erreur lors de l'initialisation de Firebase: {str(e)}")
            raise

    def get_collection(self, collection_name):
        """Récupère une collection Firestore"""
        return self.db.collection(collection_name)

    def add_document(self, collection_name, data):
        """Ajoute un document à une collection"""
        return self.db.collection(collection_name).add(data)

    def update_document(self, collection_name, document_id, data):
        """Met à jour un document existant"""
        return self.db.collection(collection_name).document(document_id).update(data)

    def delete_document(self, collection_name, document_id):
        """Supprime un document"""
        return self.db.collection(collection_name).document(document_id).delete()

    def get_document(self, collection_name, document_id):
        """Récupère un document spécifique"""
        return self.db.collection(collection_name).document(document_id).get()

    def get_all_documents(self, collection_name):
        """Récupère tous les documents d'une collection"""
        return self.db.collection(collection_name).stream()
