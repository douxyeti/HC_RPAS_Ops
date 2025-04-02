from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDIconButton
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
from app.controllers.task_controller import TaskController
from app.controllers.role_controller import RoleController

class IconListItem(MDListItem):
    """Item personnalisé pour le menu déroulant avec icône"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class TaskCard(MDCard):
    """Carte pour afficher une tâche du commandant"""
    def __init__(self, title="", description="", icon="", module="", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = ("200dp", "150dp")
        self.padding = "8dp"
        self.spacing = "8dp"
        
        # Créer le contenu de la carte
        title_box = MDBoxLayout(orientation="horizontal", adaptive_height=True)
        
        # Ajouter l'icône
        icon_button = MDIconButton(icon=icon)
        title_box.add_widget(icon_button)
        
        # Ajouter le titre
        title_label = MDLabel(
            text=title,
            font_style="H6",
            size_hint_x=None,
            width="150dp"
        )
        title_box.add_widget(title_label)
        
        # Ajouter la description
        description_label = MDLabel(
            text=description,
            size_hint_y=None,
            height="60dp"
        )
        
        # Ajouter le module
        module_label = MDLabel(
            text=f"Module: {module}",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        )
        
        # Ajouter tous les widgets à la carte
        self.add_widget(title_box)
        self.add_widget(description_label)
        self.add_widget(module_label)

class SpecializedDashboardScreen(MDScreen):
    """Écran du tableau de bord spécialisé dynamique selon le rôle"""
    controller = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = DashboardController(model=MDApp.get_running_app().model)
        self.task_controller = TaskController()
        self.role_controller = RoleController()
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

    def update_for_role(self, role_name):
        """Met à jour l'interface pour le rôle sélectionné"""
        print(f"Updating interface for role: {role_name}")
        self.current_role = role_name
        
        # Mettre à jour le titre
        self.title_label.text = f"Tableau de bord - {role_name}"
        
        # Réinitialiser le texte du menu des tâches
        self.task_label.text = "Choisissez votre tâche..."
        
        # Effacer la grille existante
        self.grid.clear_widgets()
        
        # Charger les tâches via le contrôleur
        print(f"Loading tasks for role: {role_name}")
        tasks = self.task_controller.get_tasks(role_name)
        
        if tasks:
            print(f"Loaded {len(tasks)} tasks for {role_name}")
            print(f"Loaded {len(tasks)} tasks for display")
            
            # Créer une carte pour chaque tâche
            for task in tasks:
                print(f"Creating card for task: {task.title}")
                card = TaskCard(
                    title=task.title,
                    description=task.description,
                    icon=task.icon,
                    module=task.module
                )
                self.grid.add_widget(card)
        else:
            # Afficher un message si aucune tâche n'est trouvée
            label = MDLabel(
                text="Aucune tâche disponible pour ce rôle",
                halign="center",
                valign="middle",
                size_hint_y=None,
                height=dp(200)
            )
            self.grid.add_widget(label)

    def show_task_menu(self, button):
        """Affiche le menu déroulant des tâches"""
        print("Opening task menu")
        # Réinitialiser le texte du label
        self.task_label.text = "Choisissez votre tâche..."
        
        tasks = self.task_controller.get_tasks(self.current_role)
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
        
        # Redirection selon le module
        module = task.module
        print(f"Tâche sélectionnée : {task.title}")
        print(f"Redirection vers le module : {module}")
        
        # Redirection selon le module
        if module == "admin":
            if task.title == "Gérer les rôles":
                print("Redirection vers l'écran de gestion des rôles")
                app = MDApp.get_running_app()
                app.screen_manager.transition.direction = 'left'
                app.screen_manager.current = 'roles_manager'
        # Autres redirections selon les modules...

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
