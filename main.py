import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class RedPacketSniper(App):
    def build(self):
        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        layout.add_widget(Label(
            text="RED PACKET SNIPER",
            font_size=25
        ))

        layout.add_widget(Label(
            text="Application started successfully!",
            font_size=16
        ))

        return layout

if __name__ == "__main__":
    RedPacketSniper().run()
