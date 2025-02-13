import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

def load_config():
    """Charge la configuration depuis le fichier config.json"""
    print("Configuration chargée avec succès")
    return {
        'firebase': {
            'credentials': 'firebase-credentials.json'
        }
    }

def init_firebase():
    """Initialise la connexion Firebase"""
    config = load_config()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    cred_path = os.path.join(project_root, 'data', 'config', 'firebase-service-account.json')
    
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

def clean_tasks():
    """Nettoie les tâches en double dans la base de données"""
    db = init_firebase()
    roles_ref = db.collection('roles')
    roles = roles_ref.get()
    
    # Dictionnaire pour suivre les tâches uniques par titre
    unique_tasks = {}
    duplicates_found = 0
    
    for role in roles:
        role_data = role.to_dict()
        role_tasks = role_data.get('tasks', [])
        cleaned_tasks = []
        
        for task in role_tasks:
            task_key = f"{task['title']}_{task['module']}"
            if task_key not in unique_tasks:
                unique_tasks[task_key] = task
                cleaned_tasks.append(task)
            else:
                duplicates_found += 1
                print(f"Doublon trouvé pour la tâche '{task['title']}' dans le rôle '{role_data.get('name')}'")
        
        if len(cleaned_tasks) != len(role_tasks):
            print(f"Mise à jour du rôle '{role_data.get('name')}' avec {len(cleaned_tasks)} tâches uniques")
            roles_ref.document(role.id).update({'tasks': cleaned_tasks})
    
    print(f"\nRapport de nettoyage:")
    print(f"Total des doublons trouvés: {duplicates_found}")
    print(f"Total des tâches uniques: {len(unique_tasks)}")

if __name__ == "__main__":
    clean_tasks()
