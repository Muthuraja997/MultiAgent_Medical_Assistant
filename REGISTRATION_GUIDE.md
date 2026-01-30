# User Registration System

## Overview
Complete user and doctor registration system with validation, duplicate detection, and automatic login redirect.

## Features

### Backend Implementation

#### 1. Registration Models (`backend/models/schemas.py`)

**RegisterRequest Model:**
```python
class RegisterRequest(BaseModel):
    user_id: str          # Unique ID (user_XXX or doc_XXX)
    name: str             # Full name
    password: str         # Min 6 characters
    user_type: UserType   # USER or DOCTOR
    email: Optional[str]  # Optional email
    phone: Optional[str]  # Optional phone
```

**RegisterResponse Model:**
```python
class RegisterResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str]
    user_name: Optional[str]
    user_type: Optional[UserType]
```

#### 2. Database Service (`backend/services/database_service.py`)

**register_user() Method:**
- Checks for duplicate user_id/doctor_id
- Creates appropriate collection document (users or doctors)
- Hashes password using SHA-256
- Sets default values:
  - Users: appointment_status = "SCHEDULED", doctor_id = None
  - Doctors: available_status = True
- Stores email and phone (optional)
- Returns None if ID already exists

#### 3. API Endpoint (`backend/main.py`)

**POST /api/register**

**Request Body:**
```json
{
  "user_id": "user_004",
  "name": "John Smith",
  "password": "mypassword123",
  "user_type": "USER",
  "email": "john@example.com",
  "phone": "+1234567890"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Registration successful! You can now login.",
  "user_id": "user_004",
  "user_name": "John Smith",
  "user_type": "USER"
}
```

**Error Responses:**

*Duplicate ID:*
```json
{
  "success": false,
  "message": "This user ID is already taken. Please choose another.",
  "user_id": null,
  "user_name": null,
  "user_type": null
}
```

*Invalid ID Format:*
```json
{
  "success": false,
  "message": "User ID must start with 'user_' (e.g., user_001)"
}
```

### Frontend Implementation

#### 1. Register Component (`frontend/src/pages/Register.tsx`)

**Features:**
- User type toggle (USER/DOCTOR)
- Form validation
  - User ID format validation (user_XXX or doc_XXX)
  - Password length check (min 6 characters)
  - Password confirmation match
- Real-time error messages
- Success message with auto-redirect to login
- Responsive design with Framer Motion animations
- Link back to login page

**Form Fields:**
1. **User Type Toggle** (Required)
   - USER button (blue)
   - DOCTOR button (purple)

2. **User/Doctor ID** (Required)
   - Must start with 'user_' or 'doc_' depending on type
   - Example: user_004, doc_004

3. **Full Name** (Required)
   - Any valid name

4. **Email** (Optional)
   - Valid email format

5. **Phone** (Optional)
   - Any phone format

6. **Password** (Required)
   - Minimum 6 characters
   - Password field type

7. **Confirm Password** (Required)
   - Must match password field

**Validation:**
- Client-side validation before API call
- Password match check
- ID format validation based on user type
- Displays error messages in red banner
- Displays success in green banner

#### 2. Routing (`frontend/src/App.tsx`)

**Public Routes:**
- `/login` - Login page
- `/register` - Registration page (NEW)

**Protected Routes:**
- All other routes require authentication

#### 3. Login Page Updates

Added registration link at bottom:
```tsx
<Link to="/register">Create one here</Link>
```

## Usage Examples

### Register a New User

**Via Frontend:**
1. Navigate to http://localhost:3000/register
2. Select "User" type
3. Enter user_004 as User ID
4. Enter your full name
5. Optionally add email and phone
6. Enter password (min 6 chars)
7. Confirm password
8. Click "Create Account"
9. You'll be redirected to login after 2 seconds

**Via API:**
```bash
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_004",
    "name": "Jane Doe",
    "password": "secure123",
    "user_type": "USER",
    "email": "jane@example.com",
    "phone": "+1234567890"
  }'
```

### Register a New Doctor

**Via Frontend:**
1. Navigate to http://localhost:3000/register
2. Select "Doctor" type
3. Enter doc_004 as Doctor ID
4. Enter doctor's full name (e.g., Dr. John Smith)
5. Optionally add email and phone
6. Enter password (min 6 chars)
7. Confirm password
8. Click "Create Account"

**Via API:**
```bash
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "doc_004",
    "name": "Dr. Emily Johnson",
    "password": "doctor456",
    "user_type": "DOCTOR",
    "email": "emily@hospital.com",
    "phone": "+0987654321"
  }'
```

## Testing

### Test Scenarios

1. **Successful User Registration:**
   ```bash
   curl -X POST http://localhost:8000/api/register \
     -H "Content-Type: application/json" \
     -d '{"user_id":"user_999","name":"Test User","password":"test123","user_type":"USER"}'
   ```
   Expected: `{"success":true,"message":"Registration successful!..."}`

2. **Duplicate ID Error:**
   ```bash
   # Register same user twice
   curl -X POST http://localhost:8000/api/register \
     -H "Content-Type: application/json" \
     -d '{"user_id":"user_999","name":"Another User","password":"test123","user_type":"USER"}'
   ```
   Expected: `{"success":false,"message":"This user ID is already taken..."}`

3. **Login After Registration:**
   ```bash
   curl -X POST http://localhost:8000/api/login \
     -H "Content-Type: application/json" \
     -d '{"user_id":"user_999","password":"test123","user_type":"USER"}'
   ```
   Expected: `{"success":true,"message":"Login successful",...}`

## Database Structure

### Users Collection
```json
{
  "user_id": "user_004",
  "user_name": "Jane Doe",
  "user_type": "USER",
  "appointment_status": "SCHEDULED",
  "doctor_id": null,
  "password": "hashed_password_here",
  "email": "jane@example.com",
  "phone": "+1234567890",
  "created_at": "2024-01-28T12:00:00Z"
}
```

### Doctors Collection
```json
{
  "doctor_id": "doc_004",
  "doc_name": "Dr. Emily Johnson",
  "available_status": true,
  "password": "hashed_password_here",
  "email": "emily@hospital.com",
  "phone": "+0987654321",
  "created_at": "2024-01-28T12:00:00Z"
}
```

## Security Features

1. **Password Hashing:**
   - All passwords hashed with SHA-256 before storage
   - Passwords never stored in plain text
   - Passwords never returned in API responses

2. **Validation:**
   - User ID format validation (prevents invalid IDs)
   - Password length requirements (min 6 characters)
   - Duplicate ID detection
   - Input sanitization via Pydantic models

3. **Frontend Security:**
   - Client-side validation before API calls
   - Password confirmation matching
   - Secure password input fields (type="password")

## User Experience

### Visual Design
- **Color Scheme:**
  - USER: Blue gradient (from-blue-600 to-blue-700)
  - DOCTOR: Purple gradient (from-purple-600 to-purple-700)
  
- **Animations:**
  - Smooth page entrance with Framer Motion
  - Button hover effects
  - Loading spinner during registration
  - Error/Success message fade-in

- **Responsive:**
  - Mobile-friendly layout
  - Touch-friendly buttons
  - Adaptive form sizing

### User Flow
1. User visits login page
2. Clicks "Create one here" link
3. Redirected to /register
4. Selects user type (USER/DOCTOR)
5. Fills form with required info
6. Submits registration
7. Sees success message
8. Auto-redirected to login after 2 seconds
9. Can immediately login with new credentials

## Error Messages

### Frontend Errors
- "Passwords do not match"
- "Password must be at least 6 characters long"
- "User ID must start with 'user_' (e.g., user_001)"
- "Doctor ID must start with 'doc_' (e.g., doc_001)"
- "Connection error. Please try again."

### Backend Errors
- "This user ID is already taken. Please choose another."
- "This doctor ID is already taken. Please choose another."
- "User ID must start with 'user_' (e.g., user_001)"
- "Doctor ID must start with 'doc_' (e.g., doc_001)"

## Next Steps

### Recommended Enhancements
1. **Email Verification:**
   - Send verification email after registration
   - Require email verification before login

2. **Password Strength:**
   - Add password strength indicator
   - Require special characters/numbers
   - Implement bcrypt instead of SHA-256

3. **Username Availability:**
   - Real-time ID availability check
   - Show green/red indicator while typing

4. **Multi-step Registration:**
   - Step 1: Basic info (ID, name, password)
   - Step 2: Contact info (email, phone)
   - Step 3: Additional profile info

5. **Social Login:**
   - Google OAuth
   - GitHub OAuth
   - Microsoft OAuth

6. **Terms & Conditions:**
   - Add T&C checkbox
   - Privacy policy link
   - GDPR compliance

## Files Modified/Created

### Created:
- `frontend/src/pages/Register.tsx` (345 lines)
- `REGISTRATION_GUIDE.md` (this file)

### Modified:
- `backend/models/schemas.py` - Added RegisterRequest and RegisterResponse models
- `backend/services/database_service.py` - Added register_user() method
- `backend/main.py` - Added POST /api/register endpoint
- `frontend/src/App.tsx` - Added /register route
- `frontend/src/pages/Login.tsx` - Added registration link

## Quick Start

1. **Backend:** Already running on port 8000
2. **Frontend:** Already running on port 3000
3. **Access:** http://localhost:3000/register
4. **Test:** Create a new account and login!

## Support

For issues or questions:
1. Check browser console for frontend errors
2. Check `/tmp/backend.log` for backend errors
3. Verify MongoDB connection
4. Test API endpoints with curl

---

**Status:** ✅ Complete and Working  
**Last Updated:** January 28, 2026  
**Version:** 1.0
