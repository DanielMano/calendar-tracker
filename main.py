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


#Builder.load_file('calendartracker.kv')

class CalendarGrid(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
                
        for row in range(7):
            for column in range(7):
                #self.children[0].add_widget(self.add_crazy_button(j, i))
                #self.children[0].add_widget(Label(text=f"({j}, {i})"))
                self.children[0].add_widget(self.add_day_tile_layout(column, row))
                
    def add_day_tile_layout(self, column, row):
        box_layout = BoxLayout(orientation='vertical')
        box_layout.add_widget(Button(text=f"({column}, {row})"))
        box_layout.add_widget(self.add_icon_grid_to_day_tile(column, row))
        return box_layout
    
    def add_icon_grid_to_day_tile(self, column, row):
        grid_layout = GridLayout(rows=2)
        for position in range(8):
            grid_layout.add_widget(DayActivityIcon(text=f"({column}, {row}, {position})", font_size="10"))
        return grid_layout


class DayActivityIcon(Button):
    background_color = ListProperty((0, 0, 0, 1))
    column = NumericProperty(0)
    row = NumericProperty(0)
    position = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.column, self.row, self.position = literal_eval(self.text)
        
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
