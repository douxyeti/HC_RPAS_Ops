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
            text="Tableau de bord principal",
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
            'Cadre Documentaire': {
                'icon': 'file-document-outline',
                'statuts': [
                    'Documentation mise à jour le 02/02/2024',
                    '3 documents en attente de validation',
                    '1 révision planifiée'
                ]
            },
            'Contrôle Opérationnel': {
                'icon': 'airplane',
                'statuts': [
                    '2 vols en cours',
                    'Conditions météo favorables',
                    '4 missions planifiées aujourd\'hui'
                ]
            },
            'Assurance Qualité': {
                'icon': 'check-circle-outline',
                'statuts': [
                    '98% conformité procédures',
                    '2 audits en cours',
                    '1 non-conformité à traiter'
                ]
            },
            'Gestion Sécurité': {
                'icon': 'shield-check-outline',
                'statuts': [
                    'Niveau de risque: Faible',
                    '0 incident en cours',
                    '2 exercices planifiés'
                ]
            },
            'Formation': {
                'icon': 'school-outline',
                'statuts': [
                    '3 formations en cours',
                    '2 évaluations à planifier',
                    '5 certifications à renouveler'
                ]
            },
            'Maintenance': {
                'icon': 'tools',
                'statuts': [
                    '2 maintenances préventives prévues',
                    '1 intervention en cours',
                    '4 drones opérationnels'
                ]
            },
            'Contrôle Maintenance': {
                'icon': 'clipboard-check-outline',
                'statuts': [
                    '15 inspections réalisées',
                    '2 validations en attente',
                    '1 rapport à finaliser'
                ]
            },
            'Navigation-Détection': {
                'icon': 'radar',
                'statuts': [
                    'Systèmes de navigation: OK',
                    '3 zones surveillées',
                    'Détection: Active'
                ]
            },
            'Contrôle Aérien': {
                'icon': 'air-traffic-tower',
                'statuts': [
                    'Espace aérien: Dégagé',
                    '2 autorisations en cours',
                    '1 restriction active'
                ]
            },
            'Gestion Personnel': {
                'icon': 'account-group-outline',
                'statuts': [
                    '12 personnes en service',
                    '3 plannings à valider',
                    '2 demandes en attente'
                ]
            },
            'Contrôle Sites': {
                'icon': 'map-marker-outline',
                'statuts': [
                    '5 sites actifs',
                    '2 inspections planifiées',
                    '1 rapport en cours'
                ]
            },
            'Gestion Flotte': {
                'icon': 'drone',
                'statuts': [
                    '8 drones en état opérationnel',
                    '2 drones en maintenance',
                    '1 mise à jour firmware disponible'
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
        # Réinitialiser le texte du label
        self.role_label.text = "Choisissez votre rôle"
        
        menu_items = []
        app = self.app
        roles = app.available_roles if hasattr(app, 'available_roles') else []
        
        # Trier les rôles par ordre alphabétique
        sorted_roles = sorted(roles)
        
        for role in sorted_roles:
            menu_items.append({
                "viewclass": "MDDropdownTextItem",
                "text": role,
                "on_release": lambda x=role: self.select_role(x)
            })
        
        self.menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            position="bottom",
            width=dp(300),
            max_height=dp(400),
            radius=[12, 12, 12, 12],
        )
        self.menu.open()
    
    def select_role(self, role_name):
        """Sélectionne un rôle"""
        if hasattr(self, 'menu'):
            self.menu.dismiss()
        self.role_label.text = role_name
        print(f"[DEBUG] DashboardScreen.select_role - Rôle sélectionné : {role_name}")

        # Logique de redirection basée sur le rôle
        if role_name == "Super Administrateur":
            # Rediriger vers le gestionnaire de tâches pour le Super Admin
            task_manager = self.manager.get_screen('task_manager')
            print(f"[DEBUG] DashboardScreen.select_role - Redirection vers le gestionnaire de tâches")
            task_manager.set_current_role(None, role_name)
            self.manager.current = 'task_manager'
        else:
            # Pour les autres rôles, rediriger vers le tableau de bord spécialisé
            try:
                specialized_dashboard = self.manager.get_screen('specialized_dashboard')
                print(f"[DEBUG] DashboardScreen.select_role - Redirection vers le tableau de bord spécialisé pour {role_name}")
                
                # Normaliser le nom du rôle pour l'ID
                role_id = role_name.lower().replace(' ', '_').replace('é', 'e').replace('è', 'e').replace('à', 'a')
                
                # Mettre à jour l'interface du tableau de bord spécialisé
                specialized_dashboard.update_for_role(role_name)
                
                # Effectuer la redirection
                self.manager.current = 'specialized_dashboard'
            except Exception as e:
                print(f"[ERROR] DashboardScreen.select_role - Erreur lors de la redirection : {str(e)}")
                # Afficher un message d'erreur dans la console
                print("Erreur : Impossible d'accéder au tableau de bord pour ce rôle")
    
    def logout(self, *args):
        """Déconnexion de l'utilisateur"""
        app = self.app
        if hasattr(app, 'logout'):
            app.logout()
    
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
    
    def on_pre_enter(self):
        """Appelé chaque fois que l'écran est sur le point d'être affiché"""
        # Réinitialiser le texte du label des rôles
        self.role_label.text = "Choisissez votre rôle"
    
    @property
    def app(self):
        """Obtenir l'instance de l'application"""
        from kivy.app import App
        return App.get_running_app()
