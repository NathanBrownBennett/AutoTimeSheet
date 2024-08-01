# Business Productivity Optimization App

## Overview
The Business Productivity Optimization App is designed to streamline and enhance productivity within an organization by managing timesheets, job cards, tasks, and organizational settings through a web interface. This application provides features for both administrators and regular users, with specific functionalities tailored to their roles.

## Features
User Authentication and Management

User login and logout.
User registration with verification code.
Admins can create, delete, and manage user accounts.
Password change notifications.
Timesheet Management

Create and upload timesheets.
Convert timesheet data from documents to JSON.
Admin review and approval of timesheets.
Timesheets linked to an organizational calendar.
Job Card Management

Create and manage job cards.
Admin review and approval of job cards.
Task Management

Create, modify, and delete tasks.
Tasks organized in a job board with sections for To-Do, In-Progress, and Completed.
Tasks can be moved between sections.
Organization Management

Admins can manage organization settings.
Upload company logo.
Request company name changes.
Email Notifications

Notifications for user login, registration, password changes, and task updates.
Timesheet and job card submission notifications.
Admins notified of all critical changes and submissions.
Calendar Integration

Interactive linked calendar visible to all organization members.
Calendar events can be added and managed by users.
Admin approval for specific events like sick days or holidays.

Setup Instructions
**Prerequisites**
```
Python 3.11+
Flask
Flask-SQLAlchemy
Flask-Login
Flask-Migrate
Flask-Mail
```
**Other dependencies as listed in requirements.txt**

# Installation
Clone the Repository
sh
```
git clone https://github.com/yourusername/business-productivity-optimization-app.git
cd business-productivity-optimization-app
```

## Create a Virtual Environment and Install Dependencies
sh
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Set Up the Database
Initialize the database and apply migrations:

sh
```
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Run the Application
sh
```
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

# Configuration
Update the configuration in config.py with your specific settings, such as email server details and database URI.

Project Structure
```
graphql
.
├── app.py                  # Main application entry point
├── models.py               # Database models
├── extensions.py           # Extensions and app factory
├── sqlalch_config.py       # SQLAlchemy and app configuration
├── routes/
│   ├── admin.py            # Admin-related routes
│   ├── account.py          # Account-related routes
│   ├── main.py             # Main app routes
│   ├── tasks.py            # Task-related routes
│   └── email_utils.py      # Email utility functions
├── templates/
│   ├── index.html          # Main index template
│   ├── login.html          # Login template
│   ├── register.html       # Registration template
│   ├── account_settings.html # Account settings template
│   ├── admin_dashboard.html  # Admin dashboard template
│   ├── create_job_card.html  # Create job card template
│   ├── create_timesheet.html # Create timesheet template
│   ├── employee_settings.html # Employee settings template
│   ├── info.html            # Info page template
│   └── verification.html     # Verification code template
├── static/
│   ├── style.css            # Main stylesheet
│   └── default_logo.png     # Default company logo
└── requirements.txt        # Project dependencies
```

## Key Functions

### app.py
create_app(): Initializes the Flask app with all configurations, extensions, and blueprints.
load_user(user_id): Loads a user by ID for Flask-Login.

### routes/admin.py
admin_dashboard(): Handles the admin dashboard, user creation, and displays all users.
create_job_card(): Creates a new job card.
create_timesheet(): Creates a new timesheet.

### routes/account.py
account_settings(): Displays account settings for the current user's organization.
update_account_settings(): Updates account settings for a user.
upload_logo(): Handles logo upload for the current user's organization.
request_company_name_change(): Handles company name change requests.
logout(): Logs out the current user.

### routes/main.py
index(): Displays the index page with tasks for the current user.
login(): Handles user login.
register(): Handles user registration.
info(): Displays application information.
upload_file(): Handles file uploads.

### routes/tasks.py
create_task(): Creates a new task for the current user.
delete_task(task_id): Deletes a task if the current user is an admin or the task owner.
modify_task() : modifies the entry for that task card by the tasks' id

### routes/email_utils.py
send_email(subject, recipients, body): Sends an email using Flask-Mail.
extensions.py
db: SQLAlchemy instance.
migrate: Flask-Migrate instance.
login_manager: Flask-Login instance.
mail: Flask-Mail instance.

### models.py : Defines SQLAlchemy models for User, Organisation, Config, Role, Timesheet, JobCard, and Task.

## Usage
User Registration and Verification
Users register and receive a verification code via email.
Enter the verification code on the verification page to activate the account.

## Admin Dashboard
Admins can manage users, review timesheets, and job cards, and update organization settings.
Timesheet and Job Card Management
Users can create and upload timesheets and job cards.
Admins can review and approve submissions.

## Task Management
Users can create, modify, and delete tasks.
Tasks are displayed in a job board with sections for To-Do, In-Progress, and Completed.

## Calendar Integration
An interactive calendar allows users to view and manage events.
Events are linked to timesheet entries and can be managed by the admin.


# Contributing
Contributions are welcome! Please fork the repository and submit pull requests for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

For any issues or further assistance, please contact the project maintainer at nathanbrown-bennett@hotmail.com

![generated](https://github.com/user-attachments/assets/79efea19-3790-47a6-ac2e-476949c5985a)

Explanation of Full ERD

### /Routes
**Account:** Manages user authentication and account settings.
**Admin:** Provides administrative functionalities for managing job cards, timesheets, and users.
**EmailUtil:** Contains utility function for sending emails.
**Main:** Defines main application routes, including the index and information pages, and file upload.
**SQLAlchemyConfig:** Configures SQLAlchemy for the application.
**Tasks:** Manages task-related routes.


### Templates
**Login:** Directs users to the index page upon successful login.
**Register:** Leads to the verification page where users verify their account.
**SuperAdminDashboard:** Provides super admin functionalities, leading to the admin dashboard.
**Verification:** Redirects users to the index page upon successful verification.
**AdminDashboard:** Central hub for admin tasks, allowing creation of job cards and timesheets, and managing the dashboard.
**CreateJobCard:** Connects to the dashboard for job card management.
**CreateTimesheet:** Connects to the dashboard for timesheet management.
**Customise:** Allows customization, connecting to the dashboard.
**Dashboard:** Central page for users, providing access to various functionalities like employee settings and timesheet/job card uploads.
**EmployeeSettings:** Links to account settings for employee-specific settings.
**Index:** Main landing page, providing access to info and account settings.
**Info:** Provides information about the application, linking back to the index.
**AccountSettings:** Allows users to manage their account settings, connecting back to the dashboard.

## Root Directory
**AdminRoutes:** Provides administrative routes.
**App:** Initializes the Flask application and registers blueprints.
**ConfigureMSAL:** Configures Microsoft Authentication Library (MSAL).
**ConfigureSMTP:** Configures SMTP settings for sending emails.
**CreateADCredentialsDB:** Creates a database for storing Active Directory credentials.
**CreateSQLAlchemyDB:** Creates the main database using SQLAlchemy.
**App_Extensions:** Initializes Flask extensions like SQLAlchemy, LoginManager, and Mail.
**InitExtensions:** Initializes extensions for the Flask application.
**Migration:** Manages database migrations.
**Models:** Defines the database models for users, organizations, timesheets, job cards, and tasks.
**Timesheet2JSON:** Converts timesheet data from DOCX to JSON format.
**TotalHourDict:** Calculates total hours worked by each user based on timesheet data.
**UpdateExcel:** Updates an Excel file with new data.
**Util:** Provides utility functions for saving files and checking allowed file extensions.
