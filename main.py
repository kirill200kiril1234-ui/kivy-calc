# -*- coding: utf-8 -*-
"""
FletCalc Notebook — блокнот записей по машинам.
Красивый современный дизайн: скруглённые карточки, тени, крупный шрифт,
полноэкранный режим на телефоне и планшете.
"""

import json
import os
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.metrics import sp, dp
from kivy.graphics import Color, RoundedRectangle
from kivy.animation import Animation
from kivy.utils import platform
from kivy.clock import Clock

# ---------------------------------------------------------------------------
# Полноэкранный режим на Android (скрываем статус-бар и панель навигации)
# ---------------------------------------------------------------------------
if platform == "android":
    from jnius import autoclass

    def hide_android_bars():
        try:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            View = autoclass("android.view.View")
            activity = PythonActivity.mActivity
            window = activity.getWindow()
            decor_view = window.getDecorView()
            flags = (
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            )
            decor_view.setSystemUiVisibility(flags)
        except Exception as e:
            print("Не удалось скрыть системные панели:", e)
else:
    def hide_android_bars():
        pass


# ---------------------------------------------------------------------------
# Палитра — тёмная, современная, с фиолетово-синим акцентом
# ---------------------------------------------------------------------------
BG_TOP = (0.06, 0.07, 0.12, 1)
BG_COLOR = (0.06, 0.07, 0.11, 1)
CARD_COLOR = (0.12, 0.13, 0.19, 1)
CARD_COLOR_LIGHT = (0.16, 0.17, 0.24, 1)
ACCENT = (0.45, 0.42, 0.98, 1)         # фиолетово-синий
ACCENT_SOFT = (0.30, 0.28, 0.60, 1)
ACCENT_GLOW = (0.55, 0.52, 1.0, 1)
DANGER = (0.90, 0.32, 0.42, 1)
DANGER_SOFT = (0.55, 0.20, 0.28, 1)
TEXT = (0.96, 0.96, 0.98, 1)
SUBTEXT = (0.62, 0.65, 0.75, 1)
DIVIDER = (0.22, 0.23, 0.30, 1)

FONT_TITLE = sp(30)
FONT_BIG = sp(24)
FONT_MED = sp(21)
FONT_SMALL = sp(17)

DATA_FILE = "notes.json"
RADIUS = dp(20)

# Список популярных марок машин для автодополнения при добавлении
CAR_BRANDS = [
    "Opel", "Toyota", "Volkswagen", "BMW", "Mercedes-Benz", "Audi",
    "Ford", "Renault", "Peugeot", "Skoda", "Kia", "Hyundai", "Nissan",
    "Mazda", "Honda", "Chevrolet", "Fiat", "Citroen", "Mitsubishi",
    "Suzuki", "Volvo", "Lexus", "Subaru", "Seat", "Dacia", "Chery",
    "Geely", "Haval", "Lada", "Daewoo", "Jeep", "Land Rover", "Porsche",
    "Mini", "Smart", "Infiniti", "Acura", "Alfa Romeo", "Jaguar",
]


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Переиспользуемые красивые виджеты
# ---------------------------------------------------------------------------
class RoundedBG(BoxLayout):
    """Контейнер со скруглённым цветным фоном."""

    def __init__(self, bg=CARD_COLOR, radius=RADIUS, **kwargs):
        super().__init__(**kwargs)
        self._radius = radius
        with self.canvas.before:
            self._color = Color(*bg)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def set_color(self, rgba):
        self._color.rgba = rgba


class PrettyButton(Button):
    """Кнопка со скруглёнными углами, тенью-подсветкой и лёгкой анимацией нажатия."""

    def __init__(self, bg=ACCENT, bg_soft=ACCENT_SOFT, text_color=TEXT, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = text_color
        self.bold = True
        self.font_size = FONT_MED
        self.size_hint_y = None
        self.height = dp(60)
        self._bg = bg
        self._bg_soft = bg_soft

        with self.canvas.before:
            self._shadow_color = Color(*bg_soft)
            self._shadow = RoundedRectangle(
                pos=(self.x, self.y - dp(3)), size=self.size, radius=[dp(18)]
            )
            self._color = Color(*bg)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
        self.bind(pos=self._update, size=self._update)
        self.bind(on_press=self._on_press, on_release=self._on_release)

    def _update(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._shadow.pos = (self.x, self.y - dp(3))
        self._shadow.size = self.size

    def _on_press(self, *_):
        Animation(size=(self.width * 0.98, self.height * 0.94), duration=0.06).start(self)

    def _on_release(self, *_):
        Animation(size=(self.width / 0.98, self.height / 0.94), duration=0.08).start(self)


class CarChip(PrettyButton):
    """Кнопка-«таблетка» для выбора машины."""

    def __init__(self, name, selected=False, **kwargs):
        bg = ACCENT if selected else CARD_COLOR_LIGHT
        bg_soft = ACCENT_SOFT if selected else CARD_COLOR
        super().__init__(text=name, bg=bg, bg_soft=bg_soft, **kwargs)
        self.size_hint = (None, None)
        self.height = dp(52)
        self.width = max(dp(120), sp(len(name)) * dp(2.4))
        self.font_size = FONT_SMALL
        self.padding = (dp(20), 0)


class NoteCard(RoundedBG):
    """Карточка одной записи."""

    def __init__(self, text, date_str, on_delete, **kwargs):
        super().__init__(bg=CARD_COLOR, radius=RADIUS, orientation="vertical",
                          size_hint_y=None, **kwargs)
        self.padding = dp(20)
        self.spacing = dp(10)

        top_row = BoxLayout(size_hint_y=None, height=dp(28), spacing=dp(8))
        dot = RoundedBG(bg=ACCENT, radius=dp(5), size_hint=(None, None), size=(dp(10), dp(10)))
        dot.pos_hint = {"center_y": 0.5}
        date_label = Label(
            text=date_str,
            font_size=FONT_SMALL,
            color=SUBTEXT,
            size_hint_y=None,
            height=dp(28),
            halign="left",
            valign="middle",
        )
        date_label.bind(size=lambda w, s: setattr(w, "text_size", s))
        top_row.add_widget(dot)
        top_row.add_widget(date_label)

        text_label = Label(
            text=text,
            font_size=FONT_MED,
            color=TEXT,
            size_hint_y=None,
            halign="left",
            valign="top",
            line_height=1.2,
        )
        text_label.bind(
            width=lambda w, wd: setattr(w, "text_size", (wd, None)),
            texture_size=lambda w, ts: setattr(w, "height", ts[1]),
        )

        delete_btn = PrettyButton(
            text="Удалить", bg=DANGER, bg_soft=DANGER_SOFT,
            size_hint_y=None, height=dp(46), font_size=FONT_SMALL,
        )
        delete_btn.bind(on_release=lambda *_: on_delete())

        self.add_widget(top_row)
        self.add_widget(text_label)
        self.add_widget(delete_btn)

        text_label.bind(height=self._recalc_height)
        Clock.schedule_once(lambda *_: self._recalc_height(), 0)

    def _recalc_height(self, *_):
        text_h = dp(0)
        for child in self.children:
            if isinstance(child, Label):
                text_h = child.height
        self.height = dp(20) * 2 + dp(10) * 2 + dp(28) + dp(46) + text_h


# ---------------------------------------------------------------------------
# Приложение
# ---------------------------------------------------------------------------
class NotebookApp(App):
    def build(self):
        self.title = "FletCalc — Блокнот"
        Window.clearcolor = BG_COLOR

        self.data = load_data()
        if not self.data:
            self.data = {"Моя машина": []}
            save_data(self.data)

        self.current_car = list(self.data.keys())[0]

        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(16))

        # ---------- Заголовок ----------
        header = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(12))
        badge = RoundedBG(bg=ACCENT, radius=dp(16), size_hint=(None, None), size=(dp(52), dp(52)))
        badge_label = Label(text="🚗", font_size=sp(26))
        badge.add_widget(badge_label)

        title_box = BoxLayout(orientation="vertical")
        title_label = Label(
            text="Блокнот по машинам",
            font_size=FONT_TITLE,
            bold=True,
            color=TEXT,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(38),
        )
        title_label.bind(size=lambda w, s: setattr(w, "text_size", s))
        subtitle_label = Label(
            text="Записывай всё важное о машине",
            font_size=FONT_SMALL,
            color=SUBTEXT,
            halign="left",
            valign="top",
            size_hint_y=None,
            height=dp(26),
        )
        subtitle_label.bind(size=lambda w, s: setattr(w, "text_size", s))
        title_box.add_widget(title_label)
        title_box.add_widget(subtitle_label)

        header.add_widget(badge)
        header.add_widget(title_box)
        root.add_widget(header)

        # ---------- Разделитель ----------
        divider = RoundedBG(bg=DIVIDER, radius=dp(1), size_hint_y=None, height=dp(2))
        root.add_widget(divider)

        # ---------- Выбор машины (чипы) ----------
        car_label = Label(
            text="Выберите машину",
            font_size=FONT_SMALL,
            color=SUBTEXT,
            bold=True,
            size_hint_y=None,
            height=dp(24),
            halign="left",
        )
        car_label.bind(size=lambda w, s: setattr(w, "text_size", s))
        root.add_widget(car_label)

        car_row_scroll = ScrollView(
            size_hint_y=None, height=dp(64), do_scroll_x=True, do_scroll_y=False,
            bar_width=0,
        )
        self.car_row = BoxLayout(size_hint_x=None, spacing=dp(10), padding=(dp(2), dp(2)))
        self.car_row.bind(minimum_width=self.car_row.setter("width"))
        car_row_scroll.add_widget(self.car_row)
        root.add_widget(car_row_scroll)

        add_car_btn = PrettyButton(
            text="+ Добавить машину", bg=CARD_COLOR_LIGHT, bg_soft=CARD_COLOR,
            font_size=FONT_SMALL, height=dp(50),
        )
        add_car_btn.bind(on_release=self.open_add_car_popup)
        root.add_widget(add_car_btn)

        self._rebuild_car_chips()

        # ---------- Поле ввода записи ----------
        input_card = RoundedBG(bg=CARD_COLOR, radius=RADIUS, orientation="vertical",
                                size_hint_y=None, height=dp(180), padding=dp(4))
        self.note_input = TextInput(
            hint_text="Введите запись о машине...",
            font_size=FONT_MED,
            background_color=(0, 0, 0, 0),
            foreground_color=TEXT,
            hint_text_color=SUBTEXT,
            cursor_color=ACCENT,
            padding=(dp(16), dp(16)),
            multiline=True,
        )
        input_card.add_widget(self.note_input)
        root.add_widget(input_card)

        save_btn = PrettyButton(text="💾  Сохранить запись", bg=ACCENT, bg_soft=ACCENT_SOFT)
        save_btn.bind(on_release=self.save_note)
        root.add_widget(save_btn)

        # ---------- Список записей ----------
        list_title = Label(
            text="История записей",
            font_size=FONT_BIG,
            bold=True,
            color=TEXT,
            size_hint_y=None,
            height=dp(38),
            halign="left",
        )
        list_title.bind(size=lambda w, s: setattr(w, "text_size", s))
        root.add_widget(list_title)

        self.scroll = ScrollView(bar_width=dp(4), bar_color=ACCENT, bar_inactive_color=CARD_COLOR_LIGHT)
        self.notes_box = GridLayout(cols=1, spacing=dp(14), size_hint_y=None, padding=(0, dp(4)))
        self.notes_box.bind(minimum_height=self.notes_box.setter("height"))
        self.scroll.add_widget(self.notes_box)
        root.add_widget(self.scroll)

        self.refresh_notes()

        return root

    def on_start(self):
        hide_android_bars()

    # ------------------------------------------------------------------
    def _rebuild_car_chips(self):
        self.car_row.clear_widgets()
        for name in self.data.keys():
            chip = CarChip(name=name, selected=(name == self.current_car))
            chip.bind(on_release=lambda w, n=name: self.select_car(n))
            self.car_row.add_widget(chip)

    def select_car(self, name):
        self.current_car = name
        self._rebuild_car_chips()
        self.refresh_notes()

    def open_add_car_popup(self, *_):
        overlay = ModalView(size_hint=(0.88, 0.62), background_color=(0, 0, 0, 0.6))
        card = RoundedBG(bg=CARD_COLOR, radius=RADIUS, orientation="vertical",
                          padding=dp(24), spacing=dp(14))

        title = Label(
            text="Новая машина", font_size=FONT_BIG, bold=True, color=TEXT,
            size_hint_y=None, height=dp(36),
        )
        card.add_widget(title)

        input_wrap = RoundedBG(bg=CARD_COLOR_LIGHT, radius=dp(14), size_hint_y=None, height=dp(60))
        input_field = TextInput(
            hint_text="Начните вводить марку...",
            font_size=FONT_MED,
            background_color=(0, 0, 0, 0),
            foreground_color=TEXT,
            hint_text_color=SUBTEXT,
            cursor_color=ACCENT,
            multiline=False,
            padding=(dp(14), dp(16)),
        )
        input_wrap.add_widget(input_field)
        card.add_widget(input_wrap)

        # ---------- Подсказки (автодополнение по марке) ----------
        hint_label = Label(
            text="Подсказки", font_size=FONT_SMALL, color=SUBTEXT, bold=True,
            size_hint_y=None, height=dp(22), halign="left",
        )
        hint_label.bind(size=lambda w, s: setattr(w, "text_size", s))
        card.add_widget(hint_label)

        suggestions_scroll = ScrollView(size_hint_y=1, bar_width=dp(3), bar_color=ACCENT)
        suggestions_box = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=(0, dp(2)))
        suggestions_box.bind(minimum_height=suggestions_box.setter("height"))
        suggestions_scroll.add_widget(suggestions_box)
        card.add_widget(suggestions_scroll)

        def pick_suggestion(name):
            input_field.text = name

        def update_suggestions(*_):
            suggestions_box.clear_widgets()
            query = input_field.text.strip().lower()
            if query:
                matches = [b for b in CAR_BRANDS if b.lower().startswith(query)]
            else:
                matches = CAR_BRANDS
            for brand in matches[:8]:
                item = PrettyButton(
                    text=brand, bg=CARD_COLOR_LIGHT, bg_soft=CARD_COLOR,
                    font_size=FONT_SMALL, size_hint_y=None, height=dp(46),
                )
                item.bind(on_release=lambda w, n=brand: pick_suggestion(n))
                suggestions_box.add_widget(item)
            if not matches:
                no_match = Label(
                    text="Марка не найдена — можно ввести своё название",
                    font_size=FONT_SMALL, color=SUBTEXT,
                    size_hint_y=None, height=dp(46), halign="left",
                )
                no_match.bind(size=lambda w, s: setattr(w, "text_size", s))
                suggestions_box.add_widget(no_match)

        input_field.bind(text=update_suggestions)
        update_suggestions()

        btn_row = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(12))
        cancel_btn = PrettyButton(text="Отмена", bg=CARD_COLOR_LIGHT, bg_soft=CARD_COLOR, height=dp(56))
        ok_btn = PrettyButton(text="Добавить", bg=ACCENT, bg_soft=ACCENT_SOFT, height=dp(56))
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(ok_btn)
        card.add_widget(btn_row)

        overlay.add_widget(card)

        def add_car(*_):
            name = input_field.text.strip()
            if name and name not in self.data:
                self.data[name] = []
                save_data(self.data)
                self.current_car = name
                self._rebuild_car_chips()
                self.refresh_notes()
            overlay.dismiss()

        ok_btn.bind(on_release=add_car)
        cancel_btn.bind(on_release=lambda *_: overlay.dismiss())
        overlay.open()

    def save_note(self, *_):
        text = self.note_input.text.strip()
        if not text:
            return
        date_str = datetime.now().strftime("%d.%m.%Y  %H:%M")
        self.data[self.current_car].insert(0, {"text": text, "date": date_str})
        save_data(self.data)
        self.note_input.text = ""
        self.refresh_notes()

    def refresh_notes(self):
        self.notes_box.clear_widgets()
        notes = self.data.get(self.current_car, [])
        if not notes:
            empty = Label(
                text="Записей пока нет.\nДобавьте первую заметку выше \u2191",
                font_size=FONT_MED,
                color=SUBTEXT,
                size_hint_y=None,
                height=dp(100),
                halign="center",
            )
            empty.bind(size=lambda w, s: setattr(w, "text_size", s))
            self.notes_box.add_widget(empty)
            return

        for i, note in enumerate(notes):
            card = NoteCard(
                text=note["text"],
                date_str=note["date"],
                on_delete=self._make_delete_callback(i),
            )
            self.notes_box.add_widget(card)

    def _make_delete_callback(self, index):
        def callback():
            del self.data[self.current_car][index]
            save_data(self.data)
            self.refresh_notes()
        return callback


if __name__ == "__main__":
    NotebookApp().run()
