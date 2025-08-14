"""
Contrôleur pour la gestion des tâches.
Suit le pattern MVC en séparant la logique métier de l'interface.
"""

from app.services.roles_manager_service import RolesManagerService

class TaskController:
    def __init__(self):
        self.roles_manager_service = RolesManagerService()
    
    def get_tasks(self, role_id=None):
        """Récupère les tâches pour un rôle donné ou toutes les tâches"""
        if role_id:
            return self.roles_manager_service.get_tasks_for_role(role_id)
        return self.roles_manager_service.get_all_tasks()
    
    def add_task(self, task_data):
        """Ajoute une nouvelle tâche"""
        return self.roles_manager_service.add_task(task_data)
    
    def update_task(self, task_id, task_data):
        """Met à jour une tâche existante"""
        return self.roles_manager_service.update_task(task_id, task_data)
    
    def delete_task(self, task_id):
        """Supprime une tâche"""
        return self.roles_manager_service.delete_task(task_id)
