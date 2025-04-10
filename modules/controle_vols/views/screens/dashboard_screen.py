from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.clock import Clock

class ModuleCard(MDCard):
    def __init__(self, title, status_examples, icon="information", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 15
        self.spacing = 10
        self.size_hint_y = None
        self.height = dp(200)
        self.elevation = 2
        self.radius = [12, 12, 12, 12]
        self.md_bg_color = [0.95, 0.95, 0.95, 1]

        # Header avec titre et icône
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=10
        )
        
        icon_button = MDIconButton(
            icon=icon,
            pos_hint={"center_y": 0.5}
        )
        
        title_label = MDLabel(
            text=title,
            bold=True,
            font_size="16sp",
            size_hint_y=None,
            height=dp(40)
        )
        
        header.add_widget(icon_button)
        header.add_widget(title_label)
        
        # Contenu avec exemples de statuts
        content = MDBoxLayout(
            orientation="vertical",
            spacing=5,
            padding=[5, 5]
        )
        
        for status in status_examples:
            status_box = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(30)
            )
            
            status_icon = MDIconButton(
                icon="circle-small",
                size_hint_x=None,
                width=dp(30)
            )
            
            status_label = MDLabel(
                text=status,
                font_size="14sp"
            )
            
            status_box.add_widget(status_icon)
            status_box.add_widget(status_label)
            content.add_widget(status_box)
        
        self.add_widget(header)
        self.add_widget(content)

class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Layout principal
        self.layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Barre supérieure
        top_bar = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            spacing=10,
            padding=[10, 0]
        )

        # Conteneur gauche (pour le titre)
        left_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_x=0.25
        )

        # Conteneur central (pour le menu déroulant)
        center_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_x=0.5,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # Conteneur droit (pour les icônes d'action)
        right_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_x=0.25,
            spacing=2,
            padding=[0, 0, 10, 0],
            pos_hint={'center_y': 0.5}
        )

        # Titre
        title = MDLabel(
            text="Contrôle des Vols",
            bold=True,
            font_size="24sp",
            valign="center",
            height=dp(56)
        )
        
        # Menu déroulant des rôles
        role_box = MDBoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=(dp(200), dp(56)),
            spacing=5,
            padding=[5, 0],
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        self.role_label = MDLabel(
            text="Choisissez votre rôle",
            size_hint=(None, None),
            size=(dp(160), dp(56)),
            halign="center",
            valign="center",
            pos_hint={'center_y': 0.5}
        )

        self.role_button = MDIconButton(
            icon="chevron-down",
            size_hint=(None, None),
            size=(dp(35), dp(35)),
            pos_hint={'center_y': 0.5}
        )
        self.role_button.bind(on_release=self.show_role_menu)

        # Centrer le texte dans le role_box
        role_box.add_widget(self.role_label)
        role_box.add_widget(self.role_button)
        
        # Icône notifications
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
        
        # Bouton de déconnexion
        logout_button = MDIconButton(
            icon="logout",
            on_release=self.logout,
            pos_hint={'center_y': 0.5}
        )
        
        # Ajouter les boutons au conteneur droit
        right_container.add_widget(notifications_button)
        right_container.add_widget(reports_button)
        right_container.add_widget(settings_button)
        right_container.add_widget(help_button)
        right_container.add_widget(logout_button)
        
        # Ajouter les widgets aux conteneurs
        left_container.add_widget(title)
        center_container.add_widget(role_box)
        top_bar.add_widget(left_container)
        top_bar.add_widget(center_container)
        top_bar.add_widget(right_container)
        
        # ScrollView pour la grille de cartes
        scroll = MDScrollView(
            size_hint=(1, 1),
            do_scroll_x=False
        )
        
        # Grille pour les cartes
        self.grid = MDGridLayout(
            cols=3,
            spacing=dp(20),
            padding=dp(10),
            size_hint_y=None
        )
        self.grid.bind(minimum_height=self.grid.setter('height'))
        
        # Définition des modules et leurs statuts
        modules = {
            'Planification des Vols': {
                'icon': 'calendar-clock',
                'statuts': [
                    'Planification en cours',
                    'Prochains vols: 3',
                    'Missions à valider: 2'
                ]
            },
            'Préparation des Vols': {
                'icon': 'clipboard-check-outline',
                'statuts': [
                    'Checklists à compléter: 2',
                    'Équipements prêts',
                    'Briefing à 14h30'
                ]
            },
            'Exécution des Vols': {
                'icon': 'airplane',
                'statuts': [
                    'Vols en cours: 1',
                    'Conditions météo: Favorables',
                    'Durée restante: 45min'
                ]
            },
            'Complétion des Vols': {
                'icon': 'check-circle-outline',
                'statuts': [
                    'Vols complétés: 5',
                    'Rapports à finaliser: 2',
                    'Données à analyser: 3'
                ]
            }
        }
        
        # Création des cartes
        for title, info in modules.items():
            card = ModuleCard(
                title=title,
                status_examples=info['statuts'],
                icon=info['icon']
            )
            self.grid.add_widget(card)
        
        scroll.add_widget(self.grid)
        
        # Assemblage final
        self.layout.add_widget(top_bar)
        self.layout.add_widget(scroll)
        self.add_widget(self.layout)

    def show_role_menu(self, button):
        """Affiche le menu déroulant des rôles"""
        menu_items = [
            {
                "text": "Super Admin",
                "on_release": lambda x="Super Admin": self.select_role(x)
            },
            {
                "text": "Admin",
                "on_release": lambda x="Admin": self.select_role(x)
            },
            {
                "text": "Pilote",
                "on_release": lambda x="Pilote": self.select_role(x)
            },
            {
                "text": "Co-Pilote",
                "on_release": lambda x="Co-Pilote": self.select_role(x)
            }
        ]
        
        self.menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=2,
        )
        self.menu.open()

    def select_role(self, role_name):
        """Sélectionne un rôle"""
        self.role_label.text = role_name
        self.menu.dismiss()

    def logout(self, *args):
        """Déconnexion de l'utilisateur"""
        self.manager.current = 'login'

    def show_notifications(self, *args):
        """Affiche les notifications"""
        pass

    def show_reports(self, *args):
        """Affiche les rapports"""
        pass

    def show_settings(self, *args):
        """Affiche les paramètres"""
        pass

    def show_help(self, *args):
        """Affiche l'aide"""
        pass

    def on_pre_enter(self):
        """Appelé chaque fois que l'écran est sur le point d'être affiché"""
        pass

    @property
    def app(self):
        """Obtenir l'instance de l'application"""
        return MDApp.get_running_app()
