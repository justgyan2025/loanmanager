import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        host="dpg-cuoaekqj1k6c7396g120-a.oregon-postgres.render.com",
        user="shiv",
        password="G49sKpivIJaEJbenKkpJm9A6FM7HAYiR",
        port="5432"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    # Create a cursor object
    cur = conn.cursor()
    
    try:
        # Create database
        cur.execute("CREATE DATABASE loan_manager_0bal")
        print("Database created successfully!")
        
    except psycopg2.Error as e:
        print(f"Error creating database: {e}")
    
    finally:
        # Close cursor and connection
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_database() 