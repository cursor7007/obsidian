import os
import logging
from flask import Flask, request, jsonify
from openai import OpenAI

# --- HIDE BACKGROUND LOGS ---
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# --- CONFIGURATION ---
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY"),
)

# --- MODELS ---
MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

# --- MATRIX UI ---
# PASTE YOUR FULL HTML CODE INSIDE THESE TRIPLE QUOTES

"""html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OBSIDIAN AI Mentor</title>
    <style>
        body {
            background-color: #000000;
            color: #00FF41; /* Matrix Green */
            font-family: 'Courier New', Courier, monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
        }
        h1 {
            text-shadow: 0 0 10px #00FF41;
        }
        #chatbox {
            flex-grow: 1;
            width: 100%;
            max-width: 600px;
            border: 2px solid #00FF41;
            padding: 15px;
            overflow-y: auto;
            margin-bottom: 20px;
            background-color: #0a0a0a;
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
        }
        .user-msg { color: #ffffff; margin-bottom: 10px; text-align: right;}
        .bot-msg { color: #00FF41; margin-bottom: 20px; text-align: left; border-left: 2px solid #00FF41; padding-left: 10px;}
        #input-area {
            display: flex;
            width: 100%;
            max-width: 600px;
        }
        input[type="text"] {
            flex-grow: 1;
            background-color: #000;
            color: #00FF41;
            border: 1px solid #00FF41;
            padding: 10px;
            font-family: 'Courier New', Courier, monospace;
            outline: none;
        }
        button {
            background-color: #00FF41;
            color: #000;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-weight: bold;
            font-family: 'Courier New', Courier, monospace;
            transition: 0.3s;
        }
        button:hover {
            background-color: #ffffff;
            color: #000;
        }
    </style>
</head>
<body>

    <h1>OBSIDIAN TERMINAL</h1>
    <div id="chatbox">
        <div class="bot-msg">System Initialized. I am Obsidian, your Elite Cyber Security AI Mentor. How can I assist your training today?</div>
    </div>

    <div id="input-area">
        <input type="text" id="userInput" placeholder="Enter command..." onkeypress="handleKeyPress(event)">
        <button onclick="sendMessage()">EXECUTE</button>
    </div>

    <script>
        function handleKeyPress(e) {
            if (e.keyCode === 13) {
                sendMessage();
            }
        }

        async function sendMessage() {
            const inputField = document.getElementById("userInput");
            const message = inputField.value;
            if (!message) return;

            const chatbox = document.getElementById("chatbox");
            
            // Add user message
            chatbox.innerHTML += `<div class="user-msg">User: ${message}</div>`;
            inputField.value = "";
            chatbox.scrollTop = chatbox.scrollHeight;

            // Fetch bot response
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await response.json();
                
                // Add bot message
                chatbox.innerHTML += `<div class="bot-msg">Obsidian: ${data.reply}</div>`;
                chatbox.scrollTop = chatbox.scrollHeight;
            } catch (error) {
                chatbox.innerHTML += `<div class="bot-msg" style="color: red;">Error: Connection to host failed.</div>`;
            }
        }
    </script>

</body>
</html>
"""


@app.route('/')
def home():
    return html_code

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get("message")
    
    # --- UPDATED IDENTITY: OBSIDIAN ---
    system_instruction = "You are 'Obsidian', an Elite Cyber Security AI Assistant made by Cursor."
    
    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_msg}
                ]
            )
            # Extract the text reply from the Groq API response
            reply = response.choices[0].message.content
            return jsonify({"reply": reply})
            
        except Exception as e:
            print(f"Error with model {model}: {e}")
            continue # If the first model fails, it loops to try the next one
            
    # If both models fail
    return jsonify({"reply": "System Error: Unable to reach Groq API."}), 500

# --- THE RENDER FIX (CRITICAL FOR DEPLOYMENT) ---
if __name__ == '__main__':
    # Render assigns a dynamic port. We must catch it using os.environ.get
    port = int(os.environ.get("PORT", 5000))
    
    # host='0.0.0.0' exposes the server to the internet so Render can connect
    # debug=False prevents the server from crashing in a production environment
    app.run(host='0.0.0.0', port=port, debug=False)
