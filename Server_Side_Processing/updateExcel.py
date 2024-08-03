import requests
import json
import msal
import openpyxl
import sqlite3
from datetime import datetime

# Microsoft Graph API endpoints and scopes
graph_api_endpoint = "https://graph.microsoft.com/v1.0"
excel_file_path = "/path/to/your/excel/file.xlsx"  # Update this path
scope = ["https://graph.microsoft.com/.default"]

# Function to get Azure AD credentials from the database
def get_azure_ad_credentials():
    conn = sqlite3.connect('ADCredentials.db')
    cursor = conn.cursor()
    cursor.execute("SELECT client_id, client_secret, tenant_id FROM credentials")
    client_id, client_secret, tenant_id = cursor.fetchone()
    conn.close()
    return client_id, client_secret, tenant_id

# Function to get an access token from Azure AD
def get_access_token(scope):
    client_id, client_secret, tenant_id = get_azure_ad_credentials()
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)
    result = app.acquire_token_silent(scope, account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=scope)
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception("Could not obtain access token")

# Function to update the Excel file using Microsoft Graph API
def update_excel_file(access_token, employee_data):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    workbook_url = f"{graph_api_endpoint}/me/drive/root:/{excel_file_path}:/workbook/worksheets"
    
    # Get the worksheet
    response = requests.get(workbook_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to get worksheet. Status code: {response.status_code}")
        return

    worksheets = response.json()["value"]
    sheet_id = worksheets[0]["id"]  # Assuming we're updating the first worksheet

    # Prepare the data for the API request
    cell_updates = [
        {
            "range": "A1",
            "values": [[
                "Employee Name", "Week", "Basic", "X1.5", "X2.0", "pay rate/hr", "Annual", "per month"
            ]]
        },
        {
            "range": "A2",
            "values": [[
                employee_data["Employee Name"],
                employee_data["Week"],
                employee_data["Basic"],
                employee_data["X1.5"],
                employee_data["X2.0"],
                employee_data["pay rate/hr"],
                employee_data["Annual"],
                employee_data["per month"]
            ]]
        }
    ]

    for update in cell_updates:
        update_url = f"{graph_api_endpoint}/me/drive/root:/{excel_file_path}:/workbook/worksheets/{sheet_id}/range(address='{update['range']}')"
        response = requests.patch(update_url, headers=headers, json={"values": update["values"]})
        if response.status_code != 200:
            print(f"Failed to update cell {update['range']}. Status code: {response.status_code}")
            return

    print("Excel sheet updated successfully.")

# Load calculated employee data
calculated_json_path = '/Users/nathanbrown-bennett/AutoTimeSheet/Server_Side_Processing/Server_Tests/Demo_Data/employee_data.json'
with open(calculated_json_path, 'r') as json_file:
    employee_data = json.load(json_file)

# Get access token
access_token = get_access_token(scope)

# Update the Excel file
update_excel_file(access_token, employee_data)
