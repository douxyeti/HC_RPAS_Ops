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
                return True
            return False
        except Exception as e:
            print(f"Erreur lors de la création du rôle : {e}")
            return False
            
    def update_role(self, role_id, role_data):
        """Met à jour un rôle existant"""
        try:
            self.db.update_document(self.collection, role_id, role_data)
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour du rôle : {e}")
            return False
            
    def delete_role(self, role_id):
        """Supprime un rôle"""
        try:
            self.db.delete_document(self.collection, role_id)
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression du rôle : {e}")
            return False
