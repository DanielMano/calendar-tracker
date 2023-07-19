from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty


def create_date_picker_popup(self, year: int, month: int) -> Popup:
    start_year = year
    start_month = month

    content = PopupContent(caller=self, month=start_month, year=start_year)
    popup = Popup(
        title="",
        separator_height=0,
        content=content,
        auto_dismiss=True,
        size_hint=(None, None),
        size=(500, 500),
    )
    return popup


def open_callback(self):
    if self.content.reset_year is True:
        self.content.displayed_year = self.content.current_year
    self.content.reset_year = True
    self.content.current_year = self.content.displayed_year


class PopupContent(FloatLayout):
    displayed_year = NumericProperty()

    def __init__(self, caller, month: int, year: int, **kwargs):
        self.caller = caller
        super().__init__(**kwargs)
        self.displayed_year: int = year
        self.current_year: int = year
        self.displayed_month: int = month
        self.reset_year: bool = True

    def popup_dismiss_callback(self):
        self.reset_year = False
        self.caller.dismiss_date_picker_popup(self.displayed_month, self.displayed_year)
