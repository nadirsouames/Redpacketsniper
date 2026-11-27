
from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class RedPacketSniper(App):

    def build(self):

        Window.clearcolor = (0.035, 0.035, 0.045, 1)

        root = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15)
        )

        title = Label(
            text="[b]RED PACKET SNIPER[/b]",
            markup=True,
            font_size=sp(26),
            color=(1, 0.15, 0.15, 1),
            size_hint_y=None,
            height=dp(70)
        )

        root.add_widget(title)

        status = Label(
            text="STATUS: TEST MODE",
            font_size=sp(18),
            color=(0.2, 1, 0.4, 1)
        )

        root.add_widget(status)

        message = Label(
            text="KIVY TEST SUCCESSFUL\n\nApplication is working!",
            font_size=sp(20),
            halign="center"
        )

        root.add_widget(message)

        test_button = Button(
            text="TEST BUTTON",
            size_hint_y=None,
            height=dp(55),
            background_normal="",
            background_color=(0.05, 0.45, 0.75, 1)
        )

        test_button.bind(
            on_press=lambda instance:
            setattr(status, "text", "STATUS: BUTTON WORKING")
        )

        root.add_widget(test_button)

        return root


if __name__ == "__main__":
    RedPacketSniper().run()
lf.set_status(
                    "STATUS: RUNNING",
                    (0.2, 1, 0.3, 1)
                )
            )

            Clock.schedule_once(
                lambda dt: self.add_log(
                    "Monitoring Telegram channel started."
                )
            )

        except Exception as e:
            error = str(e)
            Clock.schedule_once(
                lambda dt, msg=error: self.add_log(
                    "Scanning error: " + msg
                )
            )

    def found_code(self, code):
        try:
            Clipboard.copy(code)

            self.code_label.text = (
                "DETECTED CODE: " + code
            )

            self.add_log(
                "CODE DETECTED AND COPIED: " + code
            )

        except Exception as e:
            self.add_log(
                "Clipboard error: " + str(e)
            )

    def stop_sniper(self, instance):
        asyncio.run_coroutine_threadsafe(
            self.stop_async(),
            self.loop
        )

    async def stop_async(self):
        if self.handler and self.client:
            self.client.remove_event_handler(
                self.handler
            )

            self.handler = None

        self.running = False

        Clock.schedule_once(
            lambda dt: self.set_status(
                "STATUS: STOPPED",
                (1, 0.3, 0.3, 1)
            )
        )

        Clock.schedule_once(
            lambda dt: self.add_log(
                "Monitoring stopped."
            )
        )


if __name__ == "__main__":
    RedPacketSniper().run()
