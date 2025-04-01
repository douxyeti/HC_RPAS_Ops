"""
Écran principal du module de contrôle des vols.
"""
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from ..viewmodels import ControlVolViewModel

class ControlVolsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = ControlVolViewModel()
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Boutons de contrôle
        btn_nouveau = MDRaisedButton(
            text="Nouveau Vol",
            on_release=self.nouveau_vol
        )
        btn_demarrer = MDRaisedButton(
            text="Démarrer Vol",
            on_release=self.demarrer_vol
        )
        btn_terminer = MDRaisedButton(
            text="Terminer Vol",
            on_release=self.terminer_vol
        )
        
        # Ajout des widgets au layout
        layout.add_widget(btn_nouveau)
        layout.add_widget(btn_demarrer)
        layout.add_widget(btn_terminer)
        
        self.add_widget(layout)
        
    def nouveau_vol(self, instance):
        """Ouvre le dialogue de création d'un nouveau vol."""
        # TODO: Implémenter le dialogue de création
        pass
        
    def demarrer_vol(self, instance):
        """Démarre le vol sélectionné."""
        # TODO: Implémenter la sélection et le démarrage du vol
        pass
        
    def terminer_vol(self, instance):
        """Termine le vol actif."""
        if self.viewmodel.terminer_vol():
            # Mettre à jour l'interface
            pass
