import requests
import math

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def haversine(lat1, lon1, lat2, lon2):
    """Return distance in kilometers between two (lat,lon) points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def find_nearby_hospitals(lat, lon, radius=5000):
    """Return hospitals within *radius* meters of the given coordinates.

    Returns a list of dicts with keys: name, lat, lon, distance (km).
    """
    query = f"""
    [out:json];
    node["amenity"="hospital"](around:{radius},{lat},{lon});
    out;
    """

    response = requests.post(OVERPASS_URL, data={"data": query})
    response.raise_for_status()
    data = response.json()

    hospitals = []
    for el in data.get("elements", []):
        hospitals.append({
            "name": el.get("tags", {}).get("name", "Unknown"),
            "lat": el.get("lat"),
            "lon": el.get("lon"),
            "distance": haversine(lat, lon, el.get("lat"), el.get("lon"))
        })

    hospitals.sort(key=lambda x: x["distance"])
    return hospitals


# Groq / AI recommendation helper (optional)
try:
    from groq import Groq
    _GROQ_AVAILABLE = True
except Exception:
    Groq = None
    _GROQ_AVAILABLE = False


def get_ai_recommendation(hospitals, symptoms, api_key=None, model="llama3-8b-8192"):
    """Return a short AI recommendation string based on nearby hospitals and symptoms.

    This function requires the `groq` client to be installed and a valid `api_key`.
    If the client is not available it raises RuntimeError.
    """
    if not _GROQ_AVAILABLE:
        raise RuntimeError("Groq client not available. Install the 'groq' package to enable AI recommendations.")

    # Build short hospital summary
    hospital_text = ""
    for h in hospitals[:3]:
        hospital_text += f"{h.get('name','Unknown')} - {h.get('distance',0):.2f} km\n"

    prompt = f"""
    Patient symptoms: {symptoms}

    Nearby hospitals:
    {hospital_text}

    Recommend the most suitable hospital and explain briefly.
    """

    client = Groq(api_key=api_key or "YOUR_API_KEY")

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model,
    )

    # Defensive access into response structure
    try:
        return response.choices[0].message.content
    except Exception:
        return str(response)


def recommend_hospital(lat, lon, symptoms="", api_key=None, radius=5000):
    """Convenience wrapper that performs a nearby-hospitals lookup then runs the AI.

    Raises RuntimeError if Groq is unavailable.
    """
    hospitals = find_nearby_hospitals(lat, lon, radius=radius)
    return get_ai_recommendation(hospitals, symptoms, api_key=api_key)
