import traceback
from app.services.firebase_service import FirebaseService
from app.utils.module_initializer import ModuleInitializer
from app.utils.module_discovery import ModuleDiscovery

fs = FirebaseService.get_instance()
print('FirebaseService.get_instance ->', fs)

try:
    mi = ModuleInitializer()
    print('ModuleInitializer instance ->', mi)
    mi.initialize_with_services(fs)
    print('initialize_with_services executed.')
except Exception:
    print('FORCE INDEX ERROR:')
    traceback.print_exc()

try:
    md = ModuleDiscovery(fs)
    branch = getattr(mi, 'current_branch', None)
    print('Current branch (MI) =', branch)
    coll = f'module_indexes_modules_{md._sanitize_branch_name(branch or "")}'
    print('Checking collection:', coll)
    docs = fs.get_collection(coll) or []
    print('Docs count:', len(docs))
    for d in docs:
        print(d)
except Exception:
    traceback.print_exc()
