from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton

from test_main import DayTile


class EventManagerPopup(Popup):
    active_day_event_names = []

    def __init__(self, all_events: list, day_tile: DayTile, **kwargs):
        super().__init__(**kwargs)
        self.title_align = "center"
        self.size_hint = 0.9, 0.7
        self.content = EventManagerPopupContent(caller=self)
        self.all_events = all_events
        self.all_events_dict = dict(all_events)
        self.day_tile = day_tile
        self.auto_dismiss = False

    def update_and_open(self, day_tile: DayTile):
        self.day_tile = day_tile
        self.title = self.day_tile.date_str
        if self.day_tile.events:
            self.active_day_event_names = list(zip(*self.day_tile.events))[0]

        self.content.ids.manager_grid.clear_widgets()

        for event in self.all_events:
            if event in day_tile.events:
                self.content.ids.manager_grid.add_widget(
                    EventManagerButton(text=event[0], state="down")
                )
            else:
                self.content.ids.manager_grid.add_widget(
                    EventManagerButton(text=event[0], state="normal")
                )
        self.open()

    def confirm_selection(self):
        events_dict = dict(self.day_tile.events)
        for child in self.content.ids.manager_grid.children:
            if child.state == "down":
                if child.text not in events_dict:
                    self.day_tile.events.append(
                        event := (child.text, self.all_events_dict.get(child.text))
                    )
                    self.day_tile.add_event_to_db(event)
            else:
                if child.text in events_dict:
                    self.day_tile.events.remove(
                        event := (child.text, self.all_events_dict.get(child.text))
                    )
                    self.day_tile.remove_event_from_db(event)

        self.dismiss()


class EventManagerPopupContent(BoxLayout):
    def __init__(self, caller, **kwargs):
        super().__init__(**kwargs)
        self.caller: EventManagerPopup = caller

    def cancel_dismiss(self):
        self.caller.dismiss()

    def confirm_dismiss(self):
        self.caller.confirm_selection()


class EventManagerButton(ToggleButton):
    # TODO pretty sure i can just replace any use of this with Button
    # unless i make a kv definition of this button for styling
    pass
