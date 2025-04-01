from app.services.roles_manager_service import RolesManagerService

# Initialise le service
roles_service = RolesManagerService()

# Récupère tous les rôles
roles = roles_service.get_all_roles()

# Trie les rôles par nom pour voir l'ordre exact
sorted_roles = sorted(roles.items(), key=lambda x: x[1].get('name', ''))

print("\nListe des rôles dans l'ordre :")
print("================================")
for role_id, role_data in sorted_roles:
    print(f"\nID: {role_id}")
    print(f"Nom: {role_data.get('name', 'NON DÉFINI')}")
    print(f"Description: {role_data.get('description', 'NON DÉFINIE')}")
    print(f"Données brutes: {role_data}")
    print("--------------------------------")
