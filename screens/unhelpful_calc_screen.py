# screens/converted/unhelpful_calc_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import random

fake_errors = [
    "Stnax Error: Unexpected cheese slice.",
    "Error 404: Answer not found.",
    "Fatal Error: You tried to divide by cucumber.",
    "Upgrade to Premium Math to continue.",
    "Your math privileges have expired.",
    "Calculator tired. Try again later.",
    "Illegal equation detected. FBI notified.",
    "Do you even math, bro?",
    "Processor overheated by this equation.",
    "Result classified. Clearance required.",
    "Unexpected Error: Universe not ready.",
    "Nah. I’m good.",
    "LOL. No.",
    "Math not found. Install Linux?",
    "Critical math failure. Report to IT.",
    "Answer lost. Try again in 2042.",
]

class UnhelpfulCalcScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Display label
        self.display = Label(
            text="", font_size=28, size_hint_y=0.2,
            halign="right", valign="center"
        )
        self.display.bind(size=self.display.setter("text_size"))
        root.add_widget(self.display)

        # Buttons layout
        grid = GridLayout(cols=4, spacing=5, size_hint_y=0.7)

        buttons = [
            "7", "8", "9", "÷",
            "4", "5", "6", "×",
            "1", "2", "3", "-",
            "0", ".", "C", "+",
            "="
        ]

        for text in buttons:
            btn = Button(text=text, font_size=24)
            if text == "C":
                btn.bind(on_release=lambda x: self.clear())
            elif text == "=":
                btn.bind(on_release=lambda x: self.prank_result())
            else:
                btn.bind(on_release=lambda x, t=text: self.press(t))
            grid.add_widget(btn)

        root.add_widget(grid)

        # Back button
        back_btn = Button(text="Back", size_hint_y=0.1)
        back_btn.bind(on_release=self.go_back)
        root.add_widget(back_btn)

        self.add_widget(root)

    def press(self, key):
        current = self.display.text
        if current in fake_errors or current == "...":
            self.display.text = ""
        self.display.text += str(key)

    def clear(self, *a):
        self.display.text = ""

    def prank_result(self, *a):
        self.display.text = "..."
        # suspense delay
        Clock.schedule_once(self.display_error, 2)

    def display_error(self, *a):
        self.display.text = random.choice(fake_errors)

    def go_back(self, *a):
        if self.manager:
            self.manager.current = "dashboard"
