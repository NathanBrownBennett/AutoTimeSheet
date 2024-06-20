# Timesheet Processing Application

## Overview
This application is designed to automate the process of extracting, processing, and updating timesheet data from documents. It provides a web interface for users to upload timesheet documents, processes these documents to extract relevant data, calculates hours and pay based on the extracted data, and updates an external Excel sheet via an API. Additionally, the application allows users to download a timesheet template for their convenience.

## Features
- **Upload Timesheet:** Users can upload their timesheet documents in .docx format. The application checks if the uploaded file is in the allowed format before processing.
- **Extract Timesheet Data:** Extracts data such as employee name, week beginning, and daily entries from the uploaded document.
- **Calculate Hours and Pay:** Processes the extracted timesheet data to calculate total hours worked, including basic hours and overtime, and computes the pay.
- **Update Excel Sheet:** Updates an external Excel sheet with the calculated data using an API.
- **Download Timesheet Template:** Users can download a timesheet template document to fill out for their next submission.

## Installation
To set up the application, follow these steps:
1. Clone the repository to your local machine.
2. Ensure you have Python installed. This application was developed with Python 3.8.
3. Install the required Python packages using pip:
    ```
    pip install -r requirements.txt
    ```
4. **Important:** Before running the application, you must set up the Azure AD credentials for API authentication. Run [`create_ADCredentialsdb.py`] to create and configure the credentials database:
    ```
    python create_ADCredentialsdb.py
    ```
    Follow the prompts to enter your Azure AD Client ID, Client Secret, and Tenant ID. These credentials are necessary for the application to authenticate and update the Excel sheet via the API.
5. Configure the application settings in app.py, including the upload and processed folders' paths, and allowed file extensions.
6. Start the application:
    ```
    python app.py
    ```
7. The application will be accessible at http://localhost:5000.

## Usage
- **Uploading a Timesheet:**
  1. Navigate to http://localhost:5000.
  2. Use the upload form to select and upload your timesheet document.
- **Downloading a Timesheet Template:**
  - Click on the link provided on the main page to download a timesheet template.
- **Viewing Processed Data:**
  - After uploading a timesheet, the application will automatically process the document and provide a link to download the processed data in JSON format.

## Configuration
- **API Configuration:** Ensure you have run [`create_ADCredentialsdb.py`] to set up your Azure AD credentials for API authentication. Update [`updateexcel.py`] with your specific requirements to enable updating the Excel sheet.
- **File Extensions:** Modify app.config['ALLOWED_EXTENSIONS'] in app.py to change allowed file types for upload.

## Dependencies
- Flask: For creating the web application.
- python-docx: For reading and writing .docx files.
- requests: For making API requests to update the Excel sheet.

## Contributing
Contributions to the Timesheet Processing Application are welcome. Please ensure to follow the project's coding standards and submit a pull request for review.

## License
This project is licensed under the MIT License - see the LICENSE file for details.