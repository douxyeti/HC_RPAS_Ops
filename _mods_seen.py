from app.services.firebase_service import FirebaseService
from app.utils.module_discovery import ModuleDiscovery

fs = FirebaseService.get_instance()
md = ModuleDiscovery(fs)

# chez toi la méthode s'appelle ainsi :
mods = md.get_installed_modules() or []
print('INSTALLED MODULES:', len(mods))
for m in mods:
    print('-', m.get('id'), '| branch:', m.get('branch'), '| type:', m.get('type'), '| is_master:', m.get('is_master'))
