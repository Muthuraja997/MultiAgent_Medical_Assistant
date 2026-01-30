# Appointment Request System - Complete Implementation Guide

## Overview
Complete appointment request system where users can request appointments with available doctors, and doctors can accept/reject requests. When a doctor accepts an appointment, their status automatically changes to "busy".

## System Flow

```
1. User logs in → Sees Home page
2. Home page shows only AVAILABLE doctors (available_status = true)
3. User clicks "Request Appointment" on a doctor
4. User fills appointment request form (reason, date, time)
5. Request sent to backend → stored in appointment_requests collection
6. Doctor logs in → Sees Video Consultation page
7. Doctor views pending appointment requests
8. Doctor accepts/rejects request
9. If ACCEPTED:
   - Doctor status changes to BUSY (available_status = false)
   - Meet link is saved with the request
   - Doctor disappears from home page (no longer available)
10. If REJECTED:
   - Request marked as rejected
   - Doctor stays available
```

## Database Collections

### 1. appointment_requests Collection
```json
{
  "_id": ObjectId("..."),
  "request_id": "697a37ce819974d1e7711336",
  "user_id": "user_001",
  "user_name": "John Doe",
  "doctor_id": "doc_001",
  "reason": "Regular checkup",
  "preferred_date": "2026-02-01",
  "preferred_time": "10:00",
  "status": "PENDING|ACCEPTED|REJECTED",
  "meet_link": "https://meet.google.com/abc-defg-hij",
  "created_at": "2026-01-28T16:22:38.342000",
  "updated_at": "2026-01-28T16:23:03.005000"
}
```

### 2. doctors Collection (Updated)
```json
{
  "doctor_id": "doc_001",
  "doc_name": "Dr. Jane Smith",
  "available_status": false,  // Changes to false when appointment accepted
  "password": "hashed_password",
  "email": "doctor@example.com",
  "phone": "+1234567890",
  "created_at": "2026-01-28T15:38:02.947000",
  "updated_at": "2026-01-28T16:23:03.005000"
}
```

## Backend Implementation

### New Models (`backend/models/schemas.py`)

#### AppointmentRequestStatus Enum
```python
class AppointmentRequestStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
```

#### AppointmentRequestCreate
```python
class AppointmentRequestCreate(BaseModel):
    doctor_id: str
    reason: Optional[str]
    preferred_date: Optional[str]  # YYYY-MM-DD
    preferred_time: Optional[str]  # HH:MM
```

#### AppointmentRequestResponse
```python
class AppointmentRequestResponse(BaseModel):
    request_id: str
    user_id: str
    user_name: str
    doctor_id: str
    doctor_name: Optional[str]
    reason: Optional[str]
    preferred_date: Optional[str]
    preferred_time: Optional[str]
    status: str
    created_at: Optional[datetime]
```

#### AppointmentRequestUpdate
```python
class AppointmentRequestUpdate(BaseModel):
    status: AppointmentRequestStatus
    meet_link: Optional[str]
```

### New Database Methods (`backend/services/database_service.py`)

1. **create_appointment_request()** - Creates new appointment request
2. **get_appointment_request()** - Gets request by ID
3. **get_doctor_appointment_requests()** - Gets all requests for a doctor (with optional status filter)
4. **get_user_appointment_requests()** - Gets all requests for a user
5. **update_appointment_request()** - Updates request status and auto-changes doctor availability

### New API Endpoints (`backend/main.py`)

#### 1. Create Appointment Request
```
POST /api/appointment-requests
```

**Request Body:**
```json
{
  "user_id": "user_001",
  "doctor_id": "doc_001",
  "reason": "Regular checkup",
  "preferred_date": "2026-02-01",
  "preferred_time": "10:00"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Appointment request sent successfully",
  "request_id": "697a37ce819974d1e7711336"
}
```

#### 2. Get Doctor's Appointment Requests
```
GET /api/appointment-requests/doctor/{doctor_id}?status=PENDING
```

**Response:**
```json
[
  {
    "request_id": "697a37ce819974d1e7711336",
    "user_id": "user_001",
    "user_name": "John Doe",
    "doctor_id": "doc_001",
    "doctor_name": "Dr. Jane Smith",
    "reason": "Regular checkup",
    "preferred_date": "2026-02-01",
    "preferred_time": "10:00",
    "status": "PENDING",
    "created_at": "2026-01-28T16:22:38.342000"
  }
]
```

#### 3. Get User's Appointment Requests
```
GET /api/appointment-requests/user/{user_id}
```

#### 4. Update Appointment Request (Accept/Reject)
```
PUT /api/appointment-requests/{request_id}
```

**Request Body:**
```json
{
  "status": "ACCEPTED",
  "meet_link": "https://meet.google.com/abc-defg-hij"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Appointment request accepted"
}
```

**Auto-Updates:**
- Doctor's `available_status` set to `false`
- Doctor's `updated_at` timestamp updated

## Frontend Implementation

### 1. Home Page (`frontend/src/pages/HomePage.tsx`)

**Features:**
- **Displays only available doctors** (available_status = true)
- Doctor cards with:
  - Doctor name
  - Doctor ID
  - Email (if available)
  - Phone (if available)
  - Green "Available" badge
  - "Request Appointment" button
- **Appointment Request Modal:**
  - Reason for appointment (text area)
  - Preferred date (date picker)
  - Preferred time (time picker)
  - Submit/Cancel buttons
- **User Experience:**
  - Success message after request sent
  - Auto-closes modal after success
  - Error handling with clear messages
  - Loading states during submission

**Visibility:**
- **Users:** See all available doctors
- **Doctors:** Redirected to dashboard (don't need this page)

### 2. App Routing (`frontend/src/App.tsx`)

**Changes:**
- Default route changed from `/dashboard` to `/home`
- Added `AdminRoute` component for admin-only pages
- Admin page now restricted to users with:
  - `user_type === 'ADMIN'`, OR
  - `user_id === 'admin_001'`

**Route Structure:**
```tsx
/              → Redirects to /home
/home          → HomePage (Available doctors)
/dashboard     → Dashboard
/video-consultation → Video calls + Appointment requests (for doctors)
/admin         → AdminDashboard (Admin only)
```

### 3. Sidebar Updates (`frontend/src/components/Sidebar.tsx`)

**Changes:**
- Added "Home" menu item (with House icon)
- Admin menu item only shows for admin users
- Dynamic menu based on user role

**Menu Items:**
```
Home                (For all users)
Dashboard           (For all users)
AI Agents           (For all users)
Video Call          (For all users)
Hospitals           (For all users)
Analytics           (For all users)
Admin               (Admin only)
```

### 4. Video Consultation Page (To be updated)

**Upcoming Features:**
- Doctors see pending appointment requests
- Accept/Reject buttons
- Meet link input field when accepting
- Real-time updates of appointment status

## Testing

### 1. Create Appointment Request
```bash
curl -X POST http://localhost:8000/api/appointment-requests \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "doctor_id": "doc_001",
    "reason": "Regular checkup",
    "preferred_date": "2026-02-01",
    "preferred_time": "10:00"
  }'
```

**Expected:** Success message with request_id

### 2. View Doctor's Requests
```bash
curl http://localhost:8000/api/appointment-requests/doctor/doc_001
```

**Expected:** List of appointment requests

### 3. Accept Appointment
```bash
curl -X PUT http://localhost:8000/api/appointment-requests/{request_id} \
  -H "Content-Type: application/json" \
  -d '{
    "status": "ACCEPTED",
    "meet_link": "https://meet.google.com/abc-defg-hij"
  }'
```

**Expected:** 
- Success message
- Doctor's available_status changes to false

### 4. Check Doctor Status
```bash
curl http://localhost:8000/api/doctors/doc_001
```

**Expected:** `available_status: false`

### 5. View Available Doctors
```bash
curl http://localhost:8000/api/doctors
```

**Expected:** Only doctors with `available_status: true`

## User Flows

### User Flow
1. Login as user (user_001/password123)
2. Redirected to Home page
3. See available doctors
4. Click "Request Appointment" on a doctor
5. Fill form:
   - Reason: "Feeling unwell, need consultation"
   - Date: Tomorrow
   - Time: 2:00 PM
6. Submit request
7. See success message
8. Can view request status in Video Consultation page

### Doctor Flow
1. Login as doctor (doc_001/doctor123)
2. Go to Video Consultation page
3. See pending appointment requests
4. Review patient info and request details
5. If accepting:
   - Enter meet link
   - Click "Accept"
   - Status changes to busy
   - Disappear from home page
6. If rejecting:
   - Click "Reject"
   - Stays available

### Admin Flow
1. Login as admin (admin_001/admin123)
2. Access to Admin page (users/doctors can't access)
3. View statistics including total appointment requests
4. Manage users and doctors

## Security Features

1. **Authentication Required:**
   - All endpoints require user authentication
   - User ID validation

2. **Role-Based Access:**
   - Users can only create appointment requests
   - Doctors can only accept/reject their own requests
   - Admin has full access

3. **Data Validation:**
   - Pydantic models validate all inputs
   - Doctor existence check before creating request
   - User existence check

4. **Status Management:**
   - Automatic status updates
   - Prevents double-booking
   - Timestamp tracking

## Future Enhancements

### Phase 1 (Current)
- ✅ Home page with available doctors
- ✅ Appointment request creation
- ✅ Doctor status management
- ✅ Admin page restriction

### Phase 2 (Next)
- [ ] Doctor dashboard in Video Consultation page
- [ ] Accept/Reject UI for doctors
- [ ] Real-time notifications
- [ ] Email notifications to users

### Phase 3 (Future)
- [ ] Calendar integration
- [ ] Recurring appointments
- [ ] Appointment reminders
- [ ] Video call integration with meet links
- [ ] Prescription upload/download
- [ ] Medical history tracking
- [ ] Rating system for doctors
- [ ] Doctor availability schedule

## Environment Setup

### Backend Running
```bash
cd backend
python main.py
```
- Running on: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

### Frontend Running
```bash
cd frontend
npm run dev
```
- Running on: http://localhost:3000

## Key Files Modified/Created

### Created:
- `frontend/src/pages/HomePage.tsx` (345 lines)
- `APPOINTMENT_SYSTEM_GUIDE.md` (this file)

### Modified:
- `backend/models/schemas.py` - Added appointment request models
- `backend/services/database_service.py` - Added appointment request methods
- `backend/main.py` - Added appointment request endpoints
- `frontend/src/App.tsx` - Added AdminRoute and Home route
- `frontend/src/components/Sidebar.tsx` - Added Home link, hid Admin for non-admins

## Troubleshooting

### Issue: "User not authenticated"
**Solution:** Ensure user_id is included in request body

### Issue: "Doctor not found"
**Solution:** Verify doctor_id exists in database

### Issue: Doctor not showing on home page
**Cause:** Doctor's available_status is false (busy)
**Solution:** Either reject current appointment or wait for consultation to complete

### Issue: Can't access Admin page
**Cause:** User is not an admin
**Solution:** Login with admin credentials (admin_001) or change user_type to ADMIN

### Issue: Appointment request not appearing
**Cause:** Request status filter or database issue
**Solution:** Check without status filter, verify database connection

## API Documentation

Full API documentation available at:
```
http://localhost:8000/api/docs
```

Interactive API testing with Swagger UI.

---

**Status:** ✅ Fully Functional  
**Last Updated:** January 28, 2026  
**Version:** 1.0.0
