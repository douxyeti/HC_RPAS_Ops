from app.services.firebase_service import FirebaseService
from collections import defaultdict

def check_role_duplicates():
    """Vérifie les doublons dans la collection des rôles"""
    db = FirebaseService()
    roles = db.get_collection('roles')
    
    # Vérifier les doublons par nom
    roles_by_name = defaultdict(list)
    for role in roles:
        name = role.get('name', '')
        if name:
            roles_by_name[name].append(role)
    
    # Afficher les doublons trouvés
    print("\n=== Doublons par nom de rôle ===")
    for name, role_list in roles_by_name.items():
        if len(role_list) > 1:
            print(f"\nRôle '{name}' trouvé {len(role_list)} fois:")
            for role in role_list:
                print(f"  - ID: {role.get('id', 'NO_ID')}")
                print(f"    Description: {role.get('description', 'Aucune description')}")
                print(f"    Permissions: {role.get('permissions', [])}")
                print(f"    Tâches: {len(role.get('tasks', []))}")

if __name__ == '__main__':
    check_role_duplicates()
