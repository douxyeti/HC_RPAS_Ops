from app.services.firebase_service import FirebaseService

def clean_duplicate_tasks(simulation=True):
    """Nettoie les tâches en double dans la base de données
    
    Args:
        simulation (bool): Si True, affiche seulement les changements sans les appliquer
    """
    # Utiliser le service Firebase existant
    firebase_service = FirebaseService()
    
    # Récupérer tous les rôles
    roles_ref = firebase_service.db.collection('roles')
    roles = roles_ref.get()
    
    # Dictionnaire pour suivre les tâches uniques par titre
    unique_tasks = {}
    duplicates_found = 0
    roles_to_update = 0
    
    print("\nAnalyse des tâches en cours...")
    print("MODE SIMULATION: Aucune modification ne sera appliquée" if simulation else "MODE RÉEL: Les modifications seront appliquées")
    
    for role in roles:
        role_data = role.to_dict()
        role_tasks = role_data.get('tasks', [])
        cleaned_tasks = []
        role_name = role_data.get('name', 'Sans nom')
        
        print(f"\nVérification du rôle: {role_name}")
        
        for task in role_tasks:
            task_key = f"{task['title']}_{task['module']}"
            if task_key not in unique_tasks:
                unique_tasks[task_key] = task
                cleaned_tasks.append(task)
            else:
                duplicates_found += 1
                print(f"  - Doublon trouvé: '{task['title']}' (module: {task['module']})")
        
        if len(cleaned_tasks) != len(role_tasks):
            roles_to_update += 1
            print(f"  > Changements prevus: {len(role_tasks)} -> {len(cleaned_tasks)} taches")
            if not simulation:
                print("  > Application des changements...")
                roles_ref.document(role.id).update({'tasks': cleaned_tasks})
    
    print(f"\nRapport {'de simulation' if simulation else 'final'}:")
    print(f"- Total des doublons trouvés: {duplicates_found}")
    print(f"- Rôles nécessitant une mise à jour: {roles_to_update}")
    print(f"- Total des tâches uniques: {len(unique_tasks)}")
    
    if simulation:
        print("\nAucune modification n'a été appliquée (mode simulation)")
        print("Pour appliquer les modifications, exécutez le script avec simulation=False")

if __name__ == "__main__":
    print("Début du nettoyage des tâches en double...")
    clean_duplicate_tasks(simulation=False)  # Mode réel
    print("\nNettoyage terminé!")
