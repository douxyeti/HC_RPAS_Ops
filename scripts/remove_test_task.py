from app.services.firebase_service import FirebaseService

def remove_test_task():
    """Supprime la tâche de test 'AAAA' du rôle 'Responsable des opérations'"""
    firebase_service = FirebaseService()
    roles_ref = firebase_service.db.collection('roles')
    
    # Trouver le rôle "Responsable des opérations"
    roles = roles_ref.get()
    for role in roles:
        role_data = role.to_dict()
        if role_data.get('name') == 'Responsable des opérations':
            tasks = role_data.get('tasks', [])
            original_count = len(tasks)
            
            # Filtrer pour retirer la tâche AAAA
            tasks = [task for task in tasks if task['title'] != 'AAAA']
            
            if len(tasks) != original_count:
                print(f"Suppression de la tâche 'AAAA' du rôle 'Responsable des opérations'")
                print(f"Nombre de tâches: {original_count} -> {len(tasks)}")
                
                # Mettre à jour le rôle
                roles_ref.document(role.id).update({'tasks': tasks})
                print("Mise à jour effectuée avec succès")
            else:
                print("Tâche 'AAAA' non trouvée")
            break

if __name__ == "__main__":
    print("Début de la suppression de la tâche de test...")
    remove_test_task()
    print("Opération terminée!")
