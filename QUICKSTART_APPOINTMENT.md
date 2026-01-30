# Quick Start Guide - Appointment System

## ✅ System is Ready!

### What's New

1. **Home Page** - Browse available doctors and request appointments
2. **Appointment Requests** - Users can send appointment requests to doctors
3. **Doctor Status Management** - Doctors become "busy" when they accept appointments
4. **Admin Restrictions** - Only admins can access the admin dashboard

---

## 🚀 How to Use

### For Users

1. **Access the Application**
   ```
   Open browser: http://localhost:3000
   ```

2. **Login**
   ```
   User ID: user_001
   Password: password123
   Type: USER
   ```

3. **Browse Doctors**
   - Home page shows all available doctors
   - Click "Request Appointment" on any doctor

4. **Request Appointment**
   - Fill in:
     - Reason for visit
     - Preferred date
     - Preferred time
   - Click "Send Request"

5. **Track Requests**
   - Go to Video Consultation page
   - View your appointment requests and their status

### For Doctors

1. **Login**
   ```
   User ID: doc_001
   Password: doctor123
   Type: DOCTOR
   ```

2. **View Appointment Requests**
   - Go to Video Consultation page
   - See all pending appointment requests

3. **Accept Appointment**
   - Review patient info
   - Enter meeting link (e.g., Google Meet)
   - Click "Accept"
   - **Your status automatically changes to BUSY**
   - You'll no longer appear on the home page

4. **Reject Appointment**
   - Click "Reject"
   - Stay available for other appointments

### For Admins

1. **Login**
   ```
   User ID: admin_001
   Password: admin123
   ```

2. **Access Admin Dashboard**
   - Only admins can see the Admin menu item
   - View statistics of all users, doctors, and appointments

---

## 📊 Current System Status

### Backend
- **Status:** ✅ Running
- **URL:** http://localhost:8000
- **Health:** http://localhost:8000/api/health
- **API Docs:** http://localhost:8000/api/docs

### Frontend
- **Status:** ✅ Running
- **URL:** http://localhost:3000

### Database
- **Connection:** ✅ MongoDB Atlas
- **Collections:** users, doctors, meetings, appointment_requests

### Statistics
- **Total Doctors:** 4
- **Available Doctors:** 2
- **Busy Doctors:** 2
- **Appointment Requests:** 1+

---

## 🔑 Test Accounts

### Users
| User ID | Password | Name |
|---------|----------|------|
| user_001 | password123 | John Doe |
| user_002 | password123 | Alice Smith |
| user_003 | password123 | Bob Johnson |
| user_999 | test123 | Test User |

### Doctors
| Doctor ID | Password | Name | Status |
|-----------|----------|------|--------|
| doc_001 | doctor123 | Dr. Jane Smith | Busy |
| doc_002 | doctor123 | Dr. Michael Chen | Available |
| doc_003 | doctor123 | Dr. Sarah Williams | Available |
| doc_999 | doctor123 | Dr. Test Doctor | Busy |

### Admin
| User ID | Password | Access |
|---------|----------|--------|
| admin_001 | admin123 | Full Admin Access |

---

## 🎯 Quick Test Flow

### Test 1: User Requests Appointment

```bash
# 1. Create appointment request
curl -X POST http://localhost:8000/api/appointment-requests \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_002",
    "doctor_id": "doc_002",
    "reason": "Medical consultation",
    "preferred_date": "2026-02-01",
    "preferred_time": "14:00"
  }'

# Expected: Success with request_id
```

### Test 2: Doctor Views Requests

```bash
# 2. View doctor's pending requests
curl http://localhost:8000/api/appointment-requests/doctor/doc_002

# Expected: List with 1 pending request from user_002
```

### Test 3: Doctor Accepts Appointment

```bash
# 3. Accept the appointment (use request_id from step 1)
curl -X PUT http://localhost:8000/api/appointment-requests/{request_id} \
  -H "Content-Type: application/json" \
  -d '{
    "status": "ACCEPTED",
    "meet_link": "https://meet.google.com/xyz-test-meet"
  }'

# Expected: Success message
```

### Test 4: Verify Doctor Status Changed

```bash
# 4. Check doctor is now busy
curl http://localhost:8000/api/doctors/doc_002

# Expected: "available_status": false
```

### Test 5: Home Page Only Shows Available Doctors

```bash
# 5. Get available doctors
curl http://localhost:8000/api/doctors | python3 -m json.tool | grep available_status

# Expected: Only doctors with "available_status": true
```

---

## 🎨 UI Navigation

### Menu Items

**Home** (🏠)
- View available doctors
- Request appointments

**Dashboard** (📊)
- AI chat interface
- Medical analysis

**AI Agents** (🧠)
- Agent information
- System status

**Video Call** (📹)
- Video consultations
- Appointment requests (for doctors)
- My appointments (for users)

**Hospitals** (📍)
- Find nearby hospitals
- Location services

**Analytics** (📈)
- Usage analytics
- System metrics

**Admin** (🛡️)
- **Only visible to admins**
- User management
- System statistics

---

## 🔄 Workflow Diagram

```
USER FLOW:
Login → Home → See Available Doctors → Request Appointment → Wait for Response

DOCTOR FLOW:
Login → Video Consultation → View Pending Requests → Accept/Reject → Status Changes

ADMIN FLOW:
Login → Admin Dashboard → View All Statistics → Manage System
```

---

## 🐛 Common Issues & Solutions

### Issue: Can't see any doctors on home page
**Solution:** All doctors are busy. Check admin dashboard or wait for appointments to complete.

### Issue: Admin menu not showing
**Solution:** You're not logged in as admin. Use admin_001 credentials.

### Issue: Appointment request failed
**Solution:** 
- Check if you're logged in
- Verify doctor exists and is available
- Check console for errors

### Issue: Frontend not loading
**Solution:**
```bash
cd frontend
npm run dev
```

### Issue: Backend not responding
**Solution:**
```bash
cd backend
python main.py
```

---

## 📝 Next Steps

### Immediate
1. **Test the system** - Login and try requesting an appointment
2. **Register new users** - Use the registration page
3. **Check admin dashboard** - View system statistics

### Future Development
- [ ] Real-time notifications
- [ ] Email alerts for appointment updates
- [ ] Calendar integration
- [ ] Video call embedded in app
- [ ] Doctor availability schedule
- [ ] Appointment history
- [ ] Rating & review system

---

## 📚 Documentation

For detailed information, see:
- **Full System Guide:** `APPOINTMENT_SYSTEM_GUIDE.md`
- **Registration Guide:** `REGISTRATION_GUIDE.md`
- **Authentication Guide:** `AUTHENTICATION_GUIDE.md`
- **API Documentation:** http://localhost:8000/api/docs

---

## 🆘 Need Help?

1. Check browser console (F12) for frontend errors
2. Check `/tmp/backend.log` for backend errors
3. Test API endpoints using curl or Postman
4. Verify MongoDB connection in database_service.py

---

**Status:** ✅ All Systems Operational  
**Version:** 2.0.0  
**Last Updated:** January 28, 2026

**Happy Testing! 🎉**
