import sqlite3

def create_connection():
    return sqlite3.connect("cournell-course-sphere-data/roster_reviews.sqlite.db")

def execute_query(query, parameters=()):
    with create_connection() as connection:
        cursor = connection.execute(query, parameters)
        if cursor.description:
            return cursor.fetchall()
        return []

if __name__ == '__main__':
    execute_query()
