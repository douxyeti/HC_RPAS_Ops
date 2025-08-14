from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDListItem, MDListItemLeadingIcon
from kivy.metrics import dp
from kivy.clock import Clock

class IconListItem(MDListItem):
    """Item personnalisé pour le menu déroulant avec icône"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class TaskCard(MDCard):
    """Carte pour afficher une tâche du chef pilote"""
    def __init__(self, title, description, status, icon="checkbox-marked-circle", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 15
        self.spacing = 10
        self.size_hint_y = None
        self.height = dp(200)
        self.elevation = 2
        self.radius = [12, 12, 12, 12]
        self.md_bg_color = [1, 1, 1, 1]  # Fond blanc

        # En-tête de la carte
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=10,
            md_bg_color=[1, 1, 1, 1]  # Fond blanc
        )

        icon = MDIconButton(
            icon=icon,
            pos_hint={"center_y": 0.5},
            theme_text_color="Primary"
        )

        title_label = MDLabel(
            text=title,
            bold=True,
            font_size="16sp",
            size_hint_y=None,
            height=dp(40),
            theme_text_color="Primary"
        )

        header.add_widget(icon)
        header.add_widget(title_label)

        # Description
        description_box = MDBoxLayout(
            orientation="vertical",
            spacing=5,
            padding=[5, 5],
            md_bg_color=[1, 1, 1, 1]
        )

        description_label = MDLabel(
            text=description,
            font_size="14sp",
            theme_text_color="Primary"
        )

        # Statut avec icône
        status_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(30),
            md_bg_color=[1, 1, 1, 1]
        )

        status_icon = MDIconButton(
            icon="circle-small",
            size_hint_x=None,
            width=dp(30),
            theme_text_color="Primary"
        )

        status_label = MDLabel(
            text=f"Statut: {status}",
            font_size="14sp",
            theme_text_color="Primary"
        )

        status_box.add_widget(status_icon)
        status_box.add_widget(status_label)

        # Ajouter les widgets à description_box
        description_box.add_widget(description_label)
        description_box.add_widget(status_box)

        # Ajouter tous les éléments à la carte
        self.add_widget(header)
        self.add_widget(description_box)

class ChiefPilotDashboardScreen(MDScreen):
    """Écran du tableau de bord spécialisé pour le chef pilote"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Layout principal avec fond blanc
        self.layout = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            padding=10,
            md_bg_color=[1, 1, 1, 1]
        )
        
        # Barre supérieure
        top_bar = MDBoxLayout(
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

        # Titre
        title = MDLabel(
            text="Tableau de bord Chef pilote",
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
            text="Sélectionner une tâche",
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

        # Icône rapports
        reports_button = MDIconButton(
            icon="file-document-outline",
            on_release=self.show_reports,
            pos_hint={'center_y': 0.5}
        )

        # Icône paramètres
        settings_button = MDIconButton(
            icon="cog-outline",
            on_release=self.show_settings,
            pos_hint={'center_y': 0.5}
        )

        # Icône aide
        help_button = MDIconButton(
            icon="help-circle-outline",
            on_release=self.show_help,
            pos_hint={'center_y': 0.5}
        )

        # Bouton de retour
        back_button = MDIconButton(
            icon="arrow-left",
            on_release=self.go_back,
            pos_hint={'center_y': 0.5}
        )

        # Ajouter les widgets aux conteneurs
        left_container.add_widget(title)
        center_container.add_widget(task_box)
        right_container.add_widget(notifications_button)
        right_container.add_widget(reports_button)
        right_container.add_widget(settings_button)
        right_container.add_widget(help_button)
        right_container.add_widget(back_button)

        # Ajouter les conteneurs à la barre supérieure
        top_bar.add_widget(left_container)
        top_bar.add_widget(center_container)
        top_bar.add_widget(right_container)

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

        # Ajouter les cartes de tâches
        self.add_task_cards()

        # Assembler le layout
        scroll.add_widget(self.grid)
        self.layout.add_widget(top_bar)
        self.layout.add_widget(scroll)
        self.add_widget(self.layout)

    def add_task_cards(self):
        """Ajouter les cartes de tâches spécifiques au chef pilote"""
        tasks = [
            {
                "title": "Supervision des pilotes",
                "icon": "account-group",
                "description": "Supervision et évaluation des pilotes",
                "status": "8 pilotes actifs",
                "module": "pilot_supervision"
            },
            {
                "title": "Formation et évaluation",
                "icon": "school",
                "description": "Gestion des formations et évaluations",
                "status": "2 formations en cours",
                "module": "training_evaluation"
            },
            {
                "title": "Planification des vols",
                "icon": "airplane",
                "description": "Planification et validation des vols",
                "status": "3 vols prévus",
                "module": "flight_planning"
            },
            {
                "title": "Rapports de sécurité",
                "icon": "shield-check",
                "description": "Gestion des rapports de sécurité",
                "status": "1 rapport en attente",
                "module": "safety_reports"
            }
        ]

        for task in tasks:
            card = TaskCard(
                title=task["title"],
                description=task["description"],
                status=task["status"],
                icon=task["icon"]
            )
            self.grid.add_widget(card)

    def show_task_menu(self, button):
        """Affiche le menu déroulant des tâches"""
        tasks = [
            {
                "title": "Supervision des pilotes",
                "icon": "account-group",
                "module": "pilot_supervision"
            },
            {
                "title": "Formation et évaluation",
                "icon": "school",
                "module": "training_evaluation"
            },
            {
                "title": "Planification des vols",
                "icon": "airplane",
                "module": "flight_planning"
            },
            {
                "title": "Rapports de sécurité",
                "icon": "shield-check",
                "module": "safety_reports"
            }
        ]

        menu_items = [
            {
                "viewclass": "MDDropdownLeadingIconItem",
                "text": task["title"],
                "on_release": lambda x=task: self.select_task(x),
                "leading_icon": task["icon"]
            } for task in tasks
        ]

        self.menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            position="bottom",
            width=dp(400),
            max_height=dp(400),
            radius=[12, 12, 12, 12],
        )
        self.menu.open()

    def select_task(self, task):
        """Sélectionne une tâche et redirige vers le module approprié"""
        if hasattr(self, 'menu'):
            self.menu.dismiss()
        self.task_label.text = task["title"]
        print(f"Tâche sélectionnée : {task['title']}")
        print(f"Redirection vers le module : {task['module']}")
        # TODO: Implémenter la redirection vers le module approprié

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
