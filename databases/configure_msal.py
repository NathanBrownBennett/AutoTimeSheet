import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """Create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """Create a table from the create_table_sql statement"""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def upsert_config(conn, config_data):
    """
    Insert or update configuration data into the config table
    config_data: tuple (client_id, client_secret, tenant_id, scope, graph_api_endpoint, excel_file_path)
    """
    sql = '''INSERT OR REPLACE INTO config(name, value)
             VALUES(?, ?)'''
    try:
        c = conn.cursor()
        for name, value in config_data.items():
            c.execute(sql, (name, value))
        conn.commit()
    except Error as e:
        print(e)

def main():
    database = r"msal.db"

    sql_create_config_table = """ CREATE TABLE IF NOT EXISTS config (
                                        name text PRIMARY KEY,
                                        value text NOT NULL
                                    ); """

    # Configuration data
    config_data = {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "tenant_id": "your_tenant_id",
        "scope": "your_scope",
        "graph_api_endpoint": "your_graph_api_endpoint",
        "excel_file_path": "your_excel_file_path"
    }

    # Create a database connection
    conn = create_connection(database)

    # Create config table if it doesn't exist
    if conn is not None:
        create_table(conn, sql_create_config_table)
        upsert_config(conn, config_data)
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()