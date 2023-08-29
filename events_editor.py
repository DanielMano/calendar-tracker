from __future__ import annotations

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.list import OneLineIconListItem, IconLeftWidgetWithoutTouch
from kivymd.toast import toast

from kivy.uix.colorpicker import ColorPicker
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty

import database


class EventsInDatabaseEditor(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = MDApp.get_running_app().root

        self.create_new_event_item = OneLineIconListItem(
            IconLeftWidgetWithoutTouch(
                icon="plus",
            ),
            text="CREATE NEW EVENT",
            on_release=self.new_event_callback,
        )

        self.current_events = database.get_events_with_color_id(
            MDApp.get_running_app().conn
        )

        self.ids.event_list.clear_widgets()

        for event_id, name, hexcode, color_id in self.current_events:
            self.ids.event_list.add_widget(
                CustomListItem(
                    IconLeftWidgetWithoutTouch(
                        icon="circle",
                        theme_icon_color="Custom",
                        icon_color=hexcode,
                    ),
                    text=name,
                    # on_release=self.list_callback,
                    on_release=self.edit_event_callback,
                    hexcode=hexcode,
                    e_id=event_id,
                    c_id=color_id,
                )
            )

        self.ids.event_list.add_widget(self.create_new_event_item)

    def add_new_item(self, event_item):
        self.ids.event_list.remove_widget(self.create_new_event_item)
        self.ids.event_list.add_widget(event_item)
        self.ids.event_list.add_widget(self.create_new_event_item)

    def edit_event_callback(self, instance: CustomListItem):
        EditEventPopup(caller=self, list_item=instance).open()

    def new_event_callback(self, instance: OneLineIconListItem):
        NewEventPopup(caller=self).my_open()


class EditEventPopup(Popup):
    def __init__(self, caller, list_item, **kwargs):
        self.caller: EventsInDatabaseEditor = caller
        self.event: CustomListItem = list_item
        super().__init__(**kwargs)
        self.title = "Edit Event"
        self.title_align = "center"
        self.size_hint = (0.9, 0.7)

        self.content = EditEventContent(popup=self, name=self.event.name)


class EditEventContent(MDFloatLayout):
    popup: EditEventPopup = ObjectProperty(None)
    name = StringProperty(None)

    helper_text = StringProperty("")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.color_picker = ColorPicker(
            size_hint=(0.9, 0.85),
            pos_hint={"x": 0.05, "y": 0},
            color=self.popup.event.rgba_color,
        )

        self.add_widget(self.color_picker)

    def edit_confirm(self):
        self.check_error(self.ids.event_name)
        if self.ids.event_name.error:
            # error don't do anything
            pass
        else:
            if self.popup.event.name != self.ids.event_name.text:
                if self.popup.event.hex_color != self.color_picker.hex_color:
                    # edit event name and hex color
                    print("edit name and hex color, e_id:", self.popup.event.e_id)
                    # TODO: don't really like how this is handled, this allows for multiple events to share color
                    try:
                        (new_c_id,) = database.check_if_hexcode_exists(
                            MDApp.get_running_app().conn, self.color_picker.hex_color
                        )
                    except:
                        new_c_id = None

                    if new_c_id is not None:
                        # Change c_id associated with existing e_id, and change name
                        database.edit_event_name_and_color(
                            MDApp.get_running_app().conn,
                            self.ids.event_name.text,
                            new_c_id,
                            self.popup.event.e_id,
                        )
                    else:
                        # Change hexcode associated with existing c_id
                        database.edit_color_hexcode(
                            MDApp.get_running_app().conn,
                            self.color_picker.hex_color,
                            self.popup.event.c_id,
                        )
                        # Change name
                        database.edit_event_name(
                            MDApp.get_running_app().conn,
                            self.ids.event_name.text,
                            self.popup.event.e_id,
                        )
                else:
                    # edit just event name
                    database.edit_event_name(
                        MDApp.get_running_app().conn,
                        self.ids.event_name.text,
                        self.popup.event.e_id,
                    )
            else:
                if self.popup.event.hex_color != self.color_picker.hex_color:
                    # edit just hex color
                    # Search db to see if that color already exists
                    # TODO: don't really like how this is handled, this allows for multiple events to share color
                    try:
                        (new_c_id,) = database.check_if_hexcode_exists(
                            MDApp.get_running_app().conn, self.color_picker.hex_color
                        )
                    except:
                        new_c_id = None

                    if new_c_id is not None:
                        # Change c_id associated with existing e_id
                        database.edit_event_color(
                            MDApp.get_running_app().conn,
                            new_c_id,
                            self.popup.event.e_id,
                        )
                    else:
                        # Change hexcode associated with existing c_id
                        database.edit_color_hexcode(
                            MDApp.get_running_app().conn,
                            self.color_picker.hex_color,
                            self.popup.event.c_id,
                        )
                else:
                    # do nothing
                    pass

            # Update list item atts
            self.popup.event.left_icon.icon_color = self.color_picker.color
            self.popup.event.hex_color = self.color_picker.hex_color
            self.popup.event.rgba_color = self.color_picker.color
            self.popup.event.name = self.ids.event_name.text
            self.popup.event.text = self.ids.event_name.text
            self.popup.dismiss()

    def check_error(self, textfield):
        self.name_changed = True
        textfield.text = textfield.text.strip()
        if textfield.text == "":
            self.helper_text = "Name cannot be an empty string"
            textfield.error = True
        elif textfield.text == self.popup.event.name:
            # This is fine, do nothing
            self.name_changed = False
            pass
        else:
            if database.check_if_event_name_exists(
                MDApp.get_running_app().conn, textfield.text
            ):
                self.helper_text = "Name already in use"
                textfield.error = True

    def edit_cancel(self):
        self.popup.dismiss()


class NewEventPopup(Popup):
    def __init__(self, caller, **kwargs):
        self.caller = caller
        super(NewEventPopup, self).__init__(**kwargs)
        self.title = "Add New Event To Database"
        self.title_align = "center"
        self.size_hint = (0.9, 0.7)

        content = NewEventContent(popup=self)
        self.content = content

    def my_open(self):
        self.open()

    def my_close(self, name, hexcode, e_id, c_id):
        new_item = CustomListItem(
            IconLeftWidgetWithoutTouch(
                icon="circle",
                theme_icon_color="Custom",
                icon_color=hexcode,
            ),
            text=name,
            on_release=self.caller.edit_event_callback,
            hexcode=hexcode,
            e_id=e_id,
            c_id=c_id,
        )
        self.caller.add_new_item(new_item)
        self.dismiss()

    def my_cancel(self):
        self.dismiss()


class NewEventContent(MDFloatLayout):
    popup: NewEventPopup = ObjectProperty(None)
    helper_text = StringProperty("test")

    def my_confirm(self):
        self.check_error(self.ids.event_name)
        if self.ids.event_name.text != "":
            name = self.ids.event_name.text
            hex_code = self.ids.clr_picker.hex_color

            # If an event with that name already exists, warn with toast and do nothing.
            if database.check_if_event_name_exists(MDApp.get_running_app().conn, name):
                toast("Event with that name already exists")
                return

            # Use these things to first search db for hex_color, if in db get existing c_id
            try:
                (c_id,) = database.check_if_hexcode_exists(
                    MDApp.get_running_app().conn, hex_code
                )
            except:
                # if hex_color not in db, create a new color with that code, get new c_id
                c_id = database.create_color(MDApp.get_running_app().conn, hex_code)

            # Create new event
            e_id = database.create_event(MDApp.get_running_app().conn, (name, c_id))

            self.popup.my_close(name, hex_code, e_id, c_id)

        else:
            toast("Please provide a name")

    def check_error(self, textfield):
        self.name_changed = True
        textfield.text = textfield.text.strip()
        if textfield.text == "":
            self.helper_text = "Name cannot be an empty string"
            textfield.error = True
        elif database.check_if_event_name_exists(
            MDApp.get_running_app().conn, textfield.text
        ):
            self.helper_text = "Name already in use"
            textfield.error = True


class CustomListItem(OneLineIconListItem):
    def __init__(self, *args, hexcode, e_id, c_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.left_icon: IconLeftWidgetWithoutTouch = args[0]
        self.name = self.text
        self.hex_color = hexcode
        self.rgba_color = args[0].icon_color
        self.e_id = e_id
        self.c_id = c_id
