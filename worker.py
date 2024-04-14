import time
import mysql.connector
import threading

def amazon_continuous_price_monitor():
    db_config = {
        "host": "localhost",
        "user": "root",
        "passwd": "password",
        "database": "users_for_dbms_project"  # Replace with your database name
    }
    my_db = mysql.connector.connect(**db_config)
    my_cursor = my_db.cursor()
    while True:
        my_cursor.execute("SELECT * FROM amazon_particular_prod")
        result = my_cursor.fetchall()
        if result:
            j = 0
            for i in result:
                print(j)
                print(i)
                j += 1
                time.sleep(10)

def flipkart_continuous_price_monitor():
    db_config = {
        "host": "localhost",
        "user": "root",
        "passwd": "password",
        "database": "users_for_dbms_project"
    }
    my_db = mysql.connector.connect(**db_config)
    my_cursor = my_db.cursor()
    while True:
        my_cursor.execute("SELECT * FROM flipkart_particular_prod")
        result = my_cursor.fetchall()
        if result:
            for i in result:
                print(i)
                time.sleep(10)
        print("price monitoring")
        time.sleep(100)

if __name__=="__main__":
    # Create threads for each function
    amazon_thread = threading.Thread(target=amazon_continuous_price_monitor)
    
    # Start the threads
    amazon_thread.start()
    
    # Main thread continues execution
    flipkart_continuous_price_monitor()
