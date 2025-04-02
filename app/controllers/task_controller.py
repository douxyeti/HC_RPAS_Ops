"""
Contrôleur pour la gestion des tâches.
Suit le pattern MVC en séparant la logique métier de l'interface.
"""

from app.services.roles_manager_service import RolesManagerService
from app.models.task import Task

class TaskController:
    def __init__(self):
        self.roles_service = RolesManagerService()
    
    def get_tasks(self, role_name):
        """Récupère les tâches pour un rôle donné
        
        Args:
            role_name: Le nom du rôle
            
        Returns:
            Une liste d'objets Task
        """
        print(f"Loading tasks for role: {role_name}")
        role = self.roles_service.get_role_by_name(role_name)
        
        if role and 'tasks' in role:
            tasks = role['tasks']
            print(f"Loaded {len(tasks)} tasks for {role_name}")
            
            # Convertir les dictionnaires en objets Task
            task_objects = []
            for task_dict in tasks:
                task = Task(
                    title=task_dict.get('title', ''),
                    description=task_dict.get('description', ''),
                    module=task_dict.get('module', ''),
                    icon=task_dict.get('icon', ''),
                    status=task_dict.get('status', '')
                )
                task_objects.append(task)
                
            print(f"Loaded {len(task_objects)} tasks for display")
            return task_objects
        else:
            print(f"No tasks found for role: {role_name}")
            return []
    
    def add_task(self, task_data):
        """Ajoute une nouvelle tâche"""
        return self.roles_service.add_task(task_data)
    
    def update_task(self, task_id, task_data):
        """Met à jour une tâche existante"""
        return self.roles_service.update_task(task_id, task_data)
    
    def delete_task(self, task_id):
        """Supprime une tâche"""
        return self.roles_service.delete_task(task_id)
