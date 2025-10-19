# screens/converted/morse_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

MORSE = {
 'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
 'G': '--.', 'H': '....', 'I': '..', 'J': '.---','K': '-.-', 'L': '.-..',
 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
 'Y': '-.--', 'Z': '--..', '0': '-----','1': '.----','2': '..---',
 '3': '...--','4': '....-','5': '.....','6': '-....','7': '--...',
 '8': '---..','9': '----.',' ': '/'
}
REVERSE = {v:k for k,v in MORSE.items()}

class MorseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=8, spacing=8)
        self.input = TextInput(hint_text="Type text or morse here", size_hint_y=None, height=120)
        root.add_widget(self.input)

        btns = BoxLayout(size_hint_y=None, height=40)
        t2m = Button(text="Text → Morse")
        m2t = Button(text="Morse → Text")
        t2m.bind(on_release=self.text_to_morse)
        m2t.bind(on_release=self.morse_to_text)
        btns.add_widget(t2m)
        btns.add_widget(m2t)
        root.add_widget(btns)

        self.output = Label(text="", size_hint_y=None, height=120)
        root.add_widget(self.output)

        back = Button(text="Back", size_hint_y=None, height=48)
        back.bind(on_release=self.go_back)
        root.add_widget(back)
        self.add_widget(root)

    def text_to_morse(self, *a):
        s = self.input.text.upper()
        out = []
        for ch in s:
            out.append(MORSE.get(ch, '?'))
        self.output.text = ' '.join(out)

    def morse_to_text(self, *a):
        s = self.input.text.strip()
        words = s.split(' / ')
        out_words = []
        for w in words:
            chars = w.split()
            out_words.append(''.join(REVERSE.get(c,'?') for c in chars))
        self.output.text = ' '.join(out_words)

    def go_back(self, *a):
        if self.manager:
            self.manager.current = "dashboard"
