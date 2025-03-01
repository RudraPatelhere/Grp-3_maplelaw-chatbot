from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import pyttsx3
import os
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim  # For geolocation functionality

app = Flask(__name__)

# Load API Key for Gemini AI (Make sure to set this in your environment variables)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# Text-to-Speech Engine
tts_engine = pyttsx3.init()
AUDIO_DIR = "static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Google Scholar URL for legal case search
GOOGLE_SCHOLAR_URL = "https://scholar.google.com/scholar"

# Function to refine and improve search queries for Google Scholar
def refine_query(query):
    query = query.lower().strip()
    
    # Apply filters to ensure the query is formatted correctly
    if "child abuse" in query:
        query = f'intitle:"Child Abuse" "{query}" site:canlii.org'
    elif "canada" in query:
        query = f'"{query}" site:canlii.org'
    elif "divorce" in query:
        query = f'intitle:"Divorce Case" "{query}" site:canlii.org'
    else:
        query = f'"{query}" site:canlii.org'
    
    return query

# Function to search Google Scholar for relevant case law
def search_google_scholar(query):
    try:
        refined_query = refine_query(query)
        search_url = f"{GOOGLE_SCHOLAR_URL}?q={refined_query}&as_ylo=2021"  # Filter for cases from 2021 onwards

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            for result in soup.select(".gs_ri"):  # Google Scholar result block
                title = result.select_one(".gs_rt").text if result.select_one(".gs_rt") else "Unknown Case"
                link = result.select_one(".gs_rt a")["href"] if result.select_one(".gs_rt a") else "#"
                snippet = result.select_one(".gs_rs").text if result.select_one(".gs_rs") else "No summary available."

                # Prioritize cases where keywords match the title
                if any(keyword.lower() in title.lower() for keyword in query.split()):
                    results.append(f"<strong>{title}</strong>: <a href='{link}' target='_blank'>{link}</a><br>{snippet}")

            return "<br><br>".join(results) if results else "No relevant cases found."
        else:
            return "Error retrieving case law data."
    except Exception as e:
        return f"Error: {str(e)}"

# Function to Convert Text to Speech
def text_to_speech(text):
    audio_file = os.path.join(AUDIO_DIR, "response.mp3")
    tts_engine.save_to_file(text, audio_file)
    tts_engine.runAndWait()
    return audio_file

# Geolocation Function
def get_location_from_coordinates(latitude, longitude):
    geolocator = Nominatim(user_agent="legal-chatbot")
    try:
        location = geolocator.reverse((latitude, longitude), language='en', exactly_one=True)
        return location.address if location else "Location not found"
    except Exception as e:
        return "Unable to retrieve location"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    location_text = get_location_from_coordinates(latitude, longitude) if latitude and longitude else ""

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

        audio_path = text_to_speech(bot_response)

        return jsonify({"response": bot_response, "audio_path": audio_path, "location": location_text})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/google_scholar", methods=["POST"])
def google_scholar():
    data = request.json
    user_message = data.get("message", "")

    case_results = search_google_scholar(user_message)

    return jsonify({"response": f"Here are the **most relevant** legal cases:<br><br>{case_results}"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5003)
