from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDButton, MDButtonText

class MainScreen(MDScreen):
    """Écran principal du dashboard après connexion."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main"
        self.current_role = None
        self.role_menu = None
        self.dialog = None
        
    def on_enter(self):
        """Appelé lorsque l'écran devient actif."""
        if not self.current_role:
            self.show_role_selection()
    
    def show_role_selection(self, *args):
        """Affiche le menu de sélection du rôle."""
        if not self.role_menu:
            menu_items = [
                {
                    "text": f"{role}",
                    "on_release": lambda x=role: self.set_role(x),
                }
                for role in [
                    "Commandant de bord",
                    "Pilote",
                    "Observateur",
                    "Technicien maintenance",
                    "Gestionnaire opérations",
                    "Responsable formation"
                ]
            ]
            
            self.role_menu = MDDropdownMenu(
                caller=self.ids.toolbar,
                items=menu_items,
                width_mult=4,
                position="bottom",
            )
            
        self.role_menu.open()
        
    def set_role(self, role_name):
        """Définit le rôle sélectionné."""
        self.current_role = role_name
        self.role_menu.dismiss()
        # TODO: Mettre à jour l'interface en fonction du rôle
        
    def toggle_nav_drawer(self):
        """Ouvre/ferme le tiroir de navigation."""
        # TODO: Implémenter le tiroir de navigation
        pass
        
    def logout(self):
        """Déconnecte l'utilisateur."""
        self.manager.current = "login"
        
    def create_report(self):
        """Crée un nouveau rapport."""
        self.show_dialog("Nouveau Rapport", "Fonctionnalité en cours de développement")
        
    def view_reports(self):
        """Affiche la liste des rapports."""
        self.show_dialog("Consulter Rapports", "Fonctionnalité en cours de développement")
        
    def validate_reports(self):
        """Affiche les rapports en attente de validation."""
        self.show_dialog("Valider Rapports", "Fonctionnalité en cours de développement")
        
    def show_dialog(self, title, text):
        """Affiche une boîte de dialogue."""
        if not self.dialog:
            self.dialog = MDDialog(
                title=title,
                text=text,
                buttons=[
                    MDButton(
                        MDButtonText(text="Fermer"),
                        style="text",
                        on_press=lambda x: self.dialog.dismiss()
                    )
                ]
            )
        else:
            self.dialog.title = title
            self.dialog.text = text
            
        self.dialog.open()
