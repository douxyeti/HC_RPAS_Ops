from app.services.firebase_service import FirebaseService
from app.utils.module_discovery import ModuleDiscovery
from app.utils.module_initializer import ModuleInitializer

fs = FirebaseService.get_instance()
md = ModuleDiscovery(fs)
mi = ModuleInitializer()

module_id = 'module_feature_SLASH_invocation-routing'
branch    = mi.current_branch or ''

screens = md.get_module_screens(module_id, branch)
print('get_module_screens ->', len(screens))
for s in (screens or []):
    print('-', s.get('id'), '|', s.get('title'))
