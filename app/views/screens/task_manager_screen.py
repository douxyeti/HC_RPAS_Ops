from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDIconButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButtonText
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu

from app.models.task import Task, TaskModel
from app.services.firebase_service import FirebaseService
from app.services.roles_manager_service import RolesManagerService

class TaskCard(MDCard):
    title = StringProperty("")
    description = StringProperty("")
    icon = StringProperty("checkbox-marked-circle")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(120)
        self.padding = dp(16)
        self.spacing = dp(8)
        self.radius = dp(10)
        self.elevation = 2
        self.md_bg_color = [0.9, 0.9, 1, 1]  # Même fond bleu très clair que RoleCard
        
        # Header with title and buttons
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8)
        )
        
        # Title - même configuration que RoleCard
        title_label = MDLabel(
            text=self.title,
            theme_font_size="Custom",
            font_size="20sp",
            adaptive_height=True,
            size_hint_x=0.7
        )
        
        # Buttons container
        buttons_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_x=0.3,
            spacing=dp(4)
        )
        
        # Edit button
        edit_button = MDIconButton(
            icon="pencil",
            theme_text_color="Custom",
            text_color=[0.2, 0.2, 0.9, 1],
            on_release=lambda x: self.edit_task()
        )
        
        # Delete button
        delete_button = MDIconButton(
            icon="delete",
            theme_text_color="Custom",
            text_color=[0.9, 0.2, 0.2, 1],
            on_release=lambda x: self.delete_task()
        )
        
        buttons_box.add_widget(edit_button)
        buttons_box.add_widget(delete_button)
        
        header.add_widget(title_label)
        header.add_widget(buttons_box)
        
        # Description - même configuration que RoleCard
        description_label = MDLabel(
            text=self.description,
            adaptive_height=True
        )
        
        self.add_widget(header)
        self.add_widget(description_label)
        
    def edit_task(self):
        """Déclenche l'édition de la tâche"""
        if hasattr(self.parent.parent.parent.parent, 'show_edit_task_dialog'):
            self.parent.parent.parent.parent.show_edit_task_dialog(self.title, self.description)
            
    def delete_task(self):
        """Déclenche la suppression de la tâche"""
        if hasattr(self.parent.parent.parent.parent, 'show_delete_task_dialog'):
            self.parent.parent.parent.parent.show_delete_task_dialog(self.title)

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
    current_role_id = StringProperty('')  
    current_role_name = StringProperty('')
    tasks = ListProperty([])
    tasks_container = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_model = TaskModel(FirebaseService())
        
    def set_current_role(self, role_id, role_name=None):
        """Définit le rôle actuel et charge ses tâches"""
        print(f"[DEBUG] TaskManagerScreen.set_current_role - Entrée avec role_id: '{role_id}', role_name: '{role_name}'")
        
        roles_service = RolesManagerService()
        
        # Si on a un role_id, essayer de trouver le rôle directement
        if role_id:
            print(f"[DEBUG] TaskManagerScreen.set_current_role - Recherche par ID: '{role_id}'")
            role = roles_service.get_role(role_id)
            if role:
                print(f"[DEBUG] TaskManagerScreen.set_current_role - Rôle trouvé par ID: {role}")
                self.current_role_id = role_id
                self.current_role_name = role.get('name', role_name)
                self.load_tasks()
                return
        
        # Si on a un role_name, essayer de trouver le rôle par son nom
        if role_name:
            normalized_name = roles_service.normalize_string(role_name)
            print(f"[DEBUG] TaskManagerScreen.set_current_role - Recherche par nom normalisé: '{normalized_name}'")
            
            roles = roles_service.get_all_roles()
            print(f"[DEBUG] TaskManagerScreen.set_current_role - Comparaison avec {len(roles)} rôles:")
            for role in roles:
                role_name_db = role.get('name', '')
                role_name_normalized = roles_service.normalize_string(role_name_db)
                print(f"[DEBUG] TaskManagerScreen.set_current_role - Comparaison: '{role_name_normalized}' == '{normalized_name}' (original: '{role_name_db}')")
                if role_name_normalized == normalized_name:
                    print(f"[DEBUG] TaskManagerScreen.set_current_role - Correspondance trouvée!")
                    self.current_role_id = role.get('id')
                    self.current_role_name = role.get('name')
                    self.load_tasks()
                    return
        
        # Si on arrive ici, le rôle n'a pas été trouvé
        print(f"Rôle inconnu: {role_name}")
        self.tasks = []
        self.display_tasks()
        
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
        """Affiche le formulaire pour ajouter une tâche"""
        print("[DEBUG] TaskManagerScreen.show_add_task_dialog - Début")
        
        # Créer ou réutiliser le formulaire
        if not hasattr(self, 'task_form'):
            self.task_form = MDCard(
                orientation='vertical',
                size_hint=(None, None),
                size=(400, 450),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                padding=20,
                spacing=10
            )
        else:
            # Si le formulaire existe déjà, le nettoyer
            self.task_form.clear_widgets()
        
        # Titre du formulaire
        form_title = MDLabel(
            text="Ajouter une tâche",
            theme_font_size="Custom",
            font_size="24sp",
            halign="center",
            size_hint_y=None,
            height=dp(36)
        )
        
        # Champs de saisie
        self.title_field = MDTextField(
            hint_text="Titre de la tâche",
            helper_text="Le titre de la tâche est requis",
            helper_text_mode="on_error",
            required=True
        )
        
        self.description_field = MDTextField(
            hint_text="Description",
            multiline=True,
            helper_text="La description est optionnelle"
        )
        
        # Boutons
        buttons_box = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=50,
            pos_hint={'center_x': 0.5}
        )
        
        cancel_button = MDButton(
            style="outlined",
            on_release=self.remove_form
        )
        cancel_button.add_widget(MDButtonText(
            text="Annuler",
            theme_font_size="Custom",
            font_size="14sp"
        ))
        
        save_button = MDButton(
            style="filled",
            on_release=self.add_task
        )
        save_button.add_widget(MDButtonText(
            text="Ajouter",
            theme_font_size="Custom",
            font_size="14sp"
        ))
        
        buttons_box.add_widget(cancel_button)
        buttons_box.add_widget(save_button)
        
        # Ajouter tous les widgets au formulaire
        self.task_form.add_widget(form_title)
        self.task_form.add_widget(self.title_field)
        self.task_form.add_widget(self.description_field)
        self.task_form.add_widget(buttons_box)
        
        # Ajouter le formulaire à l'écran
        self.add_widget(self.task_form)

    def remove_form(self, *args):
        """Retire le formulaire de l'écran"""
        if hasattr(self, 'task_form'):
            self.remove_widget(self.task_form)
            delattr(self, 'task_form')
            self.title_field = None
            self.description_field = None

    def add_task(self, *args):
        """Ajoute une nouvelle tâche"""
        print("[DEBUG] TaskManagerScreen.add_task - Début de l'ajout")
        if self.title_field.text:
            # Utiliser "Aucune description" si le champ est vide
            description = self.description_field.text.strip() or "Aucune description"
            
            # Créer les données de la tâche
            task_data = {
                'title': self.title_field.text.strip(),
                'description': description,
                'module': 'operations',
                'icon': 'clipboard-check'
            }
            
            # Ajouter la tâche
            if self.task_model.add_task(self.current_role_id, task_data):
                print("[DEBUG] TaskManagerScreen.add_task - Ajout réussi")
                # Réinitialiser les champs
                self.title_field.text = ""
                self.description_field.text = ""
                
                # Fermer le formulaire et recharger les tâches
                self.remove_form()
                self.load_tasks()
            else:
                print("[DEBUG] TaskManagerScreen.add_task - Échec de l'ajout")
                self.title_field.error = True
                self.title_field.helper_text = "Erreur lors de l'ajout de la tâche"
        else:
            print("[DEBUG] TaskManagerScreen.add_task - Erreur: titre manquant")
            self.title_field.error = True
            self.title_field.helper_text = "Le titre de la tâche est requis"

    def show_edit_task_dialog(self, title, description):
        """Affiche le formulaire d'édition d'une tâche"""
        if not hasattr(self, 'edit_task_card'):
            # Créer la carte d'édition
            edit_card = MDCard(
                orientation='vertical',
                size_hint=(None, None),
                size=(400, 300),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                padding=dp(15),
                spacing=dp(10)
            )
            
            # Titre du formulaire
            title_label = MDLabel(
                text="Modifier la tâche",
                theme_font_size="Custom",
                font_size="20sp",
                adaptive_height=True
            )
            edit_card.add_widget(title_label)
            
            # Champ titre
            self.title_field = MDTextField(
                text=title,
                hint_text="Titre de la tâche",
                helper_text="Ce champ est requis",
                helper_text_mode="on_error",
                required=True
            )
            edit_card.add_widget(self.title_field)
            
            # Champ description
            self.description_field = MDTextField(
                text=description,
                hint_text="Description de la tâche",
                multiline=True,
                max_height="100dp"
            )
            edit_card.add_widget(self.description_field)
            
            # Conteneur pour les boutons
            buttons_container = MDBoxLayout(
                orientation='horizontal',
                adaptive_height=True,
                spacing=dp(10),
                pos_hint={'right': 1}
            )
            
            # Bouton Annuler
            cancel_button = MDButton(
                style="outlined",
                on_release=lambda x: self.remove_edit_form()
            )
            cancel_button.add_widget(MDButtonText(
                text="Annuler",
                theme_font_size="Custom",
                font_size="14sp"
            ))
            
            # Bouton Sauvegarder
            save_button = MDButton(
                style="filled",
                on_release=lambda x: self.update_task(title)
            )
            save_button.add_widget(MDButtonText(
                text="Sauvegarder",
                theme_font_size="Custom",
                font_size="14sp"
            ))
            
            buttons_container.add_widget(cancel_button)
            buttons_container.add_widget(save_button)
            edit_card.add_widget(buttons_container)
            
            self.edit_task_card = edit_card
            self.add_widget(edit_card)

    def remove_edit_form(self, *args):
        """Retire le formulaire d'édition"""
        if hasattr(self, 'edit_task_card'):
            self.remove_widget(self.edit_task_card)
            delattr(self, 'edit_task_card')
            self.title_field = None
            self.description_field = None

    def update_task(self, old_title):
        """Met à jour une tâche existante"""
        if not self.title_field.text:
            self.title_field.error = True
            return
            
        task_data = {
            'title': self.title_field.text.strip(),
            'description': self.description_field.text.strip() or "Aucune description"
        }
        
        if self.task_model.update_task(self.current_role_id, old_title, task_data):
            self.load_tasks()
            self.remove_edit_form()
        else:
            self.title_field.error = True
            self.title_field.helper_text = "Erreur lors de la mise à jour de la tâche"
            
    def show_delete_task_dialog(self, title):
        """Affiche la boîte de dialogue de confirmation de suppression"""
        if not hasattr(self, 'confirm_delete_card'):
            # Créer la carte de confirmation
            confirm_card = MDCard(
                orientation='vertical',
                size_hint=(None, None),
                size=(400, 200),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                padding=dp(15),
                spacing=dp(10)
            )
            
            # Titre
            title_label = MDLabel(
                text=f"Supprimer la tâche '{title}' ?",
                theme_font_size="Custom",
                font_size="20sp",
                adaptive_height=True
            )
            confirm_card.add_widget(title_label)
            
            # Message d'avertissement
            warning = MDLabel(
                text="Cette action est irréversible. Êtes-vous sûr de vouloir supprimer cette tâche ?",
                theme_font_size="Custom",
                font_size="14sp",
                adaptive_height=True
            )
            confirm_card.add_widget(warning)
            
            # Conteneur pour les boutons
            buttons_container = MDBoxLayout(
                orientation='horizontal',
                adaptive_height=True,
                spacing=dp(10),
                pos_hint={'right': 1}
            )
            
            # Bouton Annuler
            cancel_button = MDButton(
                style="outlined",
                on_release=lambda x: self.remove_delete_confirmation()
            )
            cancel_button.add_widget(MDButtonText(
                text="Annuler",
                theme_font_size="Custom",
                font_size="14sp"
            ))
            
            # Bouton Confirmer
            confirm_button = MDButton(
                style="filled",
                on_release=lambda x: self.delete_task_confirm(title)
            )
            confirm_button.add_widget(MDButtonText(
                text="Confirmer",
                theme_font_size="Custom",
                font_size="14sp"
            ))
            
            buttons_container.add_widget(cancel_button)
            buttons_container.add_widget(confirm_button)
            confirm_card.add_widget(buttons_container)
            
            self.confirm_delete_card = confirm_card
            self.add_widget(confirm_card)

    def remove_delete_confirmation(self, *args):
        """Retire la carte de confirmation de suppression"""
        if hasattr(self, 'confirm_delete_card'):
            self.remove_widget(self.confirm_delete_card)
            delattr(self, 'confirm_delete_card')

    def delete_task_confirm(self, title):
        """Supprime une tâche après confirmation"""
        self.task_model.delete_task(self.current_role_id, title)
        self.load_tasks()  
        self.remove_delete_confirmation()

    def show_menu(self, items, caller=None):
        """Affiche un menu déroulant"""
        menu = MDDropdownMenu(
            caller=caller,
            items=items,
            width_mult=4,
            max_height=dp(250),
            radius=[8, 8, 8, 8],
            background_color=[0.9, 0.9, 1, 1]
        )
        menu.open()

    def show_filter_menu(self, button):
        """Affiche le menu de filtrage des tâches"""
        menu_items = [
            {
                "text": "Toutes les tâches",
                "on_release": lambda x="all": self.filter_tasks(x),
            },
            {
                "text": "Opérations",
                "on_release": lambda x="operations": self.filter_tasks(x),
            },
            {
                "text": "Formation",
                "on_release": lambda x="formation": self.filter_tasks(x),
            },
            {
                "text": "Maintenance",
                "on_release": lambda x="maintenance": self.filter_tasks(x),
            }
        ]
        self.show_menu(menu_items, button)

    def show_sort_menu(self, button):
        """Affiche le menu de tri des tâches"""
        menu_items = [
            {
                "text": "Par titre (A-Z)",
                "on_release": lambda x="title_asc": self.sort_tasks(x),
            },
            {
                "text": "Par titre (Z-A)",
                "on_release": lambda x="title_desc": self.sort_tasks(x),
            }
        ]
        self.show_menu(menu_items, button)

    def filter_tasks(self, filter_type):
        """Filtre les tâches selon le module"""
        if filter_type == "all":
            self.load_tasks()  # Garde le comportement actuel pour "all"
        else:
            filtered_tasks = self.task_model.filter_by_module(self.tasks, filter_type)
            self.display_tasks(filtered_tasks)

    def sort_tasks(self, sort_type):
        """Trie les tâches selon le critère"""
        ascending = sort_type == "title_asc"
        sorted_tasks = self.task_model.sort_by_title(self.tasks, ascending)
        self.display_tasks(sorted_tasks)
