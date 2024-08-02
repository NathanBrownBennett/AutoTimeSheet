import os
import json
from tkinter import Tk, filedialog
from docx import Document

# Ensure the directory exists
output_dir = os.path.join('json', 'weekly')
os.makedirs(output_dir, exist_ok=True)

# Define the json_path variable
json_path = "path/to/your/json/file.json"

# Correctly form the path using forward slashes or a raw string
calculated_json_path = os.path.join(output_dir, os.path.basename(json_path).replace('.json', '_calculated.json'))

print(f"Employee will be saved to {calculated_json_path}")

def list_files(directory):
    try:
        files = os.listdir(directory)
        files = [f for f in files if os.path.isfile(os.path.join(directory, f))]
        return files
    except FileNotFoundError:
        print(f"The directory {directory} does not exist.")
        return []

def print_menu(files):
    if not files:
        print("No files found.")
        return
    print("Select a file by number:")
    for i, file in enumerate(files, start=1):
        print(f"{i}. {file}")

def get_user_selection(files):
    while True:
        try:
            choice = int(input("Enter the number of the file you want to select: "))
            if 1 <= choice <= len(files):
                return files[choice - 1]
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def open_file_dialog():
    root = Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename()
    root.destroy()
    return file_path

def extract_daily_timesheet_data(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)

    extracted_data = {
        "Employee Name": data["Employee Name"],
        "Week Beginning": data["Week Beginning"],
        "Basic Hours": 0,
        "Overtime 1.5": 0,
        "Overtime 2.0": 0
    }

    for entry in data["Entries"]:
        if entry["DATE"] == "Total normal hrs.":
            extracted_data["Basic Hours"] = float(entry["BASIC HRS"])
        elif entry["DATE"] == "Overtime hrs":
            extracted_data["Overtime 1.5"] = float(entry["O/T 1.5"])
            extracted_data["Overtime 2.0"] = float(entry["O/T 2.0"]) if entry["O/T 2.0"] else 0.0

    output_dir = 'json/weekly'
    os.makedirs(output_dir, exist_ok=True)
    output_file_path = os.path.join(output_dir, os.path.basename(json_path).replace('.json', '_hours.json'))

    with open(output_file_path, 'w') as file:
        json.dump(extracted_data, file, indent=4)

    print(f"Extracted hours data saved to {output_file_path}")


def update_ignore_list(json_path):
    with open('ignoreList.txt', 'a') as ignore_file:
        ignore_file.write(json_path + '\n')

def load_ignore_list():
    try:
        with open('ignoreList.txt', 'r') as ignore_file:
            ignore_list = ignore_file.read().splitlines()
    except FileNotFoundError:
        ignore_list = []
    return ignore_list

def main():
    fixed_directory = 'timesheets'
    output_directory = 'json/daily'
    os.makedirs(output_directory, exist_ok=True)

    print("Choose an option:")
    print("1. Select a Word document from the fixed directory to extract timesheet data")
    print("2. Select a JSON file for calculation from the fixed directory")
    choice = input("Enter your choice (1, 2): ")

    ignore_list = load_ignore_list()
    if choice == '1':
        files = list_files(fixed_directory)
        if files:
            print_menu(files)
            selected_file = get_user_selection(files)
            selected_file_path = os.path.join(fixed_directory, selected_file)
            print(f"You selected: {selected_file_path}")
        elif files in ignore_list:
            print("This file has already been processed.")
            return
        else:
            print("No files available in the directory.")
            return
    elif choice == '2':
        json_files = list_files(output_directory)
        if json_files:
            print_menu(json_files)
            selected_file = get_user_selection(json_files)
            selected_file_path = os.path.join(output_directory, selected_file)
            print(f"You selected: {selected_file_path}")
        elif selected_file_path in ignore_list:
            print("This file has already been processed.")
            return
        else:
            print("No files available in the directory.")
            return
    # Extract timesheet data from the selected Word document if choice 1 or 2
    if choice in ['1', '2']:
        timesheet_data = extract_daily_timesheet_data(selected_file_path)

        # Define the output path for the JSON file
        json_filename = os.path.splitext(os.path.basename(selected_file_path))[0] + '.json'
        json_path = os.path.join(output_directory, json_filename)

if __name__ == "__main__":
    main()
