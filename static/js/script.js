// Function to handle location retrieval and sending message
function getLocationAndSendMessage(text = null) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                let latitude = position.coords.latitude;
                let longitude = position.coords.longitude;
                sendMessage(latitude, longitude, text);
            },
            function (error) {
                console.log("Error getting location: ", error);
                sendMessage(null, null, text);
            }
        );
    } else {
        console.log("Geolocation is not supported.");
        sendMessage(null, null, text);
    }
}

function sendMessage(latitude, longitude, text = null) {
    let userMessage = text || document.getElementById("message").value;

    // Display the user message in chat
    appendMessage("user", userMessage);

    // Fetch the response from the Flask server
    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            message: userMessage,
            latitude: latitude,
            longitude: longitude,
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            // Display the bot's response in the chat box
            appendMessage("bot", formatBotResponse(data.response));

            document.getElementById("location").innerHTML = `
        <strong>📍 Location:</strong> ${data.location || "N/A"}
      `;

            // Check if audio path is available and update the audio player
            if (data.audio_path) {
                let audioPlayer = document.getElementById("audioPlayer");
                let audioSource = document.getElementById("audioSource");

                // Update the audio source with the new audio path
                audioSource.src = data.audio_path;

                // Reload the audio player to load the new audio
                audioPlayer.load();

                // Play the new audio immediately
                audioPlayer.play();

                // Show the audio player container
                document.getElementById("audioPlayerContainer").style.display = "block";
            }
        })
        .catch((error) => console.error("Error:", error));
}

// Function to append message to chat box
function appendMessage(sender, message) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("chat-message");

    const messageText = document.createElement("div");
    messageText.classList.add(sender + "-message");
    messageText.innerHTML = message;

    messageDiv.appendChild(messageText);
    document.getElementById("chat-box").appendChild(messageDiv);

    // Scroll to the bottom of chat box
    document.getElementById("chat-box").scrollTop =
        document.getElementById("chat-box").scrollHeight;
}

// Function to format the bot response, converting **text** to bold
function formatBotResponse(response) {
    // Define the section titles in order
    const sectionTitles = [
        "Introduction",
        "Key Points",
        "Example Cases",
        "Conclusion",
        "Sources",
    ];

    // Regular expression to match section headings like "**Introduction:**"
    const headingRegex = /\*\*(.*?):\*\*/g;

    let formattedResponse = "";
    let previousEnd = 0; // Keeps track of the end of the last match
    let match;
    while ((match = headingRegex.exec(response)) !== null) {
        const sectionTitle = match[1].trim();
        const startPos = match.index + match[0].length;
        const endPos = headingRegex.lastIndex;

        if (previousEnd < match.index) {
            const content = response.slice(previousEnd, match.index).trim();
            if (content) {
                const sectionIndex = sectionTitles.indexOf(sectionTitle);
                if (sectionIndex !== -1) {
                    formattedResponse += `
            <div class="response-section">
              <div class="section-title">${sectionTitles[sectionIndex]}</div>
              <div class="section-content">${content}</div>
            </div>
          `;
                } else {
                    formattedResponse += `
            <div class="response-section">
              <div class="section-content">${content}</div>
            </div>
          `;
                }
            }
        }
        previousEnd = endPos;
    }

    // Add any remaining content after the last section
    if (previousEnd < response.length) {
        const content = response.slice(previousEnd).trim();
        if (content) {
            formattedResponse += `
        <div class="response-section">
          <div class="section-content">${content}</div>
        </div>
      `;
        }
    }

    // Replace any **text** with bold text using <strong> tags
    formattedResponse = formattedResponse.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    return formattedResponse;
}

// Function to start voice recognition
function startVoiceRecognition() {
    let recognition = new (window.SpeechRecognition ||
        window.webkitSpeechRecognition)();
    recognition.lang = "en-US";
    recognition.start();

    recognition.onresult = function (event) {
        let voiceText = event.results[0][0].transcript;
        document.getElementById("message").value = voiceText;
        getLocationAndSendMessage(voiceText);
    };

    recognition.onerror = function (event) {
        console.log("Speech recognition error: ", event.error);
    };
}
