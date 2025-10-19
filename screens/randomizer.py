# screens/converted/utility_tools_screen.py
"""
Combined Utility Tools Screen
Contains: Random Number, Password Generator, List Picker, Weighted Picker, and Size Converter
"""
import os
import random
import string
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.switch import Switch

# Constants
SIMPLE_WORDS = [
    "sun", "moon", "tree", "sky", "water", "fire", "earth", "wind", "rock", "star",
    "cat", "dog", "bird", "fish", "car", "bike", "home", "code", "game", "play",
    "love", "hope", "dream", "goal", "life", "light", "dark", "blue", "red", "fun",
    "cool", "fast", "slow", "big", "small", "new", "old", "hot", "cold", "good"
]

DEFAULT_SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"


class UtilityToolsScreen(Screen):
    """
    Unified utility tools screen with multiple modes:
    - Random Number Generator
    - Password Generator
    - List Picker
    - Weighted Picker
    - Size Converter
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # State variables
        self.silent_mode = True
        self.simple_mode = False
        self.include_letters = True
        self.include_numbers = True
        self.include_symbols = True
        self.include_words = False
        self.items = []
        self.word_list = list(SIMPLE_WORDS)
        
        self.build_ui()
    
    # ==================== UI BUILDING ====================
    
    def build_ui(self):
        """Build the main UI structure"""
        main = BoxLayout(orientation="vertical", padding=8, spacing=8)
        
        # Top control bar
        main.add_widget(self._create_top_bar())
        
        # Center content area (swappable based on mode)
        self.center_box = BoxLayout(orientation="vertical")
        main.add_widget(self.center_box)
        
        # Result display area
        main.add_widget(self._create_result_area())
        
        # Bottom action buttons
        main.add_widget(self._create_bottom_bar())
        
        self.add_widget(main)
        
        # Initialize with first mode
        self._build_number_ui()
    
    def _create_top_bar(self):
        """Create the top control bar with mode selection and settings"""
        top_row = BoxLayout(size_hint_y=None, height=40, spacing=8)
        
        top_row.add_widget(Label(text="Tool:", size_hint_x=None, width=50))
        
        self.mode_spinner = Spinner(
            text="Number",
            values=["Number", "Password", "List Pick", "Weighted Pick", "Size Converter"],
            size_hint_x=0.4
        )
        self.mode_spinner.bind(text=self._on_mode_change)
        top_row.add_widget(self.mode_spinner)
        
        top_row.add_widget(Label(text="Silent:", size_hint_x=None, width=60))
        self.silent_switch = Switch(active=self.silent_mode, size_hint_x=None, width=60)
        self.silent_switch.bind(active=lambda s, v: setattr(self, 'silent_mode', v))
        top_row.add_widget(self.silent_switch)
        
        help_btn = Button(text="?", size_hint_x=None, width=50)
        help_btn.bind(on_release=self._show_help)
        top_row.add_widget(help_btn)
        
        return top_row
    
    def _create_result_area(self):
        """Create the result display area"""
        result_area = BoxLayout(orientation="vertical", size_hint_y=None, height=120, spacing=4)
        result_area.add_widget(Label(text="Result:", size_hint_y=None, height=28))
        self.result_text = TextInput(text="Select a tool and click Generate...", multiline=True, readonly=True)
        result_area.add_widget(self.result_text)
        return result_area
    
    def _create_bottom_bar(self):
        """Create the bottom action button bar"""
        bottom = BoxLayout(size_hint_y=None, height=44, spacing=8)
        
        gen_btn = Button(text="Generate", size_hint_x=0.32)
        gen_btn.bind(on_release=self._generate)
        bottom.add_widget(gen_btn)
        
        copy_btn = Button(text="Copy", size_hint_x=0.2)
        copy_btn.bind(on_release=self._copy_result)
        bottom.add_widget(copy_btn)
        
        back_btn = Button(text="Back", size_hint_x=0.2)
        back_btn.bind(on_release=self._go_back)
        bottom.add_widget(back_btn)
        
        return bottom
    
    # ==================== MODE SWITCHING ====================
    
    def _on_mode_change(self, spinner, text):
        """Handle mode changes"""
        mode_builders = {
            "Number": self._build_number_ui,
            "Password": self._build_password_ui,
            "List Pick": self._build_list_ui,
            "Weighted Pick": self._build_weighted_ui,
            "Size Converter": self._build_size_converter_ui
        }
        
        builder = mode_builders.get(text)
        if builder:
            builder()
    
    def _clear_center(self):
        """Clear the center content area"""
        self.center_box.clear_widgets()
    
    # ==================== NUMBER GENERATOR UI ====================
    
    def _build_number_ui(self):
        """Build UI for random number generator"""
        self._clear_center()
        box = GridLayout(cols=2, size_hint_y=None, height=80, spacing=8, padding=8)
        
        box.add_widget(Label(text="Min:"))
        self.num_min = TextInput(text="1", multiline=False, input_filter="int")
        box.add_widget(self.num_min)
        
        box.add_widget(Label(text="Max:"))
        self.num_max = TextInput(text="100", multiline=False, input_filter="int")
        box.add_widget(self.num_max)
        
        self.center_box.add_widget(box)
    
    def _generate_number(self):
        """Generate a random number"""
        try:
            lo = int(self.num_min.text)
            hi = int(self.num_max.text)
            if lo > hi:
                lo, hi = hi, lo
            return random.randint(lo, hi)
        except:
            return random.randint(1, 100)
    
    # ==================== PASSWORD GENERATOR UI ====================
    
    def _build_password_ui(self):
        """Build UI for password generator"""
        self._clear_center()
        layout = BoxLayout(orientation="vertical", spacing=8, padding=8)
        
        # Length input
        length_box = BoxLayout(size_hint_y=None, height=40, spacing=8)
        length_box.add_widget(Label(text="Length:", size_hint_x=None, width=80))
        self.password_length = TextInput(text="12", multiline=False, input_filter="int")
        length_box.add_widget(self.password_length)
        layout.add_widget(length_box)
        
        # Options grid
        options_grid = GridLayout(cols=2, size_hint_y=None, height=160, spacing=8)
        
        self.letters_cb = CheckBox(active=self.include_letters)
        self.letters_cb.bind(active=lambda c, v: setattr(self, 'include_letters', v))
        options_grid.add_widget(self.letters_cb)
        options_grid.add_widget(Label(text="Letters (a-Z)"))
        
        self.numbers_cb = CheckBox(active=self.include_numbers)
        self.numbers_cb.bind(active=lambda c, v: setattr(self, 'include_numbers', v))
        options_grid.add_widget(self.numbers_cb)
        options_grid.add_widget(Label(text="Numbers (0-9)"))
        
        self.symbols_cb = CheckBox(active=self.include_symbols)
        self.symbols_cb.bind(active=lambda c, v: setattr(self, 'include_symbols', v))
        options_grid.add_widget(self.symbols_cb)
        options_grid.add_widget(Label(text="Symbols (!@#...)"))
        
        self.words_cb = CheckBox(active=self.include_words)
        self.words_cb.bind(active=lambda c, v: setattr(self, 'include_words', v))
        options_grid.add_widget(self.words_cb)
        options_grid.add_widget(Label(text="Use Words"))
        
        self.simple_cb = CheckBox(active=self.simple_mode)
        self.simple_cb.bind(active=lambda c, v: setattr(self, 'simple_mode', v))
        options_grid.add_widget(self.simple_cb)
        options_grid.add_widget(Label(text="Simple Mode"))
        
        layout.add_widget(options_grid)
        
        # Import wordlist button
        import_word_btn = Button(text="Import Custom Wordlist", size_hint_y=None, height=40)
        import_word_btn.bind(on_release=self._import_wordlist)
        layout.add_widget(import_word_btn)
        
        self.center_box.add_widget(layout)
    
    def _generate_password(self):
        """Generate a password based on selected options"""
        try:
            length = int(self.password_length.text)
        except:
            length = 12
        length = max(4, min(length, 200))
        
        charset = ""
        if self.letters_cb.active:
            charset += string.ascii_letters
        if self.numbers_cb.active:
            charset += string.digits
        if self.symbols_cb.active:
            charset += DEFAULT_SYMBOLS
        
        result_parts = []
        
        # Add words if enabled
        if self.words_cb.active and self.word_list:
            word_count = 2 if self.simple_cb.active else 1
            word_count = min(word_count, max(1, length // 6))
            for _ in range(word_count):
                result_parts.append(random.choice(self.word_list))
        
        # Fill remaining with random characters
        while len("".join(result_parts)) < length:
            if charset:
                result_parts.append(random.choice(charset))
            else:
                result_parts.append(random.choice(string.ascii_letters))
        
        random.shuffle(result_parts)
        return "".join(result_parts)[:length]
    
    def _import_wordlist(self, *args):
        """Import custom wordlist from file"""
        chooser = FileChooserIconView(path=".", filters=['*.txt'], multiselect=False)
        btn = Button(text="Import", size_hint_y=None, height=40)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(chooser)
        layout.add_widget(btn)
        popup = Popup(title="Import Wordlist (.txt)", content=layout, size_hint=(0.9, 0.9))
        
        def do_import(inst):
            if chooser.selection:
                try:
                    with open(chooser.selection[0], encoding='utf-8') as f:
                        lines = [l.strip() for l in f.readlines() if l.strip()]
                    if lines:
                        self.word_list = lines
                        if not self.silent_mode:
                            self._show_popup("Success", f"Imported {len(lines)} words")
                except Exception as e:
                    if not self.silent_mode:
                        self._show_popup("Error", str(e))
            popup.dismiss()
        
        btn.bind(on_release=do_import)
        popup.open()
    
    # ==================== LIST PICKER UI ====================
    
    def _build_list_ui(self):
        """Build UI for list picker"""
        self._clear_center()
        layout = BoxLayout(orientation="vertical", spacing=8, padding=8)
        
        # Add/import row
        row = BoxLayout(size_hint_y=None, height=40, spacing=8)
        self.name_input = TextInput(hint_text="Enter item", multiline=False)
        row.add_widget(self.name_input)
        
        add_btn = Button(text="Add", size_hint_x=None, width=80)
        add_btn.bind(on_release=self._add_item)
        row.add_widget(add_btn)
        
        import_btn = Button(text="Import", size_hint_x=None, width=100)
        import_btn.bind(on_release=self._import_list)
        row.add_widget(import_btn)
        layout.add_widget(row)
        
        # List view
        sv = ScrollView(size_hint=(1, 0.6))
        self.list_grid = GridLayout(cols=1, spacing=4, size_hint_y=None)
        self.list_grid.bind(minimum_height=self.list_grid.setter('height'))
        sv.add_widget(self.list_grid)
        layout.add_widget(sv)
        
        # Actions row
        actions = BoxLayout(size_hint_y=None, height=44, spacing=8)
        actions.add_widget(Label(text="Pick count:", size_hint_x=None, width=90))
        self.pick_count = TextInput(text="1", multiline=False, input_filter="int", size_hint_x=None, width=80)
        actions.add_widget(self.pick_count)
        
        clear_btn = Button(text="Clear All", size_hint_x=None, width=100)
        clear_btn.bind(on_release=lambda *a: self._clear_items())
        actions.add_widget(clear_btn)
        layout.add_widget(actions)
        
        self.center_box.add_widget(layout)
        self._refresh_list()
    
    def _add_item(self, *args):
        """Add item to the list"""
        name = self.name_input.text.strip()
        if name and name not in self.items:
            self.items.append(name)
            self.name_input.text = ""
            self._refresh_list()
    
    def _clear_items(self):
        """Clear all items from the list"""
        self.items = []
        self._refresh_list()
    
    def _import_list(self, *args):
        """Import list from text file"""
        chooser = FileChooserIconView(path=".", filters=['*.txt'], multiselect=False)
        btn = Button(text="Import", size_hint_y=None, height=40)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(chooser)
        layout.add_widget(btn)
        popup = Popup(title="Import List from .txt", content=layout, size_hint=(0.9, 0.9))
        
        def do_import(inst):
            if chooser.selection:
                try:
                    with open(chooser.selection[0], encoding='utf-8') as f:
                        lines = [l.strip() for l in f.readlines() if l.strip()]
                    for ln in lines:
                        if ln not in self.items:
                            self.items.append(ln)
                    self._refresh_list()
                except Exception as e:
                    if not self.silent_mode:
                        self._show_popup("Error", str(e))
            popup.dismiss()
        
        btn.bind(on_release=do_import)
        popup.open()
    
    def _refresh_list(self):
        """Refresh the list display"""
        if not hasattr(self, "list_grid"):
            return
        
        self.list_grid.clear_widgets()
        for i, name in enumerate(self.items):
            row = BoxLayout(size_hint_y=None, height=36)
            
            lbl = Label(text=name, halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            row.add_widget(lbl)
            
            del_btn = Button(text="X", size_hint_x=None, width=40)
            del_btn.bind(on_release=lambda inst, idx=i: self._delete_item(idx))
            row.add_widget(del_btn)
            
            self.list_grid.add_widget(row)
    
    def _delete_item(self, idx):
        """Delete item from list by index"""
        if 0 <= idx < len(self.items):
            del self.items[idx]
            self._refresh_list()
    
    def _pick_from_list(self):
        """Pick random item(s) from list"""
        if not self.items:
            return "No items in list"
        
        try:
            count = int(self.pick_count.text)
            count = max(1, min(count, len(self.items)))
            
            if count == 1:
                return random.choice(self.items)
            else:
                chosen = random.sample(self.items, count)
                return ", ".join(chosen)
        except:
            return random.choice(self.items) if self.items else "Error"
    
    # ==================== WEIGHTED PICKER UI ====================
    
    def _build_weighted_ui(self):
        """Build UI for weighted picker"""
        self._clear_center()
        layout = BoxLayout(orientation="vertical", spacing=8, padding=8)
        
        layout.add_widget(Label(
            text="Format: name:weight (one per line, weight defaults to 1)",
            size_hint_y=None, height=30
        ))
        
        self.weighted_area = TextInput(
            text="Alice:2\nBob:1\nCharlie\nDiana:3",
            multiline=True,
            size_hint_y=0.7
        )
        layout.add_widget(self.weighted_area)
        
        self.center_box.add_widget(layout)
    
    def _do_weighted_pick(self):
        """Perform weighted random selection"""
        lines = [l.strip() for l in self.weighted_area.text.splitlines() if l.strip()]
        parsed = []
        
        for ln in lines:
            if ':' in ln:
                name, w = ln.split(':', 1)
                try:
                    weight = float(w.strip())
                except:
                    weight = 1.0
            else:
                name = ln.strip()
                weight = 1.0
            
            if name.strip():
                parsed.append((name.strip(), max(0.0, weight)))
        
        if not parsed:
            return "No valid items"
        
        names = [p[0] for p in parsed]
        weights = [p[1] for p in parsed]
        total = sum(weights)
        
        if total <= 0:
            return random.choice(names)
        
        r = random.random() * total
        acc = 0.0
        for n, w in zip(names, weights):
            acc += w
            if r <= acc:
                return n
        
        return names[-1]
    
    # ==================== SIZE CONVERTER UI ====================
    
    def _build_size_converter_ui(self):
        """Build UI for size converter"""
        self._clear_center()
        layout = BoxLayout(orientation="vertical", spacing=8, padding=8)
        
        layout.add_widget(Label(text="Enter size in bytes:", size_hint_y=None, height=30))
        
        self.size_input = TextInput(
            hint_text="e.g., 1048576",
            multiline=False,
            input_filter="int"
        )
        layout.add_widget(self.size_input)
        
        # Add some example buttons
        examples = BoxLayout(size_hint_y=None, height=40, spacing=4)
        examples.add_widget(Label(text="Quick:", size_hint_x=None, width=60))
        
        for label, value in [("1 KB", "1024"), ("1 MB", "1048576"), ("1 GB", "1073741824")]:
            btn = Button(text=label, size_hint_x=None, width=80)
            btn.bind(on_release=lambda inst, v=value: setattr(self.size_input, 'text', v))
            examples.add_widget(btn)
        
        layout.add_widget(examples)
        
        self.center_box.add_widget(layout)
    
    def _convert_size(self):
        """Convert bytes to various units"""
        try:
            size = int(self.size_input.text)
            kb = size / 1024
            mb = kb / 1024
            gb = mb / 1024
            tb = gb / 1024
            
            return (
                f"Bytes: {size:,}\n"
                f"KB: {kb:.2f}\n"
                f"MB: {mb:.2f}\n"
                f"GB: {gb:.2f}\n"
                f"TB: {tb:.2f}"
            )
        except:
            return "Invalid number - please enter bytes as an integer"
    
    # ==================== MAIN ACTIONS ====================
    
    def _generate(self, *args):
        """Generate result based on current mode"""
        mode = self.mode_spinner.text
        
        try:
            generators = {
                "Number": self._generate_number,
                "Password": self._generate_password,
                "List Pick": self._pick_from_list,
                "Weighted Pick": self._do_weighted_pick,
                "Size Converter": self._convert_size
            }
            
            generator = generators.get(mode)
            if generator:
                result = generator()
                self.result_text.text = str(result)
                
                if not self.silent_mode:
                    self._show_popup("Generated", str(result))
            else:
                self.result_text.text = "Unknown mode"
        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.result_text.text = error_msg
            if not self.silent_mode:
                self._show_popup("Error", error_msg)
    
    def _copy_result(self, *args):
        """Copy result to clipboard"""
        try:
            from kivy.core.clipboard import Clipboard
            text = self.result_text.text.strip()
            if text:
                Clipboard.copy(text)
                if not self.silent_mode:
                    self._show_popup("Copied", "Result copied to clipboard")
        except Exception:
            if not self.silent_mode:
                self._show_popup("Error", "Clipboard not available")
    
    def _show_help(self, *args):
        """Show help information"""
        help_text = (
            "AVAILABLE TOOLS:\n\n"
            "• Number: Generate random integer between min and max\n\n"
            "• Password: Create customizable passwords with letters, "
            "numbers, symbols, and optional words\n\n"
            "• List Pick: Add items and randomly pick one or more\n\n"
            "• Weighted Pick: Enter items with weights (name:weight) "
            "for weighted random selection\n\n"
            "• Size Converter: Convert bytes to KB, MB, GB, TB\n\n"
            "SETTINGS:\n"
            "• Silent Mode: Disable popup notifications\n"
            "• Simple Mode (Password): Prioritize words in passwords"
        )
        
        Popup(title="Help - Utility Tools", content=Label(text=help_text), size_hint=(0.85, 0.8)).open()
    
    def _show_popup(self, title, message):
        """Show a popup message"""
        Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.4)).open()
    
    def _go_back(self, *args):
        """Return to dashboard"""
        if self.manager:
            try:
                self.result_text.text = "Select a tool and click Generate..."
            finally:
                self.manager.current = "dashboard"


# ==================== STANDALONE TEST ====================

if __name__ == "__main__":
    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager
    
    class TestApp(App):
        def build(self):
            sm = ScreenManager()
            sm.add_widget(UtilityToolsScreen(name="utility_tools"))
            return sm
    
    TestApp().run()