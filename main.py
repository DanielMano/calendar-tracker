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

import calendar_data
import database

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
    
    def next_month(self):
        cal_app.sm.active_month += 1
        cal_app.sm.transition.direction = 'left'
        self.create_month_screen()
    
    def day_press(self, instance):
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
        popup.open()
    
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
            month = calendar_data.get_days_of_month_of_year(self.active_year, self.active_month)
            
            for week in month:
                for day in week:                    
                    btn = self.add_day(day)
                    scr.ids.day_grid.add_widget(btn)
            cal_app.sm.add_widget(scr)
            
        # Switch to new screen
        cal_app.sm.current = active_name
    
    def add_day(self, day):
        btn = DayTile()
        btn.ids.day_tile.bind(on_press=self.day_press)

        if day == self.today[2] and self.active_month == self.today[1] and self.active_year == self.today[0]:
            # If today's date, set day selection, text color to white, and underline text
            btn.ids.day_tile.line_color = cal_app.theme_cls.primary_light
            btn.ids.day_tile.text = f"[u]{day}[/u]"
            btn.ids.day_tile.text_color = "orange"
        else:
            btn.ids.day_tile.line_color = [0, 0, 0, 0]
            btn.ids.day_tile.text = str(day)
            btn.ids.day_tile.text_color = cal_app.theme_cls.primary_dark
        
        # TODO: get data from database and 1. replace day_press popup with dialog and 2. add event icons for events

        #btn.ids.event_grid.add_widget(self.add_event_icon([0.5, 0, 0.5, 1]))

        return btn
    
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
        

class CalendarScreen(Screen):
    def prev_month(self):
        cal_app.sm.prev_month()
        
    def next_month(self):
        cal_app.sm.next_month()
        
class DayPopupLayout(MDBoxLayout):
    pass

class DayTile(Widget):
    pass

class CalendarTrackerApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        
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
