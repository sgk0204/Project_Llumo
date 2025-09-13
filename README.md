# Python + MongoDB Assessment (FastAPI)

This project is a RESTful API for managing employee records, built with Python, FastAPI, and MongoDB. It fulfills all the core requirements and bonus challenges outlined in the assessment.

## Features

- **CRUD Operations**: Create, Read, Update, and Delete employee records.
- **Advanced Querying**:
  - List employees with filtering by department.
  - Search for employees based on their skills.
- **Database Aggregation**: Calculate the average salary per department.
- **Data Validation**: Uses Pydantic for robust request and response data validation.
- **Asynchronous**: Built with `async` and `await` for high performance, using the `motor` driver for MongoDB.
- **Bonus Features Implemented**:
  - **Pagination**: The `/employees` endpoint supports `page` and `page_size` query parameters.
  - **Database Indexing**: A unique index is automatically created on `employee_id` to ensure data integrity and fast lookups.

## Prerequisites

- **Python 3.8+**
- **MongoDB**: Make sure you have a running instance of MongoDB. The application connects to `mongodb://localhost:27017` by default.

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sgk0204/Project_Llumo.git
```

### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies

Install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

## How to Run the Application

### 1. Start the API Server

Use `uvicorn` to run the FastAPI application.

```bash
uvicorn main:app --reload
```

- `--reload`: This flag makes the server automatically restart after code changes, which is great for development.

### 2. Access the API

The API will be running at `http://127.0.0.1:8000`.

### 3. Explore the Interactive Docs

FastAPI provides automatic, interactive API documentation. You can access it at:

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

You can test all the endpoints directly from your browser using these interfaces.

## API Endpoints Overview

### Employee CRUD Operations

- `POST /employees`: Create a new employee.
- `GET /employees/{employee_id}`: Get a single employee by their ID.
- `PUT /employees/{employee_id}`: Update an employee's details (supports partial updates).
- `DELETE /employees/{employee_id}`: Delete an employee.

### Employee Listing and Filtering

- `GET /employees`: Get a list of all employees (supports filtering and pagination).
  - **Query Parameters**: 
    - `department` (optional): Filter employees by department
    - `page` (optional): Page number for pagination (default: 1)
    - `page_size` (optional): Number of employees per page (default: 10)

### Advanced Features

- `GET /employees/avg-salary`: Get the average salary for each department.
- `GET /employees/search`: Find employees who have a specific skill.
  - **Query Parameter**: `skill` (required): The skill to search for

## Example Usage

### Creating a New Employee

```bash
curl -X POST "http://127.0.0.1:8000/employees" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001",
    "name": "John Doe",
    "email": "john.doe@company.com",
    "department": "Engineering",
    "role": "Software Developer",
    "date_joined": "2024-01-15",
    "salary": 75000,
    "skills": ["Python", "FastAPI", "MongoDB"]
  }'
```

### Getting Employees with Filtering

```bash
# Get all employees in Engineering department
curl "http://127.0.0.1:8000/employees?department=Engineering"

# Get employees with pagination
curl "http://127.0.0.1:8000/employees?page=1&page_size=5"
```

### Searching by Skills

```bash
# Find all employees with Python skills
curl "http://127.0.0.1:8000/employees/search?skill=Python"
```

### Getting Average Salary by Department

```bash
curl "http://127.0.0.1:8000/employees/avg-salary"
```

## Project Structure

```
├── main.py              # Main FastAPI application
├── models/              # Pydantic models for request/response validation
├── database/            # Database connection and configuration
├── routes/              # API route handlers
├── requirements.txt     # Project dependencies
└── README.md           # This file
```

## Dependencies

The main dependencies for this project include:

- **FastAPI**: Modern, fast web framework for building APIs
- **Motor**: Asynchronous Python driver for MongoDB
- **Pydantic**: Data validation and settings management using Python type annotations
- **Uvicorn**: ASGI web server implementation for Python

## Database Schema

The employee collection follows this schema:

```python
{
    "employee_id": "string",    # Unique identifier
    "name": "string",           # Employee full name
    "email": "string",          # Employee email address
    "department": "string",     # Department name
    "role": "string",           # Job role/title
    "date_joined": "date",      # Date when employee joined
    "salary": "number",         # Employee salary
    "skills": ["string"]        # Array of skills
}
```

## Performance Features

- **Asynchronous Operations**: All database operations are performed asynchronously for better performance
- **Database Indexing**: Unique index on `employee_id` for fast lookups and data integrity
- **Pagination**: Efficient handling of large datasets with configurable page sizes
- **Connection Pooling**: Motor driver handles MongoDB connection pooling automatically

## Development

For development, you can run the server with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

You can test the API endpoints using:

1. **Interactive Documentation**: Visit `http://127.0.0.1:8000/docs`
2. **curl commands**: As shown in the examples above
3. **Postman**: Import the API endpoints for testing
4. **Python requests library**: For programmatic testing

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**: Ensure MongoDB is running on `localhost:27017`
2. **Port Already in Use**: Change the port using `--port` flag with uvicorn
3. **Import Errors**: Make sure all dependencies are installed in your virtual environment

### Logs

FastAPI provides detailed logs. Check the console output when running the server for any error messages.

