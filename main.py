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

from kivy.clock import Clock

from os import path
from shutil import copy

import calendar_data
import database
import date_picker_popup as dpp
import day_event_manager_popup as manager_popup
import android_storage
import CustomSpeedDial

from events_editor import EventsInDatabaseEditor

# from timeit import default_timer as timer

__version__ = "0.4.1.33"


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

        print("RootManager inited")
        (
            self.today,
            self.active_year,
            self.active_month,
            self.active_day,
        ) = calendar_data.get_today()
        self.month_names = calendar_data.get_month_names()

        self.all_events_with_ids = database.get_events(MDApp.get_running_app().conn)
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
            MDApp.get_running_app().conn, day_tile.date_str
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
        )
        if len(hexcode) == 6:
            rgba + (1.0,)
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
        # TODO requery database to get new colors to display
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
            MDApp.get_running_app().conn,
            (self.date_str, RootManager.all_events_with_ids_dict[event]),
        )

    def remove_event_from_db(self, event):
        database.delete_event_from_day_by_event_id(
            MDApp.get_running_app().conn,
            self.date_str,
            RootManager.all_events_with_ids_dict[event],
        )


class DayTileEvent(MDBoxLayout):
    pass


class DatabasePrompt(BoxLayout):
    def use_previous_db(self):
        print("main :: trying to use previous db")
        app = MDApp.get_running_app()
        app.chooser.chooser_start()

    def use_default_db(self):
        app = MDApp.get_running_app()
        copy("database.db", app.current_db_version)
        app.conn = database.create_connection(app.current_db_version)
        app.root.swap_to_root_manager()


class UberRoot(MDFloatLayout):
    def __init__(self, pick_db: bool, **kwargs):
        super().__init__(**kwargs)
        self.root_manager = None
        self.database_prompt = DatabasePrompt()
        self.events_editor = None

        if pick_db:
            self.add_widget(self.database_prompt)

        else:
            self.root_manager = RootManager()

            self.add_widget(self.root_manager)

    def swap_to_root_manager(self):
        self.clear_widgets()

        if self.root_manager is None:
            self.root_manager = RootManager()

        self.add_widget(self.root_manager)

    def swap_to_events_editor(self):
        # TODO Might not clear rootmanager widget and instead just put event editor
        # on top. Don't think it really matters.
        self.clear_widgets()
        if self.events_editor is None:
            self.events_editor = EventsInDatabaseEditor()
            print("SWAPPING TO EVENT EDITOR")
        self.add_widget(self.events_editor)


class CalendarTrackerApp(MDApp):
    conn = None
    current_db_version = None
    chooser = None

    def m(self, copied_db_path_value):
        try:
            copy(copied_db_path_value, self.current_db_version)
            self.conn = database.create_connection(self.current_db_version)
        except IOError as e:
            print(e)

        self.root.swap_to_root_manager()

    @property
    def copied_db_path(self):
        return self._p

    @copied_db_path.setter
    def copied_db_path(self, value):
        self._p = value
        Clock.schedule_once(lambda dt: self.m(value), 2)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"

        self.chooser = android_storage.Storage(root=self)

        self.current_db_version = "database_" + __version__ + ".db"
        if path.exists(self.current_db_version):
            self.conn = database.create_connection(self.current_db_version)
        else:
            print("main :: ", self.current_db_version, "doesn't exist, trigger prompt")
            return UberRoot(pick_db=True)

        return UberRoot(pick_db=False)

    def on_pause(self):
        self.chooser.save_file(self.current_db_version, self.current_db_version)
        return super().on_pause()


if __name__ == "__main__":
    CalendarTrackerApp().run()
