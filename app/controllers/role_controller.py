from ..models.role import Role

class RoleController:
    """
    Contrôleur gérant la logique des rôles dans l'application.
    Fait le lien entre les vues et le modèle Role.
    """
    
    def __init__(self):
        """Initialise le contrôleur de rôles."""
        self.current_role = None
        self._roles = {}  # Cache des rôles

    def select_role(self, role_name, screen_instance=None):
        """
        Sélectionne un rôle et gère la redirection appropriée.
        
        Args:
            role_name (str): Nom du rôle à sélectionner
            screen_instance: Instance de l'écran actuel (pour accès au screen manager)
            
        Returns:
            bool: True si la sélection a réussi, False sinon
        """
        try:
            print(f"[DEBUG] RoleController.select_role - Rôle sélectionné : {role_name}")
            self.current_role = role_name

            if not screen_instance or not hasattr(screen_instance, 'manager'):
                return True

            # Logique de redirection basée sur le rôle
            if role_name == "Super Administrateur":
                # Rediriger vers le gestionnaire de tâches pour le Super Admin
                task_manager = screen_instance.manager.get_screen('task_manager')
                print(f"[DEBUG] RoleController.select_role - Redirection vers le gestionnaire de tâches")
                task_manager.set_current_role(None, role_name)
                screen_instance.manager.current = 'task_manager'
            else:
                # Pour les autres rôles, rediriger vers le tableau de bord spécialisé
                try:
                    specialized_dashboard = screen_instance.manager.get_screen('specialized_dashboard')
                    print(f"[DEBUG] RoleController.select_role - Redirection vers le tableau de bord spécialisé pour {role_name}")
                    specialized_dashboard.update_for_role(role_name)
                    screen_instance.manager.current = 'specialized_dashboard'
                except Exception as e:
                    print(f"[ERROR] RoleController.select_role - Erreur lors de la redirection : {str(e)}")
                    return False

            return True
        except Exception as e:
            print(f"[ERROR] RoleController.select_role - Erreur inattendue : {str(e)}")
            return False

    def get_available_roles(self, app_instance=None):
        """
        Récupère la liste des rôles disponibles.
        
        Args:
            app_instance: Instance de l'application
            
        Returns:
            list: Liste des rôles disponibles
        """
        if app_instance and hasattr(app_instance, 'available_roles'):
            return sorted(app_instance.available_roles)
        return []

    def get_current_role(self):
        """
        Récupère le rôle actuellement sélectionné.
        
        Returns:
            str: Nom du rôle actuel ou None
        """
        return self.current_role
