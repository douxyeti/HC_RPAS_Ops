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
            width="240dp",
            elevation=4,
            radius=(0, 16, 16, 0)
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
            text="Tableau de bord principal",
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
            pos_hint={'center_x': 0.5, 'top': 0.85},
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
            do_scroll_y=True,
            pos_hint={'center_x': 0.5, 'top': 0.75}  
        )
        
        self.content_layout = MDBoxLayout(
            orientation='vertical',
            spacing=20,
            padding=[20, 100, 20, 20],  
            size_hint_y=None
        )
        
        # Bind la hauteur du content_layout
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        
        scroll_view.add_widget(self.content_layout)
        main_content.add_widget(scroll_view)
        
        # Ajouter le contenu principal au layout
        self.layout.add_widget(self.nav_drawer)
        self.layout.add_widget(main_content)
        self.add_widget(self.layout)
        self.add_widget(self.nav_drawer)
        
        # Charger les rôles depuis l'application
        self.roles = self.load_roles()
        
        # Initialiser les cartes
        Clock.schedule_once(self.initialize_cards)

    def load_roles(self):
        app = self.app
        return app.available_roles if hasattr(app, 'available_roles') else []

    def show_role_menu(self, button):
        menu_items = []
        
        # Récupère les rôles depuis l'application
        app = self.app
        roles = app.available_roles if hasattr(app, 'available_roles') else []
        
        for role_name in roles:
            menu_items.append({
                "viewclass": "MDDropdownTextItem",
                "text": role_name,
                "on_release": lambda x=role_name: self.select_role(x)
            })

        self.menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            position="bottom",
            width=400,
            max_height=400,
            radius=[24, 24, 24, 24],
            elevation=4,
            ver_growth="down",
            hor_growth="right",
            background_color=self.theme_cls.surfaceColor
        )
        
        # Calculer la position pour centrer le menu
        button_center_x = button.center_x
        menu_width = 400  # Largeur du menu
        self.menu.caller = button
        offset_y = 10  # Décalage vers le bas
        self.menu.pos = (button_center_x - menu_width/2, button.y - offset_y)
        
        self.menu.open()

    def select_role(self, role_name):
        self.menu.dismiss()
        self.role_label.text = role_name
        
        if hasattr(self, 'app'):
            self.app.set_role(role_name)

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
