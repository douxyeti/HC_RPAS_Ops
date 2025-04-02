from app.services.roles_manager_service import RolesManagerService
from app.models.role import Role

class RoleController:
    """Contrôleur pour la gestion des rôles"""
    
    def __init__(self):
        """Initialise le contrôleur avec le service de gestion des rôles"""
        self.service = RolesManagerService()
        
    def get_all_roles(self):
        """Récupère tous les rôles
        
        Returns:
            list: Liste d'objets Role
        """
        roles_data = self.service.get_all_roles()
        return [Role.from_dict(role_data) for role_data in roles_data]
        
    def get_role_by_name(self, role_name):
        """Récupère un rôle par son nom
        
        Args:
            role_name (str): Nom du rôle à récupérer
            
        Returns:
            Role: Instance de Role ou None si non trouvé
        """
        role_data = self.service.get_role_by_name(role_name)
        return Role.from_dict(role_data) if role_data else None
        
    def get_role(self, role_id):
        """Récupère un rôle par son ID
        
        Args:
            role_id (str): ID du rôle à récupérer
            
        Returns:
            Role: Instance de Role ou None si non trouvé
        """
        role_data = self.service.get_role(role_id)
        return Role.from_dict(role_data) if role_data else None
        
    def create_role(self, role_data):
        """Crée un nouveau rôle
        
        Args:
            role_data (dict): Données du rôle à créer
            
        Returns:
            Role: Instance du rôle créé
        """
        created_data = self.service.create_role(role_data)
        return Role.from_dict(created_data) if created_data else None
        
    def update_role(self, role_id, role_data):
        """Met à jour un rôle existant
        
        Args:
            role_id (str): ID du rôle à mettre à jour
            role_data (dict): Nouvelles données du rôle
            
        Returns:
            Role: Instance du rôle mis à jour
        """
        updated_data = self.service.update_role(role_id, role_data)
        return Role.from_dict(updated_data) if updated_data else None
        
    def delete_role(self, role_id):
        """Supprime un rôle
        
        Args:
            role_id (str): ID du rôle à supprimer
            
        Returns:
            bool: True si supprimé avec succès, False sinon
        """
        return self.service.delete_role(role_id)
