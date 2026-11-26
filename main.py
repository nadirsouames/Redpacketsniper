
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.metrics import dp, sp
from datetime import datetime


class RedPacketSniper(App):

    def build(self):
        Window.clearcolor = (0.035, 0.035, 0.045, 1)

        self.running = False

        root = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15)
        )

        # HEADER
        title = Label(
            text="[b]RED PACKET SNIPER[/b]",
            markup=True,
            font_size=sp(27),
            color=(1, 0.15, 0.15, 1),
            size_hint_y=None,
            height=dp(65)
        )
        root.add_widget(title)

        subtitle = Label(
            text="SMART CONTROL PANEL",
            font_size=sp(12),
            color=(0.65, 0.65, 0.7, 1),
            size_hint_y=None,
            height=dp(25)
        )
        root.add_widget(subtitle)

        # STATUS
        self.status = Label(
            text="STATUS: STOPPED",
            font_size=sp(18),
            bold=True,
            color=(1, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(65)
        )
        root.add_widget(self.status)

        # START BUTTON
        self.start_btn = Button(
            text="START",
            font_size=sp(19),
            bold=True,
            color=(1, 1, 1, 1),
            background_normal="",
            background_color=(0.05, 0.55, 0.22, 1),
            size_hint_y=None,
            height=dp(60)
        )
        self.start_btn.bind(on_press=self.start_sniper)
        root.add_widget(self.start_btn)

        # STOP BUTTON
        self.stop_btn = Button(
            text="STOP",
            font_size=sp(19),
            bold=True,
            color=(1, 1, 1, 1),
            background_normal="",
            background_color=(0.75, 0.08, 0.08, 1),
            size_hint_y=None,
            height=dp(60)
        )
        self.stop_btn.bind(on_press=self.stop_sniper)
        root.add_widget(self.stop_btn)

        # LOG TITLE
        log_title = Label(
            text="ACTIVITY LOG",
            font_size=sp(16),
            bold=True,
            color=(1, 0.25, 0.25, 1),
            size_hint_y=None,
            height=dp(40)
        )
        root.add_widget(log_title)

        # LOG AREA
        scroll = ScrollView()

        self.log_label = Label(
            text="Application initialized.",
            font_size=sp(13),
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            halign="left",
            valign="top"
        )

        self.log_label.bind(
            width=self.update_log_width,
            texture_size=self.update_log_height
        )

        scroll.add_widget(self.log_label)
        root.add_widget(scroll)

        self.add_log("RedPacket Sniper ready.")

        return root

    def update_log_width(self, instance, width):
        instance.text_size = (width, None)

    def update_log_height(self, instance, size):
        instance.height = size[1] + dp(20)

    def add_log(self, message):
        now = datetime.now().strftime("%H:%M:%S")
        self.log_label.text += f"\n[{now}] {message}"

    def start_sniper(self, instance):
        if self.running:
            return

        self.running = True
        self.status.text = "STATUS: RUNNING (DEMO)"
        self.status.color = (0.2, 1, 0.3, 1)

        self.add_log("Start button activated.")
        self.add_log("Demo mode only - no packet scanning.")

    def stop_sniper(self, instance):
        self.running = False
        self.status.text = "STATUS: STOPPED"
        self.status.color = (1, 0.3, 0.3, 1)

        self.add_log("Stop button activated.")


if __name__ == "__main__":
    RedPacketSniper().run()
