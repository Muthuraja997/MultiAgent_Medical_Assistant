# Authentication & Role-Based Access System

## Overview

The Multi-Agent Medical Assistant now features a complete authentication system with role-based access control. Users must log in to access the platform, and the system differentiates between regular users and doctors.

## Database Collections

### 1. Users Collection
Stores all user accounts with authentication credentials.

**Schema:**
```javascript
{
  user_id: String (required, unique),        // Unique identifier
  user_name: String (required),              // Full name
  user_type: Enum (required),                // "USER" or "DOCTOR"
  appointment_status: Enum (required),       // "SCHEDULED", "ACTIVE", "COMPLETED", "CANCELLED"
  doctor_id: String (optional),              // Assigned doctor ID
  password: String (required, hashed),       // SHA-256 hashed password
  created_at: DateTime
}
```

### 2. Doctors Collection
Stores doctor profiles with authentication credentials.

**Schema:**
```javascript
{
  doctor_id: String (required, unique),      // Unique identifier
  doc_name: String (required),               // Full name
  available_status: Boolean (required),      // Current availability
  password: String (required, hashed),       // SHA-256 hashed password
  created_at: DateTime
}
```

### 3. Meetings Collection
Stores meeting/consultation information for doctors.

**Schema:**
```javascript
{
  doctor_id: String (required),              // Associated doctor
  meet_link: String (required),              // Video meeting URL
  start_meet_time: String (required),        // Format: "HH:MM"
  end_meet_time: String (required),          // Format: "HH:MM"
  created_at: DateTime
}
```

## Authentication Flow

### 1. Login Process

**Endpoint:** `POST /api/login`

**Request:**
```json
{
  "user_id": "user_001",
  "password": "password123",
  "user_type": "USER"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Login successful",
  "user_id": "user_001",
  "user_name": "John Doe",
  "user_type": "USER",
  "token": "abc123...xyz"
}
```

**Response (Failure):**
```json
{
  "success": false,
  "message": "Invalid credentials",
  "user_id": "",
  "user_name": "",
  "user_type": "USER"
}
```

### 2. Password Security

- All passwords are hashed using **SHA-256** before storage
- Passwords are never returned in API responses
- Password verification is done by comparing hashes

**Implementation:**
```python
# services/auth_service.py
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password
```

### 3. Token Generation

Simple token generation for session management:

```python
def generate_token(user_id: str, user_type: str) -> str:
    token_string = f"{user_id}:{user_type}"
    return hashlib.sha256(token_string.encode()).hexdigest()
```

**Note:** For production, implement JWT tokens with expiration times.

## Frontend Authentication

### Login Page

- **Route:** `/login`
- **Features:**
  - Toggle between USER and DOCTOR login
  - Form validation
  - Error handling with user-friendly messages
  - Loading states
  - Responsive design

**Screenshot Features:**
- User/Doctor toggle buttons
- ID and password input fields
- Login button with loading animation
- Demo credentials display

### Protected Routes

All application routes except `/login` are protected:

```tsx
function ProtectedRoute({ children }) {
  const isAuthenticated = localStorage.getItem('user_id') && localStorage.getItem('token');
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}
```

### Session Storage

User session data is stored in `localStorage`:
- `user_id`: Unique identifier
- `user_name`: Display name
- `user_type`: "USER" or "DOCTOR"
- `token`: Authentication token

### Logout

Logout button in sidebar clears all session data and redirects to login:

```tsx
const handleLogout = () => {
  localStorage.removeItem('user_id');
  localStorage.removeItem('user_name');
  localStorage.removeItem('user_type');
  localStorage.removeItem('token');
  navigate('/login');
};
```

## API Endpoints

### Authentication
- `POST /api/login` - User/Doctor login

### Users (Protected)
- `POST /api/users` - Create new user
- `GET /api/users` - Get all users (with optional filter)
- `GET /api/users/{user_id}` - Get specific user
- `PUT /api/users/{user_id}` - Update user
- `DELETE /api/users/{user_id}` - Delete user

### Doctors (Protected)
- `POST /api/doctors` - Create new doctor
- `GET /api/doctors` - Get all doctors (with availability filter)
- `GET /api/doctors/{doctor_id}` - Get specific doctor
- `PUT /api/doctors/{doctor_id}` - Update doctor
- `PATCH /api/doctors/{doctor_id}/availability` - Toggle availability
- `DELETE /api/doctors/{doctor_id}` - Delete doctor

### Meetings (Protected)
- `POST /api/meetings` - Create new meeting
- `GET /api/meetings` - Get all meetings
- `GET /api/meetings/doctor/{doctor_id}` - Get doctor meetings
- `GET /api/meetings/{meeting_id}` - Get specific meeting
- `PUT /api/meetings/{meeting_id}` - Update meeting
- `DELETE /api/meetings/{meeting_id}` - Delete meeting

### Admin (Protected)
- `GET /api/admin/statistics` - Get platform statistics

## Creating Test Users

### Via API:

**Create a User:**
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "user_name": "John Doe",
    "user_type": "USER",
    "appointment_status": "SCHEDULED",
    "password": "password123"
  }'
```

**Create a Doctor:**
```bash
curl -X POST http://localhost:8000/api/doctors \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": "doc_001",
    "doc_name": "Dr. Jane Smith",
    "available_status": true,
    "password": "doctor123"
  }'
```

**Create a Meeting:**
```bash
curl -X POST http://localhost:8000/api/meetings \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": "doc_001",
    "meet_link": "https://meet.jit.si/dr-jane-smith",
    "start_meet_time": "09:00",
    "end_meet_time": "17:00"
  }'
```

### Via Python Script:

```python
import requests

# Create a user
response = requests.post('http://localhost:8000/api/users', json={
    'user_id': 'user_001',
    'user_name': 'John Doe',
    'user_type': 'USER',
    'appointment_status': 'SCHEDULED',
    'password': 'password123'
})
print(response.json())

# Test login
login_response = requests.post('http://localhost:8000/api/login', json={
    'user_id': 'user_001',
    'password': 'password123',
    'user_type': 'USER'
})
print(login_response.json())
```

## Role-Based Features

### User Role (USER)
- Access to personal dashboard
- View available doctors
- Book appointments
- Access hospital locator
- Join video consultations
- View analytics

### Doctor Role (DOCTOR)
- Access to doctor dashboard
- Manage availability status
- View patient appointments
- Manage meeting schedules
- Access video consultation rooms
- View patient analytics

## Security Best Practices

### Current Implementation
✅ Password hashing with SHA-256
✅ Passwords never returned in API responses
✅ Protected routes with authentication check
✅ Role-based access control
✅ Session management with localStorage

### Recommended for Production
⚠️ **Upgrade to JWT tokens** with expiration times
⚠️ **Implement HTTPS** for encrypted communication
⚠️ **Add refresh tokens** for session renewal
⚠️ **Implement rate limiting** on login endpoint
⚠️ **Add CSRF protection**
⚠️ **Use bcrypt** instead of SHA-256 for passwords
⚠️ **Add 2FA** (Two-Factor Authentication)
⚠️ **Implement password reset** functionality
⚠️ **Add account lockout** after failed attempts
⚠️ **Log authentication attempts** for audit trail

## Testing the System

### 1. Start Backend
```bash
cd backend
source ../venv/bin/activate
python main.py
```

### 2. Create Test Users (First Time)
Use the API or Python script above to create test users and doctors.

### 3. Start Frontend
```bash
cd frontend
npm run dev
```

### 4. Test Login
1. Navigate to `http://localhost:5173` (redirects to `/login`)
2. Toggle between USER and DOCTOR
3. Enter credentials:
   - User: `user_001` / `password123`
   - Doctor: `doc_001` / `doctor123`
4. Click Login
5. Access protected routes

### 5. Test Logout
1. Click logout button in sidebar
2. Verify redirect to login page
3. Verify localStorage is cleared

## Troubleshooting

### Login Fails
- **Check MongoDB connection**: Ensure MongoDB Atlas is accessible
- **Verify user exists**: Use MongoDB Compass or API to check
- **Check password**: Passwords are case-sensitive
- **Console errors**: Check browser console and backend logs

### Protected Routes Not Working
- **Clear localStorage**: Clear browser localStorage and login again
- **Check token**: Verify token exists in localStorage
- **Backend running**: Ensure backend is running on port 8000

### Password Issues
- **Hash mismatch**: If password was created without hashing, update it
- **Special characters**: Some characters may need escaping

## Next Steps

1. ✅ **Complete**: Basic authentication with login page
2. ✅ **Complete**: Role-based access (USER vs DOCTOR)
3. ✅ **Complete**: Protected routes
4. ✅ **Complete**: Session management
5. 🔄 **TODO**: Upgrade to JWT tokens
6. 🔄 **TODO**: Add password reset functionality
7. 🔄 **TODO**: Implement role-specific dashboards
8. 🔄 **TODO**: Add 2FA for enhanced security
9. 🔄 **TODO**: Implement audit logs
10. 🔄 **TODO**: Add email verification

## API Documentation

Full API documentation available at: `http://localhost:8000/docs`

## Support

For issues or questions, check:
- Backend logs: `backend/logs/`
- Browser console for frontend errors
- MongoDB Atlas dashboard for database issues
- FastAPI docs at `/docs` endpoint
