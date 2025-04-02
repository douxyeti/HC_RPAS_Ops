class Role:
    """Modèle représentant un rôle dans l'application"""
    
    def __init__(self, id=None, name=None, description=None, permissions=None, tasks=None):
        """Initialise un nouveau rôle
        
        Args:
            id (str): Identifiant unique du rôle
            name (str): Nom du rôle
            description (str): Description du rôle
            permissions (list): Liste des permissions associées au rôle
            tasks (list): Liste des tâches associées au rôle
        """
        self.id = id
        self.name = name
        self.description = description
        self.permissions = permissions or []
        self.tasks = tasks or []
        
    @classmethod
    def from_dict(cls, data):
        """Crée une instance de Role à partir d'un dictionnaire
        
        Args:
            data (dict): Données du rôle
            
        Returns:
            Role: Instance de Role
        """
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            permissions=data.get('permissions', []),
            tasks=data.get('tasks', [])
        )
        
    def to_dict(self):
        """Convertit l'instance en dictionnaire
        
        Returns:
            dict: Représentation du rôle en dictionnaire
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions,
            'tasks': self.tasks
        }
        
    def has_permission(self, permission):
        """Vérifie si le rôle a une permission spécifique
        
        Args:
            permission (str): Permission à vérifier
            
        Returns:
            bool: True si le rôle a la permission, False sinon
        """
        return 'all' in self.permissions or permission in self.permissions
