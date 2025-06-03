"""
Écran de tableau de bord des vols pour le module de contrôle opérationnel des vols.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton
from kivymd.uix.card import MDCard
from kivy.metrics import dp

class TableauBordVolsScreen(MDScreen):
    """
    Écran principal du module de contrôle des vols.
    Affiche un tableau de bord avec la liste des vols et une carte.
    """
    
    def __init__(self, **kwargs):
        """Initialise l'écran de tableau de bord des vols"""
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        """Construit l'interface utilisateur de l'écran"""
        # Layout principal
        layout = MDBoxLayout(orientation="vertical", padding=16, spacing=16)
        
        # Titre de l'écran
        title = MDLabel(
            text="Tableau de bord des opérations de vol",
            halign="center",
            font_size="24sp",
            bold=True,
            size_hint_y=None,
            height=dp(60)
        )
        layout.add_widget(title)
        
        # Contenu principal en deux colonnes
        content = MDBoxLayout(orientation="horizontal", spacing=16)
        
        # Colonne gauche (liste des vols)
        left_column = MDBoxLayout(orientation="vertical", spacing=8, size_hint_x=0.4)
        
        # En-tête de la liste des vols
        vols_header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50))
        vols_title = MDLabel(text="Vols planifiés", font_size="18sp", bold=True)
        add_button = MDButton(
            text="Nouveau vol",
            on_release=self.nouveau_vol,
            size_hint=(None, None),
            width=dp(120),
            height=dp(40)
        )
        vols_header.add_widget(vols_title)
        vols_header.add_widget(add_button)
        left_column.add_widget(vols_header)
        
        # Liste des vols (simulée)
        vols_list = MDBoxLayout(orientation="vertical", spacing=8, id="liste_vols")
        self.create_sample_vols(vols_list)
        left_column.add_widget(vols_list)
        
        # Colonne droite (carte)
        right_column = MDBoxLayout(orientation="vertical", spacing=8, size_hint_x=0.6)
        
        # En-tête de la carte
        map_header = MDLabel(text="Carte des opérations", font_size="18sp", bold=True, size_hint_y=None, height=dp(50))
        right_column.add_widget(map_header)
        
        # Carte (simulée)
        map_placeholder = MDCard(
            orientation="vertical",
            padding=16,
            id="carte"
        )
        map_label = MDLabel(
            text="[Emplacement de la carte]",
            halign="center",
            valign="center"
        )
        map_placeholder.add_widget(map_label)
        right_column.add_widget(map_placeholder)
        
        # Ajout des colonnes au contenu
        content.add_widget(left_column)
        content.add_widget(right_column)
        
        # Ajout du contenu au layout principal
        layout.add_widget(content)
        
        # Ajout du layout à l'écran
        self.add_widget(layout)
    
    def create_sample_vols(self, container):
        """Crée des exemples de vols pour démonstration"""
        sample_vols = [
            {"id": "VOL-001", "date": "18-05-2025", "drone": "DJI-001", "pilote": "Jean Dupont", "statut": "Planifié"},
            {"id": "VOL-002", "date": "19-05-2025", "drone": "DJI-002", "pilote": "Marie Martin", "statut": "Planifié"},
            {"id": "VOL-003", "date": "20-05-2025", "drone": "DJI-003", "pilote": "Pierre Durand", "statut": "Planifié"}
        ]
        
        for vol in sample_vols:
            vol_card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(100),
                padding=8,
                spacing=4,
                elevation=1
            )
            
            # Titre du vol
            header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30))
            id_label = MDLabel(text=vol["id"], bold=True)
            status_label = MDLabel(text=vol["statut"], halign="right", size_hint_x=0.3)
            header.add_widget(id_label)
            header.add_widget(status_label)
            vol_card.add_widget(header)
            
            # Détails du vol
            details = MDBoxLayout(orientation="vertical", spacing=2)
            date_label = MDLabel(text=f"Date: {vol['date']}", font_size="12sp")
            drone_label = MDLabel(text=f"Drone: {vol['drone']}", font_size="12sp")
            pilote_label = MDLabel(text=f"Pilote: {vol['pilote']}", font_size="12sp")
            details.add_widget(date_label)
            details.add_widget(drone_label)
            details.add_widget(pilote_label)
            vol_card.add_widget(details)
            
            # Actions
            actions = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30), spacing=8)
            edit_button = MDButton(
                text="Modifier",
                on_release=lambda x, vol_id=vol["id"]: self.modifier_vol(vol_id),
                size_hint=(None, None),
                width=dp(100),
                height=dp(30)
            )
            view_button = MDButton(
                text="Voir",
                on_release=lambda x, vol_id=vol["id"]: self.voir_vol(vol_id),
                size_hint=(None, None),
                width=dp(100),
                height=dp(30)
            )
            actions.add_widget(edit_button)
            actions.add_widget(view_button)
            vol_card.add_widget(actions)
            
            container.add_widget(vol_card)
    
    def nouveau_vol(self, instance):
        """Ouvre l'écran de création d'un nouveau vol"""
        registry = self._get_registry()
        if registry:
            registry.navigate_to_screen("planification_vol", app=self._get_app())
    
    def modifier_vol(self, vol_id):
        """Ouvre l'écran de modification d'un vol existant"""
        registry = self._get_registry()
        if registry:
            registry.navigate_to_screen("planification_vol", app=self._get_app(), vol_id=vol_id)
    
    def voir_vol(self, vol_id):
        """Ouvre l'écran de détails d'un vol"""
        registry = self._get_registry()
        if registry:
            registry.navigate_to_screen("suivi_vol", app=self._get_app(), vol_id=vol_id)
    
    def focus_field(self, field_id):
        """
        Met le focus sur un champ spécifique
        
        Args:
            field_id: Identifiant du champ à mettre en focus
        """
        if field_id == "liste_vols":
            # Logique pour mettre en évidence la liste des vols
            pass
        elif field_id == "carte":
            # Logique pour mettre en évidence la carte
            pass
    
    def _get_registry(self):
        """Récupère l'instance du registre du module"""
        try:
            from services.module_controle_vols import get_registry
            return get_registry()
        except Exception as e:
            print(f"Erreur lors de l'accès au registre: {str(e)}")
            return None
    
    def _get_app(self):
        """Récupère l'instance de l'application en cours"""
        from kivymd.app import MDApp
        return MDApp.get_running_app()
