"""Composant de sélection de rôle"""

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from app.services.config_service import ConfigService

class RoleSelector(MDBoxLayout):
    """Composant de sélection de rôle avec menu déroulant"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = ConfigService()
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.size = (dp(200), dp(56))
        self.spacing = 5
        self.padding = [5, 0]
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        # Label pour le rôle sélectionné
        self.role_label = MDLabel(
            text="Sélectionner un rôle",
            size_hint=(None, None),
            size=(dp(160), dp(56)),
            halign="center",
            valign="center",
            pos_hint={'center_y': 0.5}
        )
        
        # Bouton pour ouvrir le menu
        self.role_button = MDIconButton(
            icon="chevron-down",
            size_hint=(None, None),
            size=(dp(35), dp(35)),
            pos_hint={'center_y': 0.5}
        )
        self.role_button.bind(on_release=self.show_role_menu)
        
        # Ajouter les widgets
        self.add_widget(self.role_label)
        self.add_widget(self.role_button)
        
        # Menu déroulant (créé à la demande)
        self.menu = None
        self.callback = None
    
    def set_callback(self, callback):
        """Définit le callback à appeler lors de la sélection d'un rôle
        
        Args:
            callback: Fonction à appeler avec le rôle sélectionné
        """
        self.callback = callback
    
    def show_role_menu(self, button):
        """Affiche le menu déroulant des rôles"""
        if not self.menu:
            menu_items = []
            
            # Récupérer les rôles depuis la configuration
            roles_config = self.config.get_config('interface.roles', {})
            
            # Trier les rôles par nom
            sorted_roles = sorted(
                roles_config.items(),
                key=lambda x: x[1].get('name', '')
            )
            
            # Créer les éléments du menu
            for role_id, role_info in sorted_roles:
                menu_items.append({
                    "viewclass": "MDDropdownTextItem",
                    "text": role_info.get('name', role_id),
                    "on_release": lambda x=role_id: self._on_select_role(x)
                })
            
            # Créer le menu
            self.menu = MDDropdownMenu(
                caller=button,
                items=menu_items,
                position="bottom",
                width=dp(300),
                max_height=dp(400),
                radius=[12, 12, 12, 12],
                elevation=4
            )
        
        self.menu.open()
    
    def _on_select_role(self, role_id):
        """Gère la sélection d'un rôle
        
        Args:
            role_id: Identifiant du rôle sélectionné
        """
        # Fermer le menu
        if self.menu:
            self.menu.dismiss()
        
        # Mettre à jour le label
        role_info = self.config.get_config(f'interface.roles.{role_id}', {})
        self.role_label.text = role_info.get('name', role_id)
        
        # Appeler le callback
        if self.callback:
            self.callback(role_id)
    
    def set_role(self, role_id):
        """Définit le rôle sélectionné sans ouvrir le menu
        
        Args:
            role_id: Identifiant du rôle à sélectionner
        """
        role_info = self.config.get_config(f'interface.roles.{role_id}', {})
        self.role_label.text = role_info.get('name', role_id)
