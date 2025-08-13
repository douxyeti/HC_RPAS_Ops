import pkgutil, importlib
import app.services as srv

mods = [m.name for m in pkgutil.iter_modules(srv.__path__) if m.name.startswith('module_')]
print('services modules =', mods)

for m in mods:
    try:
        mod = importlib.import_module(f'app.services.{m}')
        print(m, 'get_registry =', hasattr(mod, 'get_registry'))
    except Exception as e:
        print(m, 'ERR:', e)
