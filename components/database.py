import os
import sqlite3

dir_path = os.path.join(os.environ['APPDATA'], 'Curtains')
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
file_path = os.path.join(dir_path, 'config.db')

# Connect to the database
conn = sqlite3.connect(file_path, check_same_thread=False)

# Create a cursor
cursor = conn.cursor()

# Create the table with the PRIMARY KEY constraint
cursor.execute("CREATE TABLE IF NOT EXISTS processes (proc_path TEXT PRIMARY KEY, hidden BOOL, icon BLOB)")
conn.commit()


def get_row(proc_path):
    # Execute the SELECT statement
    cursor.execute("SELECT * FROM processes WHERE proc_path=?", (proc_path,))

    # Fetch the row
    row = cursor.fetchone()
    if row:
        return row
    else:
        return None


def add_row(proc_path, hidden, icon):
    # Execute the INSERT statement
    cursor.execute("INSERT INTO processes (proc_path, hidden, icon) VALUES (?, ?, ?)", (proc_path, hidden, icon))

    # Commit the changes
    conn.commit()


def delete_row(proc_path):
    # Execute the DELETE statement
    cursor.execute("DELETE FROM processes WHERE proc_path=?", (proc_path,))

    # Commit the changes
    conn.commit()


def update_hidden(proc_path, hidden):
    # Update the row
    cursor.execute("UPDATE processes SET hidden = ? WHERE proc_path = ?", (hidden, proc_path))

    # Commit the changes
    conn.commit()


def read_locked_table():
    """returns dict: {process_path:{hidden:bool,icon:b64_str}"""
    cursor.execute("SELECT * FROM processes")

    # Fetch all rows
    rows = cursor.fetchall()

    processes = {}
    for row in rows:
        processes[row[0]] = {'hidden': bool(row[1]), 'icon': row[2]}
    return processes


def close():
    conn.close()
