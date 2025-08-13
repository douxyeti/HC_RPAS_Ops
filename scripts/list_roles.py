from app.services.roles_manager_service import RolesManagerService

def main():
    svc = RolesManagerService()
    roles = svc.get_all_roles()  # -> liste de rôles (dicts)

    # Accepte liste ou dict par sécurité
    if isinstance(roles, dict):
        roles_iter = roles.values()
    else:
        roles_iter = roles

    roles_iter = list(roles_iter)
    print(f"\nListe des rôles dans Firebase ({len(roles_iter)}):")
    print("=" * 40)

    for r in roles_iter:
        role_id = r.get("id", "inconnu")
        name = r.get("name", role_id)
        tasks = r.get("tasks") or []
        print(f"- {name} ({role_id})  {len(tasks)} tâches")
        for t in tasks:
            title = t.get("title") or t.get("id", "")
            target_module = t.get("target_module_id") or t.get("module") or ""
            target_screen = t.get("target_screen_id") or t.get("screen") or ""
            arrow = " → " if (target_module or target_screen) else ""
            dest = ".".join([x for x in [target_module, target_screen] if x])
            print(f"     {title}{arrow}{dest}")

if __name__ == "__main__":
    main()
