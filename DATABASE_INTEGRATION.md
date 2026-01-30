# MongoDB Database Integration

This document describes the MongoDB database integration for the Multi-Agent Medical Assistant platform.

## Database Schema

### Collections

#### 1. Users Collection
Stores all user accounts including patients, doctors, and admins.

**Fields:**
- `user_id` (string, required, unique): Unique identifier for the user
- `user_name` (string, required): User's full name
- `user_type` (enum, required): One of "PATIENT", "DOCTOR", or "ADMIN"
- `doctor_id` (string, optional): Associated doctor ID (for patients)
- `created_at` (datetime): Timestamp of user creation

**Example:**
```json
{
  "user_id": "user_001",
  "user_name": "John Doe",
  "user_type": "PATIENT",
  "doctor_id": "doc_123",
  "created_at": "2024-01-28T10:30:00Z"
}
```

#### 2. Doctors Collection
Stores doctor profiles and availability information.

**Fields:**
- `doctor_id` (string, required, unique): Unique identifier for the doctor
- `doc_name` (string, required): Doctor's full name
- `available_status` (boolean, required): Current availability status
- `meet_link` (string, optional): Personal meeting room link
- `start_meet_time` (string, optional): Office hours start time (HH:MM format)
- `end_meet_time` (string, optional): Office hours end time (HH:MM format)
- `created_at` (datetime): Timestamp of doctor profile creation

**Example:**
```json
{
  "doctor_id": "doc_123",
  "doc_name": "Dr. Jane Smith",
  "available_status": true,
  "meet_link": "https://meet.jit.si/dr-jane-smith",
  "start_meet_time": "09:00",
  "end_meet_time": "17:00",
  "created_at": "2024-01-28T10:30:00Z"
}
```

#### 3. Appointments Collection
Stores appointment records between patients and doctors.

**Fields:**
- `user_id` (string, required): Patient's user ID
- `doctor_id` (string, required): Doctor's ID
- `appointment_status` (enum, required): One of "SCHEDULED", "ACTIVE", "COMPLETED", or "CANCELLED"
- `scheduled_time` (datetime, required): Scheduled appointment time
- `meet_link` (string, optional): Specific meeting link for this appointment
- `created_at` (datetime): Timestamp of appointment creation

**Example:**
```json
{
  "user_id": "user_001",
  "doctor_id": "doc_123",
  "appointment_status": "SCHEDULED",
  "scheduled_time": "2024-01-30T14:00:00Z",
  "meet_link": "https://meet.jit.si/appointment-abc123",
  "created_at": "2024-01-28T10:30:00Z"
}
```

## API Endpoints

### User Management

#### Create User
```http
POST /api/users
Content-Type: application/json

{
  "user_id": "user_001",
  "user_name": "John Doe",
  "user_type": "PATIENT",
  "doctor_id": "doc_123"
}
```

#### Get All Users
```http
GET /api/users?user_type=PATIENT
```

#### Get User by ID
```http
GET /api/users/{user_id}
```

#### Update User
```http
PUT /api/users/{user_id}
Content-Type: application/json

{
  "user_name": "John Updated Doe",
  "doctor_id": "doc_456"
}
```

#### Delete User
```http
DELETE /api/users/{user_id}
```

### Doctor Management

#### Create Doctor
```http
POST /api/doctors
Content-Type: application/json

{
  "doctor_id": "doc_123",
  "doc_name": "Dr. Jane Smith",
  "available_status": true,
  "meet_link": "https://meet.jit.si/dr-jane-smith",
  "start_meet_time": "09:00",
  "end_meet_time": "17:00"
}
```

#### Get All Doctors
```http
GET /api/doctors?available_only=true
```

#### Get Doctor by ID
```http
GET /api/doctors/{doctor_id}
```

#### Update Doctor
```http
PUT /api/doctors/{doctor_id}
Content-Type: application/json

{
  "doc_name": "Dr. Jane Updated Smith",
  "available_status": false
}
```

#### Update Doctor Availability
```http
PATCH /api/doctors/{doctor_id}/availability?available=true
```

#### Delete Doctor
```http
DELETE /api/doctors/{doctor_id}
```

### Appointment Management

#### Create Appointment
```http
POST /api/appointments
Content-Type: application/json

{
  "user_id": "user_001",
  "doctor_id": "doc_123",
  "appointment_status": "SCHEDULED",
  "scheduled_time": "2024-01-30T14:00:00Z",
  "meet_link": "https://meet.jit.si/appointment-abc123"
}
```

#### Get All Appointments
```http
GET /api/appointments
```

#### Get User Appointments
```http
GET /api/appointments/user/{user_id}
```

#### Get Doctor Appointments
```http
GET /api/appointments/doctor/{doctor_id}
```

#### Get Appointment by ID
```http
GET /api/appointments/{appointment_id}
```

#### Update Appointment
```http
PUT /api/appointments/{appointment_id}
Content-Type: application/json

{
  "appointment_status": "COMPLETED"
}
```

#### Delete Appointment
```http
DELETE /api/appointments/{appointment_id}
```

### Admin Dashboard

#### Get Statistics
```http
GET /api/admin/statistics
```

**Response:**
```json
{
  "total_users": 150,
  "total_doctors": 25,
  "total_appointments": 500,
  "active_appointments": 12,
  "available_doctors": 18
}
```

## MongoDB Configuration

### Connection String
The MongoDB connection string is configured in `backend/core/config.py`:

```python
MONGODB_URI = "mongodb+srv://muthu_user:Muthu93@cluster0.b69bba9.mongodb.net/"
DATABASE_NAME = "medical_assistant_db"
```

### Environment Variables
You can also configure MongoDB via environment variables in `.env`:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=medical_assistant_db
```

## Admin Dashboard

The admin dashboard is accessible at `/admin` and provides:

### Features
1. **Statistics Overview**
   - Total users count
   - Total doctors count
   - Available doctors count
   - Total appointments
   - Active appointments (real-time)

2. **User Management**
   - View all users in a table
   - Create new users
   - Edit existing users
   - Delete users
   - Filter by user type (PATIENT, DOCTOR, ADMIN)

3. **Doctor Management**
   - View all doctors with availability status
   - Create new doctor profiles
   - Edit doctor information
   - Toggle doctor availability with one click
   - Delete doctor profiles
   - View office hours and meeting links

4. **Appointment Management**
   - View all appointments
   - Filter by status (SCHEDULED, ACTIVE, COMPLETED, CANCELLED)
   - View appointment details including meeting links
   - Real-time status updates

### Access
Currently, the admin dashboard is accessible without authentication. For production use, implement proper authentication and role-based access control.

## Database Service

The `DatabaseManager` class in `backend/services/database_service.py` provides async methods for all database operations:

### Key Methods

**Connection Management:**
- `connect_async()`: Establish MongoDB connection
- `close_async()`: Close MongoDB connection

**User Operations:**
- `create_user(user_data)`: Create a new user
- `get_user(user_id)`: Get user by ID
- `get_all_users(user_type)`: Get all users, optionally filtered by type
- `update_user(user_id, update_data)`: Update user information
- `delete_user(user_id)`: Delete a user

**Doctor Operations:**
- `create_doctor(doctor_data)`: Create a new doctor
- `get_doctor(doctor_id)`: Get doctor by ID
- `get_all_doctors(available_only)`: Get all doctors, optionally only available ones
- `update_doctor(doctor_id, update_data)`: Update doctor information
- `update_doctor_availability(doctor_id, available)`: Update doctor availability status
- `delete_doctor(doctor_id)`: Delete a doctor

**Appointment Operations:**
- `create_appointment(appointment_data)`: Create a new appointment
- `get_appointment(appointment_id)`: Get appointment by ID
- `get_user_appointments(user_id)`: Get all appointments for a user
- `get_doctor_appointments(doctor_id)`: Get all appointments for a doctor
- `get_all_appointments()`: Get all appointments
- `update_appointment(appointment_id, update_data)`: Update appointment information
- `delete_appointment(appointment_id)`: Delete an appointment

**Statistics:**
- `get_statistics()`: Get platform statistics for admin dashboard

## Testing

### Backend Testing
Test the database endpoints using the FastAPI interactive docs:

```bash
cd backend
python main.py
# Navigate to http://localhost:8000/docs
```

### Create Test Data
You can use the admin dashboard UI or make API calls:

```bash
# Create a test user
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "user_name": "Test User",
    "user_type": "PATIENT"
  }'

# Create a test doctor
curl -X POST http://localhost:8000/api/doctors \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": "test_doc_001",
    "doc_name": "Test Doctor",
    "available_status": true
  }'
```

## Dependencies

Required Python packages:
```
pymongo==4.9.1
motor==3.6.0
```

Install with:
```bash
pip install pymongo==4.9.1 motor==3.6.0
```

## Security Considerations

⚠️ **Important for Production:**

1. **Authentication**: Implement JWT-based authentication for all endpoints
2. **Role-Based Access Control**: Restrict admin endpoints to admin users only
3. **Input Validation**: All inputs are validated using Pydantic models
4. **MongoDB Credentials**: Store credentials in environment variables, never commit to git
5. **HTTPS**: Use HTTPS in production for encrypted communication
6. **Rate Limiting**: Implement rate limiting to prevent abuse
7. **Data Encryption**: Consider encrypting sensitive data at rest

## Troubleshooting

### Connection Issues
If you can't connect to MongoDB:
1. Check your internet connection
2. Verify the MongoDB URI is correct
3. Ensure your IP address is whitelisted in MongoDB Atlas
4. Check MongoDB Atlas cluster is running

### Import Errors
If you get import errors:
```bash
pip install pymongo==4.9.1 motor==3.6.0
```

### Database Not Updating
1. Check backend logs for errors
2. Verify MongoDB connection is established at startup
3. Check the database name matches in config and MongoDB Atlas

## Next Steps

1. **Authentication**: Implement user authentication with JWT tokens
2. **Authorization**: Add role-based access control
3. **Validation**: Add more comprehensive input validation
4. **Logging**: Enhance logging for better debugging
5. **Backup**: Set up automated database backups
6. **Monitoring**: Add database monitoring and alerts
7. **Testing**: Write comprehensive unit and integration tests
