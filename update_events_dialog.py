from kivy.lang.builder import Builder

from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox

import matplotlib.colors as mcols
import database as db

KV = '''
<ListItemWithCheckbox>
    IconLeftWidgetWithoutTouch:
        id: display_icon
        icon: 'circle'
        theme_text_color: "Custom"
        text_color: [1, 1, 1, 1]

    RightCheckbox:
        id: checkbox
        on_active: root.on_checkbox_active(*args)
        
<UpdateEventDialogContent>
    orientation: 'vertical'
    adaptive_height: True
    MDGridLayout:
        id: events
        orientation: 'lr-tb'
        adaptive_height: True
        cols: 2
'''

def init_dialog_data(conn):
    """Get possible events from database and load KV for dialog

    Args:
        conn (sqlite3.Connection): db connection
    """
    Builder.load_string(KV)
    
    # Create reference dict of possible events
    global all_events_dict
    db_events = db.get_events(conn)
    all_events_dict = dict(
        (x, (y, mcols.to_rgba(f"#{z}"))) for x, y, z in db_events
    )
    
def create_update_events_dialog(self, conn, date_string):
    """Creates and returns a dialog displaying which events for a day are in 
    the database

    Args:
        conn (sqlite3.Connection): db connection
        date_string (str): str of selected day, in format of 'YYYY-MM-DD', no
                        leading 0 for month or day

    Returns:
        MDDialog: dialog object for selected day
    """
    self.dialog = MDDialog(
        auto_dismiss=False,
        title="Update Events",
        type="custom",
        content_cls=UpdateEventDialogContent(conn, date_string),
        buttons=[
            MDRaisedButton(
                text="CANCEL",
                on_release=close_dialog,
            ),
            MDRaisedButton(
                text="CONFIRM",
                on_release=confirm_dialog,
            ),
        ],
    )
    return self.dialog
    
def close_dialog(self):
    """Reverts any changes to checkbox status and dismisses dialog"""
    self.parent.parent.parent.parent.content_cls.revert_event_changes()
    self.parent.parent.parent.parent.dismiss()
    
def confirm_dialog(self):
    """Update database and dismiss dialog"""
    self.parent.parent.parent.parent.content_cls.confirm_event_changes()
    self.parent.parent.parent.parent.dismiss()
    
class UpdateEventDialogContent(MDBoxLayout):
    """Class used to display the content of custom MDDialog

    Methods:
        revert_event_changes()
            Reverts changes to checkbox states and working list
        confirm_event_changes()
            Updates db with new event selections
        get_id_from_name(name=str)
            returns event_id of event with name
        
    """
    def __init__(self, conn, day_string):
        """
        Args:
            conn (sqlite3.Connection): db connection
            day_string (str): string of date
            
        Attributes:
            events_in_db (list) : list of current events for day in db
            events_to_confirm (list) : list of currently checked events
            
        """
        super().__init__(conn, day_string)
        
        self.events_in_db = []
        self.events_to_confirm = []
        self.conn = conn
        self.day_string = day_string
        
        self.event_ids_in_day = [row[0] for row in db.get_event_ids_by_day(
            conn, self.day_string)]
        
        for key in all_events_dict:
            e_name = all_events_dict[key][0]
            e_color = all_events_dict[key][1]
            
            event = ListItemWithCheckbox(text=e_name)
            event.ids.display_icon.text_color = e_color
            # If event is already in db set checkbox to active and add event
            # name to events_in_db list
            if key in self.event_ids_in_day:
                self.events_in_db.append(all_events_dict.get(key)[0])
                event.ids.checkbox.active = True
            
            self.ids.events.add_widget(event)
        # copy current events in db to working list
        self.events_to_confirm = self.events_in_db.copy()
    
    def revert_event_changes(self):
        """Reverts checkbox states and working list state"""
        for list_item in self.children[0].children:
            if list_item.text in self.events_in_db:
                list_item.ids.checkbox.active = True
            else:
                list_item.ids.checkbox.active = False
        self.events_to_confirm = self.events_in_db.copy()
        
    def confirm_event_changes(self):
        """Updates db by adding new events and deleting deselected ones
        """        
        ids_to_confirm = []
        # Add new event to db if selected event not already in
        for name in self.events_to_confirm:
            e_id = self.get_id_from_name(name)
            ids_to_confirm.append(e_id)
            if e_id not in self.event_ids_in_day:
                db.create_date(self.conn, (self.day_string, e_id))
                self.event_ids_in_day.append(e_id)
        # Delete unchecked events from db
        for ids in list(self.event_ids_in_day):
            if ids not in ids_to_confirm:
                db.delete_event_from_day_by_event_id(
                    self.conn, self.day_string, ids)
                self.event_ids_in_day.remove(ids)

        # update list of current events in db
        self.events_in_db = self.events_to_confirm.copy()
    
    def get_id_from_name(self, name):
        """Returns event_id for given event name

        Args:
            name (str): name of evnet

        Returns:
            int: event_id of event
        """
        for key, info in all_events_dict.items():
            if name in info:
                return key
        
class ListItemWithCheckbox(OneLineAvatarIconListItem):
    """Customn list item with icon on left, text in middle, checkbox on right"""
    def __init__(self, *args, **kwargs):
        """Attribute:
            ignore_state_change (boolean) : inits to true to prevent calling
                on_checkbox_active when initializing checkbox states
        """
        super().__init__(*args, **kwargs)
        self.ignore_state_change = True
        
    def on_parent(self, *args):
        """Changes ignore_state_change to false only after init has finished"""
        self.ignore_state_change = False
        
    def on_checkbox_active(self, checkbox, value):
        """Updates working list to contain curently checked events"""
        if not self.ignore_state_change:
            if value:
                self.parent.parent.events_to_confirm.append(f"{self.text}")
            else:
                self.parent.parent.events_to_confirm.remove(f"{self.text}")

class RightCheckbox(IRightBodyTouch, MDCheckbox):
    pass