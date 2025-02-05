from app.services.roles_manager_service import RolesManagerService

# Initialise le service
roles_service = RolesManagerService()

# Récupère tous les rôles
roles = roles_service.get_all_roles()

# Trie les rôles par nom
sorted_roles = sorted(roles.items(), key=lambda x: x[1].get('name', ''))

print("\nRecherche des rôles autour de 'Commandant de bord'...")
print("=================================================")

# Trouve l'index du rôle "Commandant de bord"
pilot_command_index = next(i for i, (_, role) in enumerate(sorted_roles) if role.get('name') == 'Commandant de bord')

# Affiche les rôles avant et après
start_index = max(0, pilot_command_index - 2)
end_index = min(len(sorted_roles), pilot_command_index + 3)

for i in range(start_index, end_index):
    role_id, role_data = sorted_roles[i]
    print(f"\nPosition {i}:")
    print(f"ID: {role_id}")
    print(f"Nom: {role_data.get('name', 'NON DÉFINI')}")
    print(f"Description: {role_data.get('description', 'NON DÉFINIE')}")
    print(f"Données brutes: {role_data}")
    print("--------------------------------")
