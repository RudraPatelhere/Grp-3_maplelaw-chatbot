from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import pyttsx3
import os
import requests

# Compute absolute paths for templates and static files
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# Configure Gemini AI API (replace with your actual key)
genai.configure(api_key="AIzaSyDj91yfPhGELCd4-hh6BK6c8g_xfK52aZs")

# Text-to-Speech Engine
tts_engine = pyttsx3.init()
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

def text_to_speech(text):
    audio_file = os.path.join(AUDIO_DIR, "response.mp3")
    tts_engine.save_to_file(text, audio_file)
    tts_engine.runAndWait()
    return audio_file

def reverse_geocode(lat, lon):
    """
    Use OpenStreetMap's Nominatim API to convert lat/lon into a human-friendly location.
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "json",
        "lat": lat,
        "lon": lon,
        "zoom": 10,  # City level
        "addressdetails": 1,
    }
    headers = {"User-Agent": "MAPLELAW-Hackathon-App"}
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            # Try to extract city/town/village, then state and country
            city = address.get("city") or address.get("town") or address.get("village") or ""
            state = address.get("state", "")
            country = address.get("country", "")
            location_string = ", ".join(filter(None, [city, state, country]))
            return location_string if location_string else "Ontario"
        else:
            return "Ontario"
    except Exception as e:
        print("Reverse geocoding error:", e)
        return "Ontario"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    # Use reverse geocoding to get a precise location name
    if latitude and longitude:
        location_text = reverse_geocode(latitude, longitude)
    else:
        location_text = ""

    try:
        prompt = f"""
        You are a legal expert providing professional legal advice.

        *User Question:* {user_message}
        *Location:* {location_text}

        *Your Response Should Be Well-Structured:*
        - *Introduction:* Briefly explain the legal issue.
        - *Key Points:* List relevant laws, sections, or acts.
        - *Example Cases (if applicable):* Reference real-world applications.
        - *Conclusion:* Provide practical advice on next steps.
        - *Sources:* Mention relevant legal codes or databases.

        Please keep the response concise, informative, and free of unnecessary jargon.
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        bot_response = response.text if hasattr(response, "text") else "Sorry, I couldn't process that."

        audio_path = text_to_speech(bot_response)

        return jsonify({
            "response": bot_response,
            "audio_path": audio_path,
            "location": location_text
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
