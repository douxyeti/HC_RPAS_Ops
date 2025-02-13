from app.models.task import TaskModel
from app.services.firebase_service import FirebaseService

def main():
    print("Début du nettoyage des doublons...")
    task_model = TaskModel(FirebaseService())
    
    # Nettoyer les doublons pour tous les rôles
    results = task_model.clean_all_duplicates()
    
    # Afficher les résultats
    total_duplicates = sum(results.values())
    print("\nRésultats du nettoyage :")
    print("-" * 40)
    for role_id, count in results.items():
        if count > 0:
            print(f"Rôle {role_id}: {count} doublon(s) supprimé(s)")
    print("-" * 40)
    print(f"Total : {total_duplicates} doublon(s) supprimé(s)")

if __name__ == "__main__":
    main()
