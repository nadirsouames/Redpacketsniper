
import os
import re
import asyncio
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError


CHANNEL = "binance_red_packetz"
CODE_PATTERN = re.compile(
    r"^(?=.*[A-Z])(?=.*[0-9])[A-Z0-9]{8}$"
)


class RedPacketSniper(App):

    def build(self):
        Window.clearcolor = (0.035, 0.035, 0.045, 1)

        self.client = None
        self.loop = asyncio.new_event_loop()
        self.phone_code_hash = None
        self.phone = ""
        self.handler = None
        self.running = False

        threading.Thread(
            target=self.run_loop,
            daemon=True
        ).start()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(10)
        )

        title = Label(
            text="[b]RED PACKET SNIPER[/b]",
            markup=True,
            font_size=sp(25),
            color=(1, 0.15, 0.15, 1),
            size_hint_y=None,
            height=dp(55)
        )
        root.add_widget(title)

        self.status = Label(
            text="STATUS: DISCONNECTED",
            font_size=sp(16),
            color=(1, 0.7, 0.2, 1),
            size_hint_y=None,
            height=dp(35)
        )
        root.add_widget(self.status)

        self.api_id = self.add_input(
            root, "Telegram API ID"
        )
        self.api_hash = self.add_input(
            root, "Telegram API HASH"
        )
        self.phone_input = self.add_input(
            root, "Phone number (+213...)"
        )
        self.code_input = self.add_input(
            root, "Telegram login code"
        )
        self.password_input = self.add_input(
            root, "Telegram 2FA password (if needed)"
        )

        self.add_button(
            root, "SEND LOGIN CODE",
            self.send_login_code
        )
        self.add_button(
            root, "VERIFY LOGIN",
            self.verify_login
        )
        self.add_button(
            root, "START MONITORING",
            self.start_sniper
        )
        self.add_button(
            root, "STOP MONITORING",
            self.stop_sniper
        )

        self.code_label = Label(
            text="DETECTED CODE: NONE",
            font_size=sp(19),
            color=(0.2, 1, 0.4, 1),
            size_hint_y=None,
            height=dp(45)
        )
        root.add_widget(self.code_label)

        self.logs = Label(
            text="Ready.",
            font_size=sp(13),
            halign="left",
            valign="top"
        )
        self.logs.bind(
            size=lambda obj, value:
            setattr(obj, "text_size", value)
        )
        root.add_widget(self.logs)

        return root

    def add_input(self, root, hint):
        field = TextInput(
            hint_text=hint,
            multiline=False,
            size_hint_y=None,
            height=dp(48),
            font_size=sp(14),
            padding=dp(10)
        )
        root.add_widget(field)
        return field

    def add_button(self, root, title, callback):
        button = Button(
            text=title,
            size_hint_y=None,
            height=dp(48),
            background_normal="",
            background_color=(0.12, 0.25, 0.42, 1)
        )
        button.bind(on_press=callback)
        root.add_widget(button)

    def run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def set_status(self, message, color):
        self.status.text = message
        self.status.color = color

    def add_log(self, message):
        self.logs.text = message + "\n" + self.logs.text
        self.logs.text = self.logs.text[:2500]

    def submit(self, coroutine):
        asyncio.run_coroutine_threadsafe(
            coroutine, self.loop
        )

    def send_login_code(self, instance):
        self.submit(self.login_request())

    async def login_request(self):
        try:
            api_id = int(self.api_id.text.strip())
            api_hash = self.api_hash.text.strip()
            self.phone = self.phone_input.text.strip()

            if not api_hash or not self.phone:
                raise ValueError(
                    "Enter API HASH and phone number."
                )

            if self.client:
                await self.client.disconnect()

            session = os.path.join(
                self.user_data_dir, "redpacket_session"
            )

            self.client = TelegramClient(
                session, api_id, api_hash
            )

            await self.client.connect()

            if await self.client.is_user_authorized():
                Clock.schedule_once(
                    lambda dt: self.set_status(
                        "STATUS: TELEGRAM CONNECTED",
                        (0.2, 1, 0.4, 1)
                    )
                )
                Clock.schedule_once(
                    lambda dt: self.add_log(
                        "Existing Telegram session found."
                    )
                )
                return

            result = await self.client.send_code_request(
                self.phone
            )
            self.phone_code_hash = result.phone_code_hash

            Clock.schedule_once(
                lambda dt: self.add_log(
                    "Login code sent to Telegram."
                )
            )
            Clock.schedule_once(
                lambda dt: self.set_status(
                    "STATUS: CODE SENT",
                    (1, 0.8, 0.2, 1)
                )
            )

        except Exception as e:
            self.report_error(e)

    def verify_login(self, instance):
        self.submit(self.login_verify())

    async def login_verify(self):
        try:
            if not self.client:
                raise ValueError(
                    "Send login code first."
                )

            code = self.code_input.text.strip()

            if not code:
                raise ValueError("Enter login code.")

            try:
                await self.client.sign_in(
                    self.phone,
                    code,
                    phone_code_hash=self.phone_code_hash
                )

            except SessionPasswordNeededError:
                password = self.password_input.text

                if not password:
                    raise ValueError(
                        "Enter your Telegram 2FA password."
                    )

                await self.client.sign_in(
                    password=password
                )

            Clock.schedule_once(
                lambda dt: self.set_status(
                    "STATUS: TELEGRAM CONNECTED",
                    (0.2, 1, 0.4, 1)
                )
            )
            Clock.schedule_once(
                lambda dt: self.add_log(
                    "Telegram login successful."
                )
            )

        except Exception as e:
            self.report_error(e)

    def start_sniper(self, instance):
        self.submit(self.start_async())

    async def start_async(self):
        try:
            if not self.client:
                raise ValueError("Login to Telegram first.")

            if not await self.client.is_user_authorized():
                raise ValueError("Telegram is not authorized.")

            if self.running:
                return

            async def handle_message(event):
                message = (event.raw_text or "").strip()

                if CODE_PATTERN.fullmatch(message):
                    Clock.schedule_once(
                        lambda dt, code=message:
                        self.found_code(code)
                    )

            self.handler = handle_message

            self.client.add_event_handler(
                self.handler,
                events.NewMessage(chats=CHANNEL)
            )

            self.running = True

            Clock.schedule_once(
                lambda dt: self.set_status(
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
            self.report_error(e)

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
        if self.client:
            self.submit(self.stop_async())

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

    def report_error(self, error):
        message = str(error)

        Clock.schedule_once(
            lambda dt, msg=message:
            self.add_log("ERROR: " + msg)
        )
        Clock.schedule_once(
            lambda dt: self.set_status(
                "STATUS: ERROR",
                (1, 0.2, 0.2, 1)
            )
        )

    def on_stop(self):
        if self.client:
            asyncio.run_coroutine_threadsafe(
                self.client.disconnect(),
                self.loop
            )


if __name__ == "__main__":
    RedPacketSniper().run()
