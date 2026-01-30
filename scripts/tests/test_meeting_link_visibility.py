#!/usr/bin/env python3
"""
Test script to verify meeting link visibility in API responses
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_doctor_appointments(doctor_id="doc_002"):
    """Test getting doctor's appointments with meeting links"""
    print(f"\n{'='*60}")
    print(f"Testing Doctor Appointments API")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/api/appointment-requests/doctor/{doctor_id}"
    print(f"\nGET {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            appointments = response.json()
            print(f"\nTotal Appointments: {len(appointments)}")
            
            for i, appt in enumerate(appointments, 1):
                print(f"\n--- Appointment {i} ---")
                print(f"Request ID: {appt.get('request_id')}")
                print(f"Patient: {appt.get('user_name')} ({appt.get('user_id')})")
                print(f"Status: {appt.get('status')}")
                print(f"Date: {appt.get('preferred_date')} at {appt.get('preferred_time')}")
                print(f"Reason: {appt.get('reason')}")
                
                # Check for meeting link
                if appt.get('meet_link'):
                    print(f"✅ Meeting Link: {appt.get('meet_link')}")
                    print(f"✅ Meeting ID: {appt.get('meeting_id')}")
                    print(f"✅ Room Name: {appt.get('meet_link', '').split('/')[-1]}")
                else:
                    print(f"❌ No meeting link (Status: {appt.get('status')})")
            
            # Summary
            accepted_with_links = [a for a in appointments if a.get('status') == 'ACCEPTED' and a.get('meet_link')]
            accepted_without_links = [a for a in appointments if a.get('status') == 'ACCEPTED' and not a.get('meet_link')]
            
            print(f"\n{'='*60}")
            print(f"SUMMARY:")
            print(f"  Total Appointments: {len(appointments)}")
            print(f"  Accepted with Links: {len(accepted_with_links)} ✅")
            print(f"  Accepted without Links: {len(accepted_without_links)} {'❌' if accepted_without_links else '✅'}")
            
            if accepted_without_links:
                print(f"\n⚠️  WARNING: {len(accepted_without_links)} accepted appointments are missing meeting links!")
            else:
                print(f"\n✅ All accepted appointments have meeting links!")
                
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")

def test_user_appointments(user_id="user_002"):
    """Test getting user's appointments with meeting links"""
    print(f"\n{'='*60}")
    print(f"Testing User Appointments API")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/api/appointment-requests/user/{user_id}"
    print(f"\nGET {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            appointments = response.json()
            print(f"\nTotal Appointments: {len(appointments)}")
            
            for i, appt in enumerate(appointments, 1):
                print(f"\n--- Appointment {i} ---")
                print(f"Request ID: {appt.get('request_id')}")
                print(f"Doctor: {appt.get('doctor_name')} ({appt.get('doctor_id')})")
                print(f"Status: {appt.get('status')}")
                print(f"Date: {appt.get('preferred_date')} at {appt.get('preferred_time')}")
                print(f"Reason: {appt.get('reason')}")
                
                # Check for meeting link
                if appt.get('meet_link'):
                    print(f"✅ Meeting Link: {appt.get('meet_link')}")
                    print(f"✅ Meeting ID: {appt.get('meeting_id')}")
                    print(f"✅ Room Name: {appt.get('meet_link', '').split('/')[-1]}")
                else:
                    print(f"❌ No meeting link (Status: {appt.get('status')})")
            
            # Summary
            accepted_with_links = [a for a in appointments if a.get('status') == 'ACCEPTED' and a.get('meet_link')]
            accepted_without_links = [a for a in appointments if a.get('status') == 'ACCEPTED' and not a.get('meet_link')]
            
            print(f"\n{'='*60}")
            print(f"SUMMARY:")
            print(f"  Total Appointments: {len(appointments)}")
            print(f"  Accepted with Links: {len(accepted_with_links)} ✅")
            print(f"  Accepted without Links: {len(accepted_without_links)} {'❌' if accepted_without_links else '✅'}")
            
            if accepted_without_links:
                print(f"\n⚠️  WARNING: {len(accepted_without_links)} accepted appointments are missing meeting links!")
            else:
                print(f"\n✅ All accepted appointments have meeting links!")
                
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")

def test_api_health():
    """Test if API is running"""
    print(f"\n{'='*60}")
    print(f"Testing API Health")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/api/statistics"
    print(f"\nGET {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ API is running!")
            print(f"\nStatistics:")
            print(f"  Total Users: {stats.get('total_users')}")
            print(f"  Total Doctors: {stats.get('total_doctors')}")
            print(f"  Available Doctors: {stats.get('available_doctors')}")
            print(f"  Total Appointments: {stats.get('total_appointments')}")
            return True
        else:
            print(f"❌ API Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        print(f"⚠️  Make sure the backend server is running on {BASE_URL}")
        return False

if __name__ == "__main__":
    print("\n🔍 Meeting Link Visibility Test")
    print(f"Backend URL: {BASE_URL}")
    
    # Test API health
    if not test_api_health():
        print("\n❌ Cannot proceed with tests - API is not responding")
        exit(1)
    
    # Test doctor appointments
    test_doctor_appointments()
    
    # Test user appointments
    test_user_appointments()
    
    print(f"\n{'='*60}")
    print("✅ Test completed!")
    print(f"{'='*60}\n")
