from __future__ import annotations

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.list import OneLineIconListItem, IconLeftWidgetWithoutTouch

from kivy.uix.colorpicker import ColorPicker
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty

import database


class EventsInDatabaseEditor(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = MDApp.get_running_app().root
        self.current_events = database.get_events_with_color_id(
            MDApp.get_running_app().conn
        )
        for event_id, name, hexcode, color_id in self.current_events:
            self.ids.event_list.add_widget(
                CustomListItem(
                    IconLeftWidgetWithoutTouch(
                        icon="circle",
                        theme_icon_color="Custom",
                        icon_color=hexcode,
                    ),
                    text=name,
                    on_release=self.list_callback,
                    hexcode=hexcode,
                    e_id=event_id,
                    c_id=color_id,
                )
            )

        self.ids.event_list.add_widget(
            OneLineIconListItem(
                IconLeftWidgetWithoutTouch(
                    icon="plus",
                ),
                text="CREATE NEW EVENT",
                on_release=self.new_event_callback,
            )
        )

    def list_callback(self, instance: CustomListItem):
        # print(self, instance.name, instance.hex_color, instance.rgba_color)
        # TODO bring up popup that has option to edit name, edit color, or delete
        # deleting might be bad though because instances of it might already be on days in database, then would have to decide how to handle either just removing those or what
        # KivyMD has MDColorPicker
        # MDColorPicker(size_hint=(0.9, 0.6), default_color=instance.rgba_color).open()
        # kivy has ColorPicker was looks uglier, but i think might actually be functionally better

        clr_picker = ColorPicker(color=instance.rgba_color)

        def get_clr_picker_color(btn):
            try:
                (new_c_id,) = database.check_if_hexcode_exists(
                    MDApp.get_running_app().conn, clr_picker.hex_color
                )
            except:
                new_c_id = None

            if new_c_id is not None:
                print("UPDATE", instance.c_id, "to", new_c_id)
            else:
                print(
                    "CREATE new color with hexcode",
                    clr_picker.hex_color,
                    "and swap",
                    instance.c_id,
                    "to that new c_id",
                )

                print(
                    "OR change hexcode of",
                    instance.c_id,
                    "from",
                    instance.hex_color,
                    "to",
                    clr_picker.hex_color,
                )

            instance.left_icon.icon_color = clr_picker.color

        content_layout = MDBoxLayout(orientation="vertical")
        content_layout.add_widget(
            Button(text=instance.name, on_release=get_clr_picker_color)
        )

        content_layout.add_widget(clr_picker)

        Popup(
            title="Edit Event",
            content=content_layout,
            size_hint=(0.9, 0.7),
        ).open()

    def new_event_callback(self, instance: OneLineIconListItem):
        content_layout = MDBoxLayout(orientation="vertical")

        NewEventPopup().my_open()

        print("create new event")


class NewEventPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.title = "Add New Event To Database"
        self.title_align = "center"
        # self.title_size = "30sp"
        self.size_hint = (0.9, 0.7)

        content = NewEventContent(popup=self)
        self.content = content

    def my_open(self):
        self.open()

    def my_close(self):
        self.dismiss()


class NewEventContent(MDFloatLayout):
    popup: NewEventPopup = ObjectProperty(None)

    def my_confirm(self):
        if self.ids.event_name.text != "":
            print("Name of event:", self.ids.event_name.text)

            print("Color of event:", self.ids.clr_picker.hex_color)

            # TODO use these things to first search db for hex_color, if there use c_id for creation of new event
            # if hex_color not in db, create a new color with that code, and use the new c_id for creation of the new event
            # then insert that event into the event list

            self.popup.my_close()


class CustomListItem(OneLineIconListItem):
    def __init__(self, *args, hexcode, e_id, c_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.left_icon: IconLeftWidgetWithoutTouch = args[0]
        self.name = self.text
        self.hex_color = hexcode
        self.rgba_color = args[0].icon_color
        self.e_id = e_id
        self.c_id = c_id
