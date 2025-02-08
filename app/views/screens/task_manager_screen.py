from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu

from app.services.roles_manager_service import RolesManagerService

class TaskCard(MDCard):
    def __init__(self, task_data, on_edit, on_delete, **kwargs):
        super().__init__(**kwargs)
        print(f"Création de la carte pour la tâche : {task_data}")  # Debug
        
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(120)
        self.padding = dp(16)
        self.spacing = dp(8)
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
        self.roles_manager_service = RolesManagerService()
        self.current_role_id = ''
        self.current_role_name = ''
        
        # Créer l'en-tête
        header = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            spacing=dp(10),
            padding=[dp(10), 0],
            md_bg_color=[0.2, 0.2, 0.9, 1]  # Bleu foncé
        )
        
        # Bouton retour
        back_btn = MDIconButton(
            icon="arrow-left",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            on_release=lambda x: self.go_back(),
            pos_hint={"center_y": 0.5}
        )
        header.add_widget(back_btn)
        
        # Titre
        self.title_label = MDLabel(
            text="Gestion des Tâches",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            theme_font_size="Custom",
            font_size="24sp",
            size_hint_x=0.7,
            halign="center"
        )
        header.add_widget(self.title_label)
        
        # Bouton d'ajout de tâche
        add_btn = MDIconButton(
            icon="plus",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            on_release=lambda x: self.show_add_task_dialog(),
            pos_hint={"center_y": 0.5},
            size_hint_x=0.3
        )
        header.add_widget(add_btn)
        
        # Ajouter l'en-tête à l'écran
        self.add_widget(header)
        
        # Créer la grille pour les cartes de tâches
        self.tasks_grid = MDBoxLayout(
            id='tasks_grid',
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(10), dp(10), dp(25), dp(10)],  # [gauche, haut, droite, bas]
            adaptive_height=True,
            size_hint_y=None,
            height=self.minimum_height if hasattr(self, 'minimum_height') else 0
        )
        
        # Mettre la grille dans un ScrollView
        scroll = MDScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(25),
            bar_color=[0.2, 0.2, 0.9, 1],  # Bleu
            bar_inactive_color=[0.2, 0.2, 0.9, 0.5],  # Bleu plus transparent
            bar_pos_y='right',
            scroll_type=['bars'],
            scroll_wheel_distance=dp(-40),
            size_hint=(1, 1)
        )
        scroll.add_widget(self.tasks_grid)
        self.add_widget(scroll)
        
        # Charger les tâches
        self.load_tasks()

    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        # Mettre à jour le titre si on a un rôle sélectionné
        if self.current_role_name:
            self.title_label.text = f"Tâches - {self.current_role_name}"
        else:
            self.title_label.text = "Gestion des Tâches"
            
        # Recharger les tâches
        self.load_tasks()

    def load_tasks(self):
        """Charge et affiche la liste des tâches"""
        # Effacer les tâches existantes
        self.tasks_grid.clear_widgets()
        self.tasks_grid.height = 0  # Réinitialiser la hauteur
        
        # Si on a un rôle sélectionné, charger ses tâches
        if self.current_role_id:
            tasks = self.roles_manager_service.get_tasks_for_role(self.current_role_id)
        else:
            tasks = self.roles_manager_service.get_all_tasks()
            
        # Créer une carte pour chaque tâche
        for task in tasks:
            task_card = TaskCard(
                task_data=task,
                on_edit=self.edit_task,
                on_delete=self.delete_task
            )
            self.tasks_grid.add_widget(task_card)
            # Mettre à jour la hauteur après chaque ajout
            self.tasks_grid.height += task_card.height + dp(10)  # +10 pour l'espacement
        
        # S'assurer que la hauteur minimale est respectée
        if hasattr(self.tasks_grid, 'minimum_height'):
            self.tasks_grid.height = max(self.tasks_grid.height, self.tasks_grid.minimum_height)

    def show_add_task_dialog(self):
        """Affiche le dialogue pour ajouter une nouvelle tâche."""
        self.dialog = MDDialog(
            radius=[20, 20, 20, 20],
            size_hint=(.8, None)
        )
        
        # Titre
        self.dialog.add_widget(MDDialogHeadlineText(
            text="Ajouter une nouvelle tâche",
            theme_font_size="Custom",
            font_size="24sp"
        ))
        
        # Contenu
        content_container = MDDialogContentContainer(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20)
        )
        
        # Champs de saisie
        self.task_title = MDTextField(
            hint_text="Titre de la tâche",
            mode="outlined"
        )
        content_container.add_widget(self.task_title)
        
        self.task_description = MDTextField(
            hint_text="Description de la tâche",
            mode="outlined",
            multiline=True
        )
        content_container.add_widget(self.task_description)
        
        # Menu déroulant pour le module
        self.module_button = MDButton(
            style="text",
            on_release=self.show_module_menu
        )
        self.module_button.add_widget(MDButtonText(text="Sélectionner un module"))
        content_container.add_widget(self.module_button)
        
        # Créer le menu des modules
        self.module_menu = MDDropdownMenu(
            caller=self.module_button,
            items=[
                {
                    "text": module,
                    "on_release": lambda x=module: self.select_module(x),
                }
                for module in ["operations", "maintenance", "formation", "documentation", "system"]
            ],
            width_mult=4
        )
        
        self.task_icon = MDTextField(
            hint_text="Icône (ex: account, cog, etc.)",
            mode="outlined"
        )
        content_container.add_widget(self.task_icon)
        
        self.dialog.add_widget(content_container)
        
        # Boutons
        button_container = MDDialogButtonContainer(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        # Bouton Annuler
        cancel_button = MDButton(
            style="text",
            on_release=lambda x: self.dialog.dismiss()
        )
        cancel_button.add_widget(MDButtonText(text="Annuler"))
        button_container.add_widget(cancel_button)
        
        # Bouton Sauvegarder
        save_button = MDButton(
            style="text",
            on_release=lambda x: self.save_task()
        )
        save_button.add_widget(MDButtonText(text="Sauvegarder"))
        button_container.add_widget(save_button)
        
        self.dialog.add_widget(button_container)
        self.dialog.open()

    def show_module_menu(self, button):
        """Affiche le menu des modules"""
        self.module_menu.open()

    def select_module(self, module):
        """Sélectionne un module"""
        self.module_button.text = module
        self.module_menu.dismiss()

    def add_task(self, title, description):
        """Ajoute une nouvelle tâche"""
        if title:
            # Si on a un rôle sélectionné, ajouter la tâche à ce rôle
            if self.current_role_id:
                self.roles_manager_service.add_task_to_role(
                    self.current_role_id,
                    {
                        'title': title,
                        'description': description
                    }
                )
            else:
                # Sinon, créer une tâche globale
                self.roles_manager_service.create_task({
                    'title': title,
                    'description': description
                })
            self.dialog.dismiss()
            self.load_tasks()
        else:
            self.dialog.content_cls.children[0].helper_text = "Le titre ne peut pas être vide"
            self.dialog.content_cls.children[0].error = True

    def edit_task(self, task_data):
        """Affiche le dialogue d'édition de tâche."""
        self.dialog = MDDialog(
            radius=20,
            size_hint=(.8, None)
        )
        
        # Titre
        self.dialog.add_widget(MDDialogHeadlineText(
            text="Modifier la tâche",
            theme_font_size="Custom",
            font_size="24sp"
        ))
        
        # Contenu
        content_container = MDDialogContentContainer(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20)
        )
        
        # Champs de saisie
        title_field = MDTextField(
            text=task_data["title"],
            hint_text="Titre de la tâche",
            helper_text="Requis",
            helper_text_mode="on_error",
        )
        
        description_field = MDTextField(
            text=task_data["description"],
            hint_text="Description de la tâche",
            multiline=True,
        )
        
        # Module selector button
        module_button = MDButton(
            style="text",
            text=task_data["module"],
        )
        
        # Ajouter les champs au conteneur
        content_container.add_widget(title_field)
        content_container.add_widget(description_field)
        content_container.add_widget(module_button)
        
        self.dialog.add_widget(content_container)
        
        # Boutons
        button_container = MDDialogButtonContainer(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        # Bouton Annuler
        cancel_button = MDButton(
            style="text",
            on_release=lambda x: self.dialog.dismiss()
        )
        cancel_button.add_widget(MDButtonText(text="Annuler"))
        button_container.add_widget(cancel_button)
        
        # Bouton Sauvegarder
        save_button = MDButton(
            style="text",
            on_release=lambda x: self.save_edited_task(
                task_data["id"],
                title_field.text,
                description_field.text,
                module_button.text,
                task_data["icon"]
            )
        )
        save_button.add_widget(MDButtonText(text="Sauvegarder"))
        button_container.add_widget(save_button)
        
        self.dialog.add_widget(button_container)
        
        # Create and bind the dropdown menu
        menu_items = [
            {
                "text": module,
                "on_release": lambda x=module: self.set_module(module_button, x),
            } for module in ["operations", "maintenance", "formation", "documentation"]
        ]
        self.dropdown = MDDropdownMenu(
            caller=module_button,
            items=menu_items,
            width_mult=4,
        )
        module_button.on_release = self.dropdown.open
        
        self.dialog.open()

    def set_module(self, button, module):
        """Sélectionne un module"""
        button.text = module
        self.dropdown.dismiss()

    def save_edited_task(self, task_id, title, description, module, icon):
        """Sauvegarde les modifications de la tâche"""
        if title:
            # Si on a un rôle sélectionné, mettre à jour la tâche dans ce rôle
            if self.current_role_id:
                self.roles_manager_service.update_task_in_role(
                    self.current_role_id,
                    task_id,
                    {
                        'title': title,
                        'description': description,
                        'module': module,
                        'icon': icon
                    }
                )
            else:
                # Sinon, mettre à jour la tâche globale
                self.roles_manager_service.update_task(task_id, {
                    'title': title,
                    'description': description,
                    'module': module,
                    'icon': icon
                })
            self.dialog.dismiss()
            self.load_tasks()
        else:
            self.dialog.content_cls.children[1].helper_text = "Le nom ne peut pas être vide"
            self.dialog.content_cls.children[1].error = True

    def delete_task(self, task_data):
        """Supprime une tâche après confirmation"""
        self.dialog = MDDialog(
            radius=[20, 20, 20, 20],
            size_hint=(.8, None)
        )
        
        # Titre
        self.dialog.add_widget(MDDialogHeadlineText(
            text="Confirmer la suppression",
            theme_font_size="Custom",
            font_size="24sp"
        ))
        
        # Contenu
        content_container = MDDialogContentContainer(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20)
        )
        
        content_container.add_widget(MDLabel(
            text=f"Voulez-vous vraiment supprimer la tâche '{task_data.get('title')}' ?",
            theme_text_color="Secondary"
        ))
        
        self.dialog.add_widget(content_container)
        
        # Boutons
        button_container = MDDialogButtonContainer(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        # Bouton Annuler
        cancel_button = MDButton(
            style="text",
            on_release=lambda x: self.dialog.dismiss()
        )
        cancel_button.add_widget(MDButtonText(text="Annuler"))
        button_container.add_widget(cancel_button)
        
        # Bouton Supprimer
        delete_button = MDButton(
            style="text",
            on_release=lambda x: self.confirm_delete_task(task_data)
        )
        delete_button.add_widget(MDButtonText(text="Supprimer"))
        button_container.add_widget(delete_button)
        
        self.dialog.add_widget(button_container)
        self.dialog.open()

    def confirm_delete_task(self, task_data):
        """Confirme et effectue la suppression de la tâche"""
        # Si on a un rôle sélectionné, supprimer la tâche de ce rôle
        if self.current_role_id:
            self.roles_manager_service.remove_task_from_role(self.current_role_id, task_data['id'])
        else:
            # Sinon, supprimer la tâche globale
            self.roles_manager_service.delete_task(task_data['id'])
        self.dialog.dismiss()
        self.load_tasks()

    def go_back(self):
        """Retourner à l'écran précédent"""
        self.manager.transition.direction = 'right'
        self.manager.current = 'roles_manager'

    def save_task(self):
        """Sauvegarde la nouvelle tâche"""
        title = self.task_title.text.strip()
        description = self.task_description.text.strip()
        module = self.module_button.text.strip()
        icon = self.task_icon.text.strip()
        
        if title:
            # Si on a un rôle sélectionné, ajouter la tâche à ce rôle
            if self.current_role_id:
                self.roles_manager_service.add_task_to_role(
                    self.current_role_id,
                    {
                        'title': title,
                        'description': description,
                        'module': module,
                        'icon': icon
                    }
                )
            else:
                # Sinon, créer une tâche globale
                self.roles_manager_service.create_task({
                    'title': title,
                    'description': description,
                    'module': module,
                    'icon': icon
                })
            self.dialog.dismiss()
            self.load_tasks()
        else:
            self.task_title.helper_text = "Le titre ne peut pas être vide"
            self.task_title.error = True
