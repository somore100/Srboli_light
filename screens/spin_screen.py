# screens/converted/spin_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse, PushMatrix, PopMatrix, Rotate, Triangle
from kivy.clock import Clock
from kivy.animation import Animation
from math import sin, cos, radians
import random


class WheelWidget(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.items = []
        self.rotation_angle = 0.0
        self._rotate = Rotate(angle=0, origin=(self.center_x, self.center_y))
        self.bind(pos=self._update_origin, size=self._update_origin)
        self._label_widgets = []
        self.highlight_index = None

    def _update_origin(self, *a):
        self._rotate.origin = (self.center_x, self.center_y)
        self.redraw()

    def set_items(self, items):
        self.items = [dict(i) for i in items]
        self.redraw()

    def add_item(self, name, weight=1.0):
        if name and name.strip():
            self.items.append({'name': name.strip(), 'weight': float(weight)})
            self.redraw()

    def remove_index(self, idx):
        if 0 <= idx < len(self.items):
            del self.items[idx]
            self.redraw()

    def clear(self):
        self.items = []
        self.redraw()

    def redraw(self):
        self.canvas.clear()
        # remove old labels
        for lbl in self._label_widgets:
            self.remove_widget(lbl)
        self._label_widgets = []

        if not self.items:
            return

        cx, cy = self.center_x, self.center_y
        radius = min(self.width, self.height) * 0.45
        seg_angle = 360.0 / len(self.items)

        with self.canvas:
            # Draw slices
            PushMatrix()
            self.canvas.add(self._rotate)
            for i, it in enumerate(self.items):
                hue = (i / max(1, len(self.items)))
                r = 0.6 + 0.4 * (0.5 + 0.5 * sin(hue * 6.28))
                g = 0.6 + 0.4 * (0.5 + 0.5 * sin((hue + 0.33) * 6.28))
                b = 0.6 + 0.4 * (0.5 + 0.5 * sin((hue + 0.66) * 6.28))
                if self.highlight_index == i:
                    Color(min(r + 0.2, 1), min(g + 0.2, 1), min(b + 0.2, 1), 1)
                else:
                    Color(r, g, b, 1)
                start = i * seg_angle
                Ellipse(pos=(cx - radius, cy - radius), size=(radius * 2, radius * 2),
                        angle_start=start, angle_end=start + seg_angle)
            PopMatrix()

            # Fixed pointer arrow at the top
            Color(1, 0, 0, 1)
            arrow_size = 20
            Triangle(points=[cx - arrow_size, cy + radius + 10,
                             cx + arrow_size, cy + radius + 10,
                             cx, cy + radius + 40])

        # Place labels (also rotated with the wheel)
        for i, it in enumerate(self.items):
            ang = (i + 0.5) * seg_angle  # Remove the rotation_angle from here
            rad = radians(ang)
            lx = cx + (radius * 0.65) * cos(rad) - 40
            ly = cy + (radius * 0.65) * sin(rad) - 12
            lbl = Label(text=it['name'], size_hint=(None, None), size=(80, 24))
            lbl.pos = (lx, ly)
            
            # Apply the same rotation to the label
            with lbl.canvas.before:
                PushMatrix()
                Rotate(angle=-self.rotation_angle, origin=(cx, cy))
            with lbl.canvas.after:
                PopMatrix()
                
            self.add_widget(lbl)
            self._label_widgets.append(lbl)

    def animate_rotation(self, target_degrees, duration=6.0, on_complete=None):
        anim = Animation(rotation_angle=target_degrees, duration=duration, t='out_cubic')

        def _on_progress(animation, widget, progress):
            self._rotate.angle = -self.rotation_angle
            self.redraw()

        def _on_complete(animation, widget):
            if on_complete:
                on_complete()

        anim.bind(on_progress=_on_progress, on_complete=_on_complete)
        anim.start(self)

    def get_selected_index(self):
        if not self.items:
            return None
        eff = (self.rotation_angle % 360.0)
        seg_angle = 360.0 / len(self.items)
        pointer_angle = 90.0
        relative = (pointer_angle - eff) % 360.0
        idx = int(relative // seg_angle)
        return idx % len(self.items)


class SpinScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=8, spacing=8)

        top = BoxLayout(size_hint_y=None, height=36, spacing=6)
        self.name_input = TextInput(hint_text="Name", size_hint_x=0.5, multiline=False)
        self.weight_input = TextInput(hint_text="Weight (1.0)", size_hint_x=0.2, multiline=False, input_filter='float')
        add_btn = Button(text="Add", size_hint_x=0.15)
        add_btn.bind(on_release=self._add_name)
        import_btn = Button(text="Import .txt", size_hint_x=0.15)
        import_btn.bind(on_release=self._import_txt)
        top.add_widget(self.name_input)
        top.add_widget(self.weight_input)
        top.add_widget(add_btn)
        top.add_widget(import_btn)
        root.add_widget(top)

        self.wheel = WheelWidget(size_hint=(1, 0.7))
        root.add_widget(self.wheel)

        # list area
        list_area = BoxLayout(size_hint_y=None, height=160)
        sv = ScrollView()
        self.list_grid = GridLayout(cols=1, spacing=4, size_hint_y=None)
        self.list_grid.bind(minimum_height=self.list_grid.setter('height'))
        sv.add_widget(self.list_grid)
        list_area.add_widget(sv)
        root.add_widget(list_area)

        bottom = BoxLayout(size_hint_y=None, height=56, spacing=8)
        self.spin_btn = Button(text="Spin!")
        self.spin_btn.bind(on_release=self._spin)
        bottom.add_widget(self.spin_btn)
        self.result_label = Label(text="")
        bottom.add_widget(self.result_label)
        root.add_widget(bottom)

        back = Button(text="Back", size_hint_y=None, height=44)
        back.bind(on_release=self._go_back)
        root.add_widget(back)

        self.add_widget(root)
        self._refresh_list_view()

    def _add_name(self, *a):
        name = self.name_input.text.strip()
        weight = 1.0
        try:
            weight = float(self.weight_input.text) if self.weight_input.text.strip() else 1.0
        except Exception:
            weight = 1.0
        if name:
            self.wheel.add_item(name, weight)
            self.name_input.text = ""
            self.weight_input.text = ""
            self._refresh_list_view()

    def _import_txt(self, *a):
        chooser = FileChooserIconView(path=".", filters=['*.txt'], multiselect=False)
        btn = Button(text="Import", size_hint_y=None, height=36)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(chooser)
        layout.add_widget(btn)
        popup = Popup(title="Import names from .txt", content=layout, size_hint=(0.9, 0.9))

        def _do_import(inst):
            if chooser.selection:
                fn = chooser.selection[0]
                try:
                    with open(fn, encoding='utf-8') as f:
                        lines = [l.strip() for l in f.readlines() if l.strip()]
                    for ln in lines:
                        if not any(it['name'] == ln for it in self.wheel.items):
                            self.wheel.add_item(ln, 1.0)
                    self._refresh_list_view()
                except Exception as e:
                    Popup(title="Error", content=Label(text=str(e)), size_hint=(0.6, 0.4)).open()
            popup.dismiss()

        btn.bind(on_release=_do_import)
        popup.open()

    def _refresh_list_view(self):
        self.list_grid.clear_widgets()
        for idx, it in enumerate(self.wheel.items):
            row = BoxLayout(size_hint_y=None, height=30)
            lbl = Label(text=f"{it['name']} (w={it['weight']})", halign='left')
            del_btn = Button(text="Delete", size_hint_x=None, width=80)
            del_btn.bind(on_release=lambda inst, i=idx: self._delete_name(i))
            row.add_widget(lbl)
            row.add_widget(del_btn)
            self.list_grid.add_widget(row)
        self.wheel.set_items(self.wheel.items)

    def _delete_name(self, idx):
        self.wheel.remove_index(idx)
        self._refresh_list_view()

    def _spin(self, *a):
        if not self.wheel.items:
            Popup(title="No names", content=Label(text="Add names first."), size_hint=(0.6, 0.4)).open()
            return

        n = len(self.wheel.items)
        seg = 360.0 / n
        chosen = random.randint(0, n - 1)
        offset_inside = random.uniform(seg * 0.1, seg * 0.9)
        final_relative = (chosen * seg) + offset_inside
        pointer = 90.0
        current = self.wheel.rotation_angle % 360.0
        final_angle = (pointer - final_relative) % 360.0
        full_spins = random.randint(3, 6)
        target_degrees = current + final_angle + 360.0 * full_spins

        def on_complete():
            idx = self.wheel.get_selected_index()
            self.wheel.highlight_index = idx
            self.wheel.redraw()
            chosen_name = self.wheel.items[idx]['name']
            self.result_label.text = f"Selected: {chosen_name}"
            Popup(title="Winner", content=Label(text=chosen_name), size_hint=(0.6, 0.4)).open()

        self.wheel.highlight_index = None
        self.wheel.animate_rotation(target_degrees, duration=6.0 + random.random() * 2, on_complete=on_complete)

    def _go_back(self, *a):
        if self.manager:
            self.manager.current = "dashboard"