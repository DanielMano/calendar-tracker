import sqlite3
from sqlite3 import Error

import matplotlib.pyplot as plt

""" create a database connection specified by db_file
    returns Connection object or None
"""
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
        
    return conn

# Creates the colors table
def create_colors_table(conn):
    sql = """
        CREATE TABLE IF NOT EXISTS colors ( 
        color_id INTEGER NOT NULL  PRIMARY KEY,
        hexcode VARCHAR(8) NOT NULL DEFAULT 'FFFFFF')
        """
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
    except Error as e:
        print(e)

# Creates the events table
def create_events_table(conn):
    sql = """
        CREATE TABLE IF NOT EXISTS events ( 
        event_id INTEGER NOT NULL  PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        color_id INTEGER NOT NULL,
        FOREIGN KEY ( color_id ) REFERENCES colors( color_id ))
        """
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
    except Error as e:
        print(e)

# Creates the dates table
def create_dates_table(conn):
    sql = """
        CREATE TABLE IF NOT EXISTS dates ( 
        date_id INTEGER NOT NULL  PRIMARY KEY,
        day DATE NOT NULL,
        event_id INTEGER NOT NULL,
        FOREIGN KEY ( event_id ) REFERENCES events( event_id ))
        """
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
    except Error as e:
        print(e)
        
# Add a color hexcode to the colors table
# Returns the color_id
def create_color(conn, hexcode):
    sql = """
        INSERT INTO colors(hexcode) VALUES(?)
        """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (hexcode,))
        conn.commit()
    except Error as e:
        print(e)
    finally:
        if cursor:
            return cursor.lastrowid

# Add an event to the events table
# Returns the event_id
def create_event(conn, event):
    sql = """
        INSERT INTO events(name, color_id) VALUES(?,?)
        """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, event)
        conn.commit()
    except Error as e:
        print(e)
    finally:
        if cursor:
            return cursor.lastrowid
        
# Add a date to the dates table
# Returns the date_id
def create_date(conn, date):
    #TODO create a method to add dates in batches, prevents creation and deletion of multiple cursors
    sql = """
        INSERT INTO dates(day, event_id) VALUES(?,?)
        """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (date))
        conn.commit()
    except Error as e:
        print(e)
    finally:
        if cursor:
            return cursor.lastrowid

# Delete a row from dates
def delete_event_from_day(conn, date_id):
    sql = "DELETE FROM dates WHERE date_id=?"
    cursor = conn.cursor()
    cursor.execute(sql, (date_id,))
    conn.commit()

# Delete a row from events
def delete_event_from_events(conn, event_id):
    sql = "DELETE FROM events WHERE event_id=?"
    cursor = conn.cursor()
    cursor.execute(sql, (event_id,))
    conn.commit()

# Get all events for a specific day
# Returns list of (day, event, hexcode) for given date
def get_events_by_day(conn, day):
    sql = """
        SELECT dates.date_id, events.name, colors.hexcode
        FROM dates, events, colors
        WHERE dates.event_id = events.event_id
        AND events.color_id = colors.color_id
        AND dates.day=?
        """
    cursor = conn.cursor()
    cursor.execute(sql, (day,))
    return cursor.fetchall()

def get_event_names_by_day(conn, day):
    sql = """
        SELECT events.name
        FROM dates, events
        WHERE dates.event_id = events.event_id
        AND dates.day=?
        """
    cursor = conn.cursor()
    cursor.execute(sql, (day,))
    return cursor.fetchall()

def get_colors_by_day(conn, day):
    sql = """
        SELECT colors.hexcode
        FROM dates, events, colors
        WHERE dates.event_id = events.event_id
        AND events.color_id = colors.color_id
        AND dates.day=? 
        """
    cursor = conn.cursor()
    cursor.execute(sql, (day,))
    return cursor.fetchall()

# Get all colors
# Returns list of (ids, hexcodes)
def get_colors(conn):
    """_summary_

    Args:
        conn (_type_): _description_

    Returns:
        _type_: _description_
    """
    sql = "SELECT * FROM colors"
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()
    
def get_events(conn):
    """Returns list of (event_id, name, hexcode)

    Args:
        conn (sqlite3.Connection): Connection to database

    Returns:
        list: Return all rows as a list where each row is a tuple of
        (int: event_id, str: name, str: hexcode) where hexcode is
        missing the #
    """
    sql = """
        SELECT events.event_id, events.name, colors.hexcode 
        FROM events, colors
        WHERE events.color_id = colors.color_id
        """
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

def get_event_ids_by_day(conn, day_string):
    """Return list of event_ids -> int

    Args:
        conn (sqlite3.Connection): db connection
        day_string (str): string of date to search db for

    Returns:
        list: Return all rows as a list where each row is (event_id,)
    """
    sql = """
        SELECT dates.event_id FROM dates, events
        WHERE dates.event_id = events.event_id AND dates.day=?
        """
    cursor = conn.cursor()
    cursor.execute(sql, (day_string,))
    return cursor.fetchall()

def delete_event_from_day_by_event_id(conn, day_string, e_id):
    """Deletes from dates table an event by event_id for given day

    Args:
        conn (sqlite3.Connection): db connection
        day_string (str): string of date
        e_id (int): event_id
    """
    sql = """
        DELETE FROM dates WHERE day=? and event_id=?
        """
    cursor = conn.cursor()
    cursor.execute(sql, (day_string, e_id,))
    conn.commit()