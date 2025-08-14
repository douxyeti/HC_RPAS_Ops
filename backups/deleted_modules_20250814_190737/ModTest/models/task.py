from typing import Dict, List, Optional
from datetime import datetime
import time
import random
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.event import EventDispatcher
from app.services.roles_manager_service import RolesManagerService
import logging

class Task(EventDispatcher):
    title = StringProperty('')
    description = StringProperty('')
    module = StringProperty('operations')
    icon = StringProperty('checkbox-marked')
    status = StringProperty('En attente')
    
    # Champs pour l'intégration avec les modules indexés
    target_module_id = StringProperty('')  # ID du module cible
    target_screen_id = StringProperty('')  # ID de l'écran cible
    target_field_id = StringProperty('')   # ID du champ cible (optionnel)
    
    # Champ legacy pour compatibilité avec l'ancien système
    screen = StringProperty(None)

    def __init__(self, title: str, description: str, module: str = 'operations', 
                icon: str = 'checkbox-marked', status: str = 'En attente', 
                target_module_id: str = '', target_screen_id: str = '', 
                target_field_id: str = '', screen: str = None):
        super().__init__()
        self.title = title
        self.description = description
        self.module = module
        self.icon = icon
        self.status = status
        self.target_module_id = target_module_id
        self.target_screen_id = target_screen_id
        self.target_field_id = target_field_id
        self.screen = screen

    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'description': self.description,
            'module': self.module,
            'icon': self.icon,
            'status': self.status,
            'target_module_id': self.target_module_id,
            'target_screen_id': self.target_screen_id,
            'target_field_id': self.target_field_id,
            'screen': self.screen
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
        
        # Valeurs pour l'intégration avec les modules indexés
        target_module_id = data.get('target_module_id', '')
        target_screen_id = data.get('target_screen_id', '')
        target_field_id = data.get('target_field_id', '')
        
        # Valeur legacy
        screen = data.get('screen', None)
        
        return cls(
            title=title,
            description=description,
            module=module,
            icon=icon,
            status=status,
            target_module_id=target_module_id,
            target_screen_id=target_screen_id,
            target_field_id=target_field_id,
            screen=screen
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
        self.branch_name = self._get_clean_branch_name()
        print(f"[DEBUG] TaskModel.__init__ - Branche actuelle : {self.branch_name}")
        
    def _get_clean_branch_name(self) -> str:
        """Récupère le nom de la branche Git actuelle sans le préfixe 'dev_'"""
        try:
            import subprocess
            result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True, check=True)
            branch_name = result.stdout.strip()
            if branch_name.startswith('dev_'):
                branch_name = branch_name[4:]
            return branch_name
        except Exception:
            print("[DEBUG] TaskModel._get_clean_branch_name - Erreur lors de la récupération du nom de la branche Git")
            return "default_app"

    def get_tasks(self, role_id: str) -> List[Task]:
        """Récupère toutes les tâches pour un rôle donné"""
        print(f"[DEBUG] TaskModel.get_tasks - Recherche des tâches pour role_id: '{role_id}'")
        try:
            # Pour tous les rôles, essayer d'abord avec l'ID exact
            role_doc = self.firebase_service.get_document(self.collection, role_id)
            
            if not role_doc or 'tasks' not in role_doc:
                print(f"[DEBUG] TaskModel.get_tasks - Aucune tâche trouvée pour le rôle {role_id}")
                return []
                
            print(f"[DEBUG] TaskModel.get_tasks - Document récupéré : {role_doc}")
            tasks_data = role_doc.get('tasks', [])
            
            # Vérifier et ajouter des métadonnées de branche aux tâches qui ont des index
            modifications_needed = False
            for task in tasks_data:
                if 'target_module_id' in task and 'target_screen_id' in task and 'application_name' not in task:
                    print(f"[DEBUG] TaskModel.get_tasks - Ajout du champ application_name: {self.branch_name} à la tâche {task.get('title')}")
                    task['application_name'] = self.branch_name
                    modifications_needed = True
            
            # Persister les modifications dans Firebase si nécessaire
            if modifications_needed:
                print(f"[DEBUG] TaskModel.get_tasks - Mise à jour des tâches avec application_name dans Firebase")
                self.firebase_service.update_document(self.collection, role_id, {'tasks': tasks_data})
            
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
        print(f"[DEBUG] TaskModel.add_task - Branche: {self.branch_name}, ajout d'une tâche pour le rôle {role_id}")
        try:
            # Récupérer le document du rôle
            role_doc = self.firebase_service.get_document(self.collection, role_id)

            if not role_doc:
                print(f"[DEBUG] TaskModel.add_task - Rôle {role_id} non trouvé")
                return False

            # Récupérer les données du rôle
            role_data = role_doc
            tasks = role_data.get('tasks', [])
            
            # Ajouter des métadonnées de branche aux tâches qui ont des index
            if 'target_module_id' in task_data and 'target_screen_id' in task_data:
                task_data['application_name'] = self.branch_name

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

    def update_task(self, role_id, old_title, updated_task):
        """Met à jour une tâche existante"""
        try:
            print(f"[DEBUG] TaskModel.update_task - Branche: {self.branch_name}, mise à jour de la tâche '{old_title}' pour le rôle {role_id}")
            role_doc = self.firebase_service.get_document(self.collection, role_id)
            
            if not role_doc or 'tasks' not in role_doc:
                print(f"[DEBUG] TaskModel.update_task - Rôle non trouvé ou pas de tâches")
                return False
                
            tasks = role_doc['tasks']
            task_updated = False
            
            for i, task in enumerate(tasks):
                if task['title'] == old_title:
                    # Si updated_task est déjà un dictionnaire, l'utiliser directement
                    # Sinon, appeler to_dict() s'il s'agit d'un objet Task
                    if isinstance(updated_task, dict):
                        # Ajouter des métadonnées de branche aux tâches qui ont des index
                        if 'target_module_id' in updated_task and 'target_screen_id' in updated_task:
                            updated_task['application_name'] = self.branch_name
                        tasks[i] = updated_task
                    else:
                        task_dict = updated_task.to_dict()
                        # Ajouter des métadonnées de branche aux tâches qui ont des index
                        if 'target_module_id' in task_dict and 'target_screen_id' in task_dict:
                            task_dict['application_name'] = self.branch_name
                        tasks[i] = task_dict
                    task_updated = True
                    break
            
            if task_updated:
                print(f"[DEBUG] TaskModel.update_task - Mise à jour des tâches dans Firebase")
                return self.firebase_service.update_document(
                    self.collection,
                    role_id,
                    {'tasks': tasks}
                )
            else:
                print(f"[DEBUG] TaskModel.update_task - Tâche '{old_title}' non trouvée")
                return False
                
        except Exception as e:
            print(f"[ERROR] TaskModel.update_task - Erreur lors de la mise à jour : {str(e)}")
            return False

    def delete_task(self, role_id, title):
        """Supprime une tâche"""
        try:
            print(f"[DEBUG] TaskModel.delete_task - Suppression de la tâche '{title}' pour le rôle {role_id}")
            
            # Vérifier que le rôle existe
            role_doc = self.firebase_service.get_document(self.collection, role_id)
            
            if not role_doc or 'tasks' not in role_doc:
                print(f"[DEBUG] TaskModel.delete_task - Rôle non trouvé ou pas de tâches")
                return False
            
            tasks = role_doc['tasks']
            original_count = len(tasks)
            
            # Filtrer la tâche à supprimer
            tasks = [task for task in tasks if task.get('title') != title]
            
            # Vérifier si une tâche a été supprimée
            if len(tasks) == original_count:
                print(f"[DEBUG] TaskModel.delete_task - Tâche '{title}' non trouvée")
                return False
                
            # Mettre à jour le document
            updated = self.firebase_service.update_document(
                self.collection,
                role_id,
                {'tasks': tasks}
            )
            
            if updated:
                print(f"[DEBUG] TaskModel.delete_task - Tâche '{title}' supprimée avec succès")
                return True
            else:
                print(f"[DEBUG] TaskModel.delete_task - Échec de la mise à jour dans Firebase")
                return False
                
        except Exception as e:
            print(f"[ERROR] TaskModel.delete_task - Erreur lors de la suppression : {str(e)}")
            return False

    def filter_by_module(self, tasks, module_type):
        """Filtre une liste de tâches par module"""
        if module_type == "all":
            return tasks
        return [task for task in tasks if task.get('module') == module_type]

    def sort_by_title(self, tasks, ascending=True):
        """Trie une liste de tâches par titre"""
        return sorted(tasks, key=lambda x: x.get('title', ''), reverse=not ascending)
