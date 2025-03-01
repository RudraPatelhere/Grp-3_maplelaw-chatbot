// Function to convert **bold** syntax to <strong> tags
function parseBoldSyntax(text) {
    return text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
}

// Function to append a chat message
function appendMessage(sender, text) {
    const chatWindow = document.getElementById("chatWindow");
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("chat-message", sender);

    const bubble = document.createElement("div");
    bubble.classList.add("bubble");
    bubble.innerHTML = parseBoldSyntax(text);

    messageDiv.appendChild(bubble);
    chatWindow.appendChild(messageDiv);

    // Auto-scroll to the bottom
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Function to get location and send message
function getLocationAndSendMessage(text = null) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;
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

// Function to send message and handle response
function sendMessage(latitude, longitude, text = null) {
    const userMessage = text || document.getElementById("message").value.trim();
    if (!userMessage) return;

    // Append user's message (right-aligned)
    appendMessage("user", `**You:** ${userMessage}`);

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            message: userMessage,
            latitude: latitude,
            longitude: longitude,
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                appendMessage("bot", `**Error:** ${data.error}`);
            } else {
                // Append bot's main response
                appendMessage("bot", `**Bot:**<br>${data.response}`);

                // Append location info if available
                if (data.location) {
                    appendMessage("bot", `**Location:** ${data.location}`);
                }

                // Play the latest response audio
                if (data.audio_path) {
                    updateAudioPlayer(data.audio_path);
                }
            }
        })
        .catch(error => {
            console.error("Error:", error);
            appendMessage("bot", `**Error:** Something went wrong.`);
        });

    // Clear the input field
    document.getElementById("message").value = "";
}

// Function to handle voice recognition and send message
function startVoiceRecognition() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "en-US";
    recognition.start();

    recognition.onresult = function (event) {
        const voiceText = event.results[0][0].transcript;
        document.getElementById("message").value = voiceText;
        getLocationAndSendMessage(voiceText);
    };
}

// Function to update and play the latest bot response audio
function updateAudioPlayer(audioPath) {
    let audioPlayer = document.getElementById("audioPlayer");
    let audioPlayerContainer = document.getElementById("audioPlayerContainer");
    let listenAgainButton = document.getElementById("listenAgainBtn");

    // Update the source and show the player
    audioPlayer.src = audioPath;
    audioPlayerContainer.style.display = "block";

    // Auto-play the latest audio
    audioPlayer.play();

    // Show "Listen Again" button
    listenAgainButton.style.display = "block";
}

// Function to replay the latest response
function playBotResponse() {
    let audioPlayer = document.getElementById("audioPlayer");
    if (audioPlayer.src) {
        audioPlayer.play();
    } else {
        console.error("No audio available.");
    }
}
