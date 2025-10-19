# main.py — Srboli Light
import os
import sys
from kivy.config import Config

# Disable red right-click dots (multitouch emulation)
Config.set("input", "mouse", "mouse,disable_multitouch")

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.metrics import dp

# Soft blue background
Window.clearcolor = (0.12, 0.16, 0.22, 1)

# Mobile optimizations
if sys.platform in ('android', 'ios'):
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

# --- Safe import function ---
def try_import(module_path, class_name):
    try:
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)
    except Exception as e:
        print(f"⚠️ Could not import {module_path}.{class_name}: {e}")

        class Placeholder(Screen):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                box = BoxLayout(orientation="vertical", padding=20, spacing=10)
                box.add_widget(Label(text=f"[b]{class_name}[/b]\n(Not found or failed to load)", markup=True))
                btn = Button(text="← Back", size_hint_y=None, height=dp(48))
                btn.bind(on_release=lambda *a: setattr(self.manager, "current", "dashboard"))
                box.add_widget(btn)
                self.add_widget(box)

        return Placeholder


# ✅ FIXED: Proper mapping of module -> class -> screen_name
screen_specs = {
    "screens.backrooms_screen": ("BackroomsScreen", "backrooms"),
    "screens.loading_timer_screen": ("LoadingTimerScreen", "loading_timer"),
    "screens.morse_screen": ("MorseScreen", "morse"),
    "screens.music_screen": ("MusicScreen", "music"),
    "screens.randomizer": ("UtilityToolsScreen", "randomizer"),
    "screens.spin_screen": ("SpinScreen", "spin"),
    "screens.unhelpful_calc_screen": ("UnhelpfulCalcScreen", "unhelpful_calc"),
}


# Dynamically import screens
screen_classes = {}
for mod, (cls_name, screen_name) in screen_specs.items():
    cls = try_import(mod, cls_name)
    screen_classes[screen_name] = cls


# --- Dashboard screen ---
class Dashboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=12, spacing=12)

        title = Label(
            text="[b]Srboli Light[/b]",
            markup=True,
            font_size=32,
            size_hint_y=None,
            height=dp(60),
            color=(0.8, 0.9, 1, 1)
        )
        layout.add_widget(title)

        sv = ScrollView()
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=(8, 8))
        grid.bind(minimum_height=grid.setter("height"))

        def add_btn(text, screen_name):
            b = Button(
                text=text,
                size_hint_y=None,
                height=dp(50),
                background_color=(0.2, 0.4, 0.7, 1),
                color=(1, 1, 1, 1),
            )
            b.bind(on_release=lambda *a: setattr(self.manager, "current", screen_name))
            grid.add_widget(b)

        add_btn("Backrooms Guide", "backrooms")
        add_btn("Loading / Timer", "loading_timer")
        add_btn("Morse Converter", "morse")
        add_btn("Music Player", "music")
        add_btn("Randomizer Tools", "randomizer")
        add_btn("Wheel of Names", "spin")
        add_btn("Unhelpful Calculator", "unhelpful_calc")

        sv.add_widget(grid)
        layout.add_widget(sv)

        layout.add_widget(Label(text="by domore100", size_hint_y=None, height=dp(24)))
        self.add_widget(layout)


# --- Base mixin for screens with back button ---
class ScreenWithBack(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not any(isinstance(w, Button) and w.text == "← Back" for w in self.walk()):
            back_btn = Button(
                text="← Back",
                size_hint_y=None,
                height=dp(48),
                background_color=(0.2, 0.4, 0.7, 1),
                color=(1, 1, 1, 1),
            )
            back_btn.bind(on_release=lambda *a: setattr(self.manager, "current", "dashboard"))
            self.add_widget(back_btn)


# --- Main App ---
class SrboliLightApp(App):
    def build(self):
        self.title = "Srboli Light"
        sm = ScreenManager()

        sm.add_widget(Dashboard(name="dashboard"))

        # ✅ FIXED: Use the correct screen names from screen_classes
        for screen_name, cls in screen_classes.items():
            try:
                sm.add_widget(cls(name=screen_name))
                print(f"✅ Loaded screen: {screen_name}")
            except Exception as e:
                print(f"⚠️ Failed to init {screen_name}: {e}")

        sm.current = "dashboard"
        return sm


if __name__ == "__main__":
    SrboliLightApp().run()