# services/__init__.py
import importlib, sys
_pkg = importlib.import_module('app.services')
# ré-export
for k in dir(_pkg):
    if not k.startswith('_'):
        globals()[k] = getattr(_pkg, k)
# partage le chemin pour que les sous-modules résident dans app/services
__path__ = _pkg.__path__
