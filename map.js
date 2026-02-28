// single map initialization (only when container exists)
let map = null;
const mapContainer = document.getElementById('map');
if (mapContainer) {
    // initialize map with a gentle default view; we'll move it after locating user
    map = L.map(mapContainer).setView([10.7905, 78.7047], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
}

// keep hospital markers and polyline in a layer group for easy clearing
let hospitalLayer = null;
let routePolyline = null;

function ensureLayers() {
    if (!map) return;
    if (!hospitalLayer) {
        hospitalLayer = L.layerGroup().addTo(map);
    }
}

// helper: draw hospitals and show nearest with polyline
function handleHospitalsForLocation(lat, lon) {
    const apiUrl = `http://182.18.2.8:8000/api/hospitals/nearby?lat=${lat}&lon=${lon}`;
    console.log('Fetching hospitals for', lat, lon, apiUrl);

    fetch(apiUrl)
        .then(res => res.json())
        .then(hospitals => {
            try {
                console.log('Hospitals fetched:', hospitals && hospitals.length);
                if (!Array.isArray(hospitals) || hospitals.length === 0) {
                    alert('No hospitals found nearby.');
                    return;
                }

                ensureLayers();
                // clear previous markers and route
                hospitalLayer.clearLayers();
                if (routePolyline) {
                    try { map.removeLayer(routePolyline); } catch (e) {}
                    routePolyline = null;
                }

                // Add user marker
                const userMarker = L.marker([lat, lon]);
                userMarker.bindPopup('📍 You (Tiruchirappalli)').openPopup();
                hospitalLayer.addLayer(userMarker);

                // find nearest hospital by distance property (or compute)
                let nearest = hospitals[0];
                for (let h of hospitals) {
                    if ((h.distance || Number.MAX_VALUE) < (nearest.distance || Number.MAX_VALUE)) {
                        nearest = h;
                    }
                    // add hospital markers to the hospitalLayer
                    const hm = L.marker([h.lat, h.lon]).bindPopup(`${h.name}<br>Distance: ${Number(h.distance).toFixed(2)} km`);
                    hospitalLayer.addLayer(hm);
                }

                // draw polyline to nearest hospital
                try {
                    routePolyline = L.polyline([[lat, lon], [nearest.lat, nearest.lon]], { color: 'blue', weight: 4, opacity: 0.7 }).addTo(map);
                    const bounds = L.latLngBounds([[lat, lon], [nearest.lat, nearest.lon]]);
                    map.fitBounds(bounds.pad(0.3));

                        // open nearest hospital popup from the layer (try to find it)
                        const nh = L.marker([nearest.lat, nearest.lon]);
                        nh.bindPopup(`📍 Nearest: ${nearest.name}<br>Distance: ${Number(nearest.distance).toFixed(2)} km<br><small style="display:block;margin-top:6px">Click marker to open hospital profile</small>`).openPopup();
                        // on marker click, save nearest hospital to localStorage and navigate to hospital profile
                        nh.on('click', () => {
                            try{
                                const payload = {
                                    name: nearest.name || '',
                                    lat: nearest.lat,
                                    lon: nearest.lon,
                                    distance: nearest.distance || ''
                                };
                                localStorage.setItem('nearestHospital', JSON.stringify(payload));
                            }catch(e){ console.error('Failed to save nearestHospital', e); }
                            window.location.href = 'hospital-profile.html';
                        });
                        hospitalLayer.addLayer(nh);

                        // Ask backend AI for recommendation and update dashboard UI if available
                        if (typeof getHospitalRecommendation === 'function') {
                            try {
                                getHospitalRecommendation(lat, lon).then(aiRes => {
                                    try {
                                        const aiEl = document.getElementById('aiSuggestion');
                                        const aiStatus = document.getElementById('aiStatus');
                                        if (!aiEl) return;
                                        if (aiRes && aiRes.success && aiRes.data) {
                                            aiEl.textContent = aiRes.data.recommendation || aiRes.data.message || 'AI active — no suggestion';
                                            if (aiStatus) aiStatus.textContent = 'AI: Active';
                                        } else if (aiRes && aiRes.success && aiRes.data && aiRes.data.available === false) {
                                            aiEl.textContent = 'AI service not available';
                                            if (aiStatus) aiStatus.textContent = 'AI: Unavailable';
                                        } else {
                                            aiEl.textContent = 'AI unreachable';
                                            if (aiStatus) aiStatus.textContent = 'AI: Offline';
                                        }
                                    } catch (e) { console.warn('Failed to update AI UI', e); }
                                }).catch(err => {
                                    console.warn('AI recommend error', err);
                                    const aiEl = document.getElementById('aiSuggestion');
                                    const aiStatus = document.getElementById('aiStatus');
                                    if (aiEl) aiEl.textContent = 'AI unreachable';
                                    if (aiStatus) aiStatus.textContent = 'AI: Offline';
                                });
                            } catch(e) { console.warn('AI call failed', e); }
                        }
                } catch (e) {
                    console.error('Failed to draw polyline:', e);
                }
            } catch (err) {
                console.error('Error handling hospitals data:', err);
                alert('Failed to process hospitals data. See console.');
            }
        })
        .catch(err => {
            console.error('Error fetching hospitals:', err);
            alert('Failed to fetch hospitals. Check backend.');
        });
}

function onLocationSuccess(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    console.log('User location:', lat, lon);
    handleHospitalsForLocation(lat, lon);
}

function onLocationError(err) {
    console.warn('Location error, falling back to Tiruchirappalli coords:', err && err.message ? err.message : err);
    // user-provided Tiruchirappalli coordinates fallback
    const fallbackLat = 10.7905;
    const fallbackLon = 78.7047;
    handleHospitalsForLocation(fallbackLat, fallbackLon);
}

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(onLocationSuccess, onLocationError, { enableHighAccuracy: true, timeout: 8000 });
} else {
    // no geolocation support - use fallback
    onLocationError('Geolocation not supported');
}
