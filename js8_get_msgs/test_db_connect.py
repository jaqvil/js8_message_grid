import mysql.connector
from datetime import datetime


def show_databases():
    cnx = mysql.connector.connect(user='js8user', password='!resu8sj', host='192.168.1.37', database='JS8Call_db')
    cursor = cnx.cursor()
    query = ("SHOW DATABASES;")
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print (x)
    cursor.close()
    cnx.close()


def insert_heard(_timestamp, _freq_dial, _freq_offset, _freq_actual, _speed, _grid, _type, _call_from, _call_to, _snr, _value, _heartbeat_related):
    # print("_timestamp: " + _timestamp)
    # print("_type: " + _type)
    # print("_value: " + _value)
    cnx = mysql.connector.connect(user='js8user', password='!resu8sj', host='192.168.1.37', database='JS8Call_db')
    cursor = cnx.cursor()
    query = ("INSERT INTO Heard_msgs (Timestamp, freq_dial, freq_offset, freq_actual, speed, grid, type, call_from, call_to, snr, value, heartbeat_related) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    values = ( _timestamp, _freq_dial, _freq_offset, _freq_actual, _speed, _grid, _type, _call_from, _call_to, _snr, _value, _heartbeat_related )
    cursor.execute(query, values)
    
    cnx.commit()
    cursor.close()
    cnx.close()


def show_top_100_entries():
    cnx = mysql.connector.connect(user='js8user', password='!resu8sj', host='192.168.1.37', database='JS8Call_db')
    cursor = cnx.cursor()
    query = ("SELECT * FROM Heard_msgs;")
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print (x)
    cursor.close()
    cnx.close()





if __name__ == '__main__':

    show_databases()

    insert_heard( datetime.now().strftime("%Y%m%d_%H%M%S.%f"), 7078000, 990, 7078990, 2, "JO21tp", "test type", "test from call", "test to call", "test SNR", "test value", 0 )

    show_top_100_entries()





