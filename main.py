
import os
import re
import asyncio
import threading

from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError


# TELEGRAM API CONFIGURATION
API_ID = 31592332
API_HASH = "09e145b89fcc0e9fb1567bc0933c5854"
PHONE_NUMBER = "+213671369313"
CHANNEL_USERNAME = "binance_red_packetz"

class RedPacketSniper(App):

    def build(self):
        Window.clearcolor = (0.035, 0.035, 0.045, 1)

        self.running = False
        self.authorized = False
        self.client = None
        self.handler = None
        self.phone_code_hash = None
        self.needs_2fa = False

        self.loop = asyncio.new_event_loop()

        self.thread = threading.Thread(
            target=self.run_event_loop,
            daemon=True
        )
        self.thread.start()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
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
            bold=True,
            color=(1, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(45)
        )
        root.add_widget(self.status)

        self.code_input = TextInput(
            hint_text="Telegram login code",
            multiline=False,
            size_hint_y=None,
            height=dp(48)
        )
        root.add_widget(self.code_input)

        self.password_input = TextInput(
            hint_text="2FA password (if required)",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(48)
        )
        root.add_widget(self.password_input)

        self.connect_btn = Button(
            text="CONNECT TELEGRAM / SEND CODE",
            size_hint_y=None,
            height=dp(52),
            background_normal="",
            background_color=(0.12, 0.3, 0.7, 1)
        )
        self.connect_btn.bind(
            on_press=self.connect_telegram
        )
        root.add_widget(self.connect_btn)

        self.verify_btn = Button(
            text="VERIFY LOGIN CODE",
            size_hint_y=None,
            height=dp(52),
            background_normal="",
            background_color=(0.35, 0.3, 0.65, 1)
        )
        self.verify_btn.bind(
            on_press=self.verify_login
        )
        root.add_widget(self.verify_btn)

        self.code_label = Label(
            text="DETECTED CODE: NONE",
            font_size=sp(17),
            bold=True,
            color=(0.2, 1, 0.4, 1),
            size_hint_y=None,
            height=dp(50)
        )
        root.add_widget(self.code_label)

        self.start_btn = Button(
            text="START SCANNING",
            size_hint_y=None,
            height=dp(55),
            background_normal="",
            background_color=(0.05, 0.55, 0.22, 1)
        )
        self.start_btn.bind(
            on_press=self.start_sniper
        )
        root.add_widget(self.start_btn)

        self.stop_btn = Button(
            text="STOP",
            size_hint_y=None,
            height=dp(55),
            background_normal="",
            background_color=(0.75, 0.08, 0.08, 1)
        )
        self.stop_btn.bind(
            on_press=self.stop_sniper
        )
        root.add_widget(self.stop_btn)

        log_title = Label(
            text="ACTIVITY LOG",
            font_size=sp(15),
            bold=True,
            color=(1, 0.25, 0.25, 1),
            size_hint_y=None,
            height=dp(35)
        )
        root.add_widget(log_title)

        scroll = ScrollView()

        self.log_label = Label(
            text="Application initialized.",
            font_size=sp(12),
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

    def run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def add_log(self, message):
        now = datetime.now().strftime("%H:%M:%S")
        self.log_label.text += f"\n[{now}] {message}"

    def update_log_width(self, instance, width):
        instance.text_size = (width, None)

    def update_log_height(self, instance, size):
        instance.height = size[1] + dp(20)

    def set_status(self, message, color):
        self.status.text = message
        self.status.color = color

    def connect_telegram(self, instance):
        asyncio.run_coroutine_threadsafe(
            self.connect_async(),
            self.loop
        )

    async def connect_async(self):
        try:
            if self.client is None:
                session_path = os.path.join(
                    self.user_data_dir,
                    "redpacket_session"
                )

                self.client = TelegramClient(
                    session_path,
                    API_ID,
                    API_HASH
                )

            await self.client.connect()

            if await self.client.is_user_authorized():
                self.authorized = True

                Clock.schedule_once(
                    lambda dt: self.set_status(
                        "STATUS: TELEGRAM CONNECTED",
                        (0.2, 1, 0.3, 1)
                    )
                )

                Clock.schedule_once(
                    lambda dt: self.add_log(
                        "Telegram session restored."
                    )
                )
                return

            sent = await self.client.send_code_request(
                PHONE_NUMBER
            )

            self.phone_code_hash = sent.phone_code_hash

            Clock.schedule_once(
                lambda dt: self.set_status(
                    "STATUS: CODE SENT",
                    (1, 0.8, 0.2, 1)
                )
            )

            Clock.schedule_once(
                lambda dt: self.add_log(
                    "Login code sent. Check Telegram."
                )
            )

        except Exception as e:
            error = str(e)
            Clock.schedule_once(
                lambda dt, msg=error: self.add_log(
                    "Connection error: " + msg
                )
            )

    def verify_login(self, instance):
        code = self.code_input.text.strip()
        password = self.password_input.text

        asyncio.run_coroutine_threadsafe(
            self.verify_async(code, password),
            self.loop
        )

    async def verify_async(self, code, password):
        try:
            if self.client is None:
                raise Exception("Connect to Telegram first.")

            if self.needs_2fa:
                await self.client.sign_in(
                    password=password
                )
            else:
                if not code or not self.phone_code_hash:
                    raise Exception("Enter the login code first.")

                await self.client.sign_in(
                    phone=PHONE_NUMBER,
                    code=code,
                    phone_code_hash=self.phone_code_hash
                )

            self.authorized = True
            self.needs_2fa = False

            Clock.schedule_once(
                lambda dt: self.set_status(
                    "STATUS: TELEGRAM CONNECTED",
                    (0.2, 1, 0.3, 1)
                )
            )

            Clock.schedule_once(
                lambda dt: self.add_log(
                    "Telegram login successful."
                )
            )

        except SessionPasswordNeededError:
            self.needs_2fa = True

            Clock.schedule_once(
                lambda dt: self.add_log(
                    "Two-step verification required. Enter your 2FA password."
                )
            )

        except Exception as e:
            error = str(e)
            Clock.schedule_once(
                lambda dt, msg=error: self.add_log(
                    "Login error: " + msg
                )
            )

    def start_sniper(self, instance):
        asyncio.run_coroutine_threadsafe(
            self.start_async(),
            self.loop
        )

    async def start_async(self):
        try:
            if not self.authorized:
                Clock.schedule_once(
                    lambda dt: self.add_log(
                        "Please connect and login to Telegram first."
                    )
                )
                return

            if self.running:
                return

            async def message_handler(event):
                message = event.raw_text or ""

                if re.fullmatch(r"[A-Z0-9]{8}", message):
                    code = message

                    Clock.schedule_once(
                        lambda dt, value=code: self.found_code(value)
                    )

            self.handler = message_handler

            self.client.add_event_handler(
                self.handler,
                events.NewMessage(chats=CHANNEL_USERNAME)
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
