# Hospital Locator - System Architecture

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER BROWSER                               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │   React Component: HospitalLocator.tsx                  │  │
│  │                                                           │  │
│  │   1. User clicks "Find Hospitals"                       │  │
│  │   2. Request geolocation permission                     │  │
│  │   3. Get coordinates (lat, lon)                         │  │
│  │   4. Initialize Leaflet map                             │  │
│  │   5. Display user location marker                       │  │
│  └─────────────────┬───────────────────────────────────────┘  │
│                    │                                            │
│                    │ HTTP GET Request                           │
│                    │ /api/hospitals/nearby?lat=X&lon=Y          │
│                    ▼                                            │
└────────────────────┼──────────────────────────────────────────┘
                     │
                     │
┌────────────────────┼──────────────────────────────────────────┐
│                    │        BACKEND SERVER                      │
│                    │        (FastAPI - Python)                  │
│  ┌─────────────────▼───────────────────────────────────────┐  │
│  │   API Endpoint: /api/hospitals/nearby                   │  │
│  │                                                           │  │
│  │   1. Receive lat, lon, radius parameters               │  │
│  │   2. Build Overpass API query                           │  │
│  │   3. Send request to OSM                                │  │
│  └─────────────────┬───────────────────────────────────────┘  │
│                    │                                            │
│                    │ HTTP POST with Overpass Query              │
│                    ▼                                            │
└────────────────────┼──────────────────────────────────────────┘
                     │
                     │
┌────────────────────┼──────────────────────────────────────────┐
│                    │   OPENSTREETMAP OVERPASS API               │
│  ┌─────────────────▼───────────────────────────────────────┐  │
│  │   Query Processing                                       │  │
│  │                                                           │  │
│  │   [out:json];                                           │  │
│  │   node["amenity"="hospital"](around:5000,lat,lon);      │  │
│  │   way["amenity"="hospital"](around:5000,lat,lon);       │  │
│  │   relation["amenity"="hospital"](around:5000,lat,lon);  │  │
│  │   out center;                                            │  │
│  │                                                           │  │
│  │   Returns: Hospital nodes with coordinates & metadata   │  │
│  └─────────────────┬───────────────────────────────────────┘  │
│                    │                                            │
│                    │ JSON Response                              │
│                    ▼                                            │
└────────────────────┼──────────────────────────────────────────┘
                     │
                     │
┌────────────────────┼──────────────────────────────────────────┐
│                    │        BACKEND SERVER                      │
│  ┌─────────────────▼───────────────────────────────────────┐  │
│  │   Data Processing                                        │  │
│  │                                                           │  │
│  │   For each hospital:                                    │  │
│  │   - Extract coordinates (lat, lon)                      │  │
│  │   - Get name, address, phone, etc.                      │  │
│  │   - Calculate distance (Haversine formula)              │  │
│  │   - Check if emergency services available               │  │
│  │   - Build hospital object                               │  │
│  │                                                           │  │
│  │   Sort hospitals by distance (nearest first)            │  │
│  └─────────────────┬───────────────────────────────────────┘  │
│                    │                                            │
│                    │ JSON Response                              │
│                    ▼                                            │
└────────────────────┼──────────────────────────────────────────┘
                     │
                     │
┌────────────────────┼──────────────────────────────────────────┐
│                    │      USER BROWSER                          │
│  ┌─────────────────▼───────────────────────────────────────┐  │
│  │   React Component: HospitalLocator.tsx                  │  │
│  │                                                           │  │
│  │   Receive hospital data:                                │  │
│  │   {                                                      │  │
│  │     success: true,                                       │  │
│  │     count: 12,                                           │  │
│  │     hospitals: [...]                                     │  │
│  │   }                                                      │  │
│  │                                                           │  │
│  │   1. Update state with hospital data                    │  │
│  │   2. Add markers to map (Leaflet)                       │  │
│  │      - Green markers (normal hospitals)                 │  │
│  │      - Red markers (emergency hospitals)                │  │
│  │   3. Display hospital list below map                    │  │
│  │   4. Fit map bounds to show all hospitals               │  │
│  └───────────────────────────────────────────────────────── │  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │   User Interactions                                      │  │
│  │                                                           │  │
│  │   - Click marker → Show popup with details              │  │
│  │   - Click list item → Highlight on map                  │  │
│  │   - Click "Directions" → Open Google Maps               │  │
│  │   - Click phone → Initiate call                         │  │
│  │   - Change radius → Re-fetch hospitals                  │  │
│  └───────────────────────────────────────────────────────── │  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      App.tsx (Root)                         │
│                                                             │
│  ┌──────────┐  ┌────────────┐  ┌──────────────────────┐   │
│  │ Sidebar  │  │   Header   │  │   Main Content       │   │
│  │          │  │            │  │                      │   │
│  │ - Home   │  │ Status     │  │  <Routes>            │   │
│  │ - Agents │  │ Connection │  │    /dashboard        │   │
│  │ - Charts │  │            │  │    /analytics        │   │
│  │►Hospitals│  │            │  │    /agents           │   │
│  │ - Settings│  │            │  │  ► /hospitals ◄     │   │
│  └──────────┘  └────────────┘  │                      │   │
│                                 │  <HospitalLocator /> │   │
│                                 └──────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## HospitalLocator Component Structure

```
┌─────────────────────────────────────────────────────────────┐
│               HospitalLocator Component                     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Header Section                                      │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │ 🏥 Hospital Locator                          │   │   │
│  │  │ Find nearby hospitals and medical facilities│   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Controls Section                                    │   │
│  │  ┌──────────────────┐  ┌──────────────────────┐    │   │
│  │  │ Search Radius    │  │  [Find Hospitals]    │    │   │
│  │  │ [2km|5km|10km] ▼ │  │                      │    │   │
│  │  └──────────────────┘  └──────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Map Section (Leaflet.js)                           │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │                                              │   │   │
│  │  │  🔵 Your Location                           │   │   │
│  │  │                                              │   │   │
│  │  │  🟢 Hospital #1 (Normal)                    │   │   │
│  │  │                                              │   │   │
│  │  │  🔴 Hospital #2 (Emergency)                 │   │   │
│  │  │                                              │   │   │
│  │  │  🟢 Hospital #3                             │   │   │
│  │  │                                              │   │   │
│  │  │  [OpenStreetMap tiles]                      │   │   │
│  │  │                                              │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Hospital List Section                              │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │ 🟢 1. City General Hospital    [Directions] │   │   │
│  │  │    📍 1.2 km away                           │   │   │
│  │  │    📫 123 Main St                           │   │   │
│  │  │    📞 +1-555-0100                           │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │ 🔴 2. Emergency Medical Center [Directions] │   │   │
│  │  │    🚨 Emergency Services                     │   │   │
│  │  │    📍 2.5 km away                           │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## State Management

```javascript
useState hooks:
┌──────────────────────────────────────────────────────┐
│ userLocation: { lat: number, lon: number } | null   │
│ hospitals: Hospital[]                                │
│ loading: boolean                                     │
│ error: string | null                                 │
│ selectedHospital: Hospital | null                    │
│ searchRadius: number (2000|5000|10000|20000)        │
└──────────────────────────────────────────────────────┘

useRef hooks:
┌──────────────────────────────────────────────────────┐
│ mapRef: Reference to map DOM element                 │
│ mapInstanceRef: Leaflet map instance                 │
│ markersRef: Array of Leaflet marker objects          │
└──────────────────────────────────────────────────────┘
```

## API Request Flow

```
User Action → getUserLocation()
              ↓
         navigator.geolocation.getCurrentPosition()
              ↓
         Got coordinates (lat, lon)
              ↓
         initializeMap(location) ← Create Leaflet map
              ↓
         fetchHospitals(location)
              ↓
         api.findNearbyHospitals(lat, lon, radius)
              ↓
         Backend: GET /api/hospitals/nearby
              ↓
         Backend: Query Overpass API
              ↓
         Backend: Process & calculate distances
              ↓
         Backend: Return sorted hospital list
              ↓
         Frontend: Update hospitals state
              ↓
         addHospitalMarkers(hospitals) ← Add markers to map
              ↓
         Display hospital list
              ↓
         User can interact with map & list
```

## Distance Calculation (Haversine Formula)

```
Given two points on Earth:
  Point A (user):     lat1, lon1
  Point B (hospital): lat2, lon2

Calculate:
  φ1 = lat1 in radians
  φ2 = lat2 in radians
  Δφ = (lat2 - lat1) in radians
  Δλ = (lon2 - lon1) in radians

  a = sin²(Δφ/2) + cos(φ1) × cos(φ2) × sin²(Δλ/2)
  c = 2 × atan2(√a, √(1-a))
  
  distance = R × c
  where R = 6,371,000 meters (Earth's radius)

Result: Distance in meters
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────┐
│ Potential Errors                                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 1. Geolocation Permission Denied                   │
│    → Show error message                            │
│    → Suggest enabling location                     │
│                                                     │
│ 2. Geolocation Timeout                             │
│    → Show error message                            │
│    → Suggest retry                                 │
│                                                     │
│ 3. Backend Connection Failed                       │
│    → Show error message                            │
│    → Check backend is running                      │
│                                                     │
│ 4. Overpass API Timeout                            │
│    → Show error message                            │
│    → Suggest retry or smaller radius               │
│                                                     │
│ 5. No Hospitals Found                              │
│    → Show message                                  │
│    → Suggest increasing search radius              │
│                                                     │
│ 6. Map Loading Failed                              │
│    → Check internet connection                     │
│    → Reload Leaflet from CDN                       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Security & Privacy

```
┌─────────────────────────────────────────────────────┐
│ Privacy Measures                                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ✅ Location data NEVER stored on server            │
│ ✅ Only sent to OSM Overpass API                   │
│ ✅ User must explicitly grant permission           │
│ ✅ No cookies or tracking                          │
│ ✅ No analytics or logging of location             │
│ ✅ HTTPS required in production                    │
│ ✅ CORS properly configured                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Performance Optimizations

```
┌─────────────────────────────────────────────────────┐
│ Optimization Techniques                             │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 1. Leaflet CDN Loading                             │
│    - Cached by browser                             │
│    - No build size impact                          │
│                                                     │
│ 2. Marker Cleanup                                   │
│    - Remove old markers before adding new          │
│    - Prevent memory leaks                          │
│                                                     │
│ 3. Map Bounds Fitting                               │
│    - Auto-zoom to show all hospitals               │
│    - Optimal viewing experience                    │
│                                                     │
│ 4. Debounced Updates                                │
│    - Wait for user to finish selecting radius      │
│                                                     │
│ 5. Efficient Rendering                              │
│    - Framer Motion for smooth animations           │
│    - Virtual scrolling for large lists             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

**Architecture Version**: 1.0  
**Last Updated**: January 28, 2026  
**Author**: Multi-Agent Medical Assistant Team
