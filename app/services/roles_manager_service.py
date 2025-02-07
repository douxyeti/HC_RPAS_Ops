from app.services.firebase_service import FirebaseService

class RolesManagerService:
    """Service pour la gestion des rôles et leurs tâches"""
    
    def __init__(self):
        self.db = FirebaseService()
        self.collection = 'roles'
        
    def get_all_roles(self):
        """Récupère tous les rôles"""
        return self.db.get_collection(self.collection)
        
    def get_role(self, role_id):
        """Récupère un rôle par son ID"""
        return self.db.get_document(self.collection, role_id)
        
    def create_role(self, role_data):
        """Crée un nouveau rôle
        
        Args:
            role_data: Dictionnaire contenant les données du rôle :
                      - id: Identifiant unique du rôle
                      - name: Nom du rôle
                      - description: Description du rôle
                      - tasks: Liste des tâches associées
        """
        try:
            # Vérifie que l'ID est présent
            if 'id' not in role_data:
                print("Erreur: l'ID du rôle est requis")
                return False
                
            # Initialise la liste des tâches si elle n'existe pas
            if 'tasks' not in role_data:
                role_data['tasks'] = []
                
            # Utilise l'ID fourni pour créer le document
            if self.db.add_document_with_id(self.collection, role_data['id'], role_data):
                # Met à jour la liste des rôles disponibles dans l'application
                from kivymd.app import MDApp
                app = MDApp.get_running_app()
                if hasattr(app, 'available_roles'):
                    app.available_roles.append(role_data['name'])
                    app.available_roles.sort()
                return True
            return False
        except Exception as e:
            print(f"Erreur lors de la création du rôle : {e}")
            return False
            
    def update_role(self, role_id, role_data):
        """Met à jour un rôle existant"""
        try:
            old_role = self.get_role(role_id)
            if self.db.update_document(self.collection, role_id, role_data):
                # Met à jour la liste des rôles disponibles dans l'application
                from kivymd.app import MDApp
                app = MDApp.get_running_app()
                if hasattr(app, 'available_roles') and old_role:
                    if old_role.get('name') in app.available_roles:
                        app.available_roles.remove(old_role.get('name'))
                    app.available_roles.append(role_data['name'])
                    app.available_roles.sort()
                return True
            return False
        except Exception as e:
            print(f"Erreur lors de la mise à jour du rôle : {e}")
            return False
            
    def delete_role(self, role_id):
        """Supprime un rôle"""
        try:
            role = self.get_role(role_id)
            if self.db.delete_document(self.collection, role_id):
                # Met à jour la liste des rôles disponibles dans l'application
                from kivymd.app import MDApp
                app = MDApp.get_running_app()
                if hasattr(app, 'available_roles') and role:
                    if role.get('name') in app.available_roles:
                        app.available_roles.remove(role.get('name'))
                return True
            return False
        except Exception as e:
            print(f"Erreur lors de la suppression du rôle : {e}")
            return False
            
    def get_role_tasks(self, role_id):
        """Récupère toutes les tâches d'un rôle
        
        Args:
            role_id: ID du rôle
            
        Returns:
            Liste des tâches du rôle ou liste vide si le rôle n'existe pas
        """
        role = self.get_role(role_id)
        if role and 'tasks' in role:
            return role['tasks']
        return []
        
    def add_task(self, role_id, task_data):
        """Ajoute une nouvelle tâche à un rôle
        
        Args:
            role_id: ID du rôle
            task_data: Dictionnaire contenant les données de la tâche :
                      - name: Nom de la tâche
                      - description: Description de la tâche
                      - module: Module associé (operations, maintenance, etc.)
                      - icon: Icône de la tâche
                      
        Returns:
            True si la tâche a été ajoutée avec succès, False sinon
        """
        try:
            role = self.get_role(role_id)
            if not role:
                return False
                
            # Initialise la liste des tâches si elle n'existe pas
            if 'tasks' not in role:
                role['tasks'] = []
                
            # Ajoute la nouvelle tâche
            role['tasks'].append(task_data)
            
            # Met à jour le rôle
            return self.update_role(role_id, role)
        except Exception as e:
            print(f"Erreur lors de l'ajout de la tâche : {e}")
            return False
            
    def update_task(self, role_id: str, task_index: int, task_data: dict) -> bool:
        """Met à jour une tâche existante pour un rôle donné.

        Args:
            role_id (str): L'ID du rôle
            task_index (int): L'index de la tâche à mettre à jour
            task_data (dict): Les nouvelles données de la tâche

        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        try:
            # Récupérer le rôle
            role_ref = self.db.collection('roles').document(role_id)
            role = role_ref.get()
            
            if not role.exists:
                return False
            
            # Récupérer les données du rôle
            role_data = role.to_dict()
            
            # Vérifier que l'index est valide
            if 'tasks' not in role_data or task_index >= len(role_data['tasks']):
                return False
            
            # Mettre à jour la tâche
            role_data['tasks'][task_index] = task_data
            
            # Sauvegarder les modifications
            role_ref.update(role_data)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la tâche : {str(e)}")
            return False
            
    def delete_task(self, role_id, task_index):
        """Supprime une tâche
        
        Args:
            role_id: ID du rôle
            task_index: Index de la tâche à supprimer
            
        Returns:
            True si la tâche a été supprimée avec succès, False sinon
        """
        try:
            role = self.get_role(role_id)
            if not role or 'tasks' not in role or task_index >= len(role['tasks']):
                return False
                
            # Supprime la tâche
            role['tasks'].pop(task_index)
            
            # Met à jour le rôle
            return self.update_role(role_id, role)
        except Exception as e:
            print(f"Erreur lors de la suppression de la tâche : {e}")
            return False
