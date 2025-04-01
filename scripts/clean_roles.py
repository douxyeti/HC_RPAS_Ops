from app.services.roles_manager_service import RolesManagerService

# Initialise le service
roles_service = RolesManagerService()

# IDs des rôles à supprimer
test_roles = [
    '2gqAPkoDfAIgtJRhQXnr',
    '7wsIS7fHffeLnXBYxaJ5',
    'Oiahl4gA4FM7pg6bOfjv',
    'QpFQPtYMo536gYjcLxBr',
    'cVodXFjh2nLWfaOXQxvl',
    'mxzOmo7u2GF18BfjhsvS'
]

# Supprime les rôles de test
for role_id in test_roles:
    print(f"Suppression du rôle {role_id}...")
    roles_service.delete_role(role_id)

print("\nNettoyage terminé !")
