import time
from app.services.firebase_service import FirebaseService
from app.utils.module_discovery import ModuleDiscovery

fs = FirebaseService.get_instance()
md = ModuleDiscovery(fs)

targets = [
    ('module_master', 'master'),
    ('module_RPAS_ops_master', 'RPAS_ops_master'),
]

for module_id, branch in targets:
    coll = f'module_indexes_screens_{module_id}_{md._sanitize_branch_name(branch)}'
    print('TARGET COLL =', coll)
    s = {
        'id': 'dashboardscreen',
        'title': f'Dashboard ({branch})',
        'icon': 'view_dashboard',
        'category': 'system',
        'updated_at': int(time.time())
    }
    fs.set_data_with_id(coll, s['id'], s)
    print('WROTE', coll, s['id'])
