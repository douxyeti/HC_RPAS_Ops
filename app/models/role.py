class Role:
    """
    Modèle représentant un rôle dans l'application.
    Encapsule les données et le comportement liés aux rôles.
    """
    
    def __init__(self, role_id, name, permissions=None, tasks=None, description=None):
        """
        Initialise un nouveau rôle.
        
        Args:
            role_id (str): Identifiant unique du rôle
            name (str): Nom du rôle
            permissions (list): Liste des permissions associées au rôle
            tasks (list): Liste des tâches associées au rôle
            description (str, optional): Description du rôle
        """
        self.id = role_id
        self.name = name
        self.permissions = permissions or []
        self.tasks = tasks or []
        self.description = description

    @staticmethod
    def from_dict(data):
        """
        Crée une instance de Role à partir d'un dictionnaire.
        
        Args:
            data (dict): Dictionnaire contenant les données du rôle
            
        Returns:
            Role: Une nouvelle instance de Role
        """
        return Role(
            role_id=data.get('id'),
            name=data.get('name'),
            permissions=data.get('permissions', []),
            tasks=data.get('tasks', []),
            description=data.get('description')
        )

    def to_dict(self):
        """
        Convertit l'instance en dictionnaire.
        
        Returns:
            dict: Représentation du rôle sous forme de dictionnaire
        """
        return {
            'id': self.id,
            'name': self.name,
            'permissions': self.permissions,
            'tasks': self.tasks,
            'description': self.description
        }
