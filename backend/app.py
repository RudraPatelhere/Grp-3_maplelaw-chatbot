from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import pyttsx3
import os
import time
from geopy.geocoders import Nominatim  # For geolocation functionality

# Ensure correct path settings
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# Configure Gemini AI API
genai.configure(api_key="AIzaSyDj91yfPhGELCd4-hh6BK6c8g_xfK52aZs")  # Replace with your valid API key

# Initialize Text-to-Speech Engine
tts_engine = pyttsx3.init()
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Function to Convert Text to Speech and return a web-accessible URL
def text_to_speech(text):
    timestamp = int(time.time())  # Generate a unique timestamp for each response
    audio_filename = f"response_{timestamp}.mp3"
    audio_file_path = os.path.join(AUDIO_DIR, audio_filename)

    # Save the response as an MP3 file
    tts_engine.save_to_file(text, audio_file_path)
    tts_engine.runAndWait()

    # Clean up old files
    cleanup_old_audio_files()

    # Return the URL to access this file from frontend
    return f"/static/audio/{audio_filename}"

# Function to remove old audio files (older than 5 minutes)
def cleanup_old_audio_files():
    now = time.time()
    for filename in os.listdir(AUDIO_DIR):
        file_path = os.path.join(AUDIO_DIR, filename)
        if filename.startswith("response_") and filename.endswith(".mp3"):
            file_creation_time = os.path.getctime(file_path)
            if now - file_creation_time > 300:  # Delete files older than 5 minutes
                os.remove(file_path)

# Geolocation Function to Convert Coordinates to City Name
def get_location_from_coordinates(latitude, longitude):
    geolocator = Nominatim(user_agent="legal-chatbot")
    try:
        location = geolocator.reverse((latitude, longitude), language='en', exactly_one=True)
        if location and location.raw:
            address = location.raw.get('address', {})
            city = address.get('city', address.get('town', address.get('village', '')))
            state = address.get('state', '')
            country = address.get('country', '')

            # Return formatted location (City, State, Country)
            return f"{city}, {state}, {country}".strip(", ")
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

    # Retrieve the city/state instead of a full address
    location_text = get_location_from_coordinates(latitude, longitude) if latitude and longitude else "Location not available"
    
    try:
        prompt = f"""
        You are a legal expert providing professional legal advice.

        **User Question:** {user_message}
        **Location (Approximate):** {location_text}

        **Your Response Should Be Well-Structured:**
        - **Introduction:** Briefly explain the legal issue.
        - **Key Points:** List relevant laws, sections, or acts.
        - **Example Cases (if applicable):** Reference real-world applications.
        - **Conclusion:** Provide practical advice on next steps.
        - **Sources:** Mention relevant legal codes or databases.

        Please keep the response concise, informative, and free of unnecessary jargon.
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        bot_response = response.text if hasattr(response, "text") else "Sorry, I couldn't process that."

        # Generate speech from response
        audio_url = text_to_speech(bot_response)

        return jsonify({
            "response": bot_response,
            "audio_path": audio_url,  # Send the proper URL for playback
            "location": location_text
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
