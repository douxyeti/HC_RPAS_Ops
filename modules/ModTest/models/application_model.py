from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, ListProperty
from .task import Role

class ApplicationModel(EventDispatcher):
    roles = ListProperty([])
    current_role = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_initial_data()

    def load_initial_data(self):
        # Chargement initial depuis Firebase
        self.roles = [Role(id='super_admin', name='Super Admin')]
        self.current_role = self.roles[0] if self.roles else None
