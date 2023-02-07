import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ListProperty, NumericProperty

from ast import literal_eval

import calendar_data
#Builder.load_file('calendartracker.kv')

class CalendarGrid(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_data()
                
        for row in range(6):
            for column in range(7):
                daynum = self.active_month_array[row][column]
                #TODO if daynum = 0, replace with correct days from either last or next month
                self.children[0].add_widget(self.add_day_tile_layout(column, row, daynum))
    
    def init_data(self):
        self.active_date = calendar_data.get_today_date()
        self.active_month_array = calendar_data.get_month_data(self.active_date.year, self.active_date.month)
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
        pass


class CalendarTrackerApp(App):
    def build(self):
        return CalendarGrid()

def main():
    CalendarTrackerApp().run()


if __name__ == '__main__':
    main()
