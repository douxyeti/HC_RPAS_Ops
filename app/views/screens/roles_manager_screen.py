from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFabButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    MDList,
    MDListItem,
    MDListItemLeadingIcon,
    MDListItemHeadlineText,
    MDListItemSupportingText,
    MDListItemTrailingIcon,
)
from app.services.roles_manager_service import RolesManagerService

class RolesManagerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.roles_service = RolesManagerService()
        
        # Crée la liste des rôles
        self.roles_list = MDList()
        self.add_widget(self.roles_list)
        
        # Ajoute le bouton flottant pour créer un rôle
        self.add_button = MDFabButton(
            icon="plus",
            pos_hint={"right": 0.95, "bottom": 0.05},
            on_release=lambda x: self.create_role()
        )
        self.add_widget(self.add_button)
        
        # Charge les rôles
        self.load_roles()
        
    def load_roles(self):
        """Charge et affiche la liste des rôles"""
        self.roles_list.clear_widgets()
        roles = self.roles_service.get_all_roles()
        
        for role_id, role_data in roles.items():
            role_data['id'] = role_id
            
            # Crée un élément de liste pour chaque rôle
            list_item = MDListItem()
            
            # Ajoute l'icône principale
            list_item.add_widget(MDListItemLeadingIcon(
                icon="account-circle"
            ))
            
            # Ajoute le titre et la description
            list_item.add_widget(MDListItemHeadlineText(
                text=role_data.get('name', '')
            ))
            list_item.add_widget(MDListItemSupportingText(
                text=role_data.get('description', '')
            ))
            
            # Ajoute les icônes d'action
            edit_button = MDIconButton(
                icon="pencil",
                on_release=lambda x, r=role_data: self.edit_role(r)
            )
            delete_button = MDIconButton(
                icon="delete",
                on_release=lambda x, r=role_data: self.delete_role(r)
            )
            
            list_item.add_widget(edit_button)
            list_item.add_widget(delete_button)
            
            self.roles_list.add_widget(list_item)
            
    def create_role(self):
        """Crée un nouveau rôle"""
        role_data = {
            'name': 'Nouveau rôle',
            'description': 'Description du rôle',
            'tasks': []
        }
        self.roles_service.create_role(role_data)
        self.load_roles()
        
    def edit_role(self, role_data):
        """Modifie un rôle existant"""
        # Pour l'instant, on met juste à jour le nom
        role_data['name'] = role_data['name'] + ' (modifié)'
        self.roles_service.update_role(role_data['id'], role_data)
        self.load_roles()
        
    def delete_role(self, role_data):
        """Supprime un rôle"""
        self.roles_service.delete_role(role_data['id'])
        self.load_roles()
