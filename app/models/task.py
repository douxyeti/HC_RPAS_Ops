from typing import Dict, List, Optional
from datetime import datetime
import time
import random
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.event import EventDispatcher
from app.services.roles_manager_service import RolesManagerService

class Task(EventDispatcher):
    title = StringProperty('')
    description = StringProperty('')
    module = StringProperty('operations')
    icon = StringProperty('checkbox-marked')
    status = StringProperty('En attente')  # Propriété ajoutée

    def __init__(self, title: str, description: str, module: str = 'operations', icon: str = 'checkbox-marked', status: str = 'En attente'):
        super().__init__()
        self.title = title
        self.description = description
        self.module = module
        self.icon = icon
        self.status = status  # Initialisation correcte

    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'description': self.description,
            'module': self.module,
            'icon': self.icon,
            'status': self.status  # Ajout de la propriété status
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Crée une instance de Task à partir d'un dictionnaire"""
        if not data:
            raise ValueError("Les données de la tâche sont vides")
            
        # Valeurs par défaut pour les champs obligatoires
        title = data.get('title', '')
        if not title:
            raise ValueError("Le titre de la tâche est obligatoire")
            
        description = data.get('description', '')
        module = data.get('module', 'operations')
        icon = data.get('icon', 'checkbox-marked')
        status = data.get('status', 'En attente')
        
        return cls(
            title=title,
            description=description,
            module=module,
            icon=icon,
            status=status
        )

class Role(EventDispatcher):
    id = StringProperty()
    name = StringProperty()
    permissions = ListProperty([])

    def __init__(self, id, name, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.name = name

class TaskModel:
    def __init__(self, firebase_service):
        self.firebase_service = firebase_service
        self.collection = 'roles'
        self.roles_service = RolesManagerService()

    def get_tasks(self, role_id: str) -> List[Task]:
        """Récupère toutes les tâches pour un rôle donné"""
        print(f"[DEBUG] TaskModel.get_tasks - Recherche des tâches pour role_id: '{role_id}'")
        try:
            # Cas spécial pour le Super Administrateur
            if role_id == 'super_admin':
                print("[DEBUG] TaskModel.get_tasks - Chargement des tâches du Super Administrateur")
                return [
                    Task("Gérer les rôles", "Gérer les rôles et leurs permissions", "admin", "account-cog"),
                    Task("Configuration système", "Configurer les paramètres du système", "admin", "cog"),
                    Task("Audit des opérations", "Auditer les opérations du système", "admin", "clipboard-check")
                ]

            # Pour les autres rôles, essayer d'abord avec l'ID exact
            role_doc = self.firebase_service.get_document(self.collection, role_id)
            
            # Si non trouvé, essayer avec l'ID normalisé
            if not role_doc:
                normalized_id = self.roles_service.normalize_string(role_id)
                print(f"[DEBUG] TaskModel.get_tasks - Essai avec l'ID normalisé: {normalized_id}")
                role_doc = self.firebase_service.get_document(self.collection, normalized_id)
            
            print(f"[DEBUG] TaskModel.get_tasks - Document récupéré : {role_doc}")
            
            if not role_doc:
                print(f"[DEBUG] TaskModel.get_tasks - Document non trouvé pour le rôle {role_id}")
                return []
                
            # Vérifier si le document a des tâches
            tasks_data = role_doc.get('tasks', [])
            if not tasks_data:
                print(f"[DEBUG] TaskModel.get_tasks - Aucune tâche trouvée pour le rôle {role_id}")
                return []
                
            # Convertir les données en objets Task
            tasks = []
            for task_data in tasks_data:
                try:
                    task = Task.from_dict(task_data)
                    tasks.append(task)
                except Exception as e:
                    print(f"[ERROR] TaskModel.get_tasks - Erreur lors de la conversion de la tâche : {str(e)}")
                    continue
                    
            print(f"[DEBUG] TaskModel.get_tasks - {len(tasks)} tâches trouvées")
            return tasks
            
        except Exception as e:
            print(f"[ERROR] TaskModel.get_tasks - Erreur lors de la récupération des tâches : {str(e)}")
            return []

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

    def filter_by_module(self, tasks, module_type):
        """Filtre une liste de tâches par module"""
        if module_type == "all":
            return tasks
        return [task for task in tasks if task.get('module') == module_type]

    def sort_by_title(self, tasks, ascending=True):
        """Trie une liste de tâches par titre"""
        return sorted(tasks, key=lambda x: x.get('title', ''), reverse=not ascending)
