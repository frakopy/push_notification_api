import sqlite3
from datetime import datetime



def normalize_date(date_str):
    if not date_str:
        return None
    
    # 1. Try format with 'T' (from browser: YYYY-MM-DDTHH:MM)
    try:
        # Try with seconds
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            # Try without seconds
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass # Not a 'T' format

    # 2. Try format with space (from n8n: YYYY-MM-DD HH:MM:SS)
    try:
        # Try with seconds
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            # Try without seconds
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass

    # If it reaches here, the format is unknown
    raise ValueError(f"Date format not supported: {date_str}")

def drop_table():
    conn = sqlite3.connect("notification.db")
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS tasks")

    conn.commit()
    conn.close()

def create_table():
    conn  = sqlite3.connect("notification.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NOT NULL,
        frequency TEXT NOT NULL,
        next_run DATETIME NOT NULL,
        status TEXT NOT NULL,
        topic TEXT NOT NULL,
        UNIQUE(message, next_run)
    );
    """)

    conn.commit()
    conn.close()

def insert_record(**kwargs):
    message = kwargs["message"]
    frequency = kwargs["frequency"]
    next_run = normalize_date(kwargs["next_run"]) # Calling function to normalize date
    status = kwargs["status"]
    topic = kwargs["topic"]

    try:
        conn  = sqlite3.connect("notification.db")
        cursor = conn.cursor()
        query = """
        INSERT INTO tasks (message, frequency, next_run, status, topic)
        VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(query, (message, frequency, next_run, status, topic))
        conn.commit()
        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"Error adding a new record: {e}")
        return False

def delete_record(task_id):
    try:
        conn  = sqlite3.connect("notification.db")
        cursor = conn.cursor()
        query_delete = "DELETE FROM tasks WHERE id = ?"
        cursor.execute(query_delete, (task_id,))
        conn.commit()
        conn.close()
        print("Record was successfuly deleted!")
        return True
    except:
        return False


def update_record(task_id, **kwargs): 
    conn = sqlite3.connect("notification.db")
    cursor = conn.cursor()

    if kwargs["next_run"]:
        kwargs["next_run"] = normalize_date(kwargs["next_run"])

    fields = [f"{key} = ?" for key in kwargs.keys()]
    values = [value for value in kwargs.values()]

    values.append(task_id)
    query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
    
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def get_due_tasks():
    conn = sqlite3.connect("notification.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
    SELECT id, message, frequency, next_run, status, topic
    FROM tasks
    WHERE status = 'Active'
    AND next_run <= datetime('now')
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_task(task_id):
    conn = sqlite3.connect("notification.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = f"""
    SELECT id, message, frequency, next_run, status, topic
    FROM tasks WHERE id = {task_id}
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]

def get_task_list():
    conn = sqlite3.connect("notification.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
    SELECT id, message, frequency, next_run, status, topic
    FROM tasks
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]

if __name__ == "__main__":

    # fields = {"next_run":"2026-07-07T9:45"}
    # update_record(12, **fields)
    tasks =  get_due_tasks()
    print(tasks)
