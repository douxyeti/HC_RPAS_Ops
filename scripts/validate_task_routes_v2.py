from app.services.firebase_service import FirebaseService
from app.services.roles_manager_service import RolesManagerService
import json, os, datetime

def screens_for_module(fs, module_id):
    branch = module_id.replace("module_","")
    coll = f"module_indexes_screens_{module_id}_{branch}"
    try:
        docs = fs.get_collection(coll) or []
        ids = {d.get("id") for d in docs if isinstance(d, dict) and d.get("id")}
        return ids, coll, len(docs)
    except Exception:
        return set(), coll, 0

def main():
    fs = FirebaseService()
    roles = RolesManagerService().get_all_roles()
    if isinstance(roles, dict):
        roles = list(roles.values())

    module_ids = sorted({ t.get("target_module_id") for r in roles for t in (r.get("tasks") or []) if isinstance(t, dict) and t.get("target_module_id") })
    module_screens = {}
    for mid in module_ids:
        sids, coll, count = screens_for_module(fs, mid)
        module_screens[mid] = {"screens": sids, "coll": coll, "count": count}

    summary = {"roles": len(roles), "tasks_total": 0, "tasks_routed": 0, "tasks_unrouted_ok": 0, "warnings": [], "errors": []}
    details = []

    for r in roles:
        for t in (r.get("tasks") or []):
            if not isinstance(t, dict): 
                continue
            summary["tasks_total"] += 1
            mid = t.get("target_module_id")
            sid = t.get("target_screen_id")
            entry = {
                "role_id": r.get("id"),
                "role_name": r.get("name"),
                "task_title": t.get("title") or t.get("id"),
                "target_module_id": mid,
                "target_screen_id": sid
            }

            if mid:
                screens = module_screens.get(mid, {}).get("screens", set())
                if sid and screens and sid not in screens:
                    entry["issue"] = "SCREEN_NOT_FOUND_IN_MODULE"
                    entry["known_screens_sample"] = sorted(list(screens))[:10]
                    summary["errors"].append(entry)
                else:
                    summary["tasks_routed"] += 1
                    entry["status"] = "ROUTED"
                    details.append(entry)
            else:
                # Pas de cible = OK pour le moment
                summary["tasks_unrouted_ok"] += 1
                entry["status"] = "UNROUTED_OK"
                details.append(entry)

    # Info seulement : modules sans écrans
    for mid, info in module_screens.items():
        if info["count"] == 0:
            summary["warnings"].append({"issue": "MODULE_HAS_NO_SCREENS", "module_id": mid, "coll": info["coll"]})

    os.makedirs("reports", exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_json = f"reports/task_routes_status_{stamp}.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "details": details}, f, ensure_ascii=False, indent=2)

    print(f"Rôles: {summary['roles']}")
    print(f"Tâches: {summary['tasks_total']} | Routées: {summary['tasks_routed']} | Non routées (OK): {summary['tasks_unrouted_ok']}")
    if summary["errors"]:
        print(f"Erreurs: {len(summary['errors'])} (écran introuvable dans le module)")
    if summary["warnings"]:
        print(f"Avertissements: {len(summary['warnings'])} (modules sans écrans)")
    print(f"Rapport: {out_json}")

if __name__ == "__main__":
    main()
