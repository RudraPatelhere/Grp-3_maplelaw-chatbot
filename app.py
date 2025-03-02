from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import pyttsx3
import os
import time
from geopy.geocoders import Nominatim  # For geolocation functionality
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)

# Configure Gemini AI API
genai.configure(api_key="AIzaSyDj91yfPhGELCd4-hh6BK6c8g_xfK52aZs")

# Text-to-Speech Engine
tts_engine = pyttsx3.init()
AUDIO_DIR = "static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)
# Endpoint to handle Google Scholar search requests

@app.route("/scholar_search", methods=["POST"])
def scholar_search():
    data = request.json
    query = data.get("query", "")
    
    if not query:
        return jsonify({"error": "No query provided"}), 400

    results = search_google_scholar(query)
    scholar_link = f"https://scholar.google.com/scholar?q={urllib.parse.quote(query)}"

    return jsonify({"results": results, "scholar_link": scholar_link})

# Function to Convert Text to Speech
def text_to_speech(text):
    # Create a unique filename using timestamp to ensure a new file every time
    timestamp = str(int(time.time()))  # Get current timestamp to avoid name clashes
    audio_file = os.path.join(AUDIO_DIR, f"response_{timestamp}.mp3")
    tts_engine.save_to_file(text, audio_file)
    tts_engine.runAndWait()

    # Delete the old audio files (if any) to keep only the latest one
    files = os.listdir(AUDIO_DIR)
    if len(files) > 1:  # If there are more than one file
        files.sort(key=lambda x: os.path.getmtime(os.path.join(AUDIO_DIR, x)))  # Sort by modification time
        old_files = files[:-1]  # Keep only the most recent file
        for old_file in old_files:
            os.remove(os.path.join(AUDIO_DIR, old_file))  # Delete old files

    return audio_file

# Geolocation Function to Convert Coordinates to Location
def get_location_from_coordinates(latitude, longitude):
    geolocator = Nominatim(user_agent="legal-chatbot")
    location = None
    try:
        location = geolocator.reverse((latitude, longitude), language='en', exactly_one=True)
        return location.address if location else "Location not found"
    except Exception as e:
        print(f"Error in geocoding: {e}")
        return "Unable to retrieve location"

# Google Scholar Search Function
def search_google_scholar(query):
    query_encoded = urllib.parse.quote(query)
    url = f"https://scholar.google.com/scholar?q={query_encoded}&hl=en"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for result in soup.find_all('h3', {'class': 'gs_rt'}):
            title = result.get_text()
            link = result.find('a')['href']
            results.append({'title': title, 'link': link})
        
        return results
    else:
        return []

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
        
        *User Question:* {user_message}  
        *Location (Approximate):* {location_text}  # The location is for reference purposes
        
        *Your Response Should Be Well-Structured:*
        - *Introduction:* Briefly explain the legal issue.
        - *Key Points:* List relevant laws, sections, or acts.
        - *Example Cases (if applicable):* Reference real-world applications.
        - *Conclusion:* Provide practical advice on next steps.
        - *Sources:* Mention relevant legal codes or databases.

        Please keep the response concise, informative, and free of unnecessary jargon.
        """
        
        # Make the request to the Gemini AI
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        # The response text will include the legal advice and location information
        bot_response = response.text if hasattr(response, "text") else "Sorry, I couldn't process that."

        # Convert bot response to speech
        audio_path = text_to_speech(bot_response)

        # Search Google Scholar for relevant articles
        scholar_results = search_google_scholar(user_message)

        return jsonify({
            "response": bot_response,
            "audio_path": audio_path,
            "location": location_text,
            "scholar_results": scholar_results
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5003)


