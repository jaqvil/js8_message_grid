import mysql.connector

db_config = {
            'host': '192.168.1.37',
            'user': 'js8user',
            'password': '!resu8sj',
            'database': 'JS8Call_db'
        }

print("connecting to db")

try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute("SHOW COLUMNS FROM Heard_msgs")

    data = cursor.fetchall()

    for item in data:
        print(item)
        #sleep(1)

    cursor.close()
    connection.close()
    

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Heard_msgs WHERE `Timestamp` LIKE '%:%:%' ORDER BY `id` DESC LIMIT 5")

    data = cursor.fetchall()

    for item in data:
        print(item)
        #sleep(1)

    cursor.close()
    connection.close()

except:
    print("exception")

