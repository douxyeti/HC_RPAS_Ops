import pkgutil, importlib, services
print('services path =', list(services.__path__))
mods = [m.name for m in pkgutil.iter_modules(services.__path__) if m.name.startswith('module_')]
print('services.* modules =', mods)
