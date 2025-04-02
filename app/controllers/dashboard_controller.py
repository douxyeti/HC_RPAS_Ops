from app.models.task import Task, Role

class DashboardController:
    def __init__(self, model):
        self.model = model
        self.model.bind(roles=self.on_roles_changed)
        self.current_role = None

    def load_role_tasks(self, role):
        """Charge les tâches spécifiques au rôle"""
        print(f"Loading tasks for role: {role}")
        
        # Obtenir le service de gestion des rôles
        from kivymd.app import MDApp
        roles_manager = MDApp.get_running_app().roles_manager_service
        
        # Récupérer les tâches depuis Firebase
        roles_data = roles_manager.get_all_roles()
        for role_data in roles_data:
            if role_data.get('name') == role:
                tasks = []
                for task_data in role_data.get('tasks', []):
                    tasks.append(Task(
                        title=task_data.get('title', ''),
                        description=task_data.get('description', ''),
                        module=task_data.get('module', ''),
                        status="En attente",
                        icon=task_data.get('icon', 'checkbox-marked-circle')
                    ))
                print(f"Loaded {len(tasks)} tasks for {role}")
                return tasks
        
        print(f"Rôle non trouvé dans Firebase: {role}")
        return []

    def update_role_selection(self, role_id):
        self.current_role = next((r for r in self.model.roles if r.id == role_id), None)
        return self.current_role

    def on_roles_changed(self, instance, value):
        print("Roles updated in controller")
