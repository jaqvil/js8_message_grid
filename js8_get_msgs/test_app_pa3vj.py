from js8net import *
from datetime import datetime
import test_db_connect

test_db_connect.insert_heard( 
        datetime.now().strftime("%Y%m%d_%H%M%S.%f"), 
        7078000, 
        990, 
        7078990, 
        2, 
        "JO21tp", 
        "test type", 
        "test from call", 
        "test to call", 
        "test SNR", 
        "test value",
        0
        )
#test_db_connect.insert_heard( datetime.now().strftime("%Y%m%d_%H%M%S.%f"), "test type", "test from call", "test to call", "test SNR", "test value", 0 )


counter1 = 580
counter2 = 0

start_net("minipc1.lan",42442)
print("Possibly connected... Getting call & grid")
callsign = get_callsign()
print("Callsign = " + str(callsign))
grid = get_grid()
print("Grid = " + grid)

while(True):
    counter1 = counter1 + 1
    if counter1 < 600:
        if ( not (rx_queue.empty()) ):
            with rx_lock:
                message = rx_queue.get()
                #print(datetime.now().strftime("%Y%m%d_%H%M%S") + "\t" + str(message))
                if (message['type'] == "RX.DIRECTED"):
                    print(datetime.now().strftime("%Y%m%d_%H%M%S") + "\t" + str(message))
                    heartbeat_related_flag = 0
                    if "HEARTBEAT" in message.get("value"):
                        heartbeat_related_flag = 1
                    try:
                        test_db_connect.insert_heard( 
                                datetime.now().strftime("%Y%m%d_%H%M%S.%f"), 
                                message.get("params").get("DIAL"),
                                message.get("params").get("OFFSET"),
                                message.get("params").get("FREQ"),
                                message.get("params").get("SPEED"),
                                message.get("params").get("GRID"),
                                message.get("type"), 
                                message.get("params").get("FROM"), 
                                message.get("params").get("TO"), 
                                message.get("params").get("SNR"), 
                                message.get("value"),
                                heartbeat_related_flag
                                )
                    except Exception as err:
                        print( datetime.now().strftime("%Y%m%d_%H%M%S.%f") + " - exception: Trying to add entry to db failed" + str(err));
        time.sleep(0.1)
    else:
        counter1 = 0
        print(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "\tdebug - Still alive");
        callsign = get_callsign()
        print("callsign: " + str(callsign))
        if callsign == False:
            try:
                start_net("minipc1.lan",42442)
            except Exception as err:
                print( datetime.now().strftime("%Y%m%d_%H%M%S.%f") + " " + str(err) )
  
