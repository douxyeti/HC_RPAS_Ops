from app.services.firebase_service import FirebaseService
import time
import random
import re

def create_task_id(title, module):
    """Crée un ID unique pour une tâche"""
    # Convertir le titre en snake_case
    title = title.lower()
    title = re.sub(r'[éèêë]', 'e', title)
    title = re.sub(r'[àâä]', 'a', title)
    title = re.sub(r'[ùûü]', 'u', title)
    title = re.sub(r'[îï]', 'i', title)
    title = re.sub(r'[ôö]', 'o', title)
    title = re.sub(r'[^a-z0-9\s]', '', title)
    title = re.sub(r'\s+', '_', title.strip())
    
    # Créer un ID unique avec timestamp et nombre aléatoire
    timestamp = int(time.time() * 1000)
    random_num = random.randint(1000, 9999)
    
    return f"{title}_{module}_{timestamp}_{random_num}"

def add_task_ids():
    """Ajoute des IDs uniques aux tâches qui n'en ont pas"""
    firebase_service = FirebaseService()
    roles_ref = firebase_service.db.collection('roles')
    roles = roles_ref.get()
    
    print("\nAjout des IDs aux tâches...")
    total_tasks_updated = 0
    
    for role in roles:
        role_data = role.to_dict()
        role_name = role_data.get('name', 'Sans nom')
        tasks = role_data.get('tasks', [])
        tasks_updated = False
        
        print(f"\nRôle: {role_name}")
        print(f"Nombre de tâches: {len(tasks)}")
        
        for task in tasks:
            if 'id' not in task:
                task_id = create_task_id(task['title'], task['module'])
                task['id'] = task_id
                tasks_updated = True
                total_tasks_updated += 1
                print(f"  + ID ajouté pour la tâche '{task['title']}': {task_id}")
        
        if tasks_updated:
            print(f"  > Mise à jour des tâches dans la base de données...")
            roles_ref.document(role.id).update({'tasks': tasks})
    
    print(f"\nRapport final:")
    print(f"- Total des tâches mises à jour: {total_tasks_updated}")

if __name__ == "__main__":
    print("Début de l'ajout des IDs aux tâches...")
    add_task_ids()
    print("\nOpération terminée!")
