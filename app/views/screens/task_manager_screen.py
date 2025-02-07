from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList
from kivymd.uix.appbar import MDTopAppBar

Builder.load_string('''
<TaskManagerScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(10)
        md_bg_color: [1, 1, 1, 1]

        # En-tête avec titre et boutons
        MDBoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(56)
            spacing: dp(10)
            padding: [dp(10), 0]
            md_bg_color: [0.2, 0.2, 0.9, 1]

            # Bouton retour
            MDIconButton:
                icon: "arrow-left"
                theme_text_color: "Custom"
                text_color: [1, 1, 1, 1]
                on_release: root.go_back()
                pos_hint: {"center_y": 0.5}

            # Titre
            MDLabel:
                text: "Gestion des Tâches"
                bold: True
                font_size: "24sp"
                theme_text_color: "Custom"
                text_color: [1, 1, 1, 1]
                size_hint_x: 0.9
                valign: "center"
                height: dp(56)

            # Bouton ajouter
            MDIconButton:
                icon: "plus"
                theme_text_color: "Custom"
                text_color: [1, 1, 1, 1]
                on_release: root.show_add_task_dialog()
                pos_hint: {"center_y": 0.5}

        # Zone scrollable avec la liste
        MDScrollView:
            MDList:
                id: tasks_list
                spacing: dp(10)
                padding: dp(10)
                size_hint_y: None
                height: self.minimum_height
                
                
''')

class TaskCard(MDCard):
    def __init__(self, task_data, on_edit=None, on_delete=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(120)
        self.padding = dp(16)
        self.spacing = dp(8)
        self.elevation = 1
        
        # Layout pour le titre et les boutons
        header = MDBoxLayout(orientation='horizontal', adaptive_height=True)
        
        # Titre
        title = MDLabel(
            text=task_data.get('name', ''),
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
        
        if on_edit:
            edit_btn = MDIconButton(
                icon='pencil',
                on_release=lambda x: on_edit(task_data)
            )
            actions.add_widget(edit_btn)
        
        if on_delete:
            delete_btn = MDIconButton(
                icon='delete',
                on_release=lambda x: on_delete(task_data)
            )
            actions.add_widget(delete_btn)
        
        header.add_widget(actions)
        self.add_widget(header)

class TaskInputDialog(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(12)
        self.size_hint_y = None
        self.height = dp(120)
        
        self.task_name = MDTextField(
            hint_text="Nom de la tâche",
            mode="outlined",
            required=True
        )
        self.add_widget(self.task_name)

class TaskManagerScreen(MDScreen):
    current_role_id = StringProperty("")
    current_role_name = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "task_manager"
        self.task_dialog = None
        self.edit_dialog = None
        self.delete_dialog = None
    
    def on_enter(self):
        """Called when the screen is entered"""
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks for the current role"""
        # TODO: Implement loading tasks from Firebase
        tasks_list = self.ids.tasks_list
        tasks_list.clear_widgets()
        
        # Example tasks (to be replaced with Firebase data)
        example_tasks = [
            {"id": "1", "name": "Tâche 1"},
            {"id": "2", "name": "Tâche 2"}
        ]
        
        for task in example_tasks:
            task_card = TaskCard(
                task,
                on_edit=self.show_edit_task_dialog,
                on_delete=self.show_delete_task_dialog
            )
            tasks_list.add_widget(task_card)
    
    def show_add_task_dialog(self):
        """Show dialog to add a new task"""
        dialog = MDDialog(
            radius=20,
            size_hint=(.8, None)
        )
        
        dialog.add_widget(MDDialogHeadlineText(
            text="Ajouter une tâche",
            theme_font_size="Custom",
            font_size="24sp"
        ))
        
        content_container = MDDialogContentContainer(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20)
        )
        
        name_field = MDTextField(
            hint_text="Nom de la tâche",
            mode="outlined",
            size_hint_x=1
        )
        content_container.add_widget(name_field)
        dialog.add_widget(content_container)
        
        button_container = MDDialogButtonContainer(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        cancel_button = MDButton(
            style="text",
            on_release=lambda x: dialog.dismiss()
        )
        cancel_button.add_widget(MDButtonText(text="Annuler"))
        
        create_button = MDButton(
            style="text",
            on_release=lambda x: self.add_task(name_field.text, dialog)
        )
        create_button.add_widget(MDButtonText(text="Ajouter"))
        
        button_container.add_widget(cancel_button)
        button_container.add_widget(create_button)
        dialog.add_widget(button_container)
        
        dialog.open()
    
    def show_edit_task_dialog(self, task_data):
        """Show dialog to edit a task"""
        dialog = MDDialog(
            radius=20,
            size_hint=(.8, None)
        )
        
        dialog.add_widget(MDDialogHeadlineText(
            text="Modifier la tâche",
            theme_font_size="Custom",
            font_size="24sp"
        ))
        
        content_container = MDDialogContentContainer(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20)
        )
        
        name_field = MDTextField(
            hint_text="Nom de la tâche",
            mode="outlined",
            text=task_data.get('name', ''),
            size_hint_x=1
        )
        content_container.add_widget(name_field)
        dialog.add_widget(content_container)
        
        button_container = MDDialogButtonContainer(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        cancel_button = MDButton(
            style="text",
            on_release=lambda x: dialog.dismiss()
        )
        cancel_button.add_widget(MDButtonText(text="Annuler"))
        
        save_button = MDButton(
            style="text",
            on_release=lambda x: self.edit_task(task_data['id'], name_field.text, dialog)
        )
        save_button.add_widget(MDButtonText(text="Enregistrer"))
        
        button_container.add_widget(cancel_button)
        button_container.add_widget(save_button)
        dialog.add_widget(button_container)
        
        dialog.open()
    
    def show_delete_task_dialog(self, task_data):
        """Show confirmation dialog to delete a task"""
        dialog = MDDialog(
            radius=20,
            size_hint=(.8, None)
        )
        
        dialog.add_widget(MDDialogHeadlineText(
            text="Supprimer la tâche",
            theme_font_size="Custom",
            font_size="24sp"
        ))
        
        content_container = MDDialogContentContainer(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20)
        )
        
        content_container.add_widget(MDLabel(
            text=f"Voulez-vous vraiment supprimer la tâche '{task_data.get('name', '')}'?",
            theme_text_color="Secondary"
        ))
        dialog.add_widget(content_container)
        
        button_container = MDDialogButtonContainer(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        cancel_button = MDButton(
            style="text",
            on_release=lambda x: dialog.dismiss()
        )
        cancel_button.add_widget(MDButtonText(text="Annuler"))
        
        delete_button = MDButton(
            style="text",
            on_release=lambda x: self.delete_task(task_data['id'], dialog)
        )
        delete_button.add_widget(MDButtonText(text="Supprimer"))
        
        button_container.add_widget(cancel_button)
        button_container.add_widget(delete_button)
        dialog.add_widget(button_container)
        
        dialog.open()
    
    def add_task(self, task_name, dialog):
        """Add a new task to the current role"""
        if task_name.strip():
            # TODO: Implement adding task to Firebase
            dialog.dismiss()
            self.load_tasks()
    
    def edit_task(self, task_id, new_name, dialog):
        """Edit an existing task"""
        if new_name.strip():
            # TODO: Implement task editing in Firebase
            dialog.dismiss()
            self.load_tasks()
    
    def delete_task(self, task_id, dialog):
        """Delete a task"""
        # TODO: Implement task deletion in Firebase
        dialog.dismiss()
        self.load_tasks()
    
    def go_back(self):
        """Return to the previous screen"""
        self.manager.transition.direction = 'right'
        self.manager.current = 'roles_manager'
