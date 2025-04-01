from app.services.firebase_service import FirebaseService

def check_database():
    # Initialiser le service Firebase
    firebase_service = FirebaseService()
    
    # Récupérer tous les rôles
    print("\n=== Vérification de la base de données ===")
    print("\nRécupération de tous les rôles...")
    
    # Vérifier spécifiquement le rôle Chef pilote
    chef_pilote_id = "1739113171349"
    chef_pilote = firebase_service.get_document("roles", chef_pilote_id)
    print(f"\nDétails du rôle Chef pilote (ID: {chef_pilote_id}):")
    print("----------------------------------------")
    if chef_pilote:
        print(f"Nom: {chef_pilote.get('name', 'Non défini')}")
        print(f"Description: {chef_pilote.get('description', 'Non définie')}")
        tasks = chef_pilote.get('tasks', [])
        print(f"\nNombre de tâches: {len(tasks)}")
        if tasks:
            print("\nListe des tâches:")
            for i, task in enumerate(tasks, 1):
                print(f"\nTâche {i}:")
                print(f"  - Titre: {task.get('title', 'Non défini')}")
                print(f"  - Description: {task.get('description', 'Non définie')}")
                print(f"  - Module: {task.get('module', 'Non défini')}")
                print(f"  - Icône: {task.get('icon', 'Non définie')}")
        else:
            print("Aucune tâche trouvée")
    else:
        print("Rôle non trouvé dans la base de données")

if __name__ == "__main__":
    check_database()
