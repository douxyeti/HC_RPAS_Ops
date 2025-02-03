from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.menu.menu import MDDropdownTextItem
from kivymd.uix.appbar import MDTopAppBar
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

class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Layout principal
        self.layout = MDBoxLayout(orientation='vertical', spacing=0, padding=0)
        
        # Contenu principal
        self.main_content = MDBoxLayout(
            orientation='vertical',
            spacing=20,
            padding=20,
            size_hint=(1, 1)
        )

        # Barre de titre
        top_bar = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height="56dp",
            spacing=10,
            padding=[10, 0]
        )

        # Titre
        self.title = MDLabel(
            text="Tableau de bord principal",
            bold=True,
            font_size="24sp",
            size_hint_x=0.9,
            halign="left"
        )

        # Bouton de déconnexion
        logout_button = MDIconButton(
            icon="logout",
            on_release=self.logout
        )

        top_bar.add_widget(self.title)
        top_bar.add_widget(logout_button)

        self.main_content.add_widget(top_bar)

        # Créer le sélecteur de rôle centré
        role_box = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height="56dp",
            spacing=10,
            padding=[10, 0]
        )

        role_label = MDLabel(
            text="Sélectionner un rôle :",
            size_hint_x=None,
            width="150dp",
            halign="right",
            valign="center"
        )

        role_button = MDIconButton(
            icon="chevron-down",
            on_release=self.show_role_menu
        )

        role_box.add_widget(role_label)
        role_box.add_widget(role_button)

        self.main_content.add_widget(role_box)

        # Créer un ScrollView pour le contenu
        scroll_view = MDScrollView()
        
        # Layout pour le contenu défilable
        self.content_layout = MDBoxLayout(
            orientation='vertical',
            spacing=20,
            padding=20,
            size_hint_y=None
        )
        
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        
        scroll_view.add_widget(self.content_layout)
        self.main_content.add_widget(scroll_view)
        
        # Ajouter le contenu principal au layout
        self.layout.add_widget(self.main_content)
        self.add_widget(self.layout)
        
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
        
        self.menu.open()

    def select_role(self, role_name):
        # Fermer le menu
        if hasattr(self, 'menu'):
            self.menu.dismiss()
        
        # Mettre à jour le rôle dans l'application
        app = self.app
        if hasattr(app, 'current_role'):
            app.current_role = role_name

    def initialize_cards(self, *args):
        # Créer les cartes pour chaque module
        cards = [
            {
                "title": "Gestion Opérationnelle",
                "description": "État des vols en cours\nAlertes opérationnelles\nMissions en cours\nNotifications risques",
                "icon": "airplane"
            },
            {
                "title": "Gestion Personnel",
                "description": "Formations à jour/expirées\nQualifications actives\nÉvaluations en attente\nAlertes personnel",
                "icon": "account-group"
            },
            {
                "title": "Maintenance",
                "description": "État maintenance équipements\nAlertes techniques\nInterventions planifiées\nDéfectuosités en cours",
                "icon": "wrench"
            }
        ]
        
        # Créer un conteneur pour les cartes
        cards_container = MDBoxLayout(
            orientation='horizontal',
            spacing=20,
            size_hint_y=None,
            height="220dp"  # Hauteur des cartes + padding
        )
        
        # Ajouter les cartes au conteneur
        for card_info in cards:
            card = DashboardCard(**card_info)
            cards_container.add_widget(card)
        
        # Ajouter le conteneur au contenu principal
        self.content_layout.add_widget(cards_container)

    def logout(self, *args):
        """Déconnexion de l'utilisateur"""
        app = self.app
        if hasattr(app, 'logout'):
            app.logout()

    @property
    def app(self):
        """Obtenir l'instance de l'application"""
        from kivy.app import App
        return App.get_running_app()
