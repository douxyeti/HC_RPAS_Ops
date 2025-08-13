# app/utils/task_router.py
from typing import Dict, Any, Optional
from app.utils.module_discovery import ModuleDiscovery

# Map des applis → modules (complète si tu en as d'autres)
APP_TO_MODULE = {
    "master": "module_master",
    "RPAS_ops_master": "module_RPAS_ops_master",
    "application_principale_v2": "module_dev_application_principale_v2",
    "UTM_v2": "module_dev_UTM_v2",
}

def resolve_module_id(task: Dict[str, Any]) -> Optional[str]:
    # priorité au module ciblé explicitement
    mid = task.get("target_module_id") or task.get("module_id")
    if mid:
        return mid
    # sinon déduire via application_name
    app_name = task.get("application_name") or task.get("app") or task.get("application")
    if app_name and app_name in APP_TO_MODULE:
        return APP_TO_MODULE[app_name]
    return None

def go_to_task(md: ModuleDiscovery, task: Dict[str, Any], app_instance=None) -> bool:
    module_id = resolve_module_id(task)
    screen_id = (
        task.get("target_screen_id")
        or task.get("screen")
        or task.get("screen_id")
        or "dashboardscreen"
    )
    if not module_id:
        print("[TASK ROUTER] Pas de module_id résolu pour la tâche:", task.get("title") or task.get("id"))
        return False

    ok = md.navigate_to_module_screen(
        app_instance=app_instance,
        module_id=module_id,
        screen_id=screen_id,
        field_id=task.get("target_field_id") or task.get("field_id")
    )
    print(f"[TASK ROUTER] {module_id}.{screen_id} -> {ok}")
    return ok
