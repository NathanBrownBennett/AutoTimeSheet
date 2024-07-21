import sqlite3

def create_database():
    conn = sqlite3.connect('ADCredentials.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS credentials
                      (client_id TEXT, client_secret TEXT, tenant_id TEXT)''')
    conn.commit()
    conn.close()

def insert_credentials(client_id, client_secret, tenant_id):
    conn = sqlite3.connect('ADCredentials.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM credentials")  # Clear existing credentials
    cursor.execute("INSERT INTO credentials (client_id, client_secret, tenant_id) VALUES (?, ?, ?)",
                   (client_id, client_secret, tenant_id))
    conn.commit()
    conn.close()

def main():
    create_database()
    client_id = input("Enter Azure AD Client ID: ")
    client_secret = input("Enter Azure AD Client Secret: ")
    tenant_id = input("Enter Azure AD Tenant ID: ")
    insert_credentials(client_id, client_secret, tenant_id)
    print("Azure AD credentials have been saved successfully.")

if __name__ == "__main__":
    main()