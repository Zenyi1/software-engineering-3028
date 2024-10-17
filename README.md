# Mouse Colony Management System

A web-based Mouse Colony Management System built with Django and MySQL. This system allows researchers to manage their laboratory mouse colonies efficiently, including tracking mouse breeding, genotyping, cage management, and more.

## Features

- **Mouse Breeding Records**: Track breeding pairs, litter sizes, birth dates, and weaning dates.
- **Genotype Tracking**: Record and manage the genotype of each mouse.
- **Cage Management**: Keep track of which mice are in which cages, and manage cage transfers.
- **Health Monitoring**: Log and manage health records for individual mice.
- **Reporting**: Generate reports for colony status, breeding performance, and health trends.

## Technologies Used

- **Django**
- **MySQL**

## Running this Project
1. Clone this repository.
2. Go to Microsoft Store and install python 3.10 (the project requires this version and doing it through microsoft store automatically sets all neccessary variables).
3. Run command `python3.10 -m venv .venv` (the 3.10 is important to create a virtual environment with the correct python version).
4. Activate virtual environment using `.venv/Scripts/activate`.
5. Install dependencies using `pip install -r requirements.txt`.
6. Install MySQL locally making sure you the full version with all of the optional packages.
7. During installation you will set a username (`root` is recommended) and a password, keep track of these as they will be needed for the next step.
8. Create a file called `.env` (the `.` at the beginning is important) and set out the parameters like this (make sure each variable is on a new line and there are no trailing whitespaces):
    - ``` DB_NAME=mouse_colony_db DB_USER=your_username DB_PASSWORD=your_password DB_HOST=localhost DB_PORT=3306 ```
9. Make sure you are in the correct working directory, your command line should look something like this `...\software-engineering-3028\mouse_colony_management>`.
10. Run `python database_startup.py` (only do this the first time).
11. Run `python manage.py makemigrations` (only run this if you make changes to models).
12. Run `python manage.py migrate` (only run this after running `makemigrations`).
13. Run `python manage.py createsuperuser` (only run this once to create a super user for the admin site).
14. Run `python manage.py runserver` (run this whenever you want to view the site).
15. Go to `localhost:8000` on your browser of choice.

## Contributors

- Carlos
- Gonzalo
- Jeffrey
- Muhammad
- Nathan
- Ryan
- Stan
