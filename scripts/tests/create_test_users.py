"""
Create Test Users Script

This script creates test users, doctors, and meetings in the database.
Run this after starting the backend to set up test data.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def create_test_users():
    """Create test users"""
    users = [
        {
            "user_id": "user_001",
            "user_name": "John Doe",
            "user_type": "USER",
            "appointment_status": "SCHEDULED",
            "password": "password123"
        },
        {
            "user_id": "user_002",
            "user_name": "Alice Smith",
            "user_type": "USER",
            "appointment_status": "SCHEDULED",
            "doctor_id": "doc_001",
            "password": "password123"
        },
        {
            "user_id": "user_003",
            "user_name": "Bob Johnson",
            "user_type": "USER",
            "appointment_status": "ACTIVE",
            "doctor_id": "doc_002",
            "password": "password123"
        }
    ]
    
    print("Creating test users...")
    for user in users:
        try:
            response = requests.post(f"{BASE_URL}/api/users", json=user)
            if response.status_code == 200:
                print(f"✅ Created user: {user['user_name']} ({user['user_id']})")
            else:
                print(f"❌ Failed to create {user['user_name']}: {response.json()}")
        except Exception as e:
            print(f"❌ Error creating {user['user_name']}: {str(e)}")


def create_test_doctors():
    """Create test doctors"""
    doctors = [
        {
            "doctor_id": "doc_001",
            "doc_name": "Dr. Jane Smith",
            "available_status": True,
            "password": "doctor123"
        },
        {
            "doctor_id": "doc_002",
            "doc_name": "Dr. Michael Chen",
            "available_status": True,
            "password": "doctor123"
        },
        {
            "doctor_id": "doc_003",
            "doc_name": "Dr. Sarah Williams",
            "available_status": False,
            "password": "doctor123"
        }
    ]
    
    print("\nCreating test doctors...")
    for doctor in doctors:
        try:
            response = requests.post(f"{BASE_URL}/api/doctors", json=doctor)
            if response.status_code == 200:
                print(f"✅ Created doctor: {doctor['doc_name']} ({doctor['doctor_id']})")
            else:
                print(f"❌ Failed to create {doctor['doc_name']}: {response.json()}")
        except Exception as e:
            print(f"❌ Error creating {doctor['doc_name']}: {str(e)}")


def create_test_meetings():
    """Create test meetings"""
    meetings = [
        {
            "doctor_id": "doc_001",
            "meet_link": "https://meet.jit.si/dr-jane-smith-room",
            "start_meet_time": "09:00",
            "end_meet_time": "17:00"
        },
        {
            "doctor_id": "doc_002",
            "meet_link": "https://meet.jit.si/dr-michael-chen-room",
            "start_meet_time": "10:00",
            "end_meet_time": "18:00"
        },
        {
            "doctor_id": "doc_003",
            "meet_link": "https://meet.jit.si/dr-sarah-williams-room",
            "start_meet_time": "08:00",
            "end_meet_time": "16:00"
        }
    ]
    
    print("\nCreating test meetings...")
    for meeting in meetings:
        try:
            response = requests.post(f"{BASE_URL}/api/meetings", json=meeting)
            if response.status_code == 200:
                print(f"✅ Created meeting for {meeting['doctor_id']}")
            else:
                print(f"❌ Failed to create meeting for {meeting['doctor_id']}: {response.json()}")
        except Exception as e:
            print(f"❌ Error creating meeting for {meeting['doctor_id']}: {str(e)}")


def test_login():
    """Test login functionality"""
    print("\n" + "="*60)
    print("Testing Login Functionality")
    print("="*60)
    
    # Test user login
    print("\nTesting USER login...")
    user_login = {
        "user_id": "user_001",
        "password": "password123",
        "user_type": "USER"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/login", json=user_login)
        result = response.json()
        if result.get("success"):
            print(f"✅ User login successful!")
            print(f"   Name: {result.get('user_name')}")
            print(f"   Token: {result.get('token')[:20]}...")
        else:
            print(f"❌ User login failed: {result.get('message')}")
    except Exception as e:
        print(f"❌ User login error: {str(e)}")
    
    # Test doctor login
    print("\nTesting DOCTOR login...")
    doctor_login = {
        "user_id": "doc_001",
        "password": "doctor123",
        "user_type": "DOCTOR"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/login", json=doctor_login)
        result = response.json()
        if result.get("success"):
            print(f"✅ Doctor login successful!")
            print(f"   Name: {result.get('user_name')}")
            print(f"   Token: {result.get('token')[:20]}...")
        else:
            print(f"❌ Doctor login failed: {result.get('message')}")
    except Exception as e:
        print(f"❌ Doctor login error: {str(e)}")


def get_statistics():
    """Get and display statistics"""
    print("\n" + "="*60)
    print("Platform Statistics")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/statistics")
        stats = response.json()
        print(f"\nTotal Users: {stats.get('total_users')}")
        print(f"Total Doctors: {stats.get('total_doctors')}")
        print(f"Available Doctors: {stats.get('available_doctors')}")
        print(f"Total Meetings: {stats.get('total_meetings')}")
    except Exception as e:
        print(f"❌ Error fetching statistics: {str(e)}")


def main():
    """Main function"""
    print("="*60)
    print("Multi-Agent Medical Assistant - Test Data Creator")
    print("="*60)
    print(f"\nConnecting to: {BASE_URL}")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("✅ Backend is running!\n")
    except Exception as e:
        print("❌ Backend is not running!")
        print(f"   Error: {str(e)}")
        print("\nPlease start the backend first:")
        print("   cd backend")
        print("   source ../venv/bin/activate")
        print("   python main.py")
        return
    
    # Create test data
    create_test_users()
    create_test_doctors()
    create_test_meetings()
    
    # Test login
    test_login()
    
    # Show statistics
    get_statistics()
    
    # Show credentials
    print("\n" + "="*60)
    print("Test Credentials")
    print("="*60)
    print("\nUSER Accounts:")
    print("  user_001 / password123 (John Doe)")
    print("  user_002 / password123 (Alice Smith)")
    print("  user_003 / password123 (Bob Johnson)")
    print("\nDOCTOR Accounts:")
    print("  doc_001 / doctor123 (Dr. Jane Smith)")
    print("  doc_002 / doctor123 (Dr. Michael Chen)")
    print("  doc_003 / doctor123 (Dr. Sarah Williams)")
    print("\nLogin at: http://localhost:5173/login")
    print("="*60)


if __name__ == "__main__":
    main()
