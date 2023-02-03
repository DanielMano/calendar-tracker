import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.app import App




class CalendarGrid(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class CalendarTrackerApp(App):
    def __init__(self, **kwargs):
        super(CalendarTrackerApp, self).__init__(**kwargs)
        
def main():
    CalendarTrackerApp().run()


if __name__ == '__main__':
    main()
