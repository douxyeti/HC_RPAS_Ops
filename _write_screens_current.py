import time
from app.services.firebase_service import FirebaseService
from app.utils.module_discovery import ModuleDiscovery
from app.utils.module_initializer import ModuleInitializer

fs = FirebaseService.get_instance()
md = ModuleDiscovery(fs)
mi = ModuleInitializer()

module_id = 'module_feature_SLASH_invocation-routing'
branch    = mi.current_branch or ''
coll      = f'module_indexes_screens_{module_id}_{md._sanitize_branch_name(branch)}'
print('TARGET COLL =', coll)

screens = [
    {
        'id': 'dashboardscreen',
        'title': 'Dashboard',
        'icon': 'view_dashboard',
        'category': 'system',
        'updated_at': int(time.time())
    },
    {
        'id': 'modulesadminscreen',
        'title': 'Modules',
        'icon': 'puzzle',
        'category': 'system',
        'updated_at': int(time.time())
    }
]

for s in screens:
    fs.set_data_with_id(coll, s['id'], s)
    print('WROTE', coll, s['id'])

# petit nettoyage de cache côté client
try:
    fs.clear_cache(prefix='module_indexes_screens')
except Exception:
    pass

docs = fs.get_collection(coll) or []
print('VERIFY screens count =', len(docs))
for d in docs: print(d)
