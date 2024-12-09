import mysql.connector
from datetime import datetime

def show_databases():
    """
    Show all databases in the MySQL server.
    """
    cnx = mysql.connector.connect(user='js8user', password='!resu8sj', host='192.168.1.37', database='JS8Call_db')
    cursor = cnx.cursor()
    query = ("SHOW DATABASES;")
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    cursor.close()
    cnx.close()

def insert_heard(_timestamp, _freq_dial, _freq_offset, _freq_actual, _speed, _grid, _type, _call_from, _call_to, _snr, _value, _heartbeat_related):
    """
    Insert a heard message into the database.

    Args:
        _timestamp (str): Timestamp of the message.
        _freq_dial (int): Dial frequency.
        _freq_offset (int): Offset frequency.
        _freq_actual (int): Actual frequency.
        _speed (int): Speed.
        _grid (str): Grid.
        _type (str): Type of message.
        _call_from (str): Call from.
        _call_to (str): Call to.
        _snr (str): Signal-to-noise ratio.
        _value (str): Value.
        _heartbeat_related (int): Heartbeat related.
    """
    cnx = mysql.connector.connect(user='js8user', password='!resu8sj', host='192.168.1.37', database='JS8Call_db')
    cursor = cnx.cursor()
    query = ("INSERT INTO Heard_msgs (Timestamp, freq_dial, freq_offset, freq_actual, speed, grid, type, call_from, call_to, snr, value, heartbeat_related) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    values = (_timestamp, _freq_dial, _freq_offset, _freq_actual, _speed, _grid, _type, _call_from, _call_to, _snr, _value, _heartbeat_related)
    cursor.execute(query, values)
    cnx.commit()
    cursor.close()
    cnx.close()

def show_top_100_entries():
    """
    Show the top 100 entries in the Heard_msgs table.
    """
    cnx = mysql.connector.connect(user='js8user', password='!resu8sj', host='192.168.1.37', database='JS8Call_db')
    cursor = cnx.cursor()
    query = ("SELECT * FROM Heard_msgs;")
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    cursor.close()
    cnx.close()

if __name__ == '__main__':
    show_databases()
    insert_heard(datetime.now().strftime("%Y%m%d_%H%M%S.%f"), 7078000, 990, 7078990, 2, "JO21tp", "test type", "test from call", "test to call", "test SNR", "test value", 0)
    show_top_100_entries()
