from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivymd.uix.textfield import MDTextField
from app.services.roles_manager_service import RolesManagerService
from kivy.uix.widget import Widget
from kivy.clock import Clock

class RoleCard(MDCard):
    def __init__(self, role_data, on_edit, on_delete, on_manage_tasks, **kwargs):
        super().__init__(**kwargs)
        print(f"Création de la carte pour le rôle : {role_data}")  # Debug
        
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(120)
        self.padding = dp(16)
        self.spacing = dp(8)
        self.elevation = 1
        
        # Layout pour le titre et les boutons
        header = MDBoxLayout(orientation='horizontal', adaptive_height=True)
        
        # Titre avec vérification
        title_text = role_data.get('name', '')
        print(f"Titre du rôle : {title_text}")  # Debug
        
        title = MDLabel(
            text=title_text,
            theme_font_size="Custom",
            font_size="20sp",
            adaptive_height=True
        )
        header.add_widget(title)
        
        # Boutons d'action
        actions = MDBoxLayout(
            orientation='horizontal',
            adaptive_width=True,
            spacing=dp(8)
        )
        
        edit_btn = MDIconButton(
            icon='pencil',
            on_release=lambda x: on_edit(role_data)
        )
        actions.add_widget(edit_btn)

        # Bouton de gestion des tâches
        tasks_btn = MDIconButton(
            icon='clipboard-list',
            on_release=lambda x: on_manage_tasks(role_data),
            theme_icon_color="Custom",
            icon_color=[1, 0, 0, 1]  # Rouge
        )
        actions.add_widget(tasks_btn)
        
        delete_btn = MDIconButton(
            icon='delete',
            on_release=lambda x: on_delete(role_data)
        )
        actions.add_widget(delete_btn)
        header.add_widget(actions)
        
        # Description avec vérification
        desc_text = role_data.get('description', 'Aucune description')
        print(f"Description du rôle : {desc_text}")  # Debug
        
        description = MDLabel(
            text=desc_text,
            adaptive_height=True
        )
        
        self.add_widget(header)
        self.add_widget(description)

class RolesManagerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'roles_manager'
        self.roles_manager_service = RolesManagerService()
        
        # Créer l'en-tête avec le bouton de gestion des tâches
        header = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            spacing=dp(10),
            padding=[dp(10), 0],
            md_bg_color=[0.2, 0.2, 0.9, 1]  # Bleu foncé
        )
        
        # Bouton retour
        back_btn = MDIconButton(
            icon="arrow-left",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            on_release=lambda x: self.go_back(),
            pos_hint={"center_y": 0.5}
        )
        header.add_widget(back_btn)
        
        # Titre
        title = MDLabel(
            text="Gestion des Rôles",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            theme_font_size="Custom",
            font_size="24sp",
            size_hint_x=0.7,
            halign="center"
        )
        header.add_widget(title)
        
        # Bouton rapport (redirige vers gestion des tâches)
        report_btn = MDIconButton(
            icon="file-document-outline",
            theme_text_color="Custom",
            text_color=[1, 0, 0, 1],  # Rouge comme le bouton de gestion des tâches
            on_release=lambda x: self.go_to_tasks(),
            pos_hint={"center_y": 0.5},
            size_hint_x=0.15
        )
        header.add_widget(report_btn)
        
        # Bouton d'ajout de rôle
        add_btn = MDIconButton(
            icon="plus",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            on_release=lambda x: self.show_add_role_dialog(),
            pos_hint={"center_y": 0.5},
            size_hint_x=0.15
        )
        header.add_widget(add_btn)
        
        # Ajouter l'en-tête à l'écran
        self.add_widget(header)
        
        # Créer la grille pour les cartes de rôles
        self.roles_grid = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10),
            adaptive_height=True
        )
        
        # Mettre la grille dans un ScrollView
        scroll = MDScrollView(
            do_scroll_x=False,
            size_hint=(1, 1)
        )
        scroll.add_widget(self.roles_grid)
        self.add_widget(scroll)
        
        # Charger les rôles
        self.load_roles()
        
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        self.load_roles()  # Recharge les rôles à chaque fois qu'on revient sur l'écran
        
    def load_roles(self):
        """Charge et affiche la liste des rôles"""
        roles_grid = self.ids.roles_grid
        roles_grid.clear_widgets()
        roles = self.roles_manager_service.get_all_roles()
        
        # Convertir le dictionnaire en liste et trier par nom
        sorted_roles = sorted(
            [{'id': role_id, **role_data} for role_id, role_data in roles.items()],
            key=lambda x: x.get('name', '').lower()  # Tri insensible à la casse
        )
        
        for role_data in sorted_roles:
            print(f"Chargement du rôle : ID={role_data['id']}, Nom={role_data.get('name', 'NON DÉFINI')}")
            # Vérifie que le rôle a au moins un nom
            if not role_data.get('name'):
                print(f"Rôle ignoré car sans nom : {role_data['id']}")
                continue
                
            card = RoleCard(
                role_data,
                on_edit=self.edit_role,
                on_delete=self.delete_role,
                on_manage_tasks=self.manage_tasks,
                size_hint_x=1
            )
            roles_grid.add_widget(card)
            
    def show_add_role_dialog(self):
        """Affiche un dialogue pour saisir le nom du nouveau rôle"""
        dialog = MDDialog(
            radius=20,
            title="Ajouter un nouveau rôle",
            type="custom",
            content_cls=MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                padding=dp(10),
                size_hint_y=None,
                height=dp(100),
                children=[
                    MDTextField(
                        hint_text="Nom du rôle",
                        mode="rectangle",
                        size_hint_y=None,
                        height=dp(48)
                    )
                ]
            ),
            buttons=[
                MDButton(
                    style="text",
                    on_release=lambda x: dialog.dismiss(),
                    children=[MDButtonText(text="ANNULER")]
                ),
                MDButton(
                    style="text",
                    on_release=lambda x: self.create_role(dialog),
                    children=[MDButtonText(text="CRÉER")]
                )
            ]
        )
        dialog.open()

    def create_role(self, dialog):
        """Crée un nouveau rôle avec le nom saisi"""
        role_name = dialog.content_cls.children[0].text
        if role_name.strip():
            # Générer un ID unique pour le rôle
            role_id = role_name.lower().replace(" ", "_")
            
            role_data = {
                'id': role_id,
                'name': role_name,
                'description': '',
                'permissions': [],
                'tasks': []
            }
            
            # Créer le rôle dans Firebase
            success = self.roles_manager_service.create_role(role_data)
            
            if success:
                # Fermer le dialogue
                dialog.dismiss()
                
                # Rafraîchir l'affichage
                self.load_roles()
            else:
                print("Erreur lors de la création du rôle")
        else:
            print("Le nom du rôle ne peut pas être vide")

    def add_role(self):
        """Affiche le dialogue de création d'un nouveau rôle"""
        self.show_add_role_dialog()

    def edit_role(self, role_data):
        """Ouvre l'écran d'édition pour le rôle"""
        edit_screen = self.manager.get_screen('role_edit')
        edit_screen.role_id = role_data.get('id', '')
        edit_screen.role_name = role_data.get('name', '')
        self.manager.transition.direction = 'left'
        self.manager.current = 'role_edit'

    def manage_tasks(self, role_data=None):
        """Ouvre l'écran de gestion des tâches pour le rôle"""
        task_screen = self.manager.get_screen('task_manager')
        
        # Si on vient d'une carte de rôle, définir le rôle courant
        if role_data:
            task_screen.current_role_id = role_data.get('id', '')
            task_screen.current_role_name = role_data.get('name', '')
        else:
            # Sinon, on vient du tableau de bord admin, ne pas définir de rôle courant
            task_screen.current_role_id = ''
            task_screen.current_role_name = ''
            
        self.manager.transition.direction = 'left'
        self.manager.current = 'task_manager'

    def delete_role(self, role_data):
        """Supprime un rôle après confirmation"""
        dialog = MDDialog(
            radius=20,
            size_hint=(.8, None)
        )
        
        dialog.add_widget(MDDialogHeadlineText(
            text="Confirmer la suppression",
            theme_font_size="Custom",
            font_size="24sp"
        ))
        
        content_container = MDDialogContentContainer(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20)
        )
        
        content_container.add_widget(MDLabel(
            text=f"Voulez-vous vraiment supprimer le rôle {role_data.get('name', '')} ?",
            theme_font_size="Custom",
            font_size="16sp"
        ))
        dialog.add_widget(content_container)
        
        button_container = MDDialogButtonContainer(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        cancel_button = MDButton(
            style="text",
            on_release=lambda x: dialog.dismiss()
        )
        cancel_button.add_widget(MDButtonText(text="Annuler"))
        
        delete_button = MDButton(
            style="text",
            on_release=lambda x: self.confirm_delete_role(role_data.get('id', ''), dialog)
        )
        delete_button.add_widget(MDButtonText(text="Supprimer"))
        
        button_container.add_widget(cancel_button)
        button_container.add_widget(delete_button)
        dialog.add_widget(button_container)
        
        dialog.open()

    def confirm_delete_role(self, role_id, dialog):
        """Confirme et effectue la suppression du rôle"""
        if role_id:
            self.roles_manager_service.delete_role(role_id)
            self.load_roles()
        dialog.dismiss()

    def go_to_tasks(self):
        """Rediriger vers l'écran de gestion des tâches"""
        self.manager.transition.direction = 'left'
        self.manager.current = 'task_manager'

    def go_back(self):
        """Retourner à l'écran précédent"""
        self.manager.transition.direction = 'right'
        self.manager.current = 'dashboard'
