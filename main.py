from kivy.config import Config
Config.set('graphics', 'width', '500')
Config.set('graphics', 'height', '1000')
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

import matplotlib.colors as mcols
from multipledispatch import dispatch

class CalendarScreen(Screen):
    selected_day = None
    dialog_dict = {}
    def prev_month(self):
        cal_app.sm.prev_month()
        
    def next_month(self):
        cal_app.sm.next_month()
    
    def my_callback(self, instance):
        self.update_lower_layout()
        self.selected_day.update_icons()
    
    def get_selected(self):
        #print("screen:", self, "selected_day:", self.selected_day, "-->", self.selected_day.ids.day_tile.text, "-->", self.selected_day.day_string)
        if not self.dialog_dict.get(self.selected_day.day_string):
            self.dialog_dict[self.selected_day.day_string] = update_dialog.create_update_events_dialog(self, conn, self.selected_day.day_string)
        selected_dialog = self.dialog_dict.get(self.selected_day.day_string)
        selected_dialog.bind(on_dismiss=self.my_callback)
        
        selected_dialog.open()
    
    def day_press(self, instance, day_string):
        #print("self:", self, "instance:", instance, "instance.parent:", instance.parent, "day_string:", day_string)
        self.ids.scroll_grid.clear_widgets()
        self.selected_day.ids.day_tile.line_color = [0, 0, 0, 0]
        instance.line_color = cal_app.theme_cls.primary_light
        self.selected_day = instance.parent
        
        self.update_lower_layout()
           
    def update_lower_layout(self):
        self.ids.scroll_grid.clear_widgets()
        y, m, d = self.selected_day.day_string.split('-')
        self.ids.ll_title.text = f"{cal_app.sm.month_names[int(m)]} {d}, {y}"
        event_names = database.get_event_names_by_day(conn, self.selected_day.day_string)
        for (name,) in event_names:
            lllabel = LowerLayoutLabel(text=name)
            lllabel.font_size = "32sp"
            lllabel.font_name = 'fonts/nasalization-free.rg-regular.otf'
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
        cal_app.sm.transition.direction = 'right'
        self.create_month_screen()
        
    def prev_year(self):
        cal_app.sm.active_year -= 1
        cal_app.sm.transition.direction = 'right'
        self.create_month_screen()
    
    def next_month(self):
        cal_app.sm.active_month += 1
        cal_app.sm.transition.direction = 'left'
        self.create_month_screen()
        
    def next_year(self):
        cal_app.sm.active_year += 1
        cal_app.sm.transition.direction = 'left'
        self.create_month_screen()
    
    '''def day_press(self, instance):
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
        popup.open()'''
    
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
            f_week, *m_weeks, l_week = calendar_data.get_days_of_month_of_year(self.active_year, self.active_month)
            p_month, n_month = calendar_data.get_adj_months(self.active_year, self.active_month)
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
                    if child.ids.day_tile.text == '1':
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
        #btn.ids.day_tile.bind(on_press=screen.day_press)
        btn.ids.day_tile.bind(on_press=lambda instance: screen.day_press(instance, f"{self.active_year}-{self.active_month}-{day}"))
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
        btn.ids.day_tile.bind(on_press=lambda instance: screen.day_press(instance, f"{year}-{month}-{day}"))
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
            hexcode = mcols.to_rgba(f"#{color}")
            self.ids.event_grid.add_widget(self.add_event_icon(hexcode))
    
    def add_event_icon(self, color):
        event_icon = MDIconButton(
                theme_text_color="Custom",
                md_bg_color_disabled = color,
                pos_hint= {'center_x': 0.5,'center_y': 0.5},
                icon_size = -12,
                halign = 'center',
                disabled = 'True',
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


if __name__ == '__main__':
    conn = database.create_connection("database.db")    
    
    cal_app = CalendarTrackerApp()
    cal_app.run()
