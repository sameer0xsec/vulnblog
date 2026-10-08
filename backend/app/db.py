import mysql.connector
import os

def get_conn():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "vulnblog"),
        password=os.environ.get("DB_PASS", "vulnblog123"),
        database=os.environ.get("DB_NAME", "vulnblog"),
    )

def run_raw(sql):
    """VULN: executes caller-built SQL strings directly — used by routes that
    concatenate user input into queries instead of parameterizing. Kept as a
    separate helper so every raw-SQL call site is easy to find/grep."""
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql)
    try:
        rows = cur.fetchall()
    except mysql.connector.errors.InterfaceError:
        rows = []
    conn.commit()
    cur.close()
    conn.close()
    return rows
