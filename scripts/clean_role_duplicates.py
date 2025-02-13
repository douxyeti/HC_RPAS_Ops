import sys
import os

# Ajouter le répertoire racine au PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from app.services.firebase_service import FirebaseService
from collections import defaultdict

def clean_role_duplicates():
    """Nettoie les doublons dans la collection des rôles en fusionnant les tâches"""
    db = FirebaseService()
    
    # Récupérer tous les documents avec leurs références
    roles_ref = db.db.collection('roles').get()
    roles = []
    for doc in roles_ref:
        role_data = doc.to_dict()
        role_data['doc_ref'] = doc.reference
        roles.append(role_data)
    
    # Grouper les rôles par nom
    roles_by_name = defaultdict(list)
    for role in roles:
        name = role.get('name', '')
        if name:
            roles_by_name[name].append(role)
    
    # Pour chaque groupe de rôles avec le même nom
    for name, role_list in roles_by_name.items():
        if len(role_list) > 1:
            print(f"\nTraitement des doublons pour le rôle '{name}'...")
            
            # Trouver le rôle avec un ID valide et celui avec NO_ID
            valid_role = None
            no_id_role = None
            
            for role in role_list:
                if role.get('id', 'NO_ID') != 'NO_ID':
                    valid_role = role
                else:
                    no_id_role = role
            
            if valid_role and no_id_role:
                print(f"- Fusion des tâches du rôle NO_ID vers {valid_role['id']}")
                
                # Fusionner les tâches
                valid_role_tasks = valid_role.get('tasks', [])
                no_id_tasks = no_id_role.get('tasks', [])
                
                # Ajouter uniquement les tâches qui n'existent pas déjà
                existing_task_ids = {task.get('id') for task in valid_role_tasks if task.get('id')}
                new_tasks = [task for task in no_id_tasks if task.get('id') not in existing_task_ids]
                
                if new_tasks:
                    print(f"- Ajout de {len(new_tasks)} nouvelles tâches")
                    valid_role['tasks'] = valid_role_tasks + new_tasks
                    
                    # Mettre à jour le rôle dans Firebase
                    try:
                        # Supprimer la référence du document avant la mise à jour
                        doc_ref = valid_role.pop('doc_ref')
                        doc_ref.update(valid_role)
                        print(f"- Rôle {valid_role['id']} mis à jour avec succès")
                    except Exception as e:
                        print(f"! Erreur lors de la mise à jour du rôle {valid_role['id']}: {str(e)}")
                
                # Supprimer le rôle avec NO_ID
                try:
                    no_id_role['doc_ref'].delete()
                    print("- Rôle NO_ID supprimé avec succès")
                except Exception as e:
                    print(f"! Erreur lors de la suppression du rôle NO_ID: {str(e)}")
            else:
                print(f"! Impossible de trouver une paire valide/NO_ID pour le rôle '{name}'")

if __name__ == '__main__':
    print("Début du nettoyage des doublons de rôles...")
    clean_role_duplicates()
    print("\nNettoyage terminé.")
