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
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.list import MDList
from kivymd.uix.appbar import MDTopAppBar
from app.services.roles_manager_service import RolesManagerService
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.behaviors import FocusBehavior

Builder.load_string('''
<TaskManagerScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(10)
        md_bg_color: [1, 1, 1, 1]  # Fond blanc

        # En-tête avec titre et boutons
        MDBoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(56)
            spacing: dp(10)
            padding: [dp(10), 0]
            md_bg_color: [0.12, 0.58, 0.95, 1]  # Bleu clair

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
                size_hint_x: 0.7
                valign: "center"
                height: dp(56)

            # Bouton rapport (redirige vers gestion des rôles)
            MDIconButton:
                icon: "file-document-outline"
                theme_text_color: "Custom"
                text_color: [1, 1, 1, 1]  # Blanc pour correspondre aux autres boutons
                on_release: root.go_to_roles()
                pos_hint: {"center_y": 0.5}
                size_hint_x: 0.15

            # Bouton ajouter
            MDIconButton:
                icon: "plus"
                theme_text_color: "Custom"
                text_color: [1, 1, 1, 1]
                on_release: root.show_add_task_dialog()
                pos_hint: {"center_y": 0.5}
                size_hint_x: 0.15

        # Zone scrollable avec la liste
        ScrollView:
            do_scroll_x: False
            do_scroll_y: True
            
            MDList:
                id: tasks_list
                spacing: dp(10)
                padding: dp(10)
                size_hint_y: None
                height: self.minimum_height
                md_bg_color: [1, 1, 1, 1]  # Fond blanc
''')

class TaskCard(MDCard):
    def __init__(self, task_data, task_index, on_edit=None, on_delete=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(120)
        self.padding = dp(16)
        self.spacing = dp(8)
        self.elevation = 1
        self.md_bg_color = [0.95, 0.95, 0.95, 1]  # Gris très clair pour les cartes
        
        # Layout pour le titre et les boutons
        header = MDBoxLayout(orientation='horizontal', adaptive_height=True)
        
        # Titre
        title = MDLabel(
            text=task_data.get('title', ''),
            theme_font_size="Custom",
            font_size="20sp",
            adaptive_height=True,
            size_hint_x=0.8  # Fixe la largeur du titre à 80% de la carte
        )
        header.add_widget(title)
        
        # Boutons d'action
        actions = MDBoxLayout(
            orientation='horizontal',
            adaptive_width=True,
            spacing=dp(8),
            size_hint_x=0.2  # Fixe la largeur des boutons à 20% de la carte
        )
        
        if on_edit:
            edit_btn = MDIconButton(
                icon='pencil',
                on_release=lambda x: on_edit(task_data, task_index)
            )
            actions.add_widget(edit_btn)
        
        if on_delete:
            delete_btn = MDIconButton(
                icon='delete',
                on_release=lambda x: on_delete(task_data, task_index)
            )
            actions.add_widget(delete_btn)
        
        header.add_widget(actions)
        
        # Description (avec texte par défaut si vide)
        desc_text = task_data.get('description', '')
        if not desc_text:
            desc_text = 'Aucune description'
            
        description = MDLabel(
            text=desc_text,
            adaptive_height=True,
            size_hint_x=1,  # Occupe toute la largeur
            height=dp(40)  # Hauteur minimale pour éviter le collapse
        )
        
        self.add_widget(header)
        self.add_widget(description)

class TaskManagerScreen(MDScreen):
    current_role_id = StringProperty("")
    current_role_name = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "task_manager"
        self.roles_manager_service = RolesManagerService()
        
        # Gestionnaire de focus
        Window.bind(on_touch_down=self._on_window_touch)
        self.current_dropdown = None
        self.current_text_field = None
        
    def on_enter(self):
        """Called when the screen is entered"""
        # Si on vient du tableau de bord admin, charger toutes les tâches
        if not self.current_role_id:
            self.load_all_tasks()
        else:
            self.load_tasks()

    def load_tasks(self):
        """Load tasks for the current role"""
        tasks_list = self.ids.tasks_list
        tasks_list.clear_widgets()
        
        tasks = self.roles_manager_service.get_role_tasks(self.current_role_id)
        
        for i, task in enumerate(tasks):
            task_card = TaskCard(
                task,
                i,
                on_edit=self.show_edit_task_dialog,
                on_delete=self.show_delete_task_dialog
            )
            tasks_list.add_widget(task_card)
    
    def load_all_tasks(self):
        """Load tasks from all roles"""
        # Récupérer tous les rôles
        roles = self.roles_manager_service.get_all_roles()
        
        # Nettoyer l'interface
        content_layout = self.ids.tasks_list
        content_layout.clear_widgets()
        
        # Créer une liste pour les tâches
        tasks_list = MDList(spacing=dp(10))  # Ajouter un espacement entre les éléments
        
        # Pour chaque rôle, afficher ses tâches
        for role_id, role_data in roles.items():
            # Ajouter un en-tête pour le rôle avec un padding
            role_header = MDLabel(
                text=f"Tâches de {role_data.get('name', '')}",
                theme_font_size="Custom",
                font_size="20sp",
                bold=True,
                padding=[dp(16), dp(16)]  # Augmenter le padding vertical
            )
            tasks_list.add_widget(role_header)
            
            # Ajouter les tâches du rôle
            tasks = role_data.get('tasks', [])
            for i, task in enumerate(tasks):
                task_card = TaskCard(
                    task,
                    i,
                    on_edit=lambda t, idx, r=role_data: self.show_edit_task_dialog(t, idx, r),
                    on_delete=lambda t, idx, r=role_data: self.show_delete_task_dialog(t, idx, r)
                )
                tasks_list.add_widget(task_card)
                
                # Ajouter un widget d'espacement après chaque tâche
                if i < len(tasks) - 1:  # Ne pas ajouter d'espace après la dernière tâche
                    spacer = Widget(size_hint_y=None, height=dp(10))
                    tasks_list.add_widget(spacer)
            
            # Ajouter un widget d'espacement plus grand entre les rôles
            if role_id != list(roles.keys())[-1]:  # Ne pas ajouter d'espace après le dernier rôle
                role_spacer = Widget(size_hint_y=None, height=dp(20))
                tasks_list.add_widget(role_spacer)
        
        content_layout.add_widget(tasks_list)
    
    def show_add_task_dialog(self):
        """Show dialog to add a new task"""
        # Force le focus sur le tableau pour fermer les menus déroulants
        self.ids.tasks_list.focus = True
        
        dialog = MDDialog(
            radius=20,
            size_hint=(.8, None),
            on_pre_open=self._clear_text_field_focus
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
        
        title_field = MDTextField(
            hint_text="Titre de la tâche",
            mode="filled",
            on_focus=self._on_field_focus
        )
        content_container.add_widget(title_field)
        
        description_field = MDTextField(
            hint_text="Description de la tâche",
            multiline=True,
            mode="filled",
            on_focus=self._on_field_focus
        )
        content_container.add_widget(description_field)
        
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
            on_release=lambda x: self.add_task(
                {
                    'title': title_field.text,
                    'description': description_field.text,
                    'module': '',
                    'icon': ''
                },
                dialog
            )
        )
        create_button.add_widget(MDButtonText(text="Ajouter"))
        
        button_container.add_widget(cancel_button)
        button_container.add_widget(create_button)
        dialog.add_widget(button_container)
        
        dialog.open()

    def show_edit_task_dialog(self, task_data, task_index, role=None):
        """Show dialog to edit a task"""
        # Force le focus sur le tableau pour fermer les menus déroulants
        self.ids.tasks_list.focus = True
        
        dialog = MDDialog(
            radius=20,
            size_hint=(.8, None),
            on_dismiss=self._clear_focus
        )
        
        dialog.add_widget(MDDialogHeadlineText(
            text="Modifier la tâche",
            theme_font_size="Custom",
            font_size="24sp"
        ))
        
        content = MDDialogContentContainer(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20)
        )
        
        title_field = MDTextField(
            text=task_data.get('title', ''),
            hint_text="Titre de la tâche",
            helper_text="Requis",
            helper_text_mode="on_error",
            mode="filled",
            on_focus=self._on_field_focus
        )
        
        description_field = MDTextField(
            text=task_data.get('description', ''),
            hint_text="Description de la tâche",
            multiline=True,
            mode="filled",
            on_focus=self._on_field_focus
        )
        
        content.add_widget(title_field)
        content.add_widget(description_field)
        
        dialog.add_widget(content)
        
        # Boutons
        button_container = MDDialogButtonContainer(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        cancel_btn = MDButton(
            style="text",
            on_release=lambda x: dialog.dismiss()
        )
        cancel_btn.add_widget(MDButtonText(text="Annuler"))
        
        save_btn = MDButton(
            style="text",
            on_release=lambda x: self.edit_task(
                task_index,
                {
                    'title': title_field.text,
                    'description': description_field.text,
                    'module': task_data.get('module', ''),
                    'icon': task_data.get('icon', '')
                },
                dialog,
                role
            )
        )
        save_btn.add_widget(MDButtonText(text="Enregistrer"))
        
        button_container.add_widget(cancel_btn)
        button_container.add_widget(save_btn)
        
        dialog.add_widget(button_container)
        dialog.open()

    def show_delete_task_dialog(self, task_data, task_index, role=None):
        """Show confirmation dialog to delete a task"""
        # Force le focus sur le tableau pour fermer les menus déroulants
        self.ids.tasks_list.focus = True
        
        dialog = MDDialog(
            radius=20,
            size_hint=(.8, None),
            on_pre_open=self._clear_text_field_focus
        )
        
        dialog.add_widget(MDDialogHeadlineText(
            text="Supprimer la tâche",
            theme_font_size="Custom",
            font_size="24sp"
        ))
        
        content = MDDialogContentContainer(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20)
        )
        
        content.add_widget(MDLabel(
            text=f"Voulez-vous vraiment supprimer la tâche '{task_data.get('title')}'?"
        ))
        
        dialog.add_widget(content)
        
        # Boutons
        button_container = MDDialogButtonContainer(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        cancel_btn = MDButton(
            style="text",
            on_release=lambda x: dialog.dismiss()
        )
        cancel_btn.add_widget(MDButtonText(text="Annuler"))
        
        delete_btn = MDButton(
            style="text",
            on_release=lambda x: self.delete_task(task_index, dialog, role)
        )
        delete_btn.add_widget(MDButtonText(text="Supprimer"))
        
        button_container.add_widget(cancel_btn)
        button_container.add_widget(delete_btn)
        
        dialog.add_widget(button_container)
        dialog.open()

    def add_task(self, task_data, dialog):
        """Add a new task to the current role"""
        if task_data['title'].strip():
            if self.roles_manager_service.add_task(self.current_role_id, task_data):
                dialog.dismiss()
                self.load_tasks()
    
    def edit_task(self, task_index, new_task_data, dialog, role=None):
        """Edit an existing task"""
        if role:
            # Mode admin : éditer la tâche dans le rôle spécifié
            role_id = role.get('id')
            self.roles_manager_service.edit_task(role_id, task_index, new_task_data)
            self.load_all_tasks()  # Recharger toutes les tâches
        else:
            # Mode normal : éditer la tâche dans le rôle courant
            self.roles_manager_service.edit_task(self.current_role_id, task_index, new_task_data)
            self.load_tasks()  # Recharger les tâches du rôle courant
        dialog.dismiss()

    def delete_task(self, task_index, dialog, role=None):
        """Delete a task"""
        if role:
            # Mode admin : supprimer la tâche du rôle spécifié
            role_id = role.get('id')
            self.roles_manager_service.delete_task(role_id, task_index)
            self.load_all_tasks()  # Recharger toutes les tâches
        else:
            # Mode normal : supprimer la tâche du rôle courant
            self.roles_manager_service.delete_task(self.current_role_id, task_index)
            self.load_tasks()  # Recharger les tâches du rôle courant
        dialog.dismiss()
    
    def go_back(self):
        """Return to the previous screen"""
        self.manager.transition.direction = 'right'
        self.manager.current = 'roles_manager'
    
    def go_to_roles(self):
        """Go to roles manager screen"""
        self.manager.transition.direction = 'left'
        self.manager.current = 'roles_manager'

    def _on_field_focus(self, instance, value):
        """Gère le focus des champs de texte et des menus déroulants"""
        if value:  # Si le champ obtient le focus
            self.current_text_field = instance
            # Fermer tout menu déroulant ouvert
            if self.current_dropdown:
                self.current_dropdown.dismiss()
                self.current_dropdown = None
        else:  # Si le champ perd le focus
            if instance == self.current_text_field:
                self.current_text_field = None

    def _clear_focus(self, *args):
        """Efface le focus de tous les champs et ferme les menus déroulants"""
        if self.current_dropdown:
            self.current_dropdown.dismiss()
            self.current_dropdown = None
        if self.current_text_field:
            self.current_text_field.focus = False
            self.current_text_field = None
        Window.focus = None

    def _clear_text_field_focus(self, *args):
        """Efface le focus de tous les champs de texte"""
        for widget in self.walk(restrict=True):
            if isinstance(widget, MDTextField):
                widget.focus = False

    def _on_window_touch(self, instance, touch):
        """Gère les clics en dehors des champs de texte et des menus"""
        if touch.grab_current is None:  # Si le clic n'est pas déjà géré
            # Vérifier si le clic est en dehors d'un champ de texte ou d'un menu
            if self.current_text_field and not self.current_text_field.collide_point(*self.current_text_field.to_widget(*touch.pos)):
                self._clear_focus()
            elif self.current_dropdown and not self.current_dropdown.content.collide_point(*self.current_dropdown.content.to_widget(*touch.pos)):
                self._clear_focus()
