import sqlite3
from sqlite3 import Error


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
    # TODO create a method to add dates in batches, prevents creation and deletion of multiple cursors
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


def get_events_name_hexcode_by_day(conn, day):
    sql = """
        SELECT events.name, colors.hexcode
        FROM dates, events, colors
        WHERE dates.event_id = events.event_id
        AND events.color_id = colors.color_id
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


def get_events_with_color_id(conn: sqlite3.Connection):
    """Returns list of (event_id, name, hexcode, color_id)

    Args:
        conn (sqlite3.Connection): Connection to database

    Returns:
        list: Return all rows as a list where each row is a tuple of
        (int: event_id, str: name, str: hexcode, int: color_id) where hexcode is
        missing the #
    """
    sql = """
        SELECT events.event_id, events.name, colors.hexcode, colors.color_id 
        FROM events, colors
        WHERE events.color_id = colors.color_id
        """
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()


def check_if_hexcode_exists(conn: sqlite3.Connection, hexcode: str) -> int:
    """Search colors table to check if color with specific hexcode exists.

    Args:
        conn (sqlite3.Connection): db connection
        hexcode (str): Hexcode to be searched for

    Returns:
        int: 1 if found, None if not
    """
    sql = """
        select colors.color_id from colors where colors.hexcode=?
        """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (hexcode,))
    except:
        print("database.py :: could not check if hexcode exists")
    finally:
        return cursor.fetchone()


def check_if_event_name_exists(conn: sqlite3.Connection, name: str) -> int:
    """Search events table to check if event with specific name exists.

    Args:
        conn (sqlite3.Connection): db connection
        name (str): Name to be searched for

    Returns:
        int: 1 if found, None if not
    """
    sql = """
        SELECT event_id
        FROM events
        WHERE name LIKE ?
        """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (name,))
    except:
        print("database.py :: could not check if event name exists")
    finally:
        return cursor.fetchone()


def get_events_name_hexcode(conn):
    """Returns list of (name, hexcode)

    Args:
        conn (sqlite3.Connection): Connection to database

    Returns:
        list: Return all rows as a list where each row is a tuple of
        (str: name, str: hexcode) where hexcode is missing the #
    """
    sql = """
        SELECT events.name, colors.hexcode 
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
    cursor.execute(
        sql,
        (
            day_string,
            e_id,
        ),
    )
    conn.commit()


def edit_event_color(conn: sqlite3.Connection, c_id: int, e_id: int):
    """Edit color associated with event

    Args:
        conn (sqlite3.Connection): db connection
        c_id (int): color_id of new color
        e_id (int): event_id of event to be edited
    """
    sql = """
        UPDATE events
        SET color_id = ?
        WHERE event_id = ?
        """
    cursor = conn.cursor()
    cursor.execute(
        sql,
        (
            c_id,
            e_id,
        ),
    )
    conn.commit()


def edit_event_name(conn: sqlite3.Connection, name: str, e_id: int):
    """Edit name of event

    Args:
        conn (sqlite3.Connection): db connection
        name (str): New name of event
        e_id (int): event_id of event to be edited
    """
    sql = """
        UPDATE events
        SET name = ?
        WHERE event_id = ?
        """
    cursor = conn.cursor()
    cursor.execute(
        sql,
        (
            name,
            e_id,
        ),
    )
    conn.commit()


def edit_event_name_and_color(conn: sqlite3.Connection, name: str, c_id, e_id):
    """Edit both name and color associated with event

    Args:
        conn (sqlite3.Connection): db connection
        name (str): New name of event
        c_id (int): color_id of new color of event
        e_id (int): event_id of event to be changed
    """
    sql = """
        UPDATE events
        SET name = ?, color_id = ?
        WHERE event_id = ?
        """
    cursor = conn.cursor()
    cursor.execute(
        sql,
        (
            name,
            c_id,
            e_id,
        ),
    )
    conn.commit()


def edit_color_hexcode(conn: sqlite3.Connection, hexcode: str, c_id: int):
    """Edit the hexcode value associated with a color

    Args:
        conn (sqlite3.Connection): db connection
        hexcode (str): hexcode value
        c_id (int): color_id of color to be edited
    """
    sql = """
        UPDATE colors
        SET hexcode = ?
        WHERE color_id = ?
        """
    cursor = conn.cursor()
    cursor.execute(
        sql,
        (
            hexcode,
            c_id,
        ),
    )
    conn.commit()
