# Hostel Complaint Tracker

## Project Overview

Hostel Complaint Tracker is a web-based application developed using Python and Django. It helps manage hostel complaints related to facilities such as electricity, water, internet, and cleaning. Students can submit complaints, and complaint records can be tracked through the application.

## Features

* Submit hostel complaints online.
* Enter complaint title, description, hostel block, and room number.
* Select complaint categories such as Electricity, Water, Internet, Cleaning, and Other.
* Track complaint status: Open, In Progress, and Resolved.
* Generate a unique complaint ticket number.
* Set complaint priority based on complaint type.
* Calculate target resolution time and identify overdue complaints.
* Add staff notes and record resolution time.
* Manage records through Django Admin, if configured.

## Technologies Used

* **Programming Language:** Python
* **Backend Framework:** Django
* **Frontend:** HTML, CSS, JavaScript, and Django Templates
* **Database:** The database configured in Django settings (SQLite is commonly used by default).

## Requirements

* Python installed on the computer
* pip package manager
* Project source code
* Required Python dependencies

## Installation and Setup

### Step 1: Download the Project

Download the repository from GitHub and extract it, or clone it using:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Open the project folder containing `manage.py`.

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

For Windows Command Prompt:

```bat
venv\Scripts\activate.bat
```

### Step 4: Install Dependencies

If the project contains `requirements.txt`, run:

```bash
python -m pip install -r requirements.txt
```

If there is no `requirements.txt`, install Django:

```bash
python -m pip install django
```

### Step 5: Apply Database Migrations

```bash
python manage.py migrate
```

### Step 6: Create an Admin Account

```bash
python manage.py createsuperuser
```

Follow the instructions to create your own admin username and password.

### Step 7: Run the Project

```bash
python manage.py runserver
```

Keep the terminal open while using the application.

## Application URLs

**Main Website:**

http://127.0.0.1:8000/

**Django Admin Panel:**

http://127.0.0.1:8000/admin/

The admin panel requires Django Admin to be enabled in the project settings and URL configuration. Log in using the superuser credentials created on that computer.

## How to Test the Project

1. Start the Django development server.
2. Open the main website in a browser.
3. Submit a sample hostel complaint.
4. Enter the required complaint details.
5. Check the complaint record and its generated ticket number.
6. Open the Django Admin panel to inspect or manage records, if configured.

## Troubleshooting

* **Django module not found:** Activate the virtual environment and install the required dependencies.
* **Database errors:** Run `python manage.py migrate`.
* **Admin URL not opening:** Check that Django Admin is enabled and `path("admin/", admin.site.urls)` is included in the main `urls.py`.
* **Website URL not opening:** Check the project's URL configuration and make sure the development server is running.

## Important Notes

* Run these commands from the directory containing `manage.py`.
* Create a separate superuser account on each computer where admin access is required.
* Never upload passwords or secret keys to GitHub.
* This setup is intended for local development and demonstration.

## Project Information

**Project Name:** Hostel Complaint Tracker
**Framework:** Django
**Purpose:** Hostel complaint submission and management
**Environment:** Local development server
