from firebase_admin import credentials, initialize_app, db
import os
from app.services.roles_tasks_service import RolesTasksService

def main():
    # Initialiser Firebase avec les credentials
    cred_path = os.path.join(os.path.dirname(__file__), 'config', 'firebase-credentials.json')
    cred = credentials.Certificate(cred_path)
    
    try:
        firebase_app = initialize_app(cred, {
            'databaseURL': 'https://hc-rpas-ops-default-rtdb.firebaseio.com'
        })
    except ValueError:
        # L'application est déjà initialisée
        pass

    # Référence à la base de données
    ref = db.reference('/')
    tasks_ref = ref.child('tasks')
    role_tasks_ref = ref.child('role_tasks')

    # Créer le service
    service = RolesTasksService()

    # Créer la tâche de gestion des rôles
    task_data = {
        'title': 'Gestion des rôles',
        'description': 'Gérer les rôles et leurs permissions',
        'icon': 'account-cog',
        'module': 'system'
    }

    # Ajouter la tâche
    new_task_ref = tasks_ref.push(task_data)
    task_id = new_task_ref.key

    # Assigner la tâche au super admin
    super_admin_id = "super_admin"  # ID du super admin
    service.assign_task_to_role(super_admin_id, task_id)

    print(f"Tâche 'Gestion des rôles' créée avec l'ID: {task_id}")
    print("La tâche a été assignée au super administrateur")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erreur lors de la création de la tâche: {str(e)}")
