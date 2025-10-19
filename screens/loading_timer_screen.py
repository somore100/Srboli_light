# screens/converted/loading_screen.py
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle


class LoadingTimerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        # Time inputs (H, M, S)
        time_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=40)
        self.hours_input = TextInput(hint_text="Hours", multiline=False, input_filter="int")
        self.minutes_input = TextInput(hint_text="Minutes", multiline=False, input_filter="int")
        self.seconds_input = TextInput(hint_text="Seconds", multiline=False, input_filter="int")
        time_layout.add_widget(self.hours_input)
        time_layout.add_widget(self.minutes_input)
        time_layout.add_widget(self.seconds_input)
        layout.add_widget(time_layout)

        # Shutdown toggle
        toggle_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=30)
        self.shutdown_checkbox = CheckBox(size_hint=(None, None), size=(25, 25))
        toggle_layout.add_widget(Label(text="Shutdown after completion:", size_hint_x=None, width=220))
        toggle_layout.add_widget(self.shutdown_checkbox)
        layout.add_widget(toggle_layout)

        # Start button
        self.start_btn = Button(text="Start Timer", size_hint_y=None, height=40)
        self.start_btn.bind(on_release=self.start_timer)
        layout.add_widget(self.start_btn)

        # Time remaining label
        self.time_label = Label(text="00:00:00", size_hint_y=None, height=30)
        layout.add_widget(self.time_label)

        # Progress bar area (fixed slim height)
        self.canvas_area = BoxLayout(size_hint_y=None, height=20)
        layout.add_widget(self.canvas_area)

        # Back button
        self.back_btn = Button(text="Back", size_hint_y=None, height=40)
        self.back_btn.bind(on_release=lambda x: setattr(self.manager, "current", "dashboard"))
        layout.add_widget(self.back_btn)

        self.add_widget(layout)

        # Internal state
        self._progress = 0.0
        self._duration = 0
        self._elapsed = 0
        self._event = None

    def start_timer(self, *args):
        # Parse time inputs
        h = int(self.hours_input.text) if self.hours_input.text.isdigit() else 0
        m = int(self.minutes_input.text) if self.minutes_input.text.isdigit() else 0
        s = int(self.seconds_input.text) if self.seconds_input.text.isdigit() else 0
        self._duration = h * 3600 + m * 60 + s

        if self._duration <= 0:
            self.time_label.text = "Invalid time!"
            return

        self._progress = 0.0
        self._elapsed = 0
        if self._event:
            Clock.unschedule(self._event)
        self._event = Clock.schedule_interval(self._update_timer, 0.1)

    def _update_timer(self, dt):
        self._elapsed += dt
        self._progress = min(1.0, self._elapsed / self._duration)
        self._draw_progress()

        remaining = max(0, int(self._duration - self._elapsed))
        h = remaining // 3600
        m = (remaining % 3600) // 60
        s = remaining % 60
        self.time_label.text = f"{h:02d}:{m:02d}:{s:02d}"

        if self._elapsed >= self._duration:
            Clock.unschedule(self._event)
            self._event = None
            if self.shutdown_checkbox.active:
                os.system("shutdown /s /t 1")

    def _draw_progress(self, *a):
        self.canvas_area.canvas.clear()
        with self.canvas_area.canvas:
            w = max(10, self.canvas_area.width - 20)
            h = self.canvas_area.height
            x = self.canvas_area.x + 10
            y = self.canvas_area.y

            # Background
            Color(0.18, 0.18, 0.18)
            Rectangle(pos=(x, y), size=(w, h))

            # Progress bar
            Color(0.12, 0.7, 0.9)
            Rectangle(pos=(x, y), size=(w * self._progress, h))
