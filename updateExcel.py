import requests
import json
from sheet2api import Sheet2APIClient

client = Sheet2APIClient(api_url='https://sheet2api.com/v1/7uu7v96xRROY/time-sheet')
client.get_rows()

# Load calculated employee data
calculated_json_path = '/mnt/data/employee_data.json'
with open(calculated_json_path, 'r') as json_file:
    employee_data = json.load(json_file)

# API endpoint and key (replace with actual values)
api_endpoint = "https://sheet2api.com/v1/{your_api_endpoint}"
api_key = "YOUR_API_KEY"

# Prepare the data for the API request
api_data = {
    "Employee Name": employee_data["Employee Name"],
    "Week": employee_data["Week"],
    "Basic": employee_data["Basic"],
    "X1.5": employee_data["X1.5"],
    "X2.0": employee_data["X2.0"],
    "pay rate/hr": employee_data["pay rate/hr"],
    "Annual": employee_data["Annual"],
    "per month": employee_data["per month"]
}

# Make the API request to update the Excel sheet
response = requests.post(api_endpoint, headers={"Authorization": f"Bearer {api_key}"}, json=api_data)

if response.status_code == 200:
    print("Excel sheet updated successfully.")
else:
    print(f"Failed to update Excel sheet. Status code: {response.status_code}")
