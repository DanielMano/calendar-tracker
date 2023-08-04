from kivymd.app import MDApp
from kivymd.uix.behaviors import TouchBehavior
from kivymd.uix.button import MDIconButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.clock import Clock

from timeit import default_timer as timer
from functools import partial
import itertools


"""
CustomSpeedDialFloatLayout:
        id: speed_float
        root: maincontent
        size_hint_y: 0

        ShortOrLongMDIconButton:
            id: base
            root: speed_float
            md_bg_color: app.theme_cls.primary_color
            pos_hint: {"right": 1 - (10/root.width), "y": (10/speed_float.height)}
            icon: 'plus'
"""


class CustomSpeedDialFloatLayout(MDFloatLayout):
    """Class used to contain a psuedo recreation of a fab speed dial.
    The base_button defaults to the bottom right corner, 'plus' icon, and app.theme_cls.primary_color
    as the background color of the button.
    """

    def on_kv_post(self, base_widget):
        def callback(dt):
            """Called after a frame is displayed in order to get accurate position
            info from the base_button.

            Args:
                dt (float): not used
            """
            base_btn = self.children[0]
            # ACTION REQUIRED: These are the extra button, add or remove depending on how many you need
            self.add_button_to_speed_dial(
                base_btn.pos, base_btn.height, "cross", self.short_action
            )
            self.add_button_to_speed_dial(
                base_btn.pos, base_btn.height, "check", self.short_action
            )

        # This schedule has to take at least one second in order to get correct
        # sizes and positions of objects from the kv file.
        # This might just be a computer limitation, but should be unnoticable regardless.
        Clock.schedule_once(callback, 1)
        return super().on_kv_post(base_widget)

    def add_button_to_speed_dial(self, pos: list, height: float, icon: str, callback):
        """Adds a new button to the top of the speed dial.

        Args:
            pos (list): the x, y of the base_button of the speed dial
            height (float): the height of the button being added, used to place button correctly
            icon (str): icon to be used for button, must be in kivymd.icon_definitions.md_icons
            callback (function): function bound to the button's on_press
        """
        pos_x, pos_y = pos
        pos_y += (pos_y / 2) * (len(self.children)) + height * len(self.children)
        new_btn = MDIconButton(
            icon=icon,
            md_bg_color=MDApp.get_running_app().theme_cls.accent_color,
            pos_hint={"right": 1 - (10 / self.root.width)},
            pos=(0, pos_y),
            opacity=0,
            on_press=callback,
        )
        self.add_widget(new_btn)

    def short_action(self, instance):
        """Executes different actions depending on which button is pressed.
        Match the .icon attribute of the button to the correct case.
        Requires the .icon to be unique to each button.

        Args:
            instance (MDIconButton): The MDIconButton that has called this function.
        """
        match instance.icon:
            case "check":
                pass
            case "cross":
                pass
            case "plus":
                pass

    def long_action(self, instance):
        """Called when the base_button is long held. Sets all buttons in the speed dial
        to opacity of 1 and starts the countdown until the speed dial fades away.

        Args:
            instance (ShortOrLongMDIconButton): the base_button, not used
        """
        # Gets all buttons in speed dial, ignores the base_button
        for child in itertools.islice(self.children, len(self.children) - 1):
            child.opacity = 1
        Clock.schedule_once(partial(self.start_fade, 10, 0.25), 4)

    def start_fade(self, steps: int, totaltime: float, dt: float):
        """Schedules fade actions that results with the non base_buttons to have
        an opacity of 0 after the totaltime has elapsed.

        Args:
            steps (int): The number of subdivision of the totaltime. More steps means smoother fade.
            totaltime (float): The total amount of time fading from 1 to 0 will take.
            dt (float): The time that will pass before this function is to be executed.
        """
        for i in range(steps):
            self.event = Clock.schedule_once(
                partial(self.fade_over_time, 1 / steps),
                (i * (round(totaltime / steps, 6))),
            )

    def fade_over_time(self, opacity_delta: float, dt: float):
        """Reduces the opacity of all non base_button buttons in the speed dial
        by the opacity_delta after a wait of dt seconds.

        Args:
            opacity_delta (float): The change in opacity to be committed.
            dt (float): The time that will pass before this function is to be executed.
        """
        for child in itertools.islice(self.children, len(self.children) - 1):
            child.opacity -= opacity_delta

            if child.opacity <= 0:
                print("trying to cancel")
                self.event.cancel()


class ShortOrLongMDIconButton(TouchBehavior, MDIconButton):
    """An MDIconButton that can call 2 different functions depending on length of button press.
    If the button isn't released before duration_long_touch elapses, then the long pressed
    function is called, otherwise the short press function is called.

    duration_long_touch is an NumericProperty and defaults to 0.4


    The button has two types:
    1. Standalone - the on_long_touch acts as a secondary function call to do whatever.
    If so, ACTION REQUIRED: need to add short_action() and long_action() to the root if standalone.
    2. As base_button of a Speed Dial - the on_long_touch instead brings up the other
    buttons.
    """

    def __init__(self, *args, root=None, **kwargs):
        """
        Args:
            root (object, optional): The root of the button, has to be set. Defaults to None.

        Attribute:
            start (float): Reference to time at button press. Defaults to 0.
        """
        super().__init__(*args, **kwargs)
        self.root = root
        self.start = 0

    def on_press(self):
        """Captures time upon initial touch of button."""
        self.start = timer()

    def on_release(self):
        """Captures time once button is released. If elapsed time is less than
        duration_long_touch, than the button press has been determined to be short.
        """
        stop = timer()
        waited = stop - self.start
        if waited < self.duration_long_touch:
            self.my_short_callback()

    def on_long_touch(self, touch, *args):
        """Automatically called after duration_long_touch elapses. If button is
        part of a speed dial, directs to speed dial long_action. If button is standalone,
        calls its root long_action instead.
        """
        print("-long pressed")

        if type(self.parent) is CustomSpeedDialFloatLayout:
            # Button being long pressed is the base_button of a speed dial.
            self.root.long_action(self)
        else:
            # Button is not part of a speed dial, calls root.long_action()
            self.root.long_action()

    def my_short_callback(self):
        """Called when button press resolves to be short. Changes depending of if
        button is part of a speed dial or not.
        """
        print("-short pressed")
        if type(self.parent) is CustomSpeedDialFloatLayout:
            # Button being short pressed is the base_button of a speed dial.
            self.root.short_action(self)
        else:
            # Button is not part of a speed dial, calls root.short_action()
            self.root.short_action()
