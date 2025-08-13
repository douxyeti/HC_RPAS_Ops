from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty, ListProperty, BooleanProperty
from kivy.uix.widget import Widget
from kivy.app import App
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDIconButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButtonText
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu

from app.models.task import Task, TaskModel
from app.services.firebase_service import FirebaseService
from app.services.roles_manager_service import RolesManagerService
from app.utils.module_discovery import ModuleDiscovery
from app.utils.task_router import go_to_task


class ModuleSelectorCard(MDCard):
    module_id = StringProperty()
    branch = StringProperty()
    is_selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(70)
        self.style = "elevated"
        self.md_bg_color = [1, 1, 1, 1]
        self.ripple_behavior = True
        self.shadow_softness = 2
        self.shadow_offset = (0, 1)
        self.padding = dp(4)

        self.main_layout = MDBoxLayout(orientation="horizontal", spacing=0, padding=0, size_hint=(1, 1))
        self.selection_indicator = MDBoxLayout(size_hint=(None, 1), width=dp(5), md_bg_color=[0, 0.6, 1, 1], opacity=0)
        self.content_layout = MDBoxLayout(orientation="vertical", spacing=dp(2), padding=(dp(8), 0, 0, 0), size_hint=(1, 1))
        
        self.main_layout.add_widget(self.selection_indicator)
        self.main_layout.add_widget(self.content_layout)
        super().add_widget(self.main_layout)

    def add_widget(self, widget, index=0, canvas=None):
        if hasattr(self, 'content_layout') and self.content_layout is not None:
            return self.content_layout.add_widget(widget, index, canvas)
        return super().add_widget(widget, index, canvas)

    def set_selected(self, is_selected):
        self.is_selected = is_selected
        if is_selected:
            self.md_bg_color = [0.9, 0.95, 1, 1]
            self.selection_indicator.opacity = 1
            self.elevation = 4
        else:
            self.md_bg_color = [1, 1, 1, 1]
            self.selection_indicator.opacity = 0
            self.elevation = 1


class ScreenSelectorCard(MDCard):
    screen_id = StringProperty()
    is_selected = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(50)
        self.md_bg_color = [1, 1, 1, 1]
        self.ripple_behavior = True
        self.elevation = 1
        self.padding = dp(4)

        self.main_layout = MDBoxLayout(orientation="horizontal", spacing=0, padding=0, size_hint=(1, 1))
        self.selection_indicator = MDBoxLayout(size_hint=(None, 1), width=dp(5), md_bg_color=[0, 0.6, 1, 1], opacity=0)
        self.content_layout = MDBoxLayout(orientation="vertical", spacing=dp(2), padding=(dp(8), 0, 0, 0), size_hint=(1, 1))
        
        self.main_layout.add_widget(self.selection_indicator)
        self.main_layout.add_widget(self.content_layout)
        super().add_widget(self.main_layout)

    def add_widget(self, widget, index=0, canvas=None):
        if hasattr(self, 'content_layout') and self.content_layout is not None:
            return self.content_layout.add_widget(widget, index, canvas)
        return super().add_widget(widget, index, canvas)

    def set_selected(self, is_selected):
        self.is_selected = is_selected
        if is_selected:
            self.md_bg_color = [0.9, 0.95, 1, 1]
            self.selection_indicator.opacity = 1
        else:
            self.md_bg_color = [1, 1, 1, 1]
            self.selection_indicator.opacity = 0

class TaskCard(MDCard):
    title = StringProperty("")
    description = StringProperty("")
    icon = StringProperty("checkbox-marked-circle")
    current_role = StringProperty("")
    target_module_id = StringProperty("")
    target_screen_id = StringProperty("")
    
    PROTECTED_TASKS = [
        'Configuration système',
        'Gestion des accès',
        'Maintenance système',
        'Gestion des rôles'
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.size_hint_x = 0.95  # Laisse une marge de 5% pour éviter la superposition avec la barre de défilement
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
        
        # Bouton Ouvrir (toujours visible)
        
        open_button = MDIconButton(
        
            icon="play",
        
            theme_text_color="Custom",
        
            text_color=[0.2, 0.6, 0.2, 1],
        
            on_release=lambda x: self.open_task()
        
        )
        
        buttons_box.add_widget(open_button)

        
        # Vérifier si la tâche est protégée
        is_protected = (self.current_role == 'super_admin' and 
                       self.title in self.PROTECTED_TASKS)
        
        if not is_protected:
            # Edit button
            edit_button = MDIconButton(
                icon="pencil",
                theme_text_color="Custom",
                text_color=[0.2, 0.2, 0.9, 1],
                on_release=lambda x: self.edit_task()
            )
            buttons_box.add_widget(edit_button)

            # Delete button
            delete_button = MDIconButton(
                icon="delete",
                theme_text_color="Custom",
                text_color=[0.9, 0.2, 0.2, 1],
                on_release=lambda x: self.delete_task()
            )
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
        
    def open_task(self):
        
        """Lance la tâche via TaskManagerScreen.launch_task"""
        
        # remonte au parent écran
        
        parent = getattr(self.parent, 'parent', None)
        
        if parent and hasattr(parent, 'parent'):
        
            parent = parent.parent
        
        if parent and hasattr(parent, 'parent'):
        
            parent = parent.parent
        
        # parent doit porter 'launch_task'
        
        if hasattr(parent, 'launch_task'):
        
            task = {'title': self.title, 'description': self.description}
        
            if self.target_module_id:
        
                task['target_module_id'] = self.target_module_id
        
            if self.target_screen_id:
        
                task['target_screen_id'] = self.target_screen_id
        
            parent.launch_task(task)
        
    
        
    def edit_task(self):
        """Déclenche l'édition de la tâche"""
        if hasattr(self.parent.parent.parent.parent, 'show_edit_task_dialog'):
            print(f"[DEBUG] TaskCard.edit_task - Edition de la tâche {self.title} avec index: {self.target_module_id}.{self.target_screen_id}")
            self.parent.parent.parent.parent.show_edit_task_dialog(
                self.title, 
                self.description,
                self.target_module_id,
                self.target_screen_id
            )
            
    def delete_task(self):
        """Déclenche la suppression de la tâche"""
        if hasattr(self.parent.parent.parent.parent, 'show_delete_task_dialog'):
            self.parent.parent.parent.parent.show_delete_task_dialog(self.title)

class TaskEditDialog(MDDialog):
    dialog_title = StringProperty("Nouvelle tâche")
    task_title = StringProperty("")
    task_description = StringProperty("")
    task_target_screen = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_save')
        self.register_event_type('on_cancel')
        
        # Si l'ID d'écran est passé, l'extraire
        if 'task_target_screen' in kwargs:
            self.task_target_screen = kwargs['task_target_screen']
    
    def on_save(self, *args):
        pass
        
    def on_cancel(self, *args):
        pass
        
    def get_task_data(self):
        target_info = {}
        
        # Extraire les informations d'index si présentes
        target_screen = self.ids.target_screen_field.text.strip()
        if target_screen:
            parts = target_screen.split('.')
            if len(parts) == 2:
                target_info['target_module_id'] = parts[0]
                target_info['target_screen_id'] = parts[1]
            
        return {
            'title': self.ids.title_field.text,
            'description': self.ids.description_field.text,
            **target_info
        }

class TaskManagerScreen(MDScreen):
    def launch_task(self, task: dict):
        """Route une tâche (ouvre le module/écran cible)."""
        try:
            # Reconstruit un ModuleDiscovery et passe l'instance App si dispo
            md = ModuleDiscovery(FirebaseService.get_instance())
            try:
                app = App.get_running_app()
            except Exception:
                app = None
            go_to_task(md, task, app_instance=app)
        except Exception as e:
            print(f"[TASK ROUTER] Erreur lancement tâche {task.get('title')}: {e}")
    selected_module_id = StringProperty(None)
    selected_screen_id = StringProperty(None)

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
        print(f"[DEBUG] TaskManagerScreen.display_tasks - Container: {self.tasks_container}")
        
        if self.tasks_container:
            self.tasks_container.clear_widgets()
            
            for task in tasks:
                print(f"[DEBUG] TaskManagerScreen.display_tasks - Création de carte pour la tâche : {task}")
                task_card = TaskCard(
                    title=task.get('title', ''),
                    description=task.get('description', ''),
                    current_role=self.current_role_id,
                    target_module_id=task.get('target_module_id', ''),
                    target_screen_id=task.get('target_screen_id', '')
                )
                self.tasks_container.add_widget(task_card)
                
    def go_back(self, *args):
        """Retourne à l'écran précédent"""
        self.manager.current = 'roles_manager'
        
    def show_add_task_dialog(self):
        """Affiche le formulaire pour ajouter une tâche"""
        print("[DEBUG] TaskManagerScreen.show_add_task_dialog - Affichage du formulaire")
        
        # Vérifier si le formulaire existe déjà
        if not hasattr(self, 'task_form'):
            # Créer le formulaire
            self.task_form = MDCard(
                size_hint=(None, None),
                size=(500, 550),  # Augmentation de la hauteur pour accommoder les labels
                pos_hint={"center_x": 0.5, "center_y": 0.5},
                elevation=4,
                md_bg_color=[1, 1, 1, 1],
                orientation="vertical",
                padding=15,
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
        
        # Champs de saisie avec labels
        # Label + champ pour le titre
        title_box = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(70),
            spacing=2
        )
        
        title_label = MDLabel(
            text="Titre de la tâche:",
            theme_font_size="Custom",
            font_size="14sp",
            bold=True,
            adaptive_height=True
        )
        
        self.title_field = MDTextField(
            hint_text="Titre de la tâche",
            helper_text="Le titre de la tâche est requis",
            helper_text_mode="on_error",
            required=True
        )
        
        title_box.add_widget(title_label)
        title_box.add_widget(self.title_field)
        
        # Label + champ pour la description
        description_box = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120), spacing=12
        )
        
        description_label = MDLabel(
            text="Description:",
            theme_font_size="Custom",
            font_size="14sp",
            bold=True,
            adaptive_height=True
        )
        
        self.description_field = MDTextField(
            hint_text="Description",
            multiline=True,
            helper_text="La description est optionnelle"
        )
        
        description_box.add_widget(description_label)
        description_box.add_widget(self.description_field)
        
        # Champ pour l'écran cible (module)
        target_section_box = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120), spacing=12
        )
        
        target_section_label = MDLabel(
            text="Module et écran cible:",
            theme_font_size="Custom",
            font_size="14sp",
            bold=True,
            adaptive_height=True
        )
        
        # Champ pour le module (première partie)
        module_box = MDBoxLayout(
            orientation='horizontal',
            spacing=12,
            size_hint_y=None,
            height=dp(50)
        )
        
        self.target_module_field = MDTextField(
            id="target_module_field",
            hint_text="Nom du module",
            helper_text="Ex: operations, gestion, etc.",
            size_hint_x=1.0
        )
        
        module_box.add_widget(self.target_module_field)
        
        # Champ pour l'écran (deuxième partie)
        screen_box = MDBoxLayout(
            orientation='horizontal',
            spacing=12,
            size_hint_y=None,
            height=dp(50)
        )
        
        self.target_screen_field = MDTextField(
            id="target_screen_field",
            hint_text="Nom de l'écran",
            helper_text="Ex: missions_screen, tasks_screen",
            size_hint_x=0.7
        )
        
        browse_button = MDButton(
            style="outlined",
            size_hint=(None, None),
            size=(dp(120), dp(40)),
            pos_hint={"center_y": 0.5},
            on_release=lambda x: self.open_modules_browser()
        )
        browse_button.add_widget(MDButtonText(
            text="Parcourir...",
            theme_font_size="Custom",
            font_size="14sp"
        ))
        
        screen_box.add_widget(self.target_screen_field)
        # Bouton "Parcourir" pour choisir module/écran
        browse_button = MDButton(style="elevated", size_hint=(None, None), size=(dp(120), dp(40)), pos_hint={"center_y": 0.5})
        browse_button.add_widget(MDButtonText(text="Parcourir", theme_font_size="Custom", font_size="14sp"))
        def browse_click(instance):
            print("[DEBUG] Bouton parcourir cliqué!")
            self.show_module_selector()
        browse_button.bind(on_release=browse_click)
        screen_box.add_widget(browse_button)
        target_screen_box = MDBoxLayout(
            orientation='vertical',
            spacing=12,
            size_hint_y=None,
            height=dp(110)
        )        
        target_screen_box.add_widget(module_box)
        target_screen_box.add_widget(screen_box)
        
        # Boutons
        buttons_box = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=dp(50),
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
        
        # Ajouter l'étiquette de l'écran cible au conteneur
        target_section_box.add_widget(target_section_label)
        target_section_box.add_widget(target_screen_box)
        
        # Ajouter tous les widgets au formulaire
        self.task_form.add_widget(form_title)
        self.task_form.add_widget(title_box)
        self.task_form.add_widget(description_box)
        # Ajouter un spacer pour créer plus d'espace entre description et cible
        spacer = Widget(size_hint_y=None, height=dp(20))
        self.task_form.add_widget(spacer)
        self.task_form.add_widget(target_section_box)
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
            self.target_module_field = None
            self.target_screen_field = None

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
            
            # Ajouter les informations d'écran cible si présentes
            module_id = self.target_module_field.text.strip()
            screen_id = self.target_screen_field.text.strip()
            
            if module_id and screen_id:
                task_data['target_module_id'] = module_id
                task_data['target_screen_id'] = screen_id
                # Ajouter une icône spécifique pour les tâches liées à un module
                task_data['icon'] = 'link-variant'
            
            # Ajouter la tâche
            if self.task_model.add_task(self.current_role_id, task_data):
                print("[DEBUG] TaskManagerScreen.add_task - Ajout réussi")
                # Réinitialiser les champs
                self.title_field.text = ""
                self.description_field.text = ""
                self.target_screen_field.text = ""
                
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

    def show_edit_task_dialog(self, title, description, target_module_id='', target_screen_id=''):
        """Affiche le formulaire d'édition d'une tâche"""
        print("[DEBUG] Début de show_edit_task_dialog")
        
        # Supprimer tout dialogue existant
        if hasattr(self, 'edit_task_card') and self.edit_task_card and self.edit_task_card.parent:
            self.edit_task_card.parent.remove_widget(self.edit_task_card)
        
        # Créer la carte d'édition
        edit_card = MDCard(
            orientation='vertical',
            size_hint=(None, None),
            size=(500, 550),  # Augmentation de la hauteur pour accommoder les labels
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            elevation=4,
            md_bg_color=[1, 1, 1, 1],
            padding=15,
            spacing=10
        )
        
        # Titre du formulaire
        form_title = MDLabel(
            text="Modifier la tâche",
            theme_font_size="Custom",
            font_size="24sp",
            halign="center",
            size_hint_y=None,
            height=dp(36)
        )
        edit_card.add_widget(form_title)
        
        # Label + champ pour le titre
        title_box = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(70),
            spacing=2
        )
        
        title_label = MDLabel(
            text="Titre de la tâche:",
            theme_font_size="Custom",
            font_size="14sp",
            bold=True,
            adaptive_height=True
        )
        
        self.title_field = MDTextField(
            text=title,
            hint_text="Titre de la tâche",
            helper_text="Ce champ est requis",
            helper_text_mode="on_error",
            required=True
        )
        
        title_box.add_widget(title_label)
        title_box.add_widget(self.title_field)
        edit_card.add_widget(title_box)
        
        # Label + champ pour la description
        description_box = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120), spacing=12
        )
        
        description_label = MDLabel(
            text="Description:",
            theme_font_size="Custom",
            font_size="14sp",
            bold=True,
            adaptive_height=True
        )
        
        self.description_field = MDTextField(
            text=description,
            hint_text="Description de la tâche",
            multiline=True,
            max_height="100dp"
        )
        
        description_box.add_widget(description_label)
        description_box.add_widget(self.description_field)
        edit_card.add_widget(description_box)
        # Ajouter un spacer pour créer plus d'espace entre description et cible
        spacer = Widget(size_hint_y=None, height=dp(20))
        edit_card.add_widget(spacer)
        
        # Section pour l'écran cible (module)
        target_section_box = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120), spacing=12
        )
        
        target_section_label = MDLabel(
            text="Module et écran cible:",
            theme_font_size="Custom",
            font_size="14sp",
            bold=True,
            adaptive_height=True
        )
        
        # Champ pour le module (première partie)
        module_box = MDBoxLayout(
            orientation='horizontal',
            spacing=12,
            size_hint_y=None,
            height=dp(50)
        )
        
        self.target_module_field = MDTextField(
            id="target_module_field",
            text=target_module_id,
            hint_text="Nom du module",
            helper_text="Ex: operations, gestion, etc.",
            size_hint_x=1.0
        )
        
        module_box.add_widget(self.target_module_field)
        
        # Champ pour l'écran (deuxième partie)
        screen_box = MDBoxLayout(
            orientation='horizontal',
            spacing=12,
            size_hint_y=None,
            height=dp(50)
        )
        
        self.target_screen_field = MDTextField(
            id="target_screen_field",
            text=target_screen_id,
            hint_text="Nom de l'écran",
            helper_text="Ex: missions_screen, tasks_screen",
            size_hint_x=0.7
        )
        
        target_section_box.add_widget(target_section_label)
        screen_box.add_widget(self.target_screen_field)
# -- restore "Parcourir" button to pick module->screen, fills target fields
        # Bouton "Parcourir" pour choisir module/écran
        browse_button = MDButton(style="elevated", size_hint=(None, None), size=(dp(120), dp(40)), pos_hint={"center_y": 0.5})
        browse_button.add_widget(MDButtonText(text="Parcourir", theme_font_size="Custom", font_size="14sp"))
        def browse_click(instance):
            print("[DEBUG] Bouton parcourir cliqué!")
            self.show_module_selector()
        browse_button.bind(on_release=browse_click)
        screen_box.add_widget(browse_button)
        target_section_box.add_widget(screen_box)
        edit_card.add_widget(target_section_box)
        
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
            on_release=lambda x: self.update_task(title)
        )
        save_button.add_widget(MDButtonText(
            text="Sauvegarder",
            theme_font_size="Custom",
            font_size="14sp"
        ))
        
        buttons_container.add_widget(Widget())  # Spacer
        buttons_container.add_widget(cancel_button)
        buttons_container.add_widget(save_button)
        
        edit_card.add_widget(buttons_container)
        
        # Ajouter au layout parent
        parent_layout = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, 1)
        )
        parent_layout.add_widget(Widget())  # Spacer haut
        parent_layout.add_widget(edit_card)
        parent_layout.add_widget(Widget())  # Spacer bas
        
        self.edit_task_card = parent_layout
        self.add_widget(parent_layout)

    def remove_edit_form(self, *args):
        """Retire le formulaire d'édition"""
        if hasattr(self, 'edit_task_card'):
            self.remove_widget(self.edit_task_card)
            delattr(self, 'edit_task_card')
            self.title_field = None
            self.description_field = None
            self.target_module_field = None
            self.target_screen_field = None

    def update_task(self, old_title):
        """Met à jour une tâche existante"""
        if self.title_field.text:
            # Préparer les nouvelles données
            updated_task = {
                'title': self.title_field.text.strip(),
                'description': self.description_field.text.strip() or "Aucune description"
            }
            
            # Ajouter les informations d'écran cible si présentes
            module_id = self.target_module_field.text.strip()
            screen_id = self.target_screen_field.text.strip()
            
            if module_id and screen_id:
                updated_task['target_module_id'] = module_id
                updated_task['target_screen_id'] = screen_id
                # Ajouter une icône spécifique pour les tâches liées à un module
                updated_task['icon'] = 'link-variant'
            
            # Mettre à jour la tâche
            if self.task_model.update_task(self.current_role_id, old_title, updated_task):
                print(f"[DEBUG] TaskManagerScreen.update_task - Mise à jour réussie de {old_title}")
                # Réinitialiser et fermer le formulaire
                self.remove_edit_form()
                # Recharger les tâches
                self.load_tasks()
            else:
                print(f"[DEBUG] TaskManagerScreen.update_task - Échec de la mise à jour de {old_title}")
                self.title_field.error = True
                self.title_field.helper_text = "Erreur lors de la mise à jour de la tâche"
        else:
            self.title_field.error = True
            self.title_field.helper_text = "Le titre de la tâche est requis"

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
        print(f"[DEBUG] TaskManagerScreen.delete_task_confirm - Début de la suppression de '{title}'")
        result = self.task_model.delete_task(self.current_role_id, title)
        
        if result:
            print(f"[DEBUG] TaskManagerScreen.delete_task_confirm - Suppression réussie, rechargement des tâches")
            # Recréer une nouvelle instance du modèle de tâches pour éviter les problèmes de cache
            self.task_model = TaskModel(FirebaseService())
            # Vider et reconstruire la liste de tâches
            self.tasks = []
            self.load_tasks()
        else:
            print(f"[ERROR] TaskManagerScreen.delete_task_confirm - Échec de la suppression de '{title}'")
            # On recharge quand même pour s'assurer que l'interface est à jour
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
        
    def select_module(self, module_id, branch):
        """Met à jour le module sélectionné et rafraîchit l'interface."""
        self.selected_module_id = module_id

        # Garder une référence au champ cible pour la réouverture
        target_field = self.target_screen_field if hasattr(self, 'target_screen_field') else None

        # Fermer le sélecteur actuel pour le forcer à se reconstruire
        if hasattr(self, '_selector_view') and self._selector_view.parent:
            self.remove_widget(self._selector_view)
        
        # Rouvrir le sélecteur, qui utilisera self.selected_module_id pour l'affichage
        self.show_module_selector(target_field=target_field)

    def show_module_selector(self, target_field=None):
        """Affiche un sélecteur de modules et écrans pour associer à une tâche."""
        try:
            if hasattr(self, '_selector_view') and self._selector_view and self._selector_view.parent:
                self.remove_widget(self._selector_view)

            app = App.get_running_app()
            discovery = ModuleDiscovery(app.firebase_service)
            modules = discovery.get_installed_modules()

            selected_module_info = {'id': None, 'branch': None}
            selected_screen_id = [None]

            overlay = MDBoxLayout(orientation="vertical", size_hint=(1, 1), md_bg_color=[0, 0, 0, 0.5], padding=dp(16))
            selector_card = MDCard(orientation="vertical", size_hint=(0.9, 0.9), pos_hint={"center_x": 0.5, "center_y": 0.5}, elevation=4, md_bg_color=[1, 1, 1, 1], padding=dp(16), spacing=dp(8))
            header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(8))
            title = MDLabel(text="Sélectionner un écran de module", theme_font_size="Custom", font_size="20sp", bold=True, size_hint_x=0.9)
            close_button = MDIconButton(icon="close", size_hint_x=0.1, on_release=lambda x: self.remove_widget(overlay))
            header.add_widget(title)
            header.add_widget(close_button)
            
            content = MDBoxLayout(orientation="horizontal", spacing=dp(16), size_hint_y=0.9)
            modules_box = MDBoxLayout(orientation="vertical", size_hint_x=0.5, spacing=dp(8))
            modules_title = MDLabel(text="Modules", theme_font_size="Custom", font_size="18sp", bold=True, size_hint_y=None, height=dp(30))
            modules_scroll = MDScrollView()
            modules_content = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=[0, dp(4)])
            modules_content.bind(minimum_height=modules_content.setter('height'))
            modules_scroll.add_widget(modules_content)
            modules_box.add_widget(modules_title)
            modules_box.add_widget(modules_scroll)
            
            screens_box = MDBoxLayout(orientation="vertical", size_hint_x=0.5, spacing=dp(8))
            screens_title = MDLabel(text="Écrans", theme_font_size="Custom", font_size="18sp", bold=True, size_hint_y=None, height=dp(30))
            screens_scroll = MDScrollView()
            screens_content = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=[0, dp(4)])
            screens_content.bind(minimum_height=screens_content.setter('height'))
            screens_scroll.add_widget(screens_content)
            screens_box.add_widget(screens_title)
            screens_box.add_widget(screens_scroll)
            
            content.add_widget(modules_box)
            content.add_widget(screens_box)
            
            buttons_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10), pos_hint={"right": 1})
            cancel_button = MDButton(style="outlined", on_release=lambda x: self.remove_widget(overlay))
            cancel_button.add_widget(MDButtonText(text="ANNULER"))
            select_button = MDButton(on_release=lambda x: select_and_close())
            select_button.add_widget(MDButtonText(text="SÉLECTIONNER"))
            buttons_box.add_widget(Widget())
            buttons_box.add_widget(cancel_button)
            buttons_box.add_widget(select_button)

            selector_card.add_widget(header)
            selector_card.add_widget(content)
            selector_card.add_widget(buttons_box)
            overlay.add_widget(selector_card)

            def update_screens_list(module_id, branch):
                screens_content.clear_widgets()
                screens = discovery.get_module_screens(module_id, branch)
                if not screens:
                    screens_content.add_widget(MDLabel(text="Aucun écran disponible", halign="center", theme_text_color="Secondary"))
                else:
                    for screen_data in screens:
                        screen_card = ScreenSelectorCard(screen_id=screen_data.get('id', ''))
                        screen_card.add_widget(MDLabel(text=screen_data.get('name', 'Sans nom'), bold=True))
                        screen_card.bind(on_release=lambda w, s=screen_data.get('id'): select_screen(w, s))
                        screens_content.add_widget(screen_card)

            def select_module(widget, module_id, branch):
                selected_module_info['id'] = module_id
                selected_module_info['branch'] = branch
                selected_screen_id[0] = None
                for child in modules_content.children:
                    child.set_selected(child == widget)
                update_screens_list(module_id, branch)

            def select_screen(widget, screen_id):
                selected_screen_id[0] = screen_id
                for child in screens_content.children:
                    child.set_selected(child == widget)

            def select_and_close():
                if selected_module_info['id'] and selected_screen_id[0]:
                    if hasattr(self, 'target_module_field') and self.target_module_field:
                        self.target_module_field.text = selected_module_info['id']
                    if hasattr(self, 'target_screen_field') and self.target_screen_field:
                        self.target_screen_field.text = selected_screen_id[0]
                self.remove_widget(overlay)

            for module in modules:
                card = ModuleSelectorCard(module_id=module.get('id'), branch=module.get('branch'))
                card.add_widget(MDLabel(text=f"{module.get('name', 'Unknown')}", bold=True))
                card.add_widget(MDLabel(text=f"v{module.get('version', 'N/A')} - {module.get('branch', 'N/A')}", theme_text_color="Secondary"))
                card.bind(on_release=lambda w, m_id=module.get('id'), b=module.get('branch'): select_module(w, m_id, b))
                modules_content.add_widget(card)

            self._selector_view = overlay
            self.add_widget(overlay)

        except Exception as e:
            import traceback
            print(f"[ERROR] Exception dans show_module_selector: {str(e)}")
            traceback.print_exc()
    
    def _select_module_screen(self, modal_view, module_id, screen_id):
        """Applique la sélection du module et de l'écran"""
        try:
            if module_id and screen_id and hasattr(self, 'target_screen_field'):
                # Mettre à jour le champ avec l'index sélectionné
                index = f"{module_id}.{screen_id}"
                self.target_screen_field.text = index
                print(f"[DEBUG] Index sélectionné et appliqué: {index}")
        except Exception as e:
            print(f"[ERROR] Erreur lors de la sélection du module/écran: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def open_modules_browser(self):
        """
        Ouvre le navigateur de modules et d'écrans pour la sélection.
        Cette méthode est appelée par le bouton 'Parcourir...'
        """
        print(f"[DEBUG] Bouton parcourir cliqué!")
        self.show_module_selector()













