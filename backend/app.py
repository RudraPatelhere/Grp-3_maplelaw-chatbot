from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import pyttsx3
import os
from geopy.geocoders import Nominatim  # For geolocation functionality

# Ensure correct path settings if necessary; here's an example using absolute paths:
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# Configure Gemini AI API
genai.configure(api_key="AIzaSyDj91yfPhGELCd4-hh6BK6c8g_xfK52aZs")

# Text-to-Speech Engine
tts_engine = pyttsx3.init()
# Use audio folder inside your static directory
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

def text_to_speech(text):
    audio_file = os.path.join(AUDIO_DIR, "response.mp3")
    tts_engine.save_to_file(text, audio_file)
    tts_engine.runAndWait()
    return audio_file

# Geolocation Function to Convert Coordinates to Location
def get_location_from_coordinates(latitude, longitude):
    geolocator = Nominatim(user_agent="legal-chatbot")
    try:
        location = geolocator.reverse((latitude, longitude), language='en', exactly_one=True)
        # Extract city, state, and country if available
        if location and location.address:
            return location.address
        else:
            return "Location not found"
    except Exception as e:
        print(f"Error in geocoding: {e}")
        return "Unable to retrieve location"

# Serve UI Page
@app.route("/")
def index():
    return render_template("index.html")

# Chat Endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    location_text = ""
    if latitude and longitude:
        location_text = get_location_from_coordinates(latitude, longitude)
    
    try:
        prompt = f"""
You are a legal expert providing professional legal advice.

User Question: {user_message}
Location (Approximate): {location_text}

Your Response Should Be Well-Structured:
- Introduction: Briefly explain the legal issue.
- Key Points: List relevant laws, sections, or acts.
- Example Cases (if applicable): Reference real-world applications.
- Conclusion: Provide practical advice on next steps.
- Sources: Mention relevant legal codes or databases.

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
    app.run(debug=True, host='0.0.0.0', port=5000)
