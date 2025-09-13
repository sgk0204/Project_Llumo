from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field, constr
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo
from datetime import date

DATABASE_URL = "mongodb://localhost:27017"
DATABASE_NAME = "assessment_db"
COLLECTION_NAME = "employees"

app = FastAPI(
    title="Employee Management API",
    description="An API to manage employee records using FastAPI and MongoDB.",
    version="1.0.0"
)

client: Optional[AsyncIOMotorClient] = None
db = None

@app.on_event("startup")
async def startup_db_client():
    global client, db
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client[DATABASE_NAME]
    try:
        await db[COLLECTION_NAME].create_index(
            "employee_id", unique=True
        )
    except pymongo.errors.PyMongoError as e:
        print(f"Error creating index: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()

class EmployeeBase(BaseModel):
    employee_id: constr(strip_whitespace=True, min_length=1) = Field(..., description="Unique employee identifier")
    name: str = Field(..., description="Full name of the employee")
    department: str = Field(..., description="Department the employee belongs to")
    salary: float = Field(..., gt=0, description="Employee's salary")
    joining_date: date = Field(..., description="Date of joining (YYYY-MM-DD)")
    skills: List[str] = Field(default=[], description="List of employee's skills")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "employee_id": "E456",
                "name": "Jane Smith",
                "department": "Human Resources",
                "salary": 65000,
                "joining_date": "2023-03-20",
                "skills": ["Communication", "Recruitment", "HR Policies"]
            }
        }

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[float] = Field(default=None, gt=0)
    joining_date: Optional[date] = None
    skills: Optional[List[str]] = None

    class Config:
        schema_extra = {
            "example": {
                "salary": 85000,
                "skills": ["Python", "MongoDB", "FastAPI", "Docker"]
            }
        }

class EmployeeResponse(EmployeeBase):
    pass

async def get_employee_collection():
    if db is None:
        raise HTTPException(status_code=500, detail="Database client not initialized")
    return db[COLLECTION_NAME]

@app.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(employee: EmployeeCreate):
    collection = await get_employee_collection()
    employee_dict = employee.dict()
    employee_dict['joining_date'] = employee_dict['joining_date'].isoformat()
    try:
        result = await collection.insert_one(employee_dict)
        if result.acknowledged:
            created_employee = await collection.find_one({"_id": result.inserted_id})
            return created_employee
    except pymongo.errors.DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with ID '{employee.employee_id}' already exists."
        )
    raise HTTPException(status_code=500, detail="Failed to create employee.")

@app.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee_by_id(employee_id: str):
    collection = await get_employee_collection()
    employee = await collection.find_one({"employee_id": employee_id})
    if employee:
        return employee
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee with ID '{employee_id}' not found")

@app.put("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(employee_id: str, employee_update: EmployeeUpdate):
    collection = await get_employee_collection()
    update_data = employee_update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No update fields provided.")
    if 'joining_date' in update_data and update_data['joining_date']:
        update_data['joining_date'] = update_data['joining_date'].isoformat()
    result = await collection.update_one(
        {"employee_id": employee_id},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee with ID '{employee_id}' not found")
    updated_employee = await collection.find_one({"employee_id": employee_id})
    return updated_employee

@app.delete("/employees/{employee_id}", status_code=status.HTTP_200_OK)
async def delete_employee(employee_id: str):
    collection = await get_employee_collection()
    result = await collection.delete_one({"employee_id": employee_id})
    if result.deleted_count == 1:
        return {"message": f"Employee with ID '{employee_id}' deleted successfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee with ID '{employee_id}' not found")

@app.get("/employees", response_model=List[EmployeeResponse])
async def list_employees(
    department: Optional[str] = Query(None, description="Filter employees by department"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    page_size: int = Query(10, ge=1, le=100, description="Number of employees per page")
):
    collection = await get_employee_collection()
    query = {}
    if department:
        query["department"] = department
    skip = (page - 1) * page_size
    employees_cursor = collection.find(query).sort("joining_date", pymongo.DESCENDING).skip(skip).limit(page_size)
    employees = await employees_cursor.to_list(length=page_size)
    return employees

@app.get("/employees/avg-salary", response_model=List[dict])
async def average_salary_by_department():
    collection = await get_employee_collection()
    pipeline = [
        {
            "$group": {
                "_id": "$department",
                "avg_salary": {"$avg": "$salary"}
            }
        },
        {
            "$project": {
                "department": "$_id",
                "avg_salary": {"$round": ["$avg_salary", 2]},
                "_id": 0
            }
        },
        {
            "$sort": {"department": 1}
        }
    ]
    avg_salaries_cursor = collection.aggregate(pipeline)
    return await avg_salaries_cursor.to_list(length=None)

@app.get("/employees/search", response_model=List[EmployeeResponse])
async def search_employees_by_skill(skill: str = Query(..., description="The skill to search for")):
    collection = await get_employee_collection()
    query = {"skills": skill}
    employees_cursor = collection.find(query)
    employees = await employees_cursor.to_list(length=None)
    return employees

@app.get("/")
async def root():
    return {"message": "Welcome to the Employee Management API!"}

