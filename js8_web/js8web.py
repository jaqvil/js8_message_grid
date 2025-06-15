from threading import Thread
from datetime import datetime
from flask import Flask, render_template, request, jsonify
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


def get_data_from_mysql(category_filter=None, search_column=None, search_value=None, limit=500):
    """
    Function to fetch data from MySQL
    """
    if DEBUGGING:
        print("starting get_data_from_mysql")
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Base query
        query = "SELECT `Timestamp`, freq_actual, grid, call_from, call_to, snr, `value` FROM Heard_msgs"
        where_clauses = []

        # Add category filter if specified
        if category_filter:
            if "no_hb" in category_filter:
                where_clauses.append("heartbeat_related = 0")

        # Add search filter if specified
        if search_column and search_value:
            column_index = {
                'Timestamp': 0,
                'Frequency': 1,
                'Grid': 2,
                'From': 3,
                'To': 4,
                'SNR': 5,
                'Message': 6
            }
            
            if search_column in column_index:
                column_name = {
                    'Timestamp': '`Timestamp`',
                    'Frequency': 'freq_actual',
                    'Grid': 'grid',
                    'From': 'call_from',
                    'To': 'call_to',
                    'SNR': 'snr',
                    'Message': '`value`'
                }[search_column]
                
                where_clauses.append(f"{column_name} LIKE %s")
                search_value = f"%{search_value}%"

        # Combine where clauses
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        # Add order and limit
        query += " ORDER BY `id` DESC LIMIT %s"

        # Prepare parameters
        params = []
        if search_column and search_value:
            params.append(search_value)
        params.append(limit)

        cursor.execute(query, tuple(params))

        # Fetch all rows
        data = cursor.fetchall()

        if DEBUGGING:
            print("Debugging:")
            print("Query: ", query)
            print("Parameters: ", params)
            print("")

            tempcounter = 1
            for item in data:
                print(item)
                if tempcounter >= 10:
                    break
                tempcounter = tempcounter + 1

        cursor.close()
        connection.close()

        return data
    except mysql.connector.Error as error:
        print("Error:", error)
        return None




def insert_requesting_ip_to_db(_ip_source_addr, _data_length):
    """
    This is to do a database insert the calling IP address 
    and the amount of bytes passed to it  - for interest
    moved to own function so that we can call it from a seperate thread
    """
    print("Timestamp start ip_addr dB insert: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        connector = mysql.connector.connect(**db_config)
        cursor = connector.cursor()
        query = "INSERT INTO WebQuery (`Timestamp`, IP_source_addr, Data_length) VALUES (%s, %s, %s)"
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
    """
    The mothod called to show fetched data on a webpage
    """
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

def get_latest_message_id():
    """
    Function to get the ID of the latest message
    """
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "SELECT MAX(id) FROM Heard_msgs"
        cursor.execute(query)
        latest_id = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return latest_id
    except mysql.connector.Error as error:
        print("Error:", error)
        return None

@app.route('/check_updates')
def check_updates():
    """
    Endpoint to check if there are new messages
    """
    latest_id = get_latest_message_id()
    return jsonify({'latest_id': latest_id})

@app.route('/search_more')
def search_more():
    """
    Endpoint to fetch more historical data for a search
    """
    print("Timestamp at search_more: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    search_column = request.args.get('column')
    search_value = request.args.get('value')
    current_count = int(request.args.get('count', 0))
    
    if not search_column or not search_value:
        return jsonify({'error': 'Missing search parameters'}), 400

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Map frontend column names to database column names
        column_mapping = {
            'Timestamp': '`Timestamp`',
            'Frequency': 'freq_actual',
            'Grid': 'grid',
            'From': 'call_from',
            'To': 'call_to',
            'SNR': 'snr',
            'Message': '`value`'
        }

        # Get the database column name
        db_column = column_mapping.get(search_column)
        if not db_column:
            return jsonify({'error': 'Invalid column name'}), 400

        # Construct the query to fetch more historical data
        query = f"""
            SELECT `Timestamp`, freq_actual, grid, call_from, call_to, snr, `value`
            FROM Heard_msgs
            WHERE LOWER({db_column}) LIKE LOWER(%s)
            ORDER BY `id` DESC
            LIMIT 1000
        """

        # Execute the query with the search value
        cursor.execute(query, (f"%{search_value}%",))
        
        # Fetch all rows
        data = cursor.fetchall()

        cursor.close()
        connection.close()

        if data:
            return jsonify({
                'data': data,
                'count': len(data)
            })
        return jsonify({'error': 'No data found'}), 404

    except mysql.connector.Error as error:
        print("Database error:", error)
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(
            debug=False,
            host='0.0.0.0'
            )
