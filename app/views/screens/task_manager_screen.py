from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton

from app.models.task import Task, TaskModel
from app.services.firebase_service import FirebaseService
from app.views.screens.specialized_dashboard_screen import TaskCard  # Importer le composant TaskCard

class TaskEditDialog(MDDialog):
    dialog_title = StringProperty("Nouvelle tâche")
    task_title = StringProperty("")
    task_description = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_save')
        self.register_event_type('on_cancel')
    
    def on_save(self, *args):
        pass
        
    def on_cancel(self, *args):
        pass
        
    def get_task_data(self):
        return {
            'title': self.ids.title_field.text,
            'description': self.ids.description_field.text
        }

class TaskManagerScreen(MDScreen):
    current_role_id = StringProperty('')  # Changé de None à une chaîne vide
    current_role_name = StringProperty('')
    tasks = ListProperty([])
    tasks_container = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_model = TaskModel(FirebaseService())
        
    def set_current_role(self, role_id, role_name):
        """Définit le rôle actuel"""
        print(f"[DEBUG] TaskManagerScreen.set_current_role - role_id reçu: {role_id}, role_name: {role_name}")
        # Si role_id est None, utiliser une chaîne vide
        self.current_role_id = role_id if role_id is not None else ''
        self.current_role_name = role_name
        print(f"[DEBUG] TaskManagerScreen.set_current_role - current_role_id défini à: {self.current_role_id}")
        if self.current_role_id:
            self.load_tasks()
        
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        print(f"[DEBUG] TaskManagerScreen.on_enter - current_role_id: {self.current_role_id}")
        if self.current_role_id:
            self.load_tasks()
            
    def load_tasks(self):
        """Charge la liste des tâches pour le rôle actuel"""
        if self.current_role_id:
            print(f"[DEBUG] TaskManagerScreen.load_tasks - Chargement des tâches pour le rôle {self.current_role_id}")
            tasks = self.task_model.get_tasks(self.current_role_id)
            print(f"[DEBUG] TaskManagerScreen.load_tasks - Tâches reçues du modèle : {tasks}")
            
            # Convertir les objets Task en dictionnaires
            self.tasks = [task.to_dict() for task in tasks]
            print(f"[DEBUG] TaskManagerScreen.load_tasks - Tâches converties en dictionnaires : {self.tasks}")
            
            self.display_tasks(self.tasks)
            
    def display_tasks(self, tasks):
        """Affiche les tâches dans l'interface"""
        print(f"[DEBUG] TaskManagerScreen.display_tasks - Début de l'affichage")
        print(f"[DEBUG] TaskManagerScreen.display_tasks - Nombre de tâches : {len(tasks)}")
        
        # Récupérer le container
        container = self.ids.tasks_container
        print(f"[DEBUG] TaskManagerScreen.display_tasks - Container: {container}")
        
        # Vider le container
        container.clear_widgets()
        
        # Créer une carte pour chaque tâche
        for task in tasks:
            print(f"[DEBUG] TaskManagerScreen.display_tasks - Création de carte pour la tâche : {task}")
            task_card = TaskCard(
                title=task['title'],
                description=task['description'],
                icon=task.get('icon', 'checkbox-marked-circle')
            )
            
            container.add_widget(task_card)
                
    def go_back(self, *args):
        """Retourne à l'écran précédent"""
        self.manager.current = 'roles_manager'
        
    def show_add_task_dialog(self):
        """Affiche le dialogue pour ajouter une nouvelle tâche"""
        dialog = TaskEditDialog(
            title="Nouvelle tâche",
            type="custom",
            content_cls=MDBoxLayout(
                orientation="vertical",
                spacing="12dp",
                padding="12dp",
                size_hint_y=None,
                height="120dp"
            ),
            buttons=[
                MDButton(
                    text="ANNULER",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDButton(
                    text="ENREGISTRER",
                    on_release=lambda x: self.save_task(dialog)
                ),
            ],
        )
        dialog.open()
        
    def save_task(self, dialog):
        """Sauvegarde une nouvelle tâche"""
        task_data = dialog.get_task_data()
        if task_data['title'] and task_data['description']:
            new_task = Task(
                title=task_data['title'],
                description=task_data['description'],
                module='operations',  # Par défaut
                icon='checkbox-marked-circle'  # Par défaut
            )
            self.task_model.add_task(self.current_role_id, new_task)
            self.load_tasks()  # Recharger la liste des tâches
            dialog.dismiss()
