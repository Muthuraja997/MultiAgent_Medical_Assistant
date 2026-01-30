"""
Test script for Hospital Locator API endpoint
"""
import requests
import json

def test_hospital_endpoint():
    """Test the /api/hospitals/nearby endpoint"""
    
    # Test coordinates (New York City)
    lat = 40.7128
    lon = -74.0060
    radius = 5000
    
    # Backend URL
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/hospitals/nearby"
    
    print("=" * 60)
    print("Testing Hospital Locator API")
    print("=" * 60)
    print(f"📍 Location: {lat}, {lon}")
    print(f"📏 Radius: {radius}m ({radius/1000}km)")
    print()
    
    try:
        # Make request
        print("🔄 Sending request...")
        response = requests.get(
            endpoint,
            params={"lat": lat, "lon": lon, "radius": radius},
            timeout=15
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Success: {data.get('success')}")
            print(f"📊 Hospitals found: {data.get('count')}")
            print()
            
            hospitals = data.get('hospitals', [])
            
            if hospitals:
                print("Top 5 nearest hospitals:")
                print("-" * 60)
                
                for i, hospital in enumerate(hospitals[:5], 1):
                    print(f"\n{i}. {hospital.get('name', 'Unknown')}")
                    print(f"   📍 Distance: {hospital.get('distance', 0):.2f}m ({hospital.get('distance', 0)/1000:.2f}km)")
                    print(f"   🗺️  Location: {hospital.get('lat')}, {hospital.get('lon')}")
                    if hospital.get('address'):
                        print(f"   📫 Address: {hospital.get('address')}")
                    if hospital.get('phone'):
                        print(f"   📞 Phone: {hospital.get('phone')}")
                    if hospital.get('emergency'):
                        print(f"   🚨 Emergency: Yes")
                    if hospital.get('opening_hours'):
                        print(f"   🕐 Hours: {hospital.get('opening_hours')}")
            else:
                print("❌ No hospitals found in the specified radius")
                print("   Try increasing the search radius")
            
            print()
            print("=" * 60)
            print("✅ Test completed successfully!")
            print("=" * 60)
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server is not running")
        print("   Start the server with: cd backend && python main.py")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout: Request took too long")
        print("   The OpenStreetMap API might be slow")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_different_locations():
    """Test with multiple locations"""
    
    locations = [
        {"name": "New York City", "lat": 40.7128, "lon": -74.0060},
        {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
        {"name": "London", "lat": 51.5074, "lon": -0.1278},
        {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
    ]
    
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/hospitals/nearby"
    
    print("\n\n" + "=" * 60)
    print("Testing Multiple Locations")
    print("=" * 60)
    
    for loc in locations:
        print(f"\n📍 {loc['name']}")
        try:
            response = requests.get(
                endpoint,
                params={"lat": loc['lat'], "lon": loc['lon'], "radius": 5000},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                print(f"   ✅ Found {count} hospitals")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")


if __name__ == "__main__":
    # Run basic test
    test_hospital_endpoint()
    
    # Uncomment to test multiple locations
    # test_different_locations()
