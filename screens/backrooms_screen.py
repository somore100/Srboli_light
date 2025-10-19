# screens/converted/backrooms_screen.py
import os, json
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

# Filenames it will try automatically
POSSIBLE_FILENAMES = ("backrooms_data.json", "backrooms_levels.json")
# File to persist a user-selected JSON path
PATH_SAVE = "backrooms_json_path.txt"

def find_levels_json():
    """Try: saved path -> working dir -> project root -> screens dir."""
    # 1) saved explicit path
    if os.path.exists(PATH_SAVE):
        p = open(PATH_SAVE, encoding="utf-8").read().strip()
        if p and os.path.exists(p):
            return p

    # 2) working dir
    for fn in POSSIBLE_FILENAMES:
        if os.path.exists(fn):
            return os.path.abspath(fn)

    # 3) project root (two levels up)
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    for fn in POSSIBLE_FILENAMES:
        p = os.path.join(base, fn)
        if os.path.exists(p):
            return os.path.abspath(p)

    # 4) same dir as this file
    for fn in POSSIBLE_FILENAMES:
        p = os.path.join(os.path.dirname(__file__), fn)
        if os.path.exists(p):
            return os.path.abspath(p)

    return None

def load_levels_from_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Backrooms JSON load error:", e)
        return {}

class BackroomsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.levels = {}
        self.json_path = None

        root = BoxLayout(orientation="vertical", padding=10, spacing=8)

        # top controls
        top = BoxLayout(size_hint_y=None, height=40, spacing=8)
        self.search_input = TextInput(hint_text="Enter level number or nickname", multiline=False)
        top.add_widget(self.search_input)
        search_btn = Button(text="Search", size_hint_x=None, width=120)
        search_btn.bind(on_release=self.perform_search)
        top.add_widget(search_btn)

        locate_btn = Button(text="Locate JSON", size_hint_x=None, width=140)
        locate_btn.bind(on_release=self.open_file_chooser)
        top.add_widget(locate_btn)

        root.add_widget(top)

        # info area that shows where app looked or saved path
        self.info_label = Label(text="", size_hint_y=None, height=30)
        root.add_widget(self.info_label)

        # scrollable content grid
        sv = ScrollView()
        self.grid = GridLayout(cols=1, spacing=8, size_hint_y=None, padding=(5,5))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        sv.add_widget(self.grid)
        root.add_widget(sv)

        back = Button(text="Back", size_hint_y=None, height=48)
        back.bind(on_release=self.go_back)
        root.add_widget(back)

        self.add_widget(root)

        # try to find and load json
        self.try_load_json()

    def try_load_json(self, force_search=False):
        """Attempt to load levels. If force_search True, ignore saved path and auto-find again."""
        # If user has previously saved a path, prefer it unless force_search True
        if not force_search and os.path.exists(PATH_SAVE):
            p = open(PATH_SAVE, encoding="utf-8").read().strip()
            if p:
                self.json_path = p if os.path.exists(p) else None

        # If no saved/valid path, try autofind
        if not self.json_path:
            self.json_path = find_levels_json()

        # update info label with where it looked
        looked = []
        if os.path.exists(PATH_SAVE):
            saved = open(PATH_SAVE, encoding="utf-8").read().strip()
            looked.append(f"Saved path: {saved}" if saved else "Saved path: <empty>")
        looked.extend([os.path.abspath(p) for p in POSSIBLE_FILENAMES if os.path.exists(p)])
        # Include checks we attempted
        if not looked:
            looked = ["Checked working dir, project root, and screens folder for: " + ", ".join(POSSIBLE_FILENAMES)]

        self.info_label.text = "JSON: " + (self.json_path if self.json_path else "not found — " + "; ".join(looked))

        # load
        if self.json_path and os.path.exists(self.json_path):
            self.levels = load_levels_from_file(self.json_path) or {}
            try:
                # ensure keys are strings
                self.levels = {str(k): v for k, v in self.levels.items()}
            except Exception:
                pass

        # show helpful messaging
        if not self.levels:
            self.grid.clear_widgets()
            self.grid.add_widget(Label(text="Backrooms JSON not found or failed to parse.", size_hint_y=None, height=40))
            self.grid.add_widget(Label(text="Use 'Locate JSON' to point to your file. The app will remember that path.", size_hint_y=None, height=40))
            # show what was tried
            for line in (looked if looked else []):
                self.grid.add_widget(Label(text=line, size_hint_y=None, height=20))
        else:
            # display the first level available
            first_key = next(iter(self.levels))
            self.display_level(self.levels[first_key])

    def open_file_chooser(self, *a):
        chooser = FileChooserIconView(path=".", filters=['*.json'], multiselect=False)
        btn = Button(text="Select", size_hint_y=None, height=40)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(chooser)
        layout.add_widget(btn)
        popup = Popup(title="Locate backrooms .json file", content=layout, size_hint=(0.9, 0.9))
        def _select(inst):
            if chooser.selection:
                chosen = chooser.selection[0]
                if os.path.exists(chosen):
                    # persist choice
                    with open(PATH_SAVE, "w", encoding="utf-8") as f:
                        f.write(os.path.abspath(chosen))
                    self.json_path = os.path.abspath(chosen)
                    popup.dismiss()
                    self.try_load_json()
                else:
                    Popup(title="Error", content=Label(text="File not found."), size_hint=(0.6,0.4)).open()
            else:
                popup.dismiss()
        btn.bind(on_release=_select)
        popup.open()

    def perform_search(self, *a):
        q = self.search_input.text.strip().lower()
        if not q:
            return
        entry = None
        # numeric keys
        if q.isdigit():
            entry = self.levels.get(q)
        if not entry:
            for k, v in self.levels.items():
                nick = str(v.get("nickname", "")).lower()
                if q in nick or q == k:
                    entry = v
                    break
        if not entry:
            self.grid.clear_widgets()
            self.grid.add_widget(Label(text="Not found.", size_hint_y=None, height=30))
            return
        self.display_level(entry)

    def display_level(self, level):
        self.grid.clear_widgets()
        # Title
        title = Label(text=f"[b]{level.get('nickname', 'Unnamed')}[/b]", markup=True, size_hint_y=None)
        title.bind(texture_size=lambda inst, ts: setattr(inst, "height", ts[1]))
        title.text_size = (self.width - 40, None)
        self.grid.add_widget(title)

        # helper to add wrapped labels
        def add_block(text, fixed_height=None):
            lbl = Label(text=text, size_hint_y=None, text_size=(self.width - 40, None), valign='top')
            lbl.bind(texture_size=lambda inst, ts: setattr(inst, "height", ts[1]))
            if fixed_height:
                lbl.height = fixed_height
            self.grid.add_widget(lbl)

        self.grid.add_widget(Label(text=f"Danger: {level.get('danger','Unknown')}", size_hint_y=None, height=24))
        self.grid.add_widget(Label(text=f"Expectation: {level.get('expectation','')}", size_hint_y=None, height=28))

        entities = level.get('entities', [])
        if isinstance(entities, list):
            entities = ", ".join(str(e) for e in entities)
        self.grid.add_widget(Label(text=f"Entities: {entities}", size_hint_y=None, height=28))

        self.grid.add_widget(Label(text="Description:", size_hint_y=None, height=24))
        add_block(level.get('description', ''))

        self.grid.add_widget(Label(text="Tips:", size_hint_y=None, height=24))
        for tip in level.get('tips', []):
            self.grid.add_widget(Label(text=f"- {tip}", size_hint_y=None, height=24))

    def go_back(self, *a):
        if self.manager:
            self.manager.current = "dashboard"

    # swallow right-clicks (avoid ripple artifacts)
    def on_touch_down(self, touch):
        try:
            if hasattr(touch, "button") and touch.button == "right":
                return True
        except Exception:
            pass
        return super().on_touch_down(touch)
