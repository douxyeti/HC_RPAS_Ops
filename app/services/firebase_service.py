import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
import pyrebase
from .config_service import ConfigService

class FirebaseService:
    _instance = None

    def __init__(self):
        config = ConfigService().get_firebase_config()
        
        # Initialisation de Pyrebase pour l'authentification
        self.firebase = pyrebase.initialize_app(config)
        self.auth_client = self.firebase.auth()
        
        # Initialisation de l'Admin SDK avec les permissions par défaut
        if not firebase_admin._apps:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': config['projectId'],
                'storageBucket': config['storageBucket']
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

    def get_roles_and_tasks(self):
        """Récupère tous les rôles et leurs tâches depuis Firestore"""
        try:
            roles_ref = self.db.collection('roles').get()
            roles_data = {}
            for role in roles_ref:
                roles_data[role.id] = role.to_dict()
            return roles_data
        except Exception as e:
            print(f"Erreur lors de la récupération des rôles: {str(e)}")
            return None

    def update_role_and_tasks(self, role_id, role_data):
        """Met à jour ou crée un rôle et ses tâches dans Firestore"""
        try:
            self.db.collection('roles').document(role_id).set(role_data)
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour du rôle: {str(e)}")
            return False

    def migrate_roles_from_config(self, roles_config):
        """Migre les rôles depuis la configuration vers Firestore"""
        try:
            batch = self.db.batch()
            for role_id, role_data in roles_config.items():
                role_ref = self.db.collection('roles').document(role_id)
                batch.set(role_ref, role_data)
            batch.commit()
            return True
        except Exception as e:
            print(f"Erreur lors de la migration des rôles: {str(e)}")
            return False

    def get_collection(self, collection_name):
        """Récupère tous les documents d'une collection"""
        try:
            docs = self.db.collection(collection_name).get()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"Erreur lors de la récupération de la collection: {str(e)}")
            return []

    def get_document(self, collection_name, document_id):
        """Récupère un document spécifique"""
        print(f"[DEBUG] FirebaseService.get_document - Récupération du document {document_id} dans la collection {collection_name}")
        try:
            # Récupérer la référence du document
            doc_ref = self.db.collection(collection_name).document(document_id)
            print(f"[DEBUG] FirebaseService.get_document - Référence du document obtenue : {doc_ref.path}")
            
            # Récupérer le document
            doc = doc_ref.get()
            print(f"[DEBUG] FirebaseService.get_document - Document récupéré, existe : {doc.exists}")
            
            if doc.exists:
                data = doc.to_dict()
                print(f"[DEBUG] FirebaseService.get_document - Données du document : {data}")
                return data
            else:
                print(f"[DEBUG] FirebaseService.get_document - Le document {document_id} n'existe pas dans la collection {collection_name}")
                return None
        except Exception as e:
            print(f"[ERROR] FirebaseService.get_document - Erreur lors de la récupération du document : {str(e)}")
            return None

    def add_document_with_id(self, collection_name, document_id, data):
        """Ajoute un document avec un ID spécifique"""
        try:
            self.db.collection(collection_name).document(document_id).set(data)
            return True
        except Exception as e:
            print(f"Erreur lors de l'ajout du document: {str(e)}")
            return False

    def update_document(self, collection_name, document_id, data):
        """Met à jour un document spécifique"""
        try:
            self.db.collection(collection_name).document(document_id).update(data)
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour du document: {str(e)}")
            return False

    def delete_document(self, collection_name, document_id):
        """Supprime un document spécifique"""
        try:
            self.db.collection(collection_name).document(document_id).delete()
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression du document: {str(e)}")
            return False
