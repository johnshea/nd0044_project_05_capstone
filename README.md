# Capstone

This is the final project in Udacity's Full Stack Web Developer Nanodegree Program.

It is an API for a restaurant.

This project was to build an API using authentication and host it on heroku.
## Motivation for the project
I previously worked in a restaurant and decided to use this experience as source of inspiration for this project.
## URL location for the hosted API
https://sleepy-castle-86876.herokuapp.com/
## Project dependencies
The full project dependencies can be found in `requirements.txt`

High level summary:
Flask (local), Gunicorn (hosted) - web server
Flask-SQLAlchemy - Data models, ORM
Flask-Migrate - Database migrations
Psycopg2, Psycopg2-binary - Postgres database support
Python-Jose - JWTs and Authentication

## Local development
Unzip the project.

Create a virtual environment.
```bash
python3 -m venv env
```
Activate the virtual environment.
```bash
source ./env/bin/activate
```
Run the bash script containing required configuration values.
```
source ./setup.sh
```
Install the required project dependencies.
```bash
pip3 install -r requirements.txt
```

Create the Postgres Database.
```bash
createdb -U postgres capstone
```
Define the flask environment variables.
```
export FLASK_APP=flaskr.py
export FLASK_DEBUG=true
```
Setup the database schema by running the migration scripts.
```
python manage.py db upgrade
```

Run the app.
```
flask run
```

Open a browser and navigate to http://127.0.0.1:5000/
#
_NOTE_: When finished, to exit the virtual environment run:
```bash
$ deactivate
```

## Local API Testing
In `setup.sh`, replace `SERVER_TOKEN` and `MANAGER_TOKEN` with valid JWTs before running.
```
source ./setup.sh
dropdb -U postgres capstone_test
createdb -U postgres capstone_test
psql capstone_test < test.sql -U postgres
python3 test_flaskr.py -v
```

## API Documentation

The API endpoints are built using REST architecture.

The responses are JSON encoded with the traditional HTTP status codes.

Standard HTTP verbs (GET, POST, PATCH, DELETE) are used.

## Authentication

Authentication is provided by Auth0.

API Permissions
`read:checks` - Read checks	
`read:employees` - Read employees	
`delete:employees` - Delete employees	
`create:employees` - Create employees	
`update:employees` - Update employees

To make user management easier, the API has the following roles (RBAC):

Manager - Manager (All permissions listed above.)
Server - Wait staff (Only `read:checks` and `read:employees`)

The API is pre-configured with the following users:

Server Role
Email address: server_sally@example.com
Password: ServerOne2022!

Manager Role
Email address: manager_marnie@example.com
Password: ManagerOne2022!

To create a valid and current JWT,
1. In an incognito tab browse to the login endpoint listed
2. Use the credentials listed above for the user/role you wish to impersonate
3. Copy the `access_token` (JWT) returned by Auth0 in the URL.

Auth0 Login Endpoint
https://nd0044-project-05-capstone.us.auth0.com/authorize?audience=restaurant&response_type=token&client_id=90ZsHcWVmtxIaPvs87p1yuw52UmJrb1i&redirect_uri=http://localhost:5000/login-results

Auth0 Logout Endpoint
https://nd0044-project-05-capstone.us.auth0.com/v2/logout?client_id=90ZsHcWVmtxIaPvs87p1yuw52UmJrb1i&returnTo=http://localhost:5000/logout

## Errors
Errors are returned as JSON objects in the following format:
```
{
    "success": false,
    "error": 404,
    "message": "Not Found"
}
```
200 - OK  Successful request
400 - Bad Request
401 - Unauthorized
403 - Forbidden
404 - Not Found
422 - Unprocessable Entity

## Checks
This object represents a check.


Attributes
id: int required
Unique identifier for this object.

employee_id: integer required
The employee_id that owns the check.


## Employees
This object represents an employee.

Attributes
id: int required
Unique identifier for this object

name: string required
Employee's name

### GET `/`
Permission required: None

Simple endpoint to confirm API is running.

Returns "Hello Capstone!"

### GET `/checks`
Permission required: `read:checks`

If authorized, returns a list of all checks ordered by their id in ascending order.

Example request
`$ curl -X GET  http://127.0.0.1:5000/checks`

Example response
```
{
    "checks": [
        {
            "employee_id": 1,
            "id": 1
        },
        {
            "employee_id": 1,
            "id": 2
        },
        {
            "employee_id": 1,
            "id": 3
        },
        {
            "employee_id": 2,
            "id": 4
        },
        {
            "employee_id": 2,
            "id": 5
        }
    ],
    "success": true,
    "total_checks": 5
}
```
If unauthorized, returns JSON object with a `401` error code.

Example response
```
{
  "error": 401, 
  "message": "Unauthorized", 
  "success": false
}
```
### GET `/employees`
Permission required: `read:employees`

If authorized, returns a list of all employees ordered by their id in ascending order.

Example request
`$ curl -X GET  http://127.0.0.1:5000/employees`

Example response
```
{
    "employees": [
        {
            "id": 1,
            "name": "First Employee"
        },
        {
            "id": 2,
            "name": "Second Employee"
        },
        {
            "id": 3,
            "name": "Third Postman"
        },
        {
            "id": 4,
            "name": "Fourth Employee"
        }
    ],
    "success": true,
    "total_employees": 4
}
```
If unauthorized, returns JSON object with a `401` error code.

Example response
```
{
  "error": 401, 
  "message": "Unauthorized", 
  "success": false
}
```
### DELETE `/employees/<int:employee_id>`
Permission required: `delete:employees`

Deletes an employee based on their id.

Example request
`$ curl -X DELETE -H "Authorization: Bearer <JWT token>" http://127.0.0.1:5000/employees/1`

Example response
```
{
    'success': True,
    'id': 1
}
```
If the id does not exist, an error code of `404` is returned.

Example response
```{
    "error": 404,
    "message": "Not Found",
    "success": false
}
```
### POST `/employees`
Permission required: `create:employees`

If authorized, creates an employee based on the provided name.
If the body is empty or the name is not provided, an error code of `400` is returned.

Example request
`$ curl -X POST -d '{"name": "New Employee"}' -H "Content-Type: application/json" -H "Authorization: Bearer <JWT token>" http://127.0.0.1:5000/employees
`

Example response
```
{
    'success': True,
    'id': 1
}
```
If unauthorized, returns JSON object with a `401` error code.

Example response
```
{
  "error": 401, 
  "message": "Unauthorized", 
  "success": false
}
```

### PATCH `/employees/<int:employee_id>`
Permission required: `update:employees`

Updates an employee's name based on their their id.

Example request
`$ curl -X PATCH -d '{"name": "New Name"}' -H "Content-Type: application/json" -H "Authorization: Bearer <JWT token>" http://127.0.0.1:5000/employees/1`

Example response
```
{
    'success': True,
    'id': 1
}
```
If the id does not exist, an error code of `404` is returned.
If the body is empty, an error code of `400` is returned.

Example response
```{
    "error": 404,
    "message": "Not Found",
    "success": false
}
```
