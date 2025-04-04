from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDIconButton, MDButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDListItem, MDListItemLeadingIcon
from kivymd.app import MDApp
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from app.controllers.dashboard_controller import DashboardController
from kivymd.uix.dialog import MDDialog

class IconListItem(MDListItem):
    """Item personnalisé pour le menu déroulant avec icône"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class TaskCard(MDCard):
    """Carte pour afficher une tâche du commandant"""
    def __init__(self, title, description, status=None, icon="checkbox-marked-circle", is_fixed=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 15
        self.spacing = 10
        self.size_hint_y = None
        self.height = dp(200)
        self.elevation = 2
        self.radius = [12, 12, 12, 12]
        self.md_bg_color = [1, 1, 1, 1]  # Fond blanc

        # En-tête de la carte avec indicateur de tâche fixe
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=10,
            md_bg_color=[1, 1, 1, 1]  # Fond blanc
        )

        # Conteneur pour les icônes
        icon_container = MDBoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            width=dp(80),
            spacing=2
        )

        main_icon = MDIconButton(
            icon=icon,
            pos_hint={"center_y": 0.5},
            theme_text_color="Primary"  # Couleur de texte primaire
        )
        icon_container.add_widget(main_icon)

        # Ajouter l'icône de verrouillage pour les tâches fixes
        if is_fixed:
            lock_icon = MDIconButton(
                icon="lock",
                pos_hint={"center_y": 0.5},
                theme_text_color="Primary",  # Couleur de texte primaire
                size_hint=(None, None),
                size=(dp(20), dp(20))
            )
            icon_container.add_widget(lock_icon)

        title_label = MDLabel(
            text=title,
            bold=True,
            font_size="16sp",
            size_hint_y=None,
            height=dp(40),
            theme_text_color="Primary"  # Couleur de texte primaire
        )

        header.add_widget(icon_container)
        header.add_widget(title_label)

        # Description
        description_box = MDBoxLayout(
            orientation="vertical",
            spacing=5,
            padding=[5, 5],
            md_bg_color=[1, 1, 1, 1]  # Fond blanc
        )

        description_label = MDLabel(
            text=description,
            font_size="14sp",
            theme_text_color="Primary"  # Couleur de texte primaire
        )

        # Statut avec icône
        status_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(30),
            md_bg_color=[1, 1, 1, 1]  # Fond blanc
        )

        status_icon = MDIconButton(
            icon="circle-small",
            size_hint_x=None,
            width=dp(30),
            theme_text_color="Primary"  # Couleur de texte primaire
        )

        if status:
            status_label = MDLabel(
                text=f"Statut: {status}",
                font_size="14sp",
                theme_text_color="Primary"  # Couleur de texte primaire
            )
        else:
            status_label = MDLabel(
                text="",
                font_size="14sp",
                theme_text_color="Primary"  # Couleur de texte primaire
            )

        status_box.add_widget(status_icon)
        status_box.add_widget(status_label)

        # Ajouter les widgets à description_box
        description_box.add_widget(description_label)
        description_box.add_widget(status_box)

        # Ajouter tous les éléments à la carte
        self.add_widget(header)
        self.add_widget(description_box)

class SpecializedDashboardScreen(MDScreen):
    """Écran du tableau de bord spécialisé dynamique selon le rôle"""
    controller = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = MDApp.get_running_app()
        self.controller = app.container.dashboard_controller(model=app.model)
        self.current_role = None
        self.layout = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            padding=10,
            md_bg_color=[1, 1, 1, 1]
        )
        
        # Barre supérieure
        self.top_bar = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            spacing=10,
            padding=[10, 0],
            md_bg_color=[1, 1, 1, 1]
        )

        # Conteneur gauche (pour le titre)
        left_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_x=0.25,
            md_bg_color=[1, 1, 1, 1]
        )

        # Conteneur central (pour le menu déroulant)
        center_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_x=0.5,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            md_bg_color=[1, 1, 1, 1]
        )

        # Conteneur droit (pour les icônes d'action)
        right_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_x=0.25,
            spacing=2,
            padding=[0, 0, 10, 0],
            pos_hint={'center_y': 0.5},
            md_bg_color=[1, 1, 1, 1]
        )

        # Titre dynamique
        self.title_label = MDLabel(
            text="Tableau de bord spécialisé",
            bold=True,
            font_size="24sp",
            valign="center",
            height=dp(56),
            theme_text_color="Primary"
        )

        # Menu déroulant des tâches
        task_box = MDBoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=(dp(200), dp(56)),
            spacing=5,
            padding=[5, 0],
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            md_bg_color=[1, 1, 1, 1]
        )

        self.task_label = MDLabel(
            text="Choisissez votre tâche...",
            size_hint=(None, None),
            size=(dp(160), dp(56)),
            halign="center",
            valign="center",
            pos_hint={'center_y': 0.5},
            theme_text_color="Primary"
        )

        self.task_button = MDIconButton(
            icon="chevron-down",
            size_hint=(None, None),
            size=(dp(35), dp(35)),
            pos_hint={'center_y': 0.5},
            theme_text_color="Primary"
        )
        self.task_button.bind(on_release=self.show_task_menu)

        # Ajouter les widgets au task_box
        task_box.add_widget(self.task_label)
        task_box.add_widget(self.task_button)

        # Icônes d'action
        notifications_button = MDIconButton(
            icon="bell-outline",
            on_release=self.show_notifications,
            pos_hint={'center_y': 0.5}
        )

        reports_button = MDIconButton(
            icon="file-document-outline",
            on_release=self.show_reports,
            pos_hint={'center_y': 0.5}
        )

        settings_button = MDIconButton(
            icon="cog-outline",
            on_release=self.show_settings,
            pos_hint={'center_y': 0.5}
        )

        help_button = MDIconButton(
            icon="help-circle-outline",
            on_release=self.show_help,
            pos_hint={'center_y': 0.5}
        )

        back_button = MDIconButton(
            icon="arrow-left",
            on_release=self.go_back,
            pos_hint={'center_y': 0.5}
        )

        # Ajouter les widgets aux conteneurs
        left_container.add_widget(self.title_label)
        center_container.add_widget(task_box)
        right_container.add_widget(notifications_button)
        right_container.add_widget(reports_button)
        right_container.add_widget(settings_button)
        right_container.add_widget(help_button)
        right_container.add_widget(back_button)

        # Ajouter les conteneurs à la barre supérieure
        self.top_bar.add_widget(left_container)
        self.top_bar.add_widget(center_container)
        self.top_bar.add_widget(right_container)

        # ScrollView pour la grille de cartes
        scroll = MDScrollView()
        
        # Grille pour les cartes
        self.grid = MDGridLayout(
            cols=2,
            spacing=20,
            padding=20,
            size_hint_y=None
        )
        self.grid.bind(minimum_height=self.grid.setter('height'))

        # Assembler le layout
        scroll.add_widget(self.grid)
        self.layout.add_widget(self.top_bar)
        self.layout.add_widget(scroll)
        self.add_widget(self.layout)

    def update_for_role(self, role_id):
        """Met à jour l'interface pour le rôle sélectionné"""
        print(f"Updating interface for role: {role_id}")
        print(f"Type of role_id: {type(role_id)}")  # Debug
        self.current_role = role_id
        
        # Mettre à jour le titre avec le nom du rôle
        self.title_label.text = f"Tableau de bord {role_id}"
        
        # Réinitialiser le texte du menu des tâches
        self.task_label.text = "Choisissez votre tâche..."
        
        # Effacer les cartes existantes
        self.grid.clear_widgets()
        
        # Récupérer toutes les tâches (fixes + dynamiques) pour ce rôle
        app = MDApp.get_running_app()
        task_manager = app.container.task_manager()
        tasks = task_manager.get_all_tasks(role_id)
        print(f"Loading tasks for role: {role_id}")
        print(f"Loaded {len(tasks)} tasks for {role_id}")
        
        if tasks:
            # Créer une carte pour chaque tâche
            for task in tasks:
                print(f"Creating card for task: {task['title']}")
                self.grid.add_widget(
                    TaskCard(
                        title=task['title'],
                        description=task['description'],
                        status=task.get('status', None),
                        icon=task.get('icon', 'checkbox-marked'),
                        is_fixed=task.get('is_fixed', False)
                    )
                )
        else:
            print("No tasks to display")

    def show_task_menu(self, button):
        """Affiche le menu déroulant des tâches"""
        print("Opening task menu")
        # Réinitialiser le texte du label
        self.task_label.text = "Choisissez votre tâche..."
        
        # Charger les tâches pour ce rôle
        tasks = self.controller.load_role_tasks(self.current_role)
        print(f"Loaded {len(tasks)} tasks for menu")
        
        # Trier les tâches par ordre alphabétique
        sorted_tasks = sorted(tasks, key=lambda x: x.title)
        
        menu_items = [
            {
                "viewclass": "MDDropdownTextItem",
                "text": task.title,
                "on_release": lambda x=task: self.select_task(x)
            } for task in sorted_tasks
        ]
        
        print(f"Created {len(menu_items)} menu items")

        self.menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=4,
            max_height=dp(250),
            radius=[8, 8, 8, 8],
            background_color=[0.9, 0.9, 1, 1]
        )
        self.menu.open()

    def select_task(self, task):
        """Sélectionne une tâche et redirige vers le module approprié"""
        # Fermer le menu déroulant s'il est ouvert
        if hasattr(self, 'menu'):
            self.menu.dismiss()
            
        self.task_label.text = task.title
        
        # Redirection selon le module et le rôle
        module = task.module
        print(f"Tâche sélectionnée : {task.title}")
        print(f"Redirection vers le module : {module}")
        print(f"Rôle actuel : {self.current_role}")  # Debug
        print(f"Type de rôle actuel : {type(self.current_role)}")  # Debug
        print(f"Condition rôle : {self.current_role == 'super_admin'}")  # Debug
        print(f"Condition tâche : {task.title == 'Gestion des rôles et tâches'}")  # Debug
        
        # Vérifier si c'est le Super Administrateur et la tâche de gestion des rôles
        if self.current_role == "super_admin" and task.title == "Gestion des rôles et tâches":
            print("Redirection vers l'écran de gestion des rôles")
            app = MDApp.get_running_app()
            app.screen_manager.transition.direction = 'left'
            app.screen_manager.current = 'roles_manager'
            return

        # Redirection standard selon le module
        if module:
            print(f"Redirection vers le module : {module}")
            # TODO: Implémenter les autres redirections selon les modules

    def show_notifications(self, *args):
        """Affiche les notifications"""
        print("Affichage des notifications")
        # TODO: Implémenter l'affichage des notifications
    
    def show_reports(self, *args):
        """Affiche les rapports"""
        print("Affichage des rapports")
        # TODO: Implémenter l'affichage des rapports
    
    def show_settings(self, *args):
        """Affiche les paramètres"""
        print("Affichage des paramètres")
        # TODO: Implémenter l'affichage des paramètres
    
    def show_help(self, *args):
        """Affiche l'aide"""
        print("Affichage de l'aide")
        # TODO: Implémenter l'affichage de l'aide

    def go_back(self, *args):
        """Retourne au tableau de bord principal"""
        self.manager.current = 'dashboard'

    def create_task_card(self, task):
        """Crée une carte de tâche avec les indicateurs appropriés"""
        return TaskCard(
            title=task.get('title', ''),
            description=task.get('description', ''),
            status=task.get('status'),
            icon=task.get('icon', 'checkbox-marked-circle'),
            is_fixed=task.get('is_fixed', False)
        )

    def on_delete_task(self, task_id):
        """Gère la suppression d'une tâche"""
        try:
            self.controller.delete_task(self.current_role, task_id)
            self.update_task_list()  # Rafraîchir la liste des tâches
        except ValueError as e:
            # Afficher un message d'erreur si tentative de suppression d'une tâche fixe
            self.show_error_dialog("Action non autorisée", str(e))

    def show_error_dialog(self, title, message):
        """Affiche une boîte de dialogue d'erreur"""
        self.dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
