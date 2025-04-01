from datetime import datetime
from typing import Dict, List, Optional
from firebase_admin import db
from kivymd.app import MDApp

class RolesTasksService:
    """Service pour gérer les rôles et tâches dans Firebase"""
    
    def __init__(self):
        self.ref = db.reference('/')
        self.roles_ref = self.ref.child('roles')
        self.tasks_ref = self.ref.child('tasks')
        self.role_tasks_ref = self.ref.child('role_tasks')
        
    def create_role(self, name: str, permissions: List[str], created_by: str) -> str:
        """Crée un nouveau rôle"""
        now = datetime.now().isoformat()
        role_data = {
            'name': name,
            'permissions': permissions,
            'createdAt': now,
            'updatedAt': now,
            'createdBy': created_by
        }
        new_role_ref = self.roles_ref.push(role_data)
        return new_role_ref.key
        
    def update_role(self, role_id: str, name: str, permissions: List[str]) -> None:
        """Met à jour un rôle existant"""
        role_data = {
            'name': name,
            'permissions': permissions,
            'updatedAt': datetime.now().isoformat()
        }
        self.roles_ref.child(role_id).update(role_data)
        
    def delete_role(self, role_id: str) -> None:
        """Supprime un rôle et ses associations avec les tâches"""
        self.roles_ref.child(role_id).delete()
        self.role_tasks_ref.child(role_id).delete()
        
    def get_role(self, role_id: str) -> Optional[Dict]:
        """Récupère un rôle par son ID"""
        return self.roles_ref.child(role_id).get()
        
    def get_all_roles(self) -> Dict:
        """Récupère tous les rôles"""
        return self.roles_ref.get() or {}
        
    def create_task(self, title: str, description: str, icon: str, 
                   module: str, created_by: str) -> str:
        """Crée une nouvelle tâche"""
        now = datetime.now().isoformat()
        task_data = {
            'title': title,
            'description': description,
            'icon': icon,
            'module': module,
            'createdAt': now,
            'updatedAt': now,
            'createdBy': created_by
        }
        new_task_ref = self.tasks_ref.push(task_data)
        return new_task_ref.key
        
    def update_task(self, task_id: str, title: str, description: str, 
                   icon: str, module: str) -> None:
        """Met à jour une tâche existante"""
        task_data = {
            'title': title,
            'description': description,
            'icon': icon,
            'module': module,
            'updatedAt': datetime.now().isoformat()
        }
        self.tasks_ref.child(task_id).update(task_data)
        
    def delete_task(self, task_id: str) -> None:
        """Supprime une tâche et ses associations avec les rôles"""
        self.tasks_ref.child(task_id).delete()
        # Supprimer la tâche de tous les rôles
        roles = self.get_all_roles()
        for role_id in roles:
            self.role_tasks_ref.child(role_id).child(task_id).delete()
            
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Récupère une tâche par son ID"""
        return self.tasks_ref.child(task_id).get()
        
    def get_all_tasks(self) -> Dict:
        """Récupère toutes les tâches"""
        return self.tasks_ref.get() or {}
        
    def assign_task_to_role(self, role_id: str, task_id: str) -> None:
        """Assigne une tâche à un rôle"""
        self.role_tasks_ref.child(role_id).child(task_id).set(True)
        
    def remove_task_from_role(self, role_id: str, task_id: str) -> None:
        """Retire une tâche d'un rôle"""
        self.role_tasks_ref.child(role_id).child(task_id).delete()
        
    def get_role_tasks(self, role_id: str) -> List[Dict]:
        """Récupère toutes les tâches associées à un rôle"""
        role_tasks = self.role_tasks_ref.child(role_id).get() or {}
        tasks = self.get_all_tasks()
        return [tasks[task_id] for task_id in role_tasks.keys() 
                if task_id in tasks]
                
    def is_super_admin(self, user_id: str) -> bool:
        """Vérifie si l'utilisateur est super administrateur"""
        app = MDApp.get_running_app()
        user_data = app.auth_service.get_user_data(user_id)
        return user_data and user_data.get('role') == 'super_admin'
