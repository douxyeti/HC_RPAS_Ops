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

    issues = []
    def add_issue(kind, role, task, extra=None):
        i = {
            "kind": kind,
            "role_id": role.get("id"),
            "role_name": role.get("name"),
            "task_title": task.get("title") or task.get("id"),
            "target_module_id": task.get("target_module_id") or task.get("module"),
            "target_screen_id": task.get("target_screen_id") or task.get("screen"),
        }
        if extra: i.update(extra)
        issues.append(i)

    for r in roles:
        for t in (r.get("tasks") or []):
            if not t.get("target_module_id") and t.get("module"):
                add_issue("LEGACY_TASK_WITH_MODULE_FIELD", r, t)
                continue
            mid = t.get("target_module_id")
            sid = t.get("target_screen_id")
            if not mid and not sid:
                add_issue("NO_ROUTE_INFO", r, t); continue
            if mid and mid.startswith("module_"):
                screens = module_screens.get(mid, {}).get("screens", set())
                if not screens:
                    add_issue("MODULE_HAS_NO_SCREENS", r, t, {"screens_coll": module_screens.get(mid, {}).get("coll")})
                if sid and screens and sid not in screens:
                    sample = sorted(list(screens))[:10]
                    add_issue("SCREEN_NOT_FOUND_IN_MODULE", r, t, {"known_screens_sample": sample})
            else:
                if mid:
                    add_issue("UNKNOWN_MODULE_ID_FORMAT", r, t)

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("reports", exist_ok=True)
    out_json = f"reports/task_route_issues_{stamp}.json"

    print(f"\nModules référencés: {len(module_ids)}")
    for mid in module_ids:
        info = module_screens[mid]
        print(f" - {mid}: {info['count']} écrans dans {info['coll']}")

    print(f"\nIncohérences détectées: {len(issues)}")
    kinds = {}
    for it in issues:
        kinds[it["kind"]] = kinds.get(it["kind"], 0) + 1
    for k, v in sorted(kinds.items(), key=lambda kv: kv[0]):
        print(f" - {k}: {v}")

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(issues, f, ensure_ascii=False, indent=2)
    print(f"\nDétail sauvé dans: {out_json}")

if __name__ == "__main__":
    main()
