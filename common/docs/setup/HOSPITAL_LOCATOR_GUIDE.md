# Hospital Locator Feature - Setup Guide

## Overview

The Hospital Locator is a new feature that helps users find nearby hospitals and medical facilities based on their current location. It uses OpenStreetMap's Overpass API to fetch real-time hospital data and displays them on an interactive map.

## Features

✅ **Real-time Location Detection** - Uses browser geolocation API  
✅ **Interactive Map** - Powered by Leaflet.js  
✅ **Hospital Search** - Finds hospitals within customizable radius (2-20km)  
✅ **Detailed Information** - Shows hospital name, distance, address, phone  
✅ **Emergency Services** - Highlights hospitals with emergency services  
✅ **Navigation** - Direct link to Google Maps for turn-by-turn directions  
✅ **Responsive Design** - Works on desktop and mobile devices  

## Technical Stack

### Frontend
- **React + TypeScript** - UI components
- **Leaflet.js** - Interactive maps (loaded dynamically)
- **Framer Motion** - Smooth animations
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

### Backend
- **FastAPI** - API endpoint
- **Requests** - HTTP client for Overpass API
- **OpenStreetMap Overpass API** - Hospital data source

## API Endpoint

### Find Nearby Hospitals

```http
GET /api/hospitals/nearby?lat={latitude}&lon={longitude}&radius={meters}
```

**Parameters:**
- `lat` (required): User's latitude
- `lon` (required): User's longitude  
- `radius` (optional): Search radius in meters (default: 5000)

**Response:**
```json
{
  "success": true,
  "count": 12,
  "hospitals": [
    {
      "id": 123456789,
      "name": "City General Hospital",
      "lat": 40.7128,
      "lon": -74.0060,
      "distance": 1234.56,
      "address": "123 Main St",
      "phone": "+1-555-0100",
      "emergency": true,
      "opening_hours": "24/7"
    }
  ],
  "user_location": {
    "lat": 40.7128,
    "lon": -74.0060
  },
  "search_radius": 5000
}
```

## Usage

### For Users

1. Navigate to **Hospitals** from the sidebar
2. Click **Find Hospitals** button
3. Allow location access when prompted
4. View nearby hospitals on the map
5. Click on markers or list items for details
6. Use **Directions** button for navigation

### For Developers

**Frontend Component:**
```tsx
import HospitalLocator from './pages/HospitalLocator';

// Add to routes
<Route path="/hospitals" element={<HospitalLocator />} />
```

**API Service:**
```typescript
// Find nearby hospitals
const hospitals = await api.findNearbyHospitals(lat, lon, radius);
```

**Backend Endpoint:**
```python
@app.get("/api/hospitals/nearby")
async def find_nearby_hospitals(lat: float, lon: float, radius: int = 5000):
    # Implementation in main.py
```

## How It Works

### 1. Location Detection
```javascript
navigator.geolocation.getCurrentPosition((position) => {
  const lat = position.coords.latitude;
  const lon = position.coords.longitude;
  // ... fetch hospitals
});
```

### 2. Map Initialization
```javascript
const map = L.map('map').setView([lat, lon], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
```

### 3. Hospital Data Fetch
```python
overpass_query = f"""
[out:json];
(
  node["amenity"="hospital"](around:{radius},{lat},{lon});
  way["amenity"="hospital"](around:{radius},{lat},{lon});
  relation["amenity"="hospital"](around:{radius},{lat},{lon});
);
out center;
"""
```

### 4. Distance Calculation
Uses Haversine formula:
```python
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    # ... haversine implementation
    return distance
```

## Configuration

### Search Radius Options
- 2 km - Very close proximity
- 5 km - Default, good for urban areas
- 10 km - Suburban areas
- 20 km - Rural areas

### Map Settings
- Default zoom: 13
- Tile provider: OpenStreetMap
- Attribution: Required by OSM license

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

**Requirements:**
- Geolocation API support
- JavaScript enabled
- Internet connection

## Privacy & Security

- ✅ Location data is NOT stored on server
- ✅ Only sent to OSM Overpass API
- ✅ User must grant location permission
- ✅ HTTPS required in production
- ✅ No tracking or analytics

## Troubleshooting

### "Unable to retrieve location"
- Check browser permissions
- Ensure HTTPS in production
- Verify location services enabled

### "Failed to fetch hospitals"
- Check internet connection
- Overpass API may be down
- Try reducing search radius

### Map not loading
- Check console for errors
- Verify Leaflet CDN accessible
- Clear browser cache

### No hospitals found
- Increase search radius
- Area may have limited OSM data
- Try different location

## Performance

- Initial load: < 2 seconds
- API response: 1-3 seconds (depends on OSM)
- Map rendering: < 500ms
- Marker updates: Instant

## Future Enhancements

- [ ] Filter by hospital type (general, specialty, etc.)
- [ ] Show hospital capacity/ratings
- [ ] Real-time ambulance availability
- [ ] Offline map caching
- [ ] Save favorite hospitals
- [ ] Emergency contact integration
- [ ] Multi-language support
- [ ] Accessibility improvements

## Resources

- [Leaflet Documentation](https://leafletjs.com/)
- [OpenStreetMap Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API)
- [OSM Hospital Tags](https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dhospital)
- [Geolocation API](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API)

## Credits

- Map tiles © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors
- Hospital data from OpenStreetMap
- Map library: [Leaflet](https://leafletjs.com/)

## License

This feature is part of the Multi-Agent Medical Assistant project.
Map data © OpenStreetMap contributors, ODbL license.

---

**Last Updated:** January 28, 2026
