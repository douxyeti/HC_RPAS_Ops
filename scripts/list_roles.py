from app.services.roles_manager_service import RolesManagerService

# Initialise le service
roles_service = RolesManagerService()

# Récupère tous les rôles
roles = roles_service.get_all_roles()

print("\nListe des rôles dans Firebase :")
print("================================")
for role_id, role_data in roles.items():
    print(f"\nID: {role_id}")
    print(f"Nom: {role_data.get('name', 'Non défini')}")
    print(f"Description: {role_data.get('description', 'Non définie')}")
    print(f"Tâches: {role_data.get('tasks', [])}")
    print("--------------------------------")
