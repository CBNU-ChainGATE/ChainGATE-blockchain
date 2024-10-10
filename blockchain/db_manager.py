import mysql.connector
from mysql.connector import Error


class MySQLManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")

    def close(self):
        if self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            self.connection.commit()
            print("Query executed successfully")
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()

    def fetch_query(self, query, params=None):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()

    def get_total_count(self):
        query = "SELECT COUNT(*) FROM entrance_log"
        result = self.fetch_query(query)
        if result:
            return result[0]['COUNT(*)']
        else:
            return 0

    def insert_entrance_log(self, previous_hash, timestamp, date, time, employee_id, name, position, department):
        insert_query = """
        INSERT INTO entrance_log (previous_hash, timestamp, date, time, employee_id, name, position, department)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        self.execute_query(insert_query, (previous_hash, timestamp,
                           date, time, employee_id, name, position, department))

    def search_data(self, date=None, employee_id=None, name=None, department=None):
        query = "SELECT date, time, employee_id, name, department, position FROM entrance_log"
        conditions = []
        params = []

        if date:
            conditions.append("date = %s")
            params.append(date)
        if employee_id:
            conditions.append("employee_id = %s")
            params.append(employee_id)
        if name:
            conditions.append("name = %s")
            params.append(name)
        if department:
            conditions.append("department = %s")
            params.append(department)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        else:
            return False

        results = self.fetch_query(query, tuple(params))
        return results
