from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu

from app.controllers.task_controller import TaskController

class TaskCard(MDCard):
    def __init__(self, task_data, on_edit, on_delete, **kwargs):
        super().__init__(**kwargs)
        print(f"Création de la carte pour la tâche : {task_data}")  # Debug
        
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(120)  # Conserver la hauteur originale
        self.padding = dp(16)  # Conserver le padding original
        self.spacing = dp(8)  # Conserver l'espacement original
        self.elevation = 1
        
        # Layout pour le titre et les boutons
        header = MDBoxLayout(orientation='horizontal', adaptive_height=True)
        
        # Titre avec vérification
        title_text = task_data.get('title', '')
        print(f"Titre de la tâche : {title_text}")  # Debug
        
        title = MDLabel(
            text=title_text,
            theme_font_size="Custom",
            font_size="20sp",
            adaptive_height=True
        )
        header.add_widget(title)
        
        # Boutons d'action
        actions = MDBoxLayout(
            orientation='horizontal',
            adaptive_width=True,
            spacing=dp(8)
        )
        
        edit_btn = MDIconButton(
            icon='pencil',
            on_release=lambda x: on_edit(task_data)
        )
        actions.add_widget(edit_btn)
        
        delete_btn = MDIconButton(
            icon='delete',
            on_release=lambda x: on_delete(task_data)
        )
        actions.add_widget(delete_btn)
        header.add_widget(actions)
        
        # Description avec vérification
        desc_text = task_data.get('description', 'Aucune description')
        print(f"Description de la tâche : {desc_text}")  # Debug
        
        description = MDLabel(
            text=desc_text,
            adaptive_height=True
        )
        
        self.add_widget(header)
        self.add_widget(description)

class TaskManagerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'task_manager'
        self.task_controller = TaskController()
        self.current_role_id = ''
        self.current_role_name = ''
        
        # Initialiser le dialogue
        self.task_dialog = None
        self.title_field = None
        self.description_field = None
        
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        self.load_tasks()

    def load_tasks(self):
        """Charge et affiche la liste des tâches"""
        # Effacer les tâches existantes
        self.tasks_container.clear_widgets()
        
        # Obtenir les tâches via le contrôleur
        tasks = self.task_controller.get_tasks(self.current_role_id)
            
        # Créer une carte pour chaque tâche
        for task in tasks:
            card = TaskCard(
                task_data=task,
                on_edit=self.edit_task,
                on_delete=self.delete_task
            )
            self.tasks_container.add_widget(card)

    def show_add_task_dialog(self):
        """Affiche le dialogue d'ajout de tâche"""
        if not self.task_dialog:
            self.title_field = MDTextField(
                hint_text="Titre de la tâche",
                helper_text="Entrez le titre de la tâche",
                helper_text_mode="on_error",
            )
            self.description_field = MDTextField(
                hint_text="Description de la tâche",
                helper_text="Entrez la description de la tâche",
                helper_text_mode="on_error",
                multiline=True
            )
            
            content = MDDialogContentContainer(
                orientation='vertical',
                spacing=dp(10),
                padding=dp(10),
                size_hint_y=None,
                height=dp(200)
            )
            content.add_widget(self.title_field)
            content.add_widget(self.description_field)
            
            self.task_dialog = MDDialog(
                headline_text=MDDialogHeadlineText(text="Ajouter une tâche"),
                content_container=content,
                buttons_container=MDDialogButtonContainer(
                    orientation='horizontal',
                    spacing=dp(10),
                    padding=dp(10),
                    size_hint_y=None,
                    height=dp(50)
                )
            )
            
            self.task_dialog.buttons_container.add_widget(
                MDButton(
                    MDButtonText(text="Annuler"),
                    style="text",
                    on_release=lambda x: self.task_dialog.dismiss()
                )
            )
            self.task_dialog.buttons_container.add_widget(
                MDButton(
                    MDButtonText(text="Ajouter"),
                    style="filled",
                    on_release=self.add_task
                )
            )
        
        self.task_dialog.open()

    def add_task(self, *args):
        """Ajoute une nouvelle tâche"""
        if self.title_field.text and self.description_field.text:
            task_data = {
                'title': self.title_field.text,
                'description': self.description_field.text,
                'role_id': self.current_role_id
            }
            
            # Utiliser le contrôleur pour ajouter la tâche
            self.task_controller.add_task(task_data)
            
            # Réinitialiser les champs
            self.title_field.text = ""
            self.description_field.text = ""
            
            # Fermer le dialogue et recharger les tâches
            self.task_dialog.dismiss()
            self.load_tasks()
        else:
            if not self.title_field.text:
                self.title_field.error = True
            if not self.description_field.text:
                self.description_field.error = True

    def edit_task(self, task_data):
        """Édite une tâche existante"""
        # Implémenter l'édition de tâche ici
        pass

    def delete_task(self, task_data):
        """Supprime une tâche"""
        # Utiliser le contrôleur pour supprimer la tâche
        self.task_controller.delete_task(task_data['id'])
        self.load_tasks()

    def go_back(self):
        """Retourne à l'écran précédent"""
        self.manager.current = 'roles_manager'
