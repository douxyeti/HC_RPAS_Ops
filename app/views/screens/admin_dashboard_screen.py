from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    MDList,
    MDListItem,
    MDListItemLeadingIcon,
    MDListItemHeadlineText,
    MDListItemSupportingText,
)
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.app import MDApp

class AdminDashboardScreen(MDScreen):
    """Écran d'administration pour gérer les rôles et tâches"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.roles_tasks_service = self.app.roles_tasks_service
        self.current_user = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # En-tête
        header = MDLabel(
            text="Tableau de Bord Super Administrateur",
            halign="center",
            font_style="Display"
        )
        layout.add_widget(header)
        
        # Liste des tâches disponibles
        tasks_list = MDList()
        
        # Tâche de gestion des rôles
        roles_task = MDListItem(
            on_release=lambda x: self.app.root.switch_screen('roles_manager')
        )
        
        roles_task.add_widget(MDListItemLeadingIcon(
            icon="account-cog"
        ))
        
        roles_task.add_widget(MDListItemHeadlineText(
            text="Gestion des Rôles"
        ))
        
        roles_task.add_widget(MDListItemSupportingText(
            text="Créer, modifier et supprimer les rôles du système"
        ))
        
        tasks_list.add_widget(roles_task)
        
        # Autres tâches administratives peuvent être ajoutées ici
        
        layout.add_widget(tasks_list)
        
        # Boutons d'action
        actions = MDBoxLayout(spacing=10, padding=10, size_hint_y=None, height=50)
        
        add_role_btn = MDButton(
            text="Ajouter Rôle",
            on_release=lambda x: self.show_role_dialog()
        )
        add_task_btn = MDButton(
            text="Ajouter Tâche",
            on_release=lambda x: self.show_task_dialog()
        )
        
        actions.add_widget(add_role_btn)
        actions.add_widget(add_task_btn)
        layout.add_widget(actions)
        
        # Liste des rôles et tâches
        self.roles_list = MDList()
        self.update_roles_list()
        layout.add_widget(self.roles_list)
        
        self.add_widget(layout)
        
    def update_roles_list(self):
        """Met à jour la liste des rôles"""
        self.roles_list.clear_widgets()
        roles = self.roles_tasks_service.get_all_roles()
        
        for role_id, role_data in roles.items():
            item = MDListItem()
            
            item.add_widget(MDListItemLeadingIcon(
                icon="account-circle"
            ))
            
            item.add_widget(MDListItemHeadlineText(
                text=role_data['name']
            ))
            
            item.add_widget(MDListItemSupportingText(
                text="Créer et gérer les rôles et leurs permissions"
            ))
            
            edit_icon = MDListItemLeadingIcon(
                icon="pencil",
                on_release=lambda x, r=role_id: self.show_role_dialog(r)
            )
            delete_icon = MDListItemLeadingIcon(
                icon="delete",
                on_release=lambda x, r=role_id: self.delete_role(r)
            )
            
            item.add_widget(edit_icon)
            item.add_widget(delete_icon)
            
            self.roles_list.add_widget(item)
            
    def show_role_dialog(self, role_id=None):
        """Affiche le dialogue pour ajouter/modifier un rôle"""
        role_data = None
        if role_id:
            role_data = self.roles_tasks_service.get_role(role_id)
            
        content = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        
        name_field = MDTextField(
            hint_text="Nom du rôle",
            text=role_data['name'] if role_data else ""
        )
        content.add_widget(name_field)
        
        # Liste des permissions disponibles
        permissions = ["create_user", "edit_user", "delete_user", 
                      "create_task", "edit_task", "delete_task"]
        permission_boxes = []
        
        for perm in permissions:
            checkbox = MDCheckbox(
                active=perm in (role_data.get('permissions', []) if role_data else [])
            )
            row = MDBoxLayout(orientation='horizontal')
            row.add_widget(MDLabel(text=perm))
            row.add_widget(checkbox)
            content.add_widget(row)
            permission_boxes.append((perm, checkbox))
            
        def save_role(dialog):
            permissions = [perm for perm, box in permission_boxes if box.active]
            if role_id:
                self.roles_tasks_service.update_role(
                    role_id, name_field.text, permissions
                )
            else:
                self.roles_tasks_service.create_role(
                    name_field.text, permissions, self.current_user.uid
                )
            self.update_roles_list()
            dialog.dismiss()
            
        dialog = MDDialog(
            title="Ajouter/Modifier Rôle",
            content_cls=content,
            buttons=[
                MDButton(
                    text="Annuler",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDButton(
                    text="Sauvegarder",
                    on_release=lambda x: save_role(dialog)
                )
            ]
        )
        dialog.open()
        
    def show_task_dialog(self, task_id=None):
        """Affiche le dialogue pour ajouter/modifier une tâche"""
        task_data = None
        if task_id:
            task_data = self.roles_tasks_service.get_task(task_id)
            
        content = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        
        title_field = MDTextField(
            hint_text="Titre de la tâche",
            text=task_data['title'] if task_data else ""
        )
        desc_field = MDTextField(
            hint_text="Description",
            text=task_data['description'] if task_data else "",
            multiline=True
        )
        icon_field = MDTextField(
            hint_text="Icône",
            text=task_data['icon'] if task_data else ""
        )
        module_field = MDTextField(
            hint_text="Module",
            text=task_data['module'] if task_data else ""
        )
        
        content.add_widget(title_field)
        content.add_widget(desc_field)
        content.add_widget(icon_field)
        content.add_widget(module_field)
        
        def save_task(dialog):
            if task_id:
                self.roles_tasks_service.update_task(
                    task_id, title_field.text, desc_field.text,
                    icon_field.text, module_field.text
                )
            else:
                self.roles_tasks_service.create_task(
                    title_field.text, desc_field.text,
                    icon_field.text, module_field.text,
                    self.current_user.uid
                )
            dialog.dismiss()
            
        dialog = MDDialog(
            title="Ajouter/Modifier Tâche",
            content_cls=content,
            buttons=[
                MDButton(
                    text="Annuler",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDButton(
                    text="Sauvegarder",
                    on_release=lambda x: save_task(dialog)
                )
            ]
        )
        dialog.open()
        
    def delete_role(self, role_id):
        """Supprime un rôle après confirmation"""
        def confirm_delete(dialog):
            self.roles_tasks_service.delete_role(role_id)
            self.update_roles_list()
            dialog.dismiss()
            
        dialog = MDDialog(
            title="Confirmer la suppression",
            text="Êtes-vous sûr de vouloir supprimer ce rôle ?",
            buttons=[
                MDButton(
                    text="Annuler",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDButton(
                    text="Supprimer",
                    on_release=lambda x: confirm_delete(dialog)
                )
            ]
        )
        dialog.open()
        
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        self.current_user = self.app.auth_service.current_user
        if not self.roles_tasks_service.is_super_admin(self.current_user.uid):
            self.app.switch_screen('dashboard')
        self.update_roles_list()
