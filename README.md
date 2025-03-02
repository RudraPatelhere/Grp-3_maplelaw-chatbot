  # MAPLELAW Chatbot

MAPLELAW is a legal chatbot designed to provide legal information and guidance based on user queries and location. The chatbot utilizes **Google Gemini AI** for legal responses and integrates **text-to-speech** functionality to allow users to listen to the responses.

## Features
? **Interactive Chat Interface** – Users can type or speak their legal questions.  
? **Location-Based Responses** – Uses geolocation to provide context-aware legal information.  
? **Text-to-Speech Support** – Converts responses into audio for a better experience.  
? **Modern UI** – Designed with Bootstrap for a clean and responsive interface.  
? **Multi-Platform Support** – Works on desktop and mobile devices.  

---

## Installation Guide

### **1. Clone the Repository**
```bash
 git clone https://github.com/yourusername/maplelaw-chatbot.git
 cd maplelaw-chatbot
```

### **2. Set Up Virtual Environment (Recommended)**
```bash
python -m venv venv  # Create virtual environment
source venv/bin/activate  # Activate on Mac/Linux
venv\Scripts\activate  # Activate on Windows
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Set Up API Key**
Update `app.py` with your Google Gemini API key:
```python
genai.configure(api_key="YOUR_GEMINI_API_KEY")
```

---

## Running the Chatbot

### **Run the Flask Server**
```bash
python backend/app.py
```
- The chatbot will be accessible at **http://127.0.0.1:5000**.
- If you want to run it on a mobile device, find your local IP and start Flask with:
```bash
python backend/app.py --host=0.0.0.0 --port=5000
```

---

## Usage Instructions

1. Open the chatbot UI in your browser.  
2. Enter a legal question or use voice input to ask.  
3. The bot will respond with structured legal information.  
4. Click the **?? Listen** button to hear the response.  
5. If enabled, the chatbot will provide location-based legal guidance.  

---

## Technologies Used
- **Flask** – Backend framework for API handling.
- **Google Gemini AI** – AI-based legal response generation.
- **Geopy** – Converts user coordinates into location-based responses.
- **pyttsx3** – Text-to-speech functionality.
- **Bootstrap 4** – Responsive UI framework.
- **JavaScript & jQuery** – Frontend scripting.

---

## Future Enhancements
1 Multi-language support.  
2 Improved AI-generated responses with better legal references.  
3 Enhanced voice interaction with natural voice synthesis.  
4 Deployment using Docker or cloud-based hosting.

---

## Contributors
  

---

## License
This project is licensed under the **MIT License**. Feel free to use and contribute!


