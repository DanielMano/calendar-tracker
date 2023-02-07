import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ListProperty, NumericProperty, StringProperty

from ast import literal_eval

import calendar_data
#Builder.load_file('calendartracker.kv')

class CalendarGrid(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.init_data()

        #print(self.children[0].children)
        self.day_grid_layout = self.children[0].children[0]
        self.day_name_box_layout = self.children[0].children[1]
        self.month_navigation_box_layout = self.children[0].children[2]
        
        for name in range(len(self.weekday_names)):
            self.day_name_box_layout.add_widget(Label(text=f"{self.weekday_names[name]}"))
                
        for row in range(6):
            for column in range(7):
                daynum = self.active_month_array[row][column]
                #TODO if daynum = 0, replace with correct days from either last or next month
                self.day_grid_layout.add_widget(self.add_day_tile_layout(column, row, daynum))
                    
    def init_data(self):
        self.active_date = calendar_data.get_today_date()
        self.active_month_array = calendar_data.get_month_data(self.active_date.year, self.active_date.month)
        self.weekday_names = calendar_data.get_day_names()
        if len(self.active_month_array) < 6:
            self.active_month_array.append([0, 0, 0, 0, 0, 0, 0])
        self.month_names = calendar_data.get_month_names()
                
    def add_day_tile_layout(self, column, row, daynum):
        box_layout = BoxLayout(orientation='vertical')
        box_layout.add_widget(Button(text=f"{daynum}"))
        box_layout.add_widget(self.add_icon_grid_to_day_tile(column, row))
        return box_layout
    
    def add_icon_grid_to_day_tile(self, column, row):
        grid_layout = GridLayout(rows=2)
        for position in range(8):
            grid_layout.add_widget(DayActivityIcon(column=column, row=row, position=position))
        return grid_layout


class DayActivityIcon(Button):
    background_color = ListProperty((0, 0, 0, 1))
    icon_color = ListProperty((0.2, 0.6, 1, 1))
    column = NumericProperty(0)
    row = NumericProperty(0)
    position = NumericProperty(0)
            
    def get_day_info(self):
        print(f"Pressed on day: {self.column}, {self.row}, {self.position}")


class MonthNavigationBoxLayout(BoxLayout):
    month_header_label = StringProperty()
    
    display_month = calendar_data.get_today_date().month
    month_names = calendar_data.get_month_names()
    month_header_label = str(month_names[display_month-1])
    
    def previous_month_on_press(self, instance):
        # will have to implement screenmanager to go between months
        #print(self)
        #print(instance)
        print("previous month")
    
    def next_month_on_press(self, instance):
        # will have to implement screenmanager to go between months
        #print(self)
        #print(instance)
        print("next month")
        
    def ref_pressed(self):
        # TODO bring up month and year picker
        pass
        
class DaysOfWeekBoxLayout(BoxLayout):
    pass

class CalendarTrackerApp(App):
    def build(self):
        return CalendarGrid()

def main():
    CalendarTrackerApp().run()


if __name__ == '__main__':
    main()
