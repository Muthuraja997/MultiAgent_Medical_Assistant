# 🚀 Quick Start - Authentication System

## System Overview

✅ **3 Database Collections**: Users, Doctors, Meetings  
✅ **Role-Based Auth**: USER and DOCTOR roles  
✅ **Login Page**: Beautiful UI with authentication  
✅ **Protected Routes**: All routes require login  
✅ **Session Management**: Token-based authentication  

## 📋 Quick Setup

### 1. Start Backend
```bash
cd backend
source ../venv/bin/activate
python main.py
```
Backend runs on: `http://localhost:8000`

### 2. Create Test Data
```bash
cd scripts/tests
python create_test_users.py
```

This creates:
- 3 test users
- 3 test doctors  
- 3 test meetings

### 3. Start Frontend
```bash
cd frontend
npm run dev
```
Frontend runs on: `http://localhost:5173`

### 4. Login
Navigate to `http://localhost:5173` (auto-redirects to `/login`)

**Test Credentials:**
- **User:** `user_001` / `password123`
- **Doctor:** `doc_001` / `doctor123`

## 📊 Database Schema

### Users
- user_id, user_name, user_type
- appointment_status, doctor_id
- password (hashed)

### Doctors  
- doctor_id, doc_name
- available_status
- password (hashed)

### Meetings
- doctor_id, meet_link
- start_meet_time, end_meet_time

## 🔑 API Endpoints

### Authentication
- `POST /api/login` - Login endpoint

### Users
- `POST /api/users` - Create user
- `GET /api/users` - Get all users
- `GET /api/users/{id}` - Get user by ID
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

### Doctors
- `POST /api/doctors` - Create doctor
- `GET /api/doctors` - Get all doctors
- `GET /api/doctors/{id}` - Get doctor by ID
- `PUT /api/doctors/{id}` - Update doctor
- `DELETE /api/doctors/{id}` - Delete doctor
- `PATCH /api/doctors/{id}/availability` - Toggle availability

### Meetings
- `POST /api/meetings` - Create meeting
- `GET /api/meetings` - Get all meetings
- `GET /api/meetings/doctor/{id}` - Get doctor meetings
- `PUT /api/meetings/{id}` - Update meeting
- `DELETE /api/meetings/{id}` - Delete meeting

### Admin
- `GET /api/admin/statistics` - Get statistics

## 🎯 Features

✅ **Login Page** - Role selection (USER/DOCTOR)  
✅ **Password Hashing** - SHA-256 encryption  
✅ **Protected Routes** - Auth required for all pages  
✅ **Session Storage** - localStorage management  
✅ **Logout Function** - Sidebar logout button  
✅ **User Info Display** - Current user in sidebar  

## 📱 User Roles

### USER
- Personal dashboard
- View doctors
- Book appointments
- Hospital locator
- Video consultations

### DOCTOR  
- Doctor dashboard
- Manage availability
- View appointments
- Manage meetings
- Patient analytics

## 🔐 Security

✅ Password hashing (SHA-256)  
✅ Protected routes  
✅ Token-based auth  
✅ Role-based access  
✅ Secure password storage  

## 📚 Documentation

- `AUTHENTICATION_GUIDE.md` - Full authentication docs
- `DATABASE_INTEGRATION.md` - Database schema & APIs
- `COMPLETE_SYSTEM_SUMMARY.md` - Complete implementation
- API Docs: `http://localhost:8000/docs`

## 🆘 Troubleshooting

### Login Not Working
1. Ensure backend is running
2. Check MongoDB connection
3. Verify test users were created
4. Check browser console for errors

### Protected Routes Not Working
1. Clear browser localStorage
2. Login again
3. Check if token exists in localStorage

### Create Test Users Failing
1. Ensure backend is running on port 8000
2. Check MongoDB connection string
3. Verify MongoDB Atlas is accessible

## ✅ Verification Checklist

- [ ] Backend running on `http://localhost:8000`
- [ ] MongoDB connected successfully
- [ ] Test users created
- [ ] Frontend running on `http://localhost:5173`
- [ ] Can login as USER
- [ ] Can login as DOCTOR
- [ ] Protected routes working
- [ ] Logout working
- [ ] User info displayed in sidebar

## 🎉 Success!

Your system is ready! Login and enjoy the full Medical AI Assistant platform.

**Test Accounts:**
```
USER:   user_001 / password123
DOCTOR: doc_001 / doctor123
```

Happy coding! 🚀
