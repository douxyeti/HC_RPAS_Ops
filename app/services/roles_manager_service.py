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
                      - name: Nom du rôle
                      - description: Description du rôle
                      - tasks: Liste des tâches associées
        """
        try:
            role_id = self.db.add_document(self.collection, role_data)
            if role_id:
                role_data['id'] = role_id
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
