# screens/converted/music_screen.py
import os, sys, subprocess
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.clock import Clock
import pygame

AUDIO_EXTS = (".mp3", ".wav", ".ogg", ".flac", ".m4a")


class MusicScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            pygame.mixer.init()
        except Exception:
            pass

        root = BoxLayout(orientation="vertical", padding=8, spacing=8)

        # top: info + autotoggle
        top = BoxLayout(size_hint_y=None, height=40)
        self.info = Label(text="No tracks loaded", size_hint_x=0.7)
        top.add_widget(self.info)
        self.autonext_btn = Button(text="AutoNext: ON", size_hint_x=0.3)
        self.autonext_btn.bind(on_release=self._toggle_autonext)
        top.add_widget(self.autonext_btn)
        root.add_widget(top)

        # big timeline bar (cosmetic but updated to reflect position)
        self.timeline = Slider(min=0, max=1, value=0, size_hint_y=None, height=56)
        root.add_widget(self.timeline)
        self.time_label = Label(text="00:00 / 00:00", size_hint_y=None, height=28)
        root.add_widget(self.time_label)

        # playlist UI
        self.playlist_box = BoxLayout(orientation="vertical", size_hint_y=0.4)
        root.add_widget(self.playlist_box)

        # controls row
        controls = BoxLayout(size_hint_y=None, height=48, spacing=6)
        self.load_btn = Button(text="Load (multi-select)")
        self.play_btn = Button(text="Play")
        self.stop_btn = Button(text="Stop")
        self.prev10_btn = Button(text="-10s")
        self.next10_btn = Button(text="+10s")
        self.prev_btn = Button(text="Prev")
        self.next_btn = Button(text="Next")

        self.load_btn.bind(on_release=self.load_songs)
        self.play_btn.bind(on_release=self.play_current)
        self.stop_btn.bind(on_release=self.stop_music)
        self.prev10_btn.bind(on_release=lambda x: self.seek_relative(-10))
        self.next10_btn.bind(on_release=lambda x: self.seek_relative(10))
        self.prev_btn.bind(on_release=self.prev_track)
        self.next_btn.bind(on_release=self.next_track)

        for w in (self.load_btn, self.play_btn, self.stop_btn,
                  self.prev10_btn, self.next10_btn, self.prev_btn, self.next_btn):
            controls.add_widget(w)

        root.add_widget(controls)

        back = Button(text="Back", size_hint_y=None, height=44)
        back.bind(on_release=lambda x: setattr(self.manager, "current", "dashboard"))
        root.add_widget(back)

        self.add_widget(root)

        # playback state
        self.playlist = []
        self.current_index = None
        self.playing = False
        self.autonext = True
        self.update_ev = None
        self._durations = {}           # cached durations
        self.current_start_pos = 0.0   # absolute start position (seconds) for current play

    # ----- loading & playlist UI -----
    def load_songs(self, *a):
        chooser = FileChooserIconView(path=".", multiselect=True)
        popup_layout = BoxLayout(orientation="vertical")
        popup_layout.add_widget(chooser)
        select_btn = Button(text="Add selected", size_hint_y=None, height=40)
        popup_layout.add_widget(select_btn)
        popup = Popup(title="Select audio files", content=popup_layout, size_hint=(0.9, 0.9))

        def do_add(inst):
            added = 0
            for p in chooser.selection:
                if os.path.isfile(p) and p.lower().endswith(AUDIO_EXTS):
                    if p not in self.playlist:
                        self.playlist.append(p)
                        added += 1
            if added:
                self._refresh_playlist_ui()
            popup.dismiss()

        select_btn.bind(on_release=do_add)
        popup.open()

    def _refresh_playlist_ui(self):
        self.playlist_box.clear_widgets()
        for idx, p in enumerate(self.playlist):
            btn = Button(text=os.path.basename(p), size_hint_y=None, height=40)
            btn.bind(on_release=lambda inst, i=idx: self.select_and_play(i))
            self.playlist_box.add_widget(btn)
        self.info.text = f"{len(self.playlist)} tracks loaded"

    def select_and_play(self, index):
        self.current_index = index
        self.play_current()

    # ----- playback control -----
    def play_current(self, *a):
        if not self.playlist:
            return
        if self.current_index is None:
            self.current_index = 0
        track = self.playlist[self.current_index]
        try:
            # load and play from start
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            self.current_start_pos = 0.0
            self.playing = True
            dur = self._get_duration(track) or 0.0
            self.timeline.max = dur if dur > 0 else 1.0
            self.timeline.value = 0.0
            self.time_label.text = f"0:00 / {self._fmt(dur)}"
        except Exception:
            # fallback to opening externally (won't be tracked)
            try:
                if sys.platform.startswith("win"):
                    os.startfile(track)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", track])
                else:
                    subprocess.Popen(["xdg-open", track])
                self.info.text = f"Opened externally: {os.path.basename(track)}"
                self.playing = True
                self.timeline.max = 1.0
            except Exception as ex:
                self.info.text = f"Play error: {ex}"
                self.playing = False
                return

        if self.update_ev:
            self.update_ev.cancel()
        self.update_ev = Clock.schedule_interval(self._update, 0.5)

    def stop_music(self, *a):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self.playing = False
        if self.update_ev:
            self.update_ev.cancel()
            self.update_ev = None
        self.time_label.text = "Stopped"

    def _update(self, dt):
        # called periodically to update timeline and handle AutoNext
        try:
            busy = pygame.mixer.music.get_busy()
        except Exception:
            busy = False

        # if not busy but we think we are playing => track likely finished
        if self.playing and not busy:
            if self.autonext and self.playlist:
                # advance to next
                if self.current_index is None:
                    self.current_index = 0
                else:
                    self.current_index = (self.current_index + 1) % len(self.playlist)
                self.play_current()
                return
            else:
                self.stop_music()
                return

        # update position using get_pos + current_start_pos
        try:
            pos_ms = pygame.mixer.music.get_pos()
            pos = (pos_ms / 1000.0) if pos_ms >= 0 else 0.0
            absolute = self.current_start_pos + pos
        except Exception:
            absolute = 0.0

        # update timeline safely
        try:
            self.timeline.value = min(absolute, self.timeline.max)
            self.time_label.text = f"{self._fmt(absolute)} / {self._fmt(self.timeline.max)}"
        except Exception:
            pass

    def _get_duration(self, path):
        if path in self._durations:
            return self._durations[path]
        try:
            s = pygame.mixer.Sound(path)
            dur = s.get_length()
            self._durations[path] = dur
            return dur
        except Exception:
            return None

    def _fmt(self, seconds):
        try:
            s = int(seconds or 0)
            m = s // 60
            s = s % 60
            return f"{m}:{s:02d}"
        except Exception:
            return "0:00"

    # ----- seeking & nav -----
    def seek_relative(self, seconds):
        if not self.playlist or self.current_index is None:
            return
        # compute current absolute position as best we can
        try:
            pos_ms = pygame.mixer.music.get_pos()
            pos = (pos_ms / 1000.0) if pos_ms >= 0 else 0.0
        except Exception:
            pos = 0.0
        absolute = self.current_start_pos + pos
        new = max(0.0, absolute + seconds)
        # clamp to length
        if hasattr(self.timeline, "max") and self.timeline.max:
            new = min(new, self.timeline.max - 0.01)

        # attempt to play from new position (best-effort)
        track = self.playlist[self.current_index]
        try:
            pygame.mixer.music.stop()
            # NOTE: pygame.mixer.music.play(start=sec) works for many formats/backends
            pygame.mixer.music.play(start=new)
            self.current_start_pos = new
            self.playing = True
        except Exception:
            # fallback: try reload and play
            try:
                pygame.mixer.music.load(track)
                pygame.mixer.music.play()
                self.current_start_pos = 0.0
            except Exception:
                pass

        # ensure update loop
        if self.update_ev:
            self.update_ev.cancel()
        self.update_ev = Clock.schedule_interval(self._update, 0.5)
        # update UI immediately
        self.timeline.value = new
        self.time_label.text = f"{self._fmt(new)} / {self._fmt(self.timeline.max)}"

    def prev_track(self, *a):
        if not self.playlist:
            return
        if self.current_index is None:
            self.current_index = 0
        else:
            self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_current()

    def next_track(self, *a):
        if not self.playlist:
            return
        if self.current_index is None:
            self.current_index = 0
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_current()

    def _toggle_autonext(self, *a):
        self.autonext = not self.autonext
        self.autonext_btn.text = "AutoNext: ON" if self.autonext else "AutoNext: OFF"

    # keep playing if user leaves the screen
    def on_leave(self, *a):
        pass
