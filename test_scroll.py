from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivy.lang import Builder
from kivy.metrics import dp

KV = '''
<TestCard>:
    size_hint_y: None
    height: "100dp"
    md_bg_color: "blue"
    radius: [8]
    padding: "8dp"

MDScreen:
    MDScrollView:
        size_hint: 1, 1
        scroll_type: ['bars']
        bar_width: "20dp"
        MDBoxLayout:
            id: card_box
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: "8dp"
            padding: ["8dp", "8dp", "28dp", "8dp"]  # gauche, haut, droite, bas
'''

class TestCard(MDCard):
    pass

class TestApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        screen = Builder.load_string(KV)
        # Ajouter 20 cartes pour avoir un long contenu défilant
        for i in range(20):
            card = TestCard()
            screen.ids.card_box.add_widget(card)
        return screen

if __name__ == '__main__':
    TestApp().run()
