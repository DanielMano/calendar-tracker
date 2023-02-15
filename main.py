from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup

import calendar_data

class ScreenManager(ScreenManager):
    def init_data(self):
        # YYYY, M where [1-12], D
        self.active_year, self.active_month, self.active_day = calendar_data.get_today_date_string()
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
                    btn = Button(text=str(day))
                    btn.bind(on_press=self.day_press)
                    scr.ids.day_grid.add_widget(btn)
            cal_app.sm.add_widget(scr)
            
        # Switch to new screen
        cal_app.sm.current = active_name

class CalendarScreen(Screen):
    def prev_month(self):
        cal_app.sm.prev_month()
        
    def next_month(self):
        cal_app.sm.next_month()
        
class DayPopupLayout(BoxLayout):
    pass

class CalendarTrackerApp(App):
    def build(self):
        # Create screen manager
        self.sm = ScreenManager()
        self.sm.init_data()
        # Create and display current month screen on startup
        self.sm.create_month_screen()
        
        return self.sm


if __name__ == '__main__':
    cal_app = CalendarTrackerApp()
    cal_app.run()
