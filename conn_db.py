import psycopg2 

def db_conn():
    conn = psycopg2.connect(
        database='pgbp',
        host='localhost',
        user='postgres',
        password='1719',
        port='5432'
    )
    return conn 
