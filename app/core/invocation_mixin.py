from typing import Any, Dict, Optional
from app.core.invocation import fetch_and_consume_invocation


class InvocationConsumerMixin:
    """
    À mixer dans la classe App/ScreenManager du TEMPLATE.
    Suppose l'existence des attributs/méthodes dans l'héritier:
      - self.root.current : pour changer de route (Kivy)
      - handle_invocation_params(dict) : optionnelle
      - constantes de module: MODULE_NAME (str), ROUTE_ON_INVOCATION (str, optionnelle)
    """

    def _route_switch(self, route: str) -> None:
        try:
            self.root.current = route
        except Exception:
            pass

    def _dispatch_params(self, params: Dict[str, Any]) -> None:
        handler = getattr(self, "handle_invocation_params", None)
        if callable(handler):
            try:
                handler(params)
            except Exception:
                pass

    def consume_invocation_for_self(
        self,
        firebase_service,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Cherche une invocation pour ce module (MODULE_NAME) et l'applique.
        - Route: invoc['route'] OU ROUTE_ON_INVOCATION si définie et que 'route' absent.
        - Params: invoc.get('params', {}), passé à handle_invocation_params si présent.
        Retourne le dict d'invocation si consommé, sinon None.
        """
        module_name = getattr(self, "MODULE_NAME", None)
        if not module_name:
            return None

        invoc = fetch_and_consume_invocation(firebase_service, user_id, module_name)
        if not invoc:
            return None

        route = invoc.get("route") or getattr(self, "ROUTE_ON_INVOCATION", None)
        if route:
            self._route_switch(route)

        params = invoc.get("params") or {}
        if isinstance(params, dict):
            self._dispatch_params(params)

        return invoc
