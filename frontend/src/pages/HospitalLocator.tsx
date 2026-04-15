/**
 * Hospital Locator Component
 * Find nearby hospitals using OpenStreetMap data
 */
import { useState, useEffect, useRef } from 'react';
import { MapPin, Navigation, Phone, Clock, AlertCircle, Loader2, Building2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { api } from '../services/api';

// Leaflet types
declare const L: any;

interface Hospital {
  id: number;
  name: string;
  lat: number;
  lon: number;
  distance?: number;
  address?: string;
  phone?: string;
  emergency?: boolean;
  opening_hours?: string;
}

/** Same path on localhost; includes port only when the current page URL has one (avoids http://localhost:/path). */
function localhostUrlForCurrentPath(): string {
  const { port, pathname } = window.location;
  const portPart = port ? `:${port}` : '';
  return `http://localhost${portPart}${pathname}`;
}

function ngrokPortHint(): string {
  return window.location.port || '3000';
}

const HospitalLocator = () => {
  const [userLocation, setUserLocation] = useState<{ lat: number; lon: number } | null>(null);
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedHospital, setSelectedHospital] = useState<Hospital | null>(null);
  const [searchRadius, setSearchRadius] = useState(5000); // meters
  const mapRef = useRef<any>(null);
  const mapInstanceRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);

  // Initialize Leaflet
  useEffect(() => {
    // Load Leaflet CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    document.head.appendChild(link);

    // Load Leaflet JS
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    script.async = true;
    script.onload = () => {
      console.log('Leaflet loaded successfully');
    };
    document.head.appendChild(script);

    return () => {
      document.head.removeChild(link);
      document.head.removeChild(script);
    };
  }, []);

  // Get user location
  const getUserLocation = () => {
    setLoading(true);
    setError(null);

    // Check if geolocation is supported
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      setLoading(false);
      return;
    }

    // Check if page is served over HTTPS or localhost
    const isSecure = window.location.protocol === 'https:' || 
                     window.location.hostname === 'localhost' || 
                     window.location.hostname === '127.0.0.1';

    if (!isSecure) {
      const currentUrl = window.location.href;
      const isLocalNetwork = /^http:\/\/(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)/.test(currentUrl);
      
      let errorMsg = 'Geolocation requires HTTPS or localhost. ';
      
      if (isLocalNetwork) {
        errorMsg +=
          'You are accessing via local network IP. Please use one of these options instead: (1) ' +
          localhostUrlForCurrentPath() +
          ' or (2) Setup ngrok for HTTPS access.';
      } else {
        errorMsg += 'Please access via HTTPS URL (e.g., https://your-ngrok-url.ngrok-free.dev) or use localhost for testing.';
      }
      
      setError(errorMsg);
      setLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const location = {
          lat: position.coords.latitude,
          lon: position.coords.longitude,
        };
        setUserLocation(location);
        initializeMap(location);
        fetchHospitals(location);
      },
      (error) => {
        let errorMessage = `Unable to retrieve your location: ${error.message}`;
        
        // Provide helpful error messages based on error code
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Location permission denied. Please allow location access in your browser settings.';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location information is unavailable. Please try again.';
            break;
          case error.TIMEOUT:
            errorMessage = 'Location request timed out. Please try again.';
            break;
        }
        
        setError(errorMessage);
        setLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  };

  // Initialize map
  const initializeMap = (location: { lat: number; lon: number }) => {
    if (!mapRef.current || typeof L === 'undefined') return;

    // Clear existing map
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
    }

    // Create new map
    const map = L.map(mapRef.current).setView([location.lat, location.lon], 13);

    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map);

    // Add user location marker
    const userIcon = L.divIcon({
      className: 'custom-user-marker',
      html: '<div style="background: #3b82f6; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>',
      iconSize: [20, 20],
    });

    L.marker([location.lat, location.lon], { icon: userIcon })
      .addTo(map)
      .bindPopup('<strong>Your Location</strong>')
      .openPopup();

    mapInstanceRef.current = map;
  };

  // Fetch hospitals from backend
  const fetchHospitals = async (location: { lat: number; lon: number }) => {
    try {
      setLoading(true);
      const response = await api.findNearbyHospitals(location.lat, location.lon, searchRadius);
      
      const hospitalsData: Hospital[] = response.hospitals || [];
      setHospitals(hospitalsData);
      addHospitalMarkers(hospitalsData);
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch hospitals');
      setLoading(false);
    }
  };

  // Add hospital markers to map
  const addHospitalMarkers = (hospitals: Hospital[]) => {
    if (!mapInstanceRef.current) return;

    // Clear existing markers
    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current = [];

    // Add new markers
    hospitals.forEach((hospital, index) => {
      if (!hospital.lat || !hospital.lon) return;

      const hospitalIcon = L.divIcon({
        className: 'custom-hospital-marker',
        html: `<div style="background: ${hospital.emergency ? '#ef4444' : '#10b981'}; width: 32px; height: 32px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 12px;">${index + 1}</div>`,
        iconSize: [32, 32],
      });

      const marker = L.marker([hospital.lat, hospital.lon], { icon: hospitalIcon })
        .addTo(mapInstanceRef.current)
        .bindPopup(`
          <div style="min-width: 200px;">
            <strong style="font-size: 14px;">${hospital.name || 'Hospital'}</strong>
            ${hospital.distance ? `<p style="margin: 4px 0; font-size: 12px;">📍 ${(hospital.distance / 1000).toFixed(2)} km away</p>` : ''}
            ${hospital.address ? `<p style="margin: 4px 0; font-size: 11px;">📍 ${hospital.address}</p>` : ''}
            ${hospital.phone ? `<p style="margin: 4px 0; font-size: 11px;">📞 ${hospital.phone}</p>` : ''}
            ${hospital.emergency ? '<p style="margin: 4px 0; font-size: 11px; color: #ef4444;">🚨 Emergency Services Available</p>' : ''}
          </div>
        `);

      marker.on('click', () => {
        setSelectedHospital(hospital);
      });

      markersRef.current.push(marker);
    });

    // Fit map to show all markers
    if (hospitals.length > 0 && userLocation) {
      const bounds = L.latLngBounds(
        hospitals.map((h) => [h.lat, h.lon]).concat([[userLocation.lat, userLocation.lon]])
      );
      mapInstanceRef.current.fitBounds(bounds, { padding: [50, 50] });
    }
  };

  // Open directions in Google Maps
  const openDirections = (hospital: Hospital) => {
    if (!userLocation) return;
    const url = `https://www.google.com/maps/dir/?api=1&origin=${userLocation.lat},${userLocation.lon}&destination=${hospital.lat},${hospital.lon}`;
    window.open(url, '_blank');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 text-white shadow-xl"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Hospital Locator</h1>
            <p className="text-blue-100">Find nearby hospitals and medical facilities</p>
          </div>
          <Building2 className="w-16 h-16 opacity-50" />
        </div>
      </motion.div>

      {/* Controls */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-xl shadow-lg p-6"
      >
        <div className="flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Radius
            </label>
            <select
              value={searchRadius}
              onChange={(e) => setSearchRadius(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={2000}>2 km</option>
              <option value={5000}>5 km</option>
              <option value={10000}>10 km</option>
              <option value={20000}>20 km</option>
            </select>
          </div>

          <button
            onClick={getUserLocation}
            disabled={loading}
            className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <Navigation className="w-5 h-5" />
                Find Hospitals
              </>
            )}
          </button>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg"
          >
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-red-800 font-medium">Error</p>
                <p className="text-red-700 text-sm">{error}</p>
                
                {/* Show HTTPS help if it's a secure context issue */}
                {(error.includes('HTTPS') || error.includes('localhost')) && (
                  <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-blue-800 font-medium text-sm mb-2">💡 Quick Fix Options:</p>
                    
                    {/* Option 1: Localhost Link */}
                    <div className="mb-3 p-2 bg-white rounded border border-blue-300">
                      <p className="text-blue-800 text-xs font-semibold mb-1">✅ Option 1: Use Localhost (Easiest)</p>
                      <a
                        href={localhostUrlForCurrentPath()}
                        className="text-blue-600 hover:text-blue-800 underline text-xs font-mono break-all"
                      >
                        {localhostUrlForCurrentPath()}
                      </a>
                      <p className="text-gray-600 text-xs mt-1">👆 Click to open in localhost</p>
                    </div>
                    
                    {/* Option 2: Ngrok HTTPS */}
                    <div className="p-2 bg-white rounded border border-blue-300">
                      <p className="text-blue-800 text-xs font-semibold mb-1">✅ Option 2: Use Ngrok HTTPS</p>
                      <code className="text-xs text-gray-700 block bg-gray-100 p-2 rounded">
                        ngrok http {ngrokPortHint()}
                      </code>
                      <p className="text-gray-600 text-xs mt-1">Then use the <strong>https://</strong> URL provided</p>
                    </div>
                    
                    <p className="text-blue-600 text-xs mt-2">
                      Current URL: <code className="bg-blue-100 px-1 rounded">{window.location.href}</code>
                    </p>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* Map Container */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white rounded-xl shadow-lg overflow-hidden"
      >
        <div
          ref={mapRef}
          style={{ height: '500px', width: '100%' }}
          className="relative"
        >
          {!userLocation && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-50 z-10">
              <div className="text-center">
                <MapPin className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 font-medium">Click "Find Hospitals" to get started</p>
                <p className="text-gray-500 text-sm mt-2">
                  We'll use your location to find nearby medical facilities
                </p>
              </div>
            </div>
          )}
        </div>
      </motion.div>

      {/* Hospital List */}
      {hospitals.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Found {hospitals.length} Hospital{hospitals.length !== 1 ? 's' : ''}
          </h2>

          <div className="space-y-3">
            {hospitals.map((hospital, index) => (
              <motion.div
                key={hospital.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.05 * index }}
                onClick={() => setSelectedHospital(hospital)}
                className={`p-4 border rounded-lg cursor-pointer transition-all duration-300 hover:shadow-md ${
                  selectedHospital?.id === hospital.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold ${
                        hospital.emergency ? 'bg-red-500' : 'bg-green-500'
                      }`}>
                        {index + 1}
                      </span>
                      <h3 className="font-semibold text-gray-900">
                        {hospital.name || 'Hospital'}
                      </h3>
                      {hospital.emergency && (
                        <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-medium rounded">
                          Emergency
                        </span>
                      )}
                    </div>

                    <div className="space-y-1 text-sm text-gray-600 ml-8">
                      {hospital.distance && (
                        <div className="flex items-center gap-2">
                          <MapPin className="w-4 h-4" />
                          <span>{(hospital.distance / 1000).toFixed(2)} km away</span>
                        </div>
                      )}
                      {hospital.address && (
                        <div className="flex items-center gap-2">
                          <MapPin className="w-4 h-4" />
                          <span>{hospital.address}</span>
                        </div>
                      )}
                      {hospital.phone && (
                        <div className="flex items-center gap-2">
                          <Phone className="w-4 h-4" />
                          <a
                            href={`tel:${hospital.phone}`}
                            className="text-blue-600 hover:underline"
                            onClick={(e) => e.stopPropagation()}
                          >
                            {hospital.phone}
                          </a>
                        </div>
                      )}
                      {hospital.opening_hours && (
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4" />
                          <span>{hospital.opening_hours}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      openDirections(hospital);
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 text-sm"
                  >
                    <Navigation className="w-4 h-4" />
                    Directions
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default HospitalLocator;
