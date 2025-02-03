from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDFabButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.menu.menu import MDDropdownTextItem
from kivymd.uix.segmentedbutton import MDSegmentedButton, MDSegmentedButtonItem
from kivymd.uix.chip import MDChip
from kivy.metrics import dp
from kivy.clock import Clock
import json
import os

class TabContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.adaptive_height = True
        self.spacing = 10
        self.padding = 10

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
            spacing=10,
            padding=10,
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

        # Boutons de navigation
        nav_box = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height="48dp",
            spacing=10,
            padding=[10, 0]
        )
        
        nav_items = [
            {"text": "Vue Générale", "icon": "view-dashboard"},
            {"text": "Opérations", "icon": "airplane"},
            {"text": "Maintenance", "icon": "wrench"},
            {"text": "Personnel", "icon": "account-group"}
        ]
        
        for item in nav_items:
            btn = MDIconButton(
                icon=item["icon"],
                on_release=lambda x, text=item["text"]: self.switch_view(text)
            )
            nav_box.add_widget(btn)
        
        self.main_content.add_widget(nav_box)

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

        # Filtres rapides avec MDChips
        filters_box = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height="50dp",
            spacing=10,
            padding=[10, 0]
        )
        
        filters = ["Tous", "Priorité haute", "En cours", "Terminé"]
        for filter_text in filters:
            chip = MDChip(
                on_release=lambda x, text=filter_text: self.filter_selected(text)
            )
            chip.text = filter_text
            filters_box.add_widget(chip)
            
        self.main_content.add_widget(filters_box)

        # Boutons segmentés pour la vue
        view_box = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height="50dp",
            padding=[10, 0]
        )
        
        segmented_button = MDSegmentedButton(
            size_hint_x=None,
            width="300dp"
        )
        
        for text in ["Vue Carte", "Vue Liste", "Vue Calendrier"]:
            label = MDLabel(text=text)
            item = MDSegmentedButtonItem()
            item.add_widget(label)
            segmented_button.add_widget(item)
            
        view_box.add_widget(segmented_button)
        self.main_content.add_widget(view_box)

        # Créer un ScrollView pour le contenu
        scroll_view = MDScrollView(
            size_hint=(1, 0.8),
            do_scroll_x=False,
            do_scroll_y=True
        )
        
        # Layout pour le contenu défilable
        self.content_layout = MDBoxLayout(
            orientation='vertical',
            spacing=20,
            padding=20,
            size_hint_y=None
        )
        
        # Bind la hauteur minimale
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        
        # Ajouter les cartes de test
        cards_data = [
            {
                "title": "État des Opérations",
                "description": "3 vols en cours\n2 missions planifiées\nConditions météo: Favorables",
                "icon": "airplane"
            },
            {
                "title": "Maintenance",
                "description": "1 drone en maintenance\n2 interventions planifiées\nAucune alerte critique",
                "icon": "wrench"
            },
            {
                "title": "Personnel",
                "description": "8 pilotes disponibles\n3 formations en cours\n1 évaluation à planifier",
                "icon": "account-group"
            },
            {
                "title": "Statistiques",
                "description": "15 vols cette semaine\n45 heures de vol cumulées\n98% de missions réussies",
                "icon": "chart-bar"
            }
        ]
        
        for card_data in cards_data:
            card = DashboardCard(
                title=card_data["title"],
                description=card_data["description"],
                icon=card_data["icon"]
            )
            self.content_layout.add_widget(card)
        
        scroll_view.add_widget(self.content_layout)
        self.main_content.add_widget(scroll_view)
        
        # Ajouter le contenu principal au layout
        self.layout.add_widget(self.main_content)
        self.add_widget(self.layout)
        
        # Charger les rôles depuis l'application
        self.roles = self.load_roles()
        
        # Initialiser les cartes
        Clock.schedule_once(self.initialize_cards)
        
        # Ajouter un MDFabButton pour les actions rapides
        fab_button = MDFabButton(
            icon="plus",
            pos_hint={"right": 0.95, "bottom": 0.05},
            on_release=self.show_quick_actions
        )
        self.add_widget(fab_button)

    def switch_view(self, view_name):
        """Change la vue active"""
        print(f"Changement vers la vue : {view_name}")

    def load_roles(self):
        app = self.app
        return app.available_roles if hasattr(app, 'available_roles') else []

    def show_role_menu(self, button):
        menu_items = []
        
        # Récupère les rôles depuis l'application
        app = self.app
        roles = app.available_roles if hasattr(app, 'available_roles') else []
        sorted_roles = sorted(roles, key=lambda x: x.lower())
        for role_name in sorted_roles:
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
        pass

    def filter_selected(self, filter_text):
        """Gestionnaire pour la sélection des filtres"""
        print(f"Filtre sélectionné : {filter_text}")

    def show_quick_actions(self, instance):
        """Afficher le menu des actions rapides"""
        quick_actions = [
            {"text": "Nouvelle mission", "icon": "airplane-plus"},
            {"text": "Rapport rapide", "icon": "file-document-plus"},
            {"text": "Alerte maintenance", "icon": "alert"},
        ]
        
        menu_items = [
            {
                "viewclass": "MDDropdownTextItem",
                "text": action["text"],
                "on_release": lambda x=action["text"]: self.quick_action_selected(x)
            }
            for action in quick_actions
        ]
        
        self.quick_menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width=200,
            position="top",
            radius=[12, 12, 12, 12],
        )
        self.quick_menu.open()

    def quick_action_selected(self, action):
        """Gestionnaire pour la sélection des actions rapides"""
        print(f"Action rapide sélectionnée : {action}")
        if hasattr(self, 'quick_menu'):
            self.quick_menu.dismiss()

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
