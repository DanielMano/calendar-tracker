from __future__ import annotations
from kivy.config import Config

Config.set("graphics", "width", "500")
Config.set("graphics", "height", "1000")

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import (
    ObjectProperty,
    StringProperty,
    ColorProperty,
    BooleanProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

import calendar_data
import database
import date_picker_popup as dpp
import day_event_manager_popup as manager_popup

# from timeit import default_timer as timer

__version__ = "0.3.26.1"


class RootManager(BoxLayout):
    screen_manager: ScreenManager = ObjectProperty(None)
    header_date = StringProperty()
    footer_title = StringProperty("lower layout title")
    picker_popup: Popup = None
    event_manager_popup: manager_popup.EventManagerPopup = None
    selected_day: DayTile = None
    all_events: list = []
    all_events_with_ids_dict: dict = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        (
            self.today,
            self.active_year,
            self.active_month,
            self.active_day,
        ) = calendar_data.get_today()
        self.month_names = calendar_data.get_month_names()

        self.all_events_with_ids = database.get_events(conn)
        for event_id, name, hexcode in self.all_events_with_ids:
            self.all_events_with_ids_dict[(name, hexcode)] = event_id

        for _, name, hexcode in self.all_events_with_ids:
            self.all_events.append((name, hexcode))

        self.create_month_screen()

    def prev_year(self):
        self.active_year -= 1
        self.screen_manager.transition.direction = "right"
        self.create_month_screen()

    def prev_month(self):
        self.active_month -= 1
        self.screen_manager.transition.direction = "right"
        self.create_month_screen()

    def next_month(self):
        self.active_month += 1
        self.screen_manager.transition.direction = "left"
        self.create_month_screen()

    def next_year(self):
        self.active_year += 1
        self.screen_manager.transition.direction = "left"
        self.create_month_screen()

    def open_picker_popup(self):
        if self.picker_popup is None:
            self.picker_popup = dpp.create_date_picker_popup(
                self,
                int(self.active_year),
                calendar_data.month_name_to_num.get(self.active_month),
            )

        content = self.picker_popup.content
        if content.reset_year is True:
            content.displayed_year = content.current_year
        content.reset_year = True
        content.current_year = content.displayed_year

        self.picker_popup.open()

    def dismiss_date_picker_popup(self, new_month: int, new_year: int):
        if new_year > self.active_year:
            self.screen_manager.transition.direction = "left"
        elif new_year < self.active_year:
            self.screen_manager.transition.direction = "right"
        elif new_month < self.active_month:
            self.screen_manager.transition.direction = "right"
        else:
            self.screen_manager.transition.direction = "left"
        self.picker_popup.dismiss()
        self.active_month = new_month
        self.active_year = new_year
        self.create_month_screen()

    def create_month_screen(self, new_month: int = None, new_year: int = None):
        # FIXME might just remove these arguments, not used yet
        if new_month is not None:
            self.active_month = new_month
        if new_year is not None:
            self.active_year = new_year

        # If month is December or January, loop month and inc/dec year
        if self.active_month == 13:
            self.active_month = 1
            self.active_year += 1
        elif self.active_month == 0:
            self.active_month = 12
            self.active_year -= 1

        # Set the name of the new screen
        active_name = f"{self.month_names[self.active_month]} {self.active_year}"

        # If a screen with this name doesn't exist, create it
        if not self.screen_manager.has_screen(active_name):
            scr = CalendarScreen(name=active_name, screen_manager=self)

            # Update header_date to display current month
            self.header_date = active_name

            # Get list of lists where each list is a week starting at sunday
            # isolate first week and last week to replace 0 with correct day
            # from either previous or next month
            f_week, *regular_weeks, l_week = calendar_data.get_days_of_month_of_year(
                self.active_year, self.active_month
            )
            prev_month, next_month = calendar_data.get_adj_months(
                self.active_year, self.active_month
            )

            # For 1st week if day = 0, replace it with correct day from previous month
            for day, prev_month_day in zip(
                f_week, calendar_data.get_last_week(*prev_month)
            ):
                if day == 0:
                    btn = self.add_day(prev_month_day, prev_month, scr)
                else:
                    btn = self.add_day(day, screen=scr)
                scr.ids.grid.add_widget(btn)
            # These days will never be 0, so create as normal
            for week in regular_weeks:
                for day in week:
                    btn = self.add_day(day, screen=scr)
                    scr.ids.grid.add_widget(btn)
            # For last week, if day is 0, replace with correct day from next month
            for day, next_month_day in zip(
                l_week, calendar_data.get_first_week(*next_month)
            ):
                if day == 0:
                    btn = self.add_day(next_month_day, next_month, scr)
                else:
                    btn = self.add_day(day, screen=scr)
                scr.ids.grid.add_widget(btn)

            self.screen_manager.add_widget(scr)

        # Switch to the new screen
        self.screen_manager.current = active_name

    def set_selected_day(self, day_tile: DayTile):
        # TODO this is called 3 times at start of app and twice when switching to a new screen
        if self.selected_day is not None:
            self.selected_day.line_color = [0, 0, 0, 0]
        self.selected_day = day_tile
        day_tile.line_color = [1, 1, 1, 1]

        # set lower layout header to be in format (monthname day, year)
        year, month, day = day_tile.date_str.split("-")
        self.footer_title = (
            self.month_names[int(month)] + " " + str(int(day)) + ", " + year
        )

        # clear lower layout, replace with events for new selected day
        self.ids.lower_grid.clear_widgets()
        for event, _ in day_tile.events:
            self.ids.lower_grid.add_widget(Label(text=event))

    def set_lower_layout(self, instance):
        self.ids.lower_grid.clear_widgets()
        for event, _ in self.selected_day.events:
            self.ids.lower_grid.add_widget(Label(text=event))
        self.set_day_tile_event_colors()

    def add_day(
        self,
        day: str,
        calendar_month: tuple[str, str] = None,
        screen: CalendarScreen = None,
    ) -> DayTile:
        day_tile = DayTile()

        # Use correct month and year for
        if calendar_month is None:
            calendar_month = self.active_year, self.active_month
            day_tile.text_color = MDApp.get_running_app().theme_cls.primary_color

        day_tile.date_str = f"{calendar_month[0]}-{calendar_month[1]:02d}-{day:02d}"
        day_tile.set_day()

        day_tile.ids.tile.bind(
            on_release=lambda instance: day_tile.on_click(instance, self)
        )

        day_tile.events = database.get_events_name_hexcode_by_day(
            conn, day_tile.date_str
        )
        # add colors to day_tile to signal specific event
        # if there are 8 or more events, replace the 8th with a '+' and dont display any more
        # this is to prevent clutter
        for *_, hexcode in day_tile.events:
            if len(day_tile.ids.grid.children) < 7:
                day_tile.ids.grid.add_widget(
                    DayTileEvent(md_bg_color=self.hex_to_rgba(hexcode))
                )
            else:
                more = DayTileEvent(line_color=[0, 0, 0, 0])
                more.add_widget(Label(text="+"))
                day_tile.ids.grid.add_widget(more)
                break

        # find the first of the month, save ref and highlight it as the selected day
        if screen.highlighted_day is None and day_tile.day_num == "1":
            screen.highlighted_day = day_tile
            self.set_selected_day(day_tile)

        # if todays date is in the month, replace it as the selected day instead of the first
        if day_tile.date_str == str(self.today):
            screen.highlighted_day = day_tile
            day_tile.text_color = MDApp.get_running_app().theme_cls.accent_color
            day_tile.underline = True
            self.set_selected_day(day_tile)

        return day_tile

    def set_day_tile_event_colors(self, day_tile: DayTile = None):
        if day_tile is None:
            day_tile = self.selected_day

        # clear existing colors
        day_tile.ids.grid.clear_widgets()
        # add colors to day_tile to signal specific event
        # if there are 8 or more events, replace the 8th with a '+' and dont display any more
        # this is to prevent clutter
        for *_, hexcode in day_tile.events:
            if len(day_tile.ids.grid.children) < 7:
                day_tile.ids.grid.add_widget(
                    DayTileEvent(md_bg_color=self.hex_to_rgba(hexcode))
                )
            else:
                more = DayTileEvent(line_color=[0, 0, 0, 0])
                more.add_widget(Label(text="+"))
                day_tile.ids.grid.add_widget(more)
                break

    def add_events_to_selected_day(self):
        self.event_manager_popup = (
            manager_popup.EventManagerPopup(self.all_events, self.selected_day)
            if self.event_manager_popup is None
            else self.event_manager_popup
        )
        self.event_manager_popup.bind(on_dismiss=self.set_lower_layout)
        self.event_manager_popup.update_and_open(self.selected_day)

    def hex_to_rgba(self, hexcode):
        """Convert hexcode color to rgba tuple

        Args:
            hexcode (str): hexcode either with or without leading '#'

        Returns:
            rgba: tuple containing rgba values, a is always 1.0
        """
        hexcode = hexcode.lstrip("#")
        lv = len(hexcode)
        rgba = tuple(
            j / 255
            for j in tuple(
                int(hexcode[i : i + lv // 3], 16) for i in range(0, lv, lv // 3)
            )
        ) + (1.0,)
        return rgba


class CalendarScreen(Screen):
    screen_manager: RootManager = ObjectProperty(None)
    highlighted_day: DayTile = None

    def on_pre_enter(self, *args):
        self.screen_manager.set_selected_day(self.highlighted_day)
        return super().on_pre_enter(*args)

    def on_enter(self, *args):
        # print("on_enter:", self.name)
        # date_test = self.screen_manager.today
        # TODO replace keeping track of the active date using ints to using a datetime.date object
        # for entire app, apparently not supposed to use strings and int for keeping track of date
        # can use replace or import relativedelta from datetime, relativedelta might be better
        # print(date_test)
        # date_test = date_test.replace(year=date_test.year + 1)
        # print(date_test)
        return super().on_enter(*args)


class DayTile(MDFloatLayout):
    date_str: str = None
    day_num = StringProperty()
    line_color = ColorProperty([0, 0, 0, 0])
    text_color = ColorProperty([0.5, 0.5, 0.5, 1])
    underline = BooleanProperty(False)
    events: list = None

    def set_day(self):
        # converting into an int strips the leading zero, then convert back to a string
        self.day_num = str(int(self.date_str.split("-")[2]))

    def on_click(self, _, caller: RootManager):
        caller.set_selected_day(self)

    def add_event_to_db(self, event):
        database.create_date(
            conn, (self.date_str, RootManager.all_events_with_ids_dict[event])
        )

    def remove_event_from_db(self, event):
        database.delete_event_from_day_by_event_id(
            conn, self.date_str, RootManager.all_events_with_ids_dict[event]
        )


class DayTileEvent(MDBoxLayout):
    pass


class CalendarTrackerApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        return RootManager()


if __name__ == "__main__":
    conn = database.create_connection("database.db")
    CalendarTrackerApp().run()

'''from kivy.config import Config

Config.set("graphics", "width", "500")
Config.set("graphics", "height", "1000")
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import ListProperty

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel

import calendar_data
import database
import update_events_dialog as update_dialog
import date_picker_popup as dpp

from multipledispatch import dispatch

__version__ = "0.3.26.1"


class CalendarScreen(Screen):
    selected_day = None
    dialog_dict = {}
    custompopup: Popup = None

    def open_date_picker_popup(self):
        screen_year, screen_month = self.name.split("-")
        if self.custompopup is None:
            self.custompopup = dpp.create_date_picker_popup(
                self,
                int(screen_year),
                calendar_data.month_name_to_num.get(screen_month),
            )

        self.custompopup.open()

    def dismiss_date_picker_popup(self, new_month: int, new_year: int):
        if new_year > cal_app.sm.active_year:
            cal_app.sm.transition.direction = "left"
        if new_year < cal_app.sm.active_year:
            cal_app.sm.transition.direction = "right"
        self.custompopup.dismiss()
        cal_app.sm.active_month = new_month
        cal_app.sm.active_year = new_year
        cal_app.sm.create_month_screen()

    def prev_month(self):
        cal_app.sm.prev_month()

    def next_month(self):
        cal_app.sm.next_month()

    def my_callback(self, instance):
        self.update_lower_layout()
        self.selected_day.update_icons()

    def get_selected(self):
        # print("screen:", self, "selected_day:", self.selected_day, "-->", self.selected_day.ids.day_tile.text, "-->", self.selected_day.day_string)
        if not self.dialog_dict.get(self.selected_day.day_string):
            self.dialog_dict[
                self.selected_day.day_string
            ] = update_dialog.create_update_events_dialog(
                self, conn, self.selected_day.day_string
            )
        selected_dialog = self.dialog_dict.get(self.selected_day.day_string)
        selected_dialog.bind(on_dismiss=self.my_callback)

        selected_dialog.open()

    def day_press(self, instance, day_string):
        # print("self:", self, "instance:", instance, "instance.parent:", instance.parent, "day_string:", day_string)
        self.ids.scroll_grid.clear_widgets()
        self.selected_day.ids.day_tile.line_color = [0, 0, 0, 0]
        instance.line_color = cal_app.theme_cls.primary_light
        self.selected_day = instance.parent

        self.update_lower_layout()

    def update_lower_layout(self):
        self.ids.scroll_grid.clear_widgets()
        y, m, d = self.selected_day.day_string.split("-")
        self.ids.ll_title.text = f"{cal_app.sm.month_names[int(m)]} {d}, {y}"
        event_names = database.get_event_names_by_day(
            conn, self.selected_day.day_string
        )
        for (name,) in event_names:
            lllabel = LowerLayoutLabel(text=name)
            lllabel.font_size = "32sp"
            lllabel.font_name = "fonts/nasalization-free.rg-regular.otf"
            self.ids.scroll_grid.add_widget(lllabel)


class ScreenManager(ScreenManager):
    def init_data(self):
        # YYYY, M where [1-12], D
        self.today = calendar_data.get_today_date_string()
        self.active_year, self.active_month, self.active_day = self.today
        # List of month names where 0 = '', 1 = 'January', and 12 = 'December'
        self.month_names = calendar_data.get_month_names()

    def prev_month(self):
        cal_app.sm.active_month -= 1
        cal_app.sm.transition.direction = "right"
        self.create_month_screen()

    def prev_year(self):
        cal_app.sm.active_year -= 1
        cal_app.sm.transition.direction = "right"
        self.create_month_screen()

    def next_month(self):
        cal_app.sm.active_month += 1
        cal_app.sm.transition.direction = "left"
        self.create_month_screen()

    def next_year(self):
        cal_app.sm.active_year += 1
        cal_app.sm.transition.direction = "left"
        self.create_month_screen()

    """def day_press(self, instance):
        # Create popup for day
        popup = Popup(size_hint =(None, None), size =(self.width * .8, self.height * .8))
        # Set title
        popup.title = f"{self.active_month} / {instance.text} / {self.active_year}"
        popup.title_align = 'center'
        popup.title_size = 30
        # Set layout
        layout = DayPopupLayout()
        layout.ids.y_m.text = f"{self.active_year} - {self.active_month}"
        layout.ids.day.text = f"{instance.text}"
        layout.ids.dismiss.bind(on_release=popup.dismiss)
        popup.content = layout
        
        # Open popup for day
        popup.open()"""

    def create_month_screen(self):
        # If month is December or January, loop month and inc/dec year
        if self.active_month == 13:
            self.active_month = 1
            self.active_year += 1
        elif self.active_month == 0:
            self.active_month = 12
            self.active_year -= 1

        # Set the name of the new screen
        active_name = f"{self.active_year}-{self.month_names[self.active_month]}"

        # If a screen with this name doesn't exist, create it
        if not cal_app.sm.has_screen(active_name):
            scr = CalendarScreen()
            scr.name = active_name

            # Change data for new screen
            scr.ids.header_label.text = scr.name

            # Get list of lists where each list is a week starting at sunday
            # isolate first week and last week to replace 0 with correct day
            # from either previous or next month
            f_week, *m_weeks, l_week = calendar_data.get_days_of_month_of_year(
                self.active_year, self.active_month
            )
            p_month, n_month = calendar_data.get_adj_months(
                self.active_year, self.active_month
            )
            # For 1st week if day = 0, replace it with correct day from previous month
            for day, pm_day in zip(f_week, calendar_data.get_last_week(*p_month)):
                if day == 0:
                    btn = self.add_day(pm_day, scr, p_month)
                else:
                    btn = self.add_day(day, scr)
                scr.ids.day_grid.add_widget(btn)
            # These days will never be 0, so create as normal
            for week in m_weeks:
                for day in week:
                    btn = self.add_day(day, scr)
                    scr.ids.day_grid.add_widget(btn)
            # For last week, if day is 0, replace with correct day from next month
            for day, nm_day in zip(l_week, calendar_data.get_first_week(*n_month)):
                if day == 0:
                    btn = self.add_day(nm_day, scr, n_month)
                else:
                    btn = self.add_day(day, scr)
                scr.ids.day_grid.add_widget(btn)

            # If today's date isn't in this screen's month, select the first of
            # the month and outline it
            if scr.selected_day == None:
                for child in reversed(scr.ids.day_grid.children):
                    if child.ids.day_tile.text == "1":
                        scr.selected_day = child
                        child.ids.day_tile.line_color = cal_app.theme_cls.primary_light
                        break

            scr.update_lower_layout()
            cal_app.sm.add_widget(scr)

        # Switch to new screen
        cal_app.sm.current = active_name

    @dispatch(int, CalendarScreen)
    def add_day(self, day, screen):
        btn = DayTile()
        # btn.ids.day_tile.bind(on_press=screen.day_press)
        btn.ids.day_tile.bind(
            on_press=lambda instance: screen.day_press(
                instance, f"{self.active_year}-{self.active_month}-{day}"
            )
        )
        btn.day_string = f"{self.active_year}-{self.active_month}-{day}"
        if (
            day == self.today[2]
            and self.active_month == self.today[1]
            and self.active_year == self.today[0]
        ):
            # If its today, select day, set text to orange, and underline text
            btn.ids.day_tile.text = f"[u]{day}[/u]"
            btn.ids.day_tile.text_color = cal_app.theme_cls.accent_color
            screen.selected_day = btn
            btn.ids.day_tile.line_color = cal_app.theme_cls.primary_light
        else:
            btn.ids.day_tile.line_color = [0, 0, 0, 0]
            btn.ids.day_tile.text = str(day)
            btn.ids.day_tile.text_color = cal_app.theme_cls.primary_color

        btn.update_icons()

        return btn

    @dispatch(int, CalendarScreen, tuple)
    def add_day(self, day, screen, other_month):
        btn = DayTile()
        year, month = other_month
        btn.ids.day_tile.bind(
            on_press=lambda instance: screen.day_press(
                instance, f"{year}-{month}-{day}"
            )
        )
        btn.day_string = f"{year}-{month}-{day}"
        btn.ids.day_tile.line_color = [0, 0, 0, 0]
        btn.ids.day_tile.text = str(day)
        btn.ids.day_tile.text_color = "gray"
        return btn


class DayPopupLayout(MDBoxLayout):
    pass


class DayTile(Widget):
    day_string = None

    def update_icons(self):
        self.ids.event_grid.clear_widgets()
        # Search db for events on this day, if exist return its hexcode
        colors = database.get_colors_by_day(conn, self.day_string)
        for (color,) in colors:
            hexcode = update_dialog.hex_to_rgba(color)
            self.ids.event_grid.add_widget(self.add_event_icon(hexcode))

    def add_event_icon(self, color):
        event_icon = MDIconButton(
            theme_text_color="Custom",
            md_bg_color_disabled=color,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            icon_size=-12,
            halign="center",
            disabled="True",
        )
        return event_icon


class LowerLayoutLabel(MDLabel):
    pass


class CalendarTrackerApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"

        # Initiate update dialog kv
        update_dialog.init_dialog_data(conn)

        # Create screen manager
        self.sm = ScreenManager()
        self.sm.init_data()
        # Create and display current month screen on startup
        self.sm.create_month_screen()

        return self.sm


if __name__ == "__main__":
    conn = database.create_connection("database.db")

    cal_app = CalendarTrackerApp()
    cal_app.run()
'''
