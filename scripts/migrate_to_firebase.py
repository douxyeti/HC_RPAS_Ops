import json
import os
from datetime import datetime
from firebase_admin import initialize_app, credentials, db

def load_config():
    """Charge la configuration existante depuis config.json"""
    config_path = os.path.join('data', 'config', 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def migrate_roles_and_tasks():
    """Migre les rôles et tâches vers Firebase"""
    # Initialiser Firebase
    cred_path = os.path.join('config', 'firebase-credentials.json')
    cred = credentials.Certificate(cred_path)
    app = initialize_app(cred, {
        'databaseURL': 'https://hc-rpas-ops-default-rtdb.firebaseio.com'
    })
    
    # Références Firebase
    ref = db.reference('/')
    roles_ref = ref.child('roles')
    tasks_ref = ref.child('tasks')
    role_tasks_ref = ref.child('role_tasks')
    
    # Charger la configuration existante
    config = load_config()
    roles = config.get('interface', {}).get('roles', {})
    
    # Migrer les rôles et leurs tâches
    now = datetime.now().isoformat()
    system_user = 'system_migration'
    
    # Dictionnaire pour stocker les ID des tâches
    task_ids = {}
    
    # Créer les tâches uniques
    all_tasks = set()
    for role_info in roles.values():
        for task in role_info.get('tasks', []):
            task_tuple = (
                task['title'],
                task.get('description', ''),
                task.get('icon', ''),
                task.get('module', '')
            )
            all_tasks.add(task_tuple)
    
    # Ajouter les tâches à Firebase
    for task in all_tasks:
        task_data = {
            'title': task[0],
            'description': task[1],
            'icon': task[2],
            'module': task[3],
            'createdAt': now,
            'updatedAt': now,
            'createdBy': system_user
        }
        new_task_ref = tasks_ref.push(task_data)
        task_ids[task[0]] = new_task_ref.key
    
    # Migrer les rôles et leurs associations avec les tâches
    for role_id, role_info in roles.items():
        # Créer le rôle
        role_data = {
            'name': role_info['name'],
            'permissions': role_info.get('permissions', []),
            'createdAt': now,
            'updatedAt': now,
            'createdBy': system_user
        }
        new_role_ref = roles_ref.push(role_data)
        new_role_id = new_role_ref.key
        
        # Associer les tâches au rôle
        role_tasks = {}
        for task in role_info.get('tasks', []):
            task_id = task_ids.get(task['title'])
            if task_id:
                role_tasks[task_id] = True
        
        if role_tasks:
            role_tasks_ref.child(new_role_id).set(role_tasks)
    
    print("Migration terminée avec succès !")
    print(f"Nombre de rôles migrés : {len(roles)}")
    print(f"Nombre de tâches uniques migrées : {len(all_tasks)}")

if __name__ == '__main__':
    migrate_roles_and_tasks()
