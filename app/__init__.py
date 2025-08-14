# app/__init__.py
try:
    from .services import firebase_branchless_shim  # noqa: F401
except Exception:
    # On évite de bloquer l'app si jamais le import échoue
    pass

from .services import module_picker_filter_shim  # noqa: F401
