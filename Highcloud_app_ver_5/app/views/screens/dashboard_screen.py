from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.scrollview import MDScrollView
from kivy.clock import Clock

class DashboardCard(MDCard):
    def __init__(self, title, description, icon="information", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 15
        self.spacing = 10
        self.size_hint_y = None
        self.height = 200
        self.elevation = 2

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
            font_style="H6",
            size_hint_y=None,
            height=40
        )
        
        header.add_widget(icon_button)
        header.add_widget(title_label)
        
        # Description
        description_label = MDLabel(
            text=description,
            size_hint_y=None,
            height=100
        )
        
        # Ajouter les widgets à la carte
        self.add_widget(header)
        self.add_widget(description_label)

class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Barre supérieure
        top_bar = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=60,
            spacing=10,
            padding=[10, 5, 10, 5]
        )
        
        # Titre
        self.title = MDLabel(
            text="Tableau de bord",
            font_style="H5"
        )
        
        # Boutons de la barre supérieure
        change_role_button = MDIconButton(
            icon="account-switch",
            on_release=self.change_role
        )
        
        logout_button = MDIconButton(
            icon="logout",
            on_release=self.logout
        )
        
        top_bar.add_widget(self.title)
        top_bar.add_widget(change_role_button)
        top_bar.add_widget(logout_button)
        
        self.layout.add_widget(top_bar)
        
        # Contenu principal avec ScrollView
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
        self.layout.add_widget(scroll_view)
        self.add_widget(self.layout)
        
        # Initialiser les cartes
        Clock.schedule_once(self.initialize_cards)

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

    def change_role(self, *args):
        if hasattr(self, 'app'):
            self.app.switch_screen('role')

    def logout(self, *args):
        if hasattr(self, 'app'):
            self.app.switch_screen('login')

    @property
    def app(self):
        from kivy.app import App
        return App.get_running_app()
