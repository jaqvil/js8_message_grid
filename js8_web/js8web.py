from threading import Thread
from datetime import datetime
from flask import Flask, render_template, request
import mysql.connector



app = Flask(__name__)
# MySQL Configuration
db_config = {
            'host': '192.168.1.37',
            #'host': 'mariadb-vm.lan',
            'user': 'js8user',
            'password': '!resu8sj',
            'database': 'JS8Call_db'
            }

DEBUGGING = False

# Function to fetch data from MySQL
def get_data_from_mysql(category_filter=None):
    if DEBUGGING:
        print("starting get_data_from_mysql")
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Modify this query according to your database schema
        query = "SELECT `Timestamp`, freq_actual, grid, call_from, call_to, snr, `value` FROM Heard_msgs"
        if category_filter:
            #categories = ",".join(["'{}'".format(cat) for cat in category_filter])
            if "no_hb" in category_filter:
                query += " WHERE heartbeat_related = 0" 

        query += " ORDER BY `id` DESC LIMIT 500"

        cursor.execute(query)
         
        # Fetch all rows
        data = cursor.fetchall()
        
        if DEBUGGING:
            print("Debugging:")
            print("Query: ", query)
            print("")

            tempcounter = 1
            for item in data:
                print(item)
                if tempcounter >= 10:
                    break;
                tempcounter = tempcounter + 1

        cursor.close()
        connection.close()
        
        return data
    except mysql.connector.Error as error:
        print("Error:", error)
        return None



### This is to insert the calling IP address and the amount of bytes passed to it
### in the dB table - for interest
### moved to own function so that we can call it from a seperate thread
def insert_requesting_ip_to_db(_ip_source_addr, _data_length):
    
    print("Timestamp start ip_addr dB insert: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        connector = mysql.connector.connect(**db_config)
        cursor = connector.cursor()
        query = ("INSERT INTO WebQuery (`Timestamp`, IP_source_addr, Data_length) VALUES (%s, %s, %s)")
        values = (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), _ip_source_addr, _data_length)
        cursor.execute( query, values)
        connector.commit()
        cursor.close()
        connector.close()

        print("Timestamp after ip_addr dB insert: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    except Exception as ex:
        print("Error inserting requesting IP addr\n", ex)



@app.route('/')
def display_data():
    print("Timestamp at request: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    requesting_ip = request.remote_addr
    #print(requesting_ip)
    category_filter = request.args.getlist('category')
    # Fetch data from MySQL
    data = get_data_from_mysql(category_filter)
    print("Timestamp after getting data: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Requesting IP: ", requesting_ip)

    # insert to dB
    thread = Thread(target=insert_requesting_ip_to_db, args=(requesting_ip, len(data)))
    thread.start()
   
    if data:
        # Pass the data to the HTML template
        print("Timestamp before render_template: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return render_template('index.html', data=data)
    
    return "Failed to retrieve data from the database."

if __name__ == '__main__':
    app.run(
            debug=False,
            host='0.0.0.0'
            )
