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
            docs = self.db.collection(collection_name).stream()
            return {doc.id: doc.to_dict() for doc in docs}
        except Exception as e:
            print(f"Erreur lors de la récupération de la collection {collection_name}: {e}")
            return {}
            
    def get_document(self, collection_name, doc_id):
        """Récupère un document spécifique"""
        try:
            doc = self.db.collection(collection_name).document(doc_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération du document {doc_id}: {e}")
            return None
            
    def add_document(self, collection_name, data):
        """Ajoute un nouveau document à une collection"""
        try:
            doc_ref = self.db.collection(collection_name).add(data)
            return doc_ref[1].id
        except Exception as e:
            print(f"Erreur lors de l'ajout du document: {e}")
            return None
            
    def add_document_with_id(self, collection, doc_id, data):
        """Ajoute un nouveau document avec un ID spécifique dans une collection
        
        Args:
            collection: Nom de la collection
            doc_id: ID du document à créer
            data: Données du document
            
        Returns:
            bool: True si le document a été créé avec succès, False sinon
        """
        try:
            # Crée une référence au document avec l'ID spécifié
            doc_ref = self.db.collection(collection).document(doc_id)
            # Ajoute les données au document
            doc_ref.set(data)
            return True
        except Exception as e:
            print(f"Erreur lors de l'ajout du document : {e}")
            return False
            
    def update_document(self, collection_name, doc_id, data):
        """Met à jour un document existant"""
        try:
            self.db.collection(collection_name).document(doc_id).update(data)
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour du document {doc_id}: {e}")
            return False
            
    def delete_document(self, collection_name, doc_id):
        """Supprime un document"""
        try:
            self.db.collection(collection_name).document(doc_id).delete()
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression du document {doc_id}: {e}")
            return False
