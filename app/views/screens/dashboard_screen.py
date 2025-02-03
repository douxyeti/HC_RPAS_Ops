from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.list import MDList
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.menu.menu import MDDropdownTextItem
from kivy.clock import Clock
import json
import os

class DashboardCard(MDCard):
    def __init__(self, title, description, icon="information", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 15
        self.spacing = 10
        self.size_hint_y = None
        self.height = 200
        self.elevation = 2
        self.radius = [12, 12, 12, 12]

        # Header avec titre et icône
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=40,
            spacing=10
        )
        
        icon_button = MDIconButton(
            icon=icon,
            pos_hint={"center_y": 0.5}
        )
        
        title_label = MDLabel(
            text=title,
            bold=True,
            font_size="18sp",
            size_hint_y=None,
            height=40
        )
        
        header.add_widget(icon_button)
        header.add_widget(title_label)
        
        # Description
        description_label = MDLabel(
            text=description,
            font_size="14sp",
            size_hint_y=None,
            height=100
        )
        
        # Ajouter les widgets à la carte
        self.add_widget(header)
        self.add_widget(description_label)

class NavigationItem(MDBoxLayout):
    def __init__(self, icon, text, on_release=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 48
        self.spacing = 10
        self.padding = [10, 0, 10, 0]
        
        # Icône
        self.icon_button = MDIconButton(
            icon=icon,
            pos_hint={"center_y": 0.5}
        )
        
        # Texte
        self.label = MDLabel(
            text=text,
            size_hint_y=None,
            height=48,
            pos_hint={"center_y": 0.5}
        )
        
        self.add_widget(self.icon_button)
        self.add_widget(self.label)
        
        if on_release:
            self.bind(on_touch_down=lambda x, y: on_release(text) if self.collide_point(*y.pos) else None)

class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Layout principal avec navigation drawer
        self.layout = MDBoxLayout(orientation='horizontal')
        
        # Navigation Drawer (menu de gauche)
        self.nav_drawer = MDNavigationDrawer(
            anchor="left",
            size_hint_x=None,
            width="240dp"
        )
        
        # Liste des items de navigation
        nav_list = MDList()
        nav_items = [
            ("Tableau de bord", "view-dashboard"),
            ("Gestion des vols", "airplane"),
            ("Maintenance", "tools"),
            ("Personnel", "account-group"),
            ("Paramètres", "cog")
        ]
        
        for text, icon in nav_items:
            item = NavigationItem(
                icon=icon,
                text=text,
                on_release=self.nav_item_selected
            )
            nav_list.add_widget(item)
            
        self.nav_drawer.add_widget(nav_list)
        
        # Contenu principal
        main_content = MDBoxLayout(
            orientation='vertical',
            spacing=20,
            padding=20
        )

        # Barre supérieure avec titre
        top_bar = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50,
            spacing=10,
            padding=[10, 0]
        )

        self.title = MDLabel(
            text="HC RPAS Ops",
            font_style="Headline",
            font_size="24sp"
        )

        # Bouton de déconnexion
        logout_button = MDIconButton(
            icon="logout",
            on_release=self.logout
        )

        # Ajouter les widgets à la barre supérieure
        top_bar.add_widget(self.title)
        top_bar.add_widget(logout_button)

        main_content.add_widget(top_bar)

        # Créer le sélecteur de rôle centré
        role_box = MDBoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=(300, 50),
            pos_hint={'center_x': 0.5, 'top': 0.95},
            spacing=10,
            padding=[0, 20]
        )
        
        self.role_label = MDLabel(
            text="Choisissez votre rôle",
            size_hint_x=None,
            width=200,
            halign="right"
        )
        
        role_button = MDIconButton(
            icon="chevron-down",
            on_release=self.show_role_menu
        )
        
        role_box.add_widget(self.role_label)
        role_box.add_widget(role_button)
        
        # Ajouter le sélecteur de rôle au début du contenu principal
        self.add_widget(role_box)

        # Contenu des cartes avec ScrollView
        scroll_view = MDScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )
        
        self.content_layout = MDBoxLayout(
            orientation='vertical',
            spacing=20,
            padding=20,
            size_hint_y=None
        )
        
        # Bind la hauteur du content_layout
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        
        scroll_view.add_widget(self.content_layout)
        main_content.add_widget(scroll_view)
        
        # Ajouter le contenu principal au layout
        self.layout.add_widget(main_content)
        self.add_widget(self.layout)
        self.add_widget(self.nav_drawer)
        
        # Charger les rôles depuis le fichier config
        self.roles = self.load_roles()
        
        # Créer le menu déroulant des rôles
        menu_items = []
        # Créer une liste triée des rôles par nom
        sorted_roles = sorted(self.roles.items(), key=lambda x: x[1]["name"])
        
        for role_id, role_info in sorted_roles:
            menu_items.append({
                "viewclass": "MDDropdownTextItem",
                "text": role_info["name"],
                "on_release": lambda x=role_id: self.select_role(x)
            })
        
        self.menu = MDDropdownMenu(
            caller=role_button,
            items=menu_items,
            position="bottom",
            width=600,
            max_height=400,
            radius=[24, 24, 24, 24],
            elevation=4,
            ver_growth="down",
            hor_growth="right"
        )
        
        # Initialiser les cartes
        Clock.schedule_once(self.initialize_cards)

    def load_roles(self):
        config_path = os.path.join('data', 'config', 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                roles = config['interface']['roles']
                
                # Liste complète des rôles selon toutes les versions
                complete_roles = {
                    "super_admin": {
                        "name": "Super Administrateur",
                        "permissions": ["all", "system.config"]
                    },
                    "admin": {
                        "name": "Administrateur",
                        "permissions": ["all"]
                    },
                    "admin_assistant": {
                        "name": "Adjoint(e) administratif(ve)",
                        "permissions": ["documentation.view", "documentation.edit", "personnel.view"]
                    },
                    "auditor": {
                        "name": "Auditeur",
                        "permissions": ["operations.view", "maintenance.view", "personnel.view", "documentation.view"]
                    },
                    "senior_manager": {
                        "name": "Gestionnaire supérieur responsable",
                        "permissions": ["operations.all", "personnel.all", "maintenance.all"]
                    },
                    "ops_manager": {
                        "name": "Responsable des opérations",
                        "permissions": ["operations.all", "personnel.view"]
                    },
                    "chief_pilot": {
                        "name": "Chef pilote",
                        "permissions": ["operations.all", "personnel.view", "formation.all"]
                    },
                    "pilot_command": {
                        "name": "Commandant de bord",
                        "permissions": ["operations.all", "maintenance.view"]
                    },
                    "site_manager": {
                        "name": "Gestionnaire de site",
                        "permissions": ["operations.view", "maintenance.view"]
                    },
                    "mission_specialist": {
                        "name": "Spécialiste de mission",
                        "permissions": ["operations.view", "operations.edit"]
                    },
                    "payload_operator": {
                        "name": "Opérateur de charge utile",
                        "permissions": ["operations.view"]
                    },
                    "pilot_controls": {
                        "name": "Pilote aux commandes",
                        "permissions": ["operations.view", "operations.edit"]
                    },
                    "copilot": {
                        "name": "Copilote",
                        "permissions": ["operations.view"]
                    },
                    "pilot": {
                        "name": "Pilote",
                        "permissions": ["operations.view", "operations.edit", "maintenance.view"]
                    },
                    "ground_station": {
                        "name": "Opérateur de station au sol",
                        "permissions": ["operations.view"]
                    },
                    "ground_observer": {
                        "name": "Observateur au sol",
                        "permissions": ["operations.view"]
                    },
                    "system_maintainer": {
                        "name": "Mainteneur du système",
                        "permissions": ["maintenance.all"]
                    },
                    "sgs_manager": {
                        "name": "Responsable SGS",
                        "permissions": ["operations.view", "maintenance.view", "personnel.view"]
                    },
                    "quality_manager": {
                        "name": "Responsable assurance de la qualité",
                        "permissions": ["operations.view", "maintenance.view", "personnel.view"]
                    },
                    "training_manager": {
                        "name": "Responsable formation",
                        "permissions": ["formation.all", "personnel.view"]
                    },
                    "formateur": {
                        "name": "Formateur",
                        "permissions": ["formation.view", "formation.edit", "personnel.view"]
                    },
                    "evaluator": {
                        "name": "Évaluateur",
                        "permissions": ["formation.all", "personnel.view"]
                    },
                    "examiner": {
                        "name": "Examinateur",
                        "permissions": ["formation.all", "personnel.view"]
                    },
                    "instructor": {
                        "name": "Instructeur",
                        "permissions": ["formation.all", "personnel.view"]
                    },
                    "inspector": {
                        "name": "Inspecteur",
                        "permissions": ["operations.view", "maintenance.view", "personnel.view"]
                    },
                    "maintenance_technician": {
                        "name": "Technicien Maintenance",
                        "permissions": ["maintenance.view", "maintenance.edit", "operations.view"]
                    },
                    "safety_officer": {
                        "name": "Agent de sécurité",
                        "permissions": ["operations.view", "maintenance.view"]
                    },
                    "quality_inspector": {
                        "name": "Inspecteur qualité",
                        "permissions": ["operations.view", "maintenance.view"]
                    },
                    "operations_coordinator": {
                        "name": "Coordinateur des opérations",
                        "permissions": ["operations.view", "operations.edit"]
                    },
                    "flight_director": {
                        "name": "Directeur des vols",
                        "permissions": ["operations.all"]
                    },
                    "maintenance_manager": {
                        "name": "Gestionnaire de maintenance",
                        "permissions": ["maintenance.all"]
                    },
                    "training_coordinator": {
                        "name": "Coordinateur de formation",
                        "permissions": ["formation.view", "formation.edit"]
                    },
                    "compliance_officer": {
                        "name": "Agent de conformité",
                        "permissions": ["operations.view", "maintenance.view", "personnel.view"]
                    },
                    "documentation_manager": {
                        "name": "Gestionnaire de documentation",
                        "permissions": ["documentation.all"]
                    }
                }
                
                # Remplacer les rôles existants par la liste complète
                roles.clear()
                roles.update(complete_roles)
                return roles
                
        except Exception as e:
            print(f"Erreur lors du chargement des rôles : {e}")
            return {}

    def show_role_menu(self, button):
        menu_items = []
        sorted_roles = sorted(self.roles.items(), key=lambda x: x[1]["name"])
        
        for role_id, role_info in sorted_roles:
            menu_items.append({
                "viewclass": "MDDropdownTextItem",
                "text": role_info["name"],
                "on_release": lambda x=role_id: self.select_role(x)
            })

        self.menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            position="bottom",
            width=300,
            max_height=400,
            radius=[24, 24, 24, 24],
            elevation=4,
            ver_growth="down",
            hor_growth="right"
        )
        
        # Calculer la position pour centrer le menu
        button_center_x = button.center_x
        menu_width = 300  # Largeur du menu
        self.menu.caller = button
        self.menu.pos = (button_center_x - menu_width/2, button.y)
        
        self.menu.open()

    def select_role(self, role_id):
        self.menu.dismiss()
        role_info = self.roles[role_id]
        self.role_label.text = role_info["name"]
        
        if hasattr(self, 'app'):
            self.app.set_role(role_id)

    def toggle_nav_drawer(self, *args):
        self.nav_drawer.set_state("open")
        
    def nav_item_selected(self, text):
        print(f"Menu sélectionné : {text}")
        self.nav_drawer.set_state("close")

    def initialize_cards(self, *args):
        # Carte 1: Gestion Opérationnelle
        card1 = DashboardCard(
            title="Gestion Opérationnelle",
            description="État des vols en cours\nAlertes opérationnelles\nMissions en cours\nNotifications risques",
            icon="airplane"
        )
        self.content_layout.add_widget(card1)
        
        # Carte 2: Gestion Personnel
        card2 = DashboardCard(
            title="Gestion Personnel",
            description="Formations à jour/expirées\nQualifications actives\nÉvaluations en attente\nAlertes personnel",
            icon="account-group"
        )
        self.content_layout.add_widget(card2)
        
        # Carte 3: Maintenance
        card3 = DashboardCard(
            title="Maintenance",
            description="État maintenance équipements\nAlertes techniques\nInterventions planifiées\nDéfectuosités en cours",
            icon="tools"
        )
        self.content_layout.add_widget(card3)
        
        # Carte 4: Rapport de Situation
        card4 = DashboardCard(
            title="Rapport de Situation",
            description="Nombre de drones actifs/inactifs\nVols planifiés pour la journée\nRapports en attente de validation",
            icon="file-document"
        )
        self.content_layout.add_widget(card4)

    def logout(self, *args):
        if hasattr(self, 'app'):
            self.app.switch_screen('login')

    @property
    def app(self):
        from kivy.app import App
        return App.get_running_app()
