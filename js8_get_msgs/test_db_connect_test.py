import unittest
import mysql.connector

class TestDBConnection(unittest.TestCase):

    def test_connection(self):
        try:
            cnx = mysql.connector.connect(user='js8user', password='!resu8sj', host='192.168.1.37', database='JS8Call_db')
            cursor = cnx.cursor()
            cursor.execute("SHOW TABLES LIKE 'Heard_msgs'")
            result = cursor.fetchone()
            self.assertIsNotNone(result, "Heard_msgs table does not exist in the database.")
        except mysql.connector.Error as err:
            self.fail(f"Database connection failed: {err}")
        finally:
            if cursor:
                cursor.close()
            if cnx:
                cnx.close()

if __name__ == '__main__':
    unittest.main()
