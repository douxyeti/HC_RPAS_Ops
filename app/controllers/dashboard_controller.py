from app.models.task import Task, Role

class DashboardController:
    def __init__(self, model):
        self.model = model
        self.model.bind(roles=self.on_roles_changed)
        self.current_role = None

    def load_role_tasks(self, role):
        """Charge les tâches spécifiques au rôle"""
        print(f"Loading tasks for role: {role}")
        
        # Définir les tâches selon le rôle
        if role == "Super Administrateur":
            tasks = [
                Task(
                    title="Gérer les rôles",
                    description="Configurer les rôles et permissions",
                    module="admin",
                    status="En attente"
                ),
                Task(
                    title="Configuration système",
                    description="Paramètres système et sécurité",
                    module="admin",
                    status="En attente"
                ),
                Task(
                    title="Audit des opérations",
                    description="Vérifier les logs et rapports",
                    module="admin",
                    status="En attente"
                )
            ]
        elif role == "Commandant de bord":
            tasks = [
                Task(
                    title="Planifier les vols",
                    description="Créer et gérer les plans de vol",
                    module="operations",
                    status="En attente"
                ),
                Task(
                    title="Rapports de mission",
                    description="Rédiger les rapports de mission",
                    module="operations",
                    status="En attente"
                ),
                Task(
                    title="Gestion d'équipe",
                    description="Gérer l'équipe de vol",
                    module="operations",
                    status="En attente"
                )
            ]
        elif role == "Copilote":
            tasks = [
                Task(
                    title="Vérifications pré-vol",
                    description="Liste de contrôle avant vol",
                    module="operations",
                    status="En attente"
                ),
                Task(
                    title="Assistance navigation",
                    description="Support à la navigation",
                    module="operations",
                    status="En attente"
                ),
                Task(
                    title="Maintenance équipement",
                    description="Suivi de la maintenance",
                    module="operations",
                    status="En attente"
                )
            ]
        else:
            print(f"Rôle inconnu: {role}")
            tasks = []
        
        print(f"Loaded {len(tasks)} tasks for {role}")
        return tasks

    def update_role_selection(self, role_id):
        self.current_role = next((r for r in self.model.roles if r.id == role_id), None)
        return self.current_role

    def on_roles_changed(self, instance, value):
        print("Roles updated in controller")
