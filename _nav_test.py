from app.utils.module_discovery import ModuleDiscovery
from app.services.firebase_service import FirebaseService
from app.utils.module_initializer import ModuleInitializer

fs = FirebaseService.get_instance()
md = ModuleDiscovery(fs)
mi = ModuleInitializer()

module_id = 'module_feature_SLASH_invocation-routing'
ok = md.navigate_to_module_screen(
    app_instance=None,   # remplace par l'instance si tu l'as
    module_id=module_id,
    screen_id='dashboardscreen'
)
print('navigate_to_module_screen ->', ok)
