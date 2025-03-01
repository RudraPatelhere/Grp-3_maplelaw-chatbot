// Function to convert **bold** syntax to <strong> tags
function parseBoldSyntax(text) {
    return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

// Function to append a chat message
function appendMessage(sender, text) {
    const chatWindow = document.getElementById('chatWindow');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message', sender);

    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    bubble.innerHTML = parseBoldSyntax(text);

    messageDiv.appendChild(bubble);
    chatWindow.appendChild(messageDiv);

    // Auto-scroll to the bottom
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

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

function sendMessage(latitude, longitude, text = null) {
    const userMessage = text || document.getElementById('message').value.trim();
    if (!userMessage) return;

    // Append user's message (right-aligned)
    appendMessage('user', `**You:** ${userMessage}`);

    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: userMessage,
            latitude: latitude,
            longitude: longitude,
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                appendMessage('bot', `**Error:** ${data.error}`);
            } else {
                // Append bot's main response
                appendMessage('bot', `**Bot:**<br>${data.response}`);

                // Append location info if available
                if (data.location) {
                    appendMessage('bot', `**Location:** ${data.location}`);
                }

                // Play audio if available
                if (data.audio_path) {
                    const audioPlayer = document.getElementById('audioPlayer');
                    const audioPlayerContainer = document.getElementById('audioPlayerContainer');
                    audioPlayer.src = data.audio_path;
                    audioPlayerContainer.style.display = 'block';
                    audioPlayer.play();
                }
            }
        })
        .catch(error => {
            console.error("Error:", error);
            appendMessage('bot', `**Error:** Something went wrong.`);
        });

    // Clear the input field
    document.getElementById('message').value = "";
}

function startVoiceRecognition() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.start();

    recognition.onresult = function (event) {
        const voiceText = event.results[0][0].transcript;
        document.getElementById('message').value = voiceText;
        getLocationAndSendMessage(voiceText);
    };
}
