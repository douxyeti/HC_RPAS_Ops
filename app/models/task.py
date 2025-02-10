from typing import Dict, List, Optional
from datetime import datetime
import time
import random

class Task:
    def __init__(self, title: str, description: str, module: str = 'operations', icon: str = 'checkbox-marked'):
        self.title = title
        self.description = description
        self.module = module
        self.icon = icon

    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'description': self.description,
            'module': self.module,
            'icon': self.icon
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        return cls(
            title=data.get('title', ''),
            description=data.get('description', ''),
            module=data.get('module', 'operations'),
            icon=data.get('icon', 'checkbox-marked')
        )

class TaskModel:
    def __init__(self, firebase_service):
        self.firebase_service = firebase_service
        self.collection = 'roles'

    def get_tasks(self, role_id: str) -> List[Task]:
        """Récupère toutes les tâches pour un rôle donné"""
        print(f"[DEBUG] TaskModel.get_tasks - Recherche des tâches pour le rôle : {role_id}")
        role_doc = self.firebase_service.get_document(self.collection, role_id)
        print(f"[DEBUG] TaskModel.get_tasks - Document récupéré : {role_doc}")
        
        if not role_doc or 'tasks' not in role_doc:
            print(f"[DEBUG] TaskModel.get_tasks - Aucune tâche trouvée pour le rôle {role_id}")
            return []
            
        tasks = [Task.from_dict(task) for task in role_doc['tasks']]
        print(f"[DEBUG] TaskModel.get_tasks - {len(tasks)} tâches trouvées")
        return tasks

    def add_task(self, role_id, task_data):
        """Ajoute une nouvelle tâche au rôle spécifié"""
        print(f"[DEBUG] TaskModel.add_task - Ajout d'une tâche pour le rôle {role_id}")
        try:
            # Récupérer le document du rôle
            role_doc = self.firebase_service.get_document(self.collection, role_id)

            if not role_doc:
                print(f"[DEBUG] TaskModel.add_task - Rôle {role_id} non trouvé")
                return False

            # Récupérer les données du rôle
            role_data = role_doc
            tasks = role_data.get('tasks', [])

            # Générer un ID unique pour la tâche
            task_id = f"{task_data['title'].lower().replace(' ', '_')}_{task_data['module']}_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
            task_data['id'] = task_id

            # Ajouter la nouvelle tâche à la liste
            tasks.append(task_data)

            # Mettre à jour le document
            self.firebase_service.update_document(
                self.collection,
                role_id,
                {'tasks': tasks}
            )
            print(f"[DEBUG] TaskModel.add_task - Tâche ajoutée avec succès")
            return True

        except Exception as e:
            print(f"[DEBUG] TaskModel.add_task - Erreur : {str(e)}")
            return False

    def update_task(self, role_id: str, task_index: int, task: Task) -> bool:
        """Met à jour une tâche existante"""
        role_doc = self.firebase_service.get_document(self.collection, role_id)
        if not role_doc or 'tasks' not in role_doc:
            return False

        tasks = role_doc['tasks']
        if task_index < 0 or task_index >= len(tasks):
            return False

        tasks[task_index] = task.to_dict()
        return self.firebase_service.update_document(
            self.collection,
            role_id,
            {'tasks': tasks}
        )

    def delete_task(self, role_id: str, task_index: int) -> bool:
        """Supprime une tâche"""
        role_doc = self.firebase_service.get_document(self.collection, role_id)
        if not role_doc or 'tasks' not in role_doc:
            return False

        tasks = role_doc['tasks']
        if task_index < 0 or task_index >= len(tasks):
            return False

        tasks.pop(task_index)
        return self.firebase_service.update_document(
            self.collection,
            role_id,
            {'tasks': tasks}
        )

    def update_task(self, role_id, old_title, updated_task):
        """Met à jour une tâche existante"""
        role_ref = self.firebase_service.db.collection('roles').document(role_id)
        role_data = role_ref.get().to_dict()
        
        if role_data and 'tasks' in role_data:
            tasks = role_data['tasks']
            for i, task in enumerate(tasks):
                if task['title'] == old_title:
                    tasks[i] = updated_task.to_dict()
                    role_ref.update({'tasks': tasks})
                    break
                    
    def delete_task(self, role_id, title):
        """Supprime une tâche"""
        role_ref = self.firebase_service.db.collection('roles').document(role_id)
        role_data = role_ref.get().to_dict()
        
        if role_data and 'tasks' in role_data:
            tasks = role_data['tasks']
            tasks = [task for task in tasks if task['title'] != title]
            role_ref.update({'tasks': tasks})
