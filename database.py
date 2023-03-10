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

# Get all colors
# Returns list of (ids, hexcodes)
def get_colors(conn):
    sql = "SELECT * FROM colors"
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()