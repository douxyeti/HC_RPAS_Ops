from app.services.firebase_service import FirebaseService
import json
from datetime import datetime

def verify_tasks_format():
    """Vérifie le format des tâches dans la base de données"""
    firebase_service = FirebaseService()
    roles_ref = firebase_service.db.collection('roles')
    roles = roles_ref.get()
    
    print("\nVérification du format des tâches...")
    
    # Structure attendue pour une tâche
    required_fields = ['id', 'title', 'description', 'module']
    issues_found = []
    tasks_by_id = {}
    
    for role in roles:
        role_data = role.to_dict()
        role_name = role_data.get('name', 'Sans nom')
        tasks = role_data.get('tasks', [])
        
        print(f"\nRôle: {role_name}")
        print(f"Nombre de tâches: {len(tasks)}")
        
        for task in tasks:
            # Vérifier les champs requis
            missing_fields = [field for field in required_fields if field not in task]
            if missing_fields:
                issues_found.append(f"Tâche dans le rôle '{role_name}' manque les champs: {', '.join(missing_fields)}")
                continue
            
            # Vérifier le format de l'ID
            task_id = task.get('id')
            if task_id in tasks_by_id:
                issues_found.append(f"ID en double trouvé: {task_id} dans le rôle '{role_name}'")
            else:
                tasks_by_id[task_id] = {'role': role_name, 'task': task}
            
            # Afficher les détails de la tâche
            print(f"\n  Tâche: {task['title']}")
            print(f"  - ID: {task_id}")
            print(f"  - Module: {task['module']}")
    
    print("\nRésumé de la vérification:")
    print(f"Total des tâches vérifiées: {len(tasks_by_id)}")
    
    if issues_found:
        print("\nProblèmes trouvés:")
        for issue in issues_found:
            print(f"- {issue}")
    else:
        print("\nAucun problème trouvé. Toutes les tâches ont un format correct.")

if __name__ == "__main__":
    verify_tasks_format()
