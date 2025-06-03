import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
import pyrebase
import time
import threading
from kivy.clock import Clock
from functools import partial
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
        
        # Cache pour optimiser les requêtes
        self._cache = {}
        self._cache_expiry = {}
        self._cache_timeout = 60  # Expiration du cache en secondes

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

    def get_roles_and_tasks_async(self, callback):
        """Version asynchrone de get_roles_and_tasks avec callback"""
        def fetch_data():
            # Vérifier d'abord le cache
            cache_key = self._get_cache_key("get_roles_and_tasks")
            if cache_key in self._cache and time.time() < self._cache_expiry.get(cache_key, 0):
                print(f"[DEBUG] FirebaseService.get_roles_and_tasks_async - Utilisation du cache")
                data = self._cache[cache_key]
                # Utiliser Clock pour appeler le callback dans le thread principal
                Clock.schedule_once(lambda dt: callback(data), 0)
                return
            
            print(f"[DEBUG] FirebaseService.get_roles_and_tasks_async - Récupération des rôles")
            try:
                roles_ref = self.db.collection('roles').get()
                roles_list = []
                for role in roles_ref:
                    role_data = role.to_dict()
                    role_data['id'] = role.id
                    roles_list.append(role_data)
                
                # Mettre en cache
                self._cache[cache_key] = roles_list
                self._cache_expiry[cache_key] = time.time() + self._cache_timeout
                
                # Appeler le callback dans le thread principal
                Clock.schedule_once(lambda dt: callback(roles_list), 0)
            except Exception as e:
                print(f"[ERROR] FirebaseService.get_roles_and_tasks_async - Erreur : {str(e)}")
                Clock.schedule_once(lambda dt: callback([]), 0)
        
        # Exécuter dans un thread séparé
        threading.Thread(target=fetch_data, daemon=True).start()

    def get_roles_and_tasks(self):
        """Récupère tous les rôles et leurs tâches depuis Firestore"""
        # Générer la clé de cache
        cache_key = self._get_cache_key("get_roles_and_tasks")
        
        # Vérifier si les données sont en cache et valides
        if cache_key in self._cache and time.time() < self._cache_expiry.get(cache_key, 0):
            print(f"[DEBUG] FirebaseService.get_roles_and_tasks - Utilisation du cache")
            return self._cache[cache_key]
        
        try:
            roles_ref = self.db.collection('roles').get()
            roles_list = []
            for role in roles_ref:
                role_data = role.to_dict()
                role_data['id'] = role.id
                roles_list.append(role_data)
            
            # Mettre en cache les résultats
            self._cache[cache_key] = roles_list
            self._cache_expiry[cache_key] = time.time() + self._cache_timeout
            
            return roles_list
        except Exception as e:
            print(f"Erreur lors de la récupération des rôles: {str(e)}")
            return []

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

    def get_collection_async(self, collection_name, callback):
        """Version asynchrone de get_collection avec callback"""
        def fetch_data():
            # Vérifier d'abord le cache
            cache_key = self._get_cache_key("get_collection", collection_name)
            if cache_key in self._cache and time.time() < self._cache_expiry.get(cache_key, 0):
                print(f"[DEBUG] FirebaseService.get_collection_async - Utilisation du cache pour {collection_name}")
                data = self._cache[cache_key]
                # Utiliser Clock pour appeler le callback dans le thread principal
                Clock.schedule_once(lambda dt: callback(data), 0)
                return
            
            print(f"[DEBUG] FirebaseService.get_collection_async - Récupération de la collection {collection_name}")
            try:
                docs = self.db.collection(collection_name).get()
                result = [doc.to_dict() for doc in docs]
                
                # Mettre en cache
                self._cache[cache_key] = result
                self._cache_expiry[cache_key] = time.time() + self._cache_timeout
                
                # Appeler le callback dans le thread principal
                Clock.schedule_once(lambda dt: callback(result), 0)
            except Exception as e:
                print(f"[ERROR] FirebaseService.get_collection_async - Erreur : {str(e)}")
                Clock.schedule_once(lambda dt: callback([]), 0)
        
        # Exécuter dans un thread séparé
        threading.Thread(target=fetch_data, daemon=True).start()

    def get_collection(self, collection_name):
        """Récupère tous les documents d'une collection"""
        # Générer la clé de cache
        cache_key = self._get_cache_key("get_collection", collection_name)
        
        # Vérifier si les données sont en cache et valides
        if cache_key in self._cache and time.time() < self._cache_expiry.get(cache_key, 0):
            print(f"[DEBUG] FirebaseService.get_collection - Utilisation du cache pour {collection_name}")
            return self._cache[cache_key]
            
        try:
            print(f"[DEBUG] FirebaseService.get_collection - Récupération de la collection {collection_name} depuis Firebase")
            docs = self.db.collection(collection_name).get()
            
            # Log pour voir combien de documents sont récupérés
            doc_count = len(docs) if docs else 0
            print(f"[DEBUG] FirebaseService.get_collection - {doc_count} documents récupérés dans {collection_name}")
            
            result = [doc.to_dict() for doc in docs]
            
            # Log pour afficher un aperçu des données récupérées
            if result:
                print(f"[DEBUG] FirebaseService.get_collection - Premier document: {str(result[0])[:200]}...")
            else:
                print(f"[DEBUG] FirebaseService.get_collection - Aucun document trouvé dans {collection_name}")
            
            # Mettre en cache les résultats
            self._cache[cache_key] = result
            self._cache_expiry[cache_key] = time.time() + self._cache_timeout
            
            return result
        except Exception as e:
            print(f"Erreur lors de la récupération de la collection: {str(e)}")
            return []

    def _get_cache_key(self, method, *args):
        """Génère une clé unique pour le cache"""
        return f"{method}:{':'.join(str(arg) for arg in args)}"

    def get_document_async(self, collection_name, document_id, callback):
        """Version asynchrone de get_document avec callback pour éviter de bloquer l'interface"""
        def fetch_data():
            # Vérifier d'abord le cache
            cache_key = self._get_cache_key("get_document", collection_name, document_id)
            if cache_key in self._cache and time.time() < self._cache_expiry.get(cache_key, 0):
                print(f"[DEBUG] FirebaseService.get_document_async - Utilisation du cache pour {document_id} dans {collection_name}")
                data = self._cache[cache_key]
                # Utiliser Clock pour appeler le callback dans le thread principal
                Clock.schedule_once(lambda dt: callback(data), 0)
                return
                
            print(f"[DEBUG] FirebaseService.get_document_async - Récupération du document {document_id} dans la collection {collection_name}")
            try:
                # Récupérer la référence du document
                doc_ref = self.db.collection(collection_name).document(document_id)
                
                # Récupérer le document
                doc = doc_ref.get()
                
                if doc.exists:
                    data = doc.to_dict()
                    print(f"[DEBUG] FirebaseService.get_document_async - Données du document récupérées")
                    
                    # Mettre en cache
                    self._cache[cache_key] = data
                    self._cache_expiry[cache_key] = time.time() + self._cache_timeout
                    
                    # Appeler le callback dans le thread principal
                    Clock.schedule_once(lambda dt: callback(data), 0)
                else:
                    print(f"[DEBUG] FirebaseService.get_document_async - Le document {document_id} n'existe pas")
                    Clock.schedule_once(lambda dt: callback(None), 0)
            except Exception as e:
                print(f"[ERROR] FirebaseService.get_document_async - Erreur : {str(e)}")
                Clock.schedule_once(lambda dt: callback(None), 0)
        
        # Exécuter dans un thread séparé
        threading.Thread(target=fetch_data, daemon=True).start()

    def get_document(self, collection_name, document_id):
        """Récupère un document spécifique"""
        # Générer la clé de cache
        cache_key = self._get_cache_key("get_document", collection_name, document_id)
        
        # Vérifier si les données sont en cache et valides
        if cache_key in self._cache and time.time() < self._cache_expiry.get(cache_key, 0):
            print(f"[DEBUG] FirebaseService.get_document - Utilisation du cache pour {document_id} dans {collection_name}")
            return self._cache[cache_key]
        
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
                
                # Mettre en cache les résultats
                self._cache[cache_key] = data
                self._cache_expiry[cache_key] = time.time() + self._cache_timeout
                
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
            
            # Invalider le cache de la collection entière
            cache_key = self._get_cache_key("get_collection", collection_name)
            if cache_key in self._cache:
                del self._cache[cache_key]
                if cache_key in self._cache_expiry:
                    del self._cache_expiry[cache_key]
            
            return True
        except Exception as e:
            print(f"Erreur lors de l'ajout du document: {str(e)}")
            return False

    def update_document(self, collection_name, document_id, data):
        """Met à jour un document spécifique"""
        try:
            self.db.collection(collection_name).document(document_id).update(data)
            
            # Invalider le cache pour ce document
            cache_key = self._get_cache_key("get_document", collection_name, document_id)
            if cache_key in self._cache:
                del self._cache[cache_key]
                if cache_key in self._cache_expiry:
                    del self._cache_expiry[cache_key]
            
            # Invalider aussi le cache de la collection entière
            cache_key = self._get_cache_key("get_collection", collection_name)
            if cache_key in self._cache:
                del self._cache[cache_key]
                if cache_key in self._cache_expiry:
                    del self._cache_expiry[cache_key]
            
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour du document: {str(e)}")
            return False

    def delete_document(self, collection_name, document_id):
        """Supprime un document spécifique"""
        try:
            self.db.collection(collection_name).document(document_id).delete()
            
            # Invalider le cache pour ce document
            cache_key = self._get_cache_key("get_document", collection_name, document_id)
            if cache_key in self._cache:
                del self._cache[cache_key]
                if cache_key in self._cache_expiry:
                    del self._cache_expiry[cache_key]
            
            # Invalider aussi le cache de la collection entière
            cache_key = self._get_cache_key("get_collection", collection_name)
            if cache_key in self._cache:
                del self._cache[cache_key]
                if cache_key in self._cache_expiry:
                    del self._cache_expiry[cache_key]
            
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression du document: {str(e)}")
            return False

    def clear_cache(self):
        """Vide entièrement le cache"""
        self._cache = {}
        self._cache_expiry = {}
        print("[DEBUG] FirebaseService - Cache vidé")
