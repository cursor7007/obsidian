import os
import logging
from flask import Flask, request, jsonify
from openai import OpenAI

# --- HIDE BACKGROUND LOGS ---
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# --- GROQ API CONFIGURATION ---
# Render will automatically pull the GROQ_API_KEY from your Environment Variables
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY"),
)

# --- MODELS ---
MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

# --- THE MATRIX UI ---
html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OBSIDIAN AI</title>
    <style>
        body {
            background-color: #000000;
            color: #00FF41; 
            font-family: 'Courier New', Courier, monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
        }
        h1 { text-shadow: 0 0 10px #00FF41; }
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
        #input-area { display: flex; width: 100%; max-width: 600px; }
        input[type="text"] {
            flex-grow: 1; background-color: #000; color: #00FF41;
            border: 1px solid #00FF41; padding: 10px;
            font-family: 'Courier New', Courier, monospace; outline: none;
        }
        button {
            background-color: #00FF41; color: #000; border: none;
            padding: 10px 20px; cursor: pointer; font-weight: bold;
            font-family: 'Courier New', Courier, monospace;
        }
    </style>
</head>
<body>
    <h1>OBSIDIAN TERMINAL</h1>
    <div id="chatbox">
        <div class="bot-msg">System Initialized. I am Obsidian, your Elite Cyber Security AI Assistant.</div>
    </div>
    <div id="input-area">
        <input type="text" id="userInput" placeholder="Enter command..." onkeypress="handleKeyPress(event)">
        <button onclick="sendMessage()">EXECUTE</button>
    </div>

    <script>
        function handleKeyPress(e) { if (e.keyCode === 13) sendMessage(); }

        async function sendMessage() {
            const inputField = document.getElementById("userInput");
            const message = inputField.value;
            if (!message) return;

            const chatbox = document.getElementById("chatbox");
            chatbox.innerHTML += `<div class="user-msg">User: ${message}</div>`;
            inputField.value = "";
            chatbox.scrollTop = chatbox.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await response.json();
                chatbox.innerHTML += `<div class="bot-msg">Obsidian: ${data.reply}</div>`;
                chatbox.scrollTop = chatbox.scrollHeight;
            } catch (error) {
                chatbox.innerHTML += `<div class="bot-msg" style="color: red;">Error: Connection failed.</div>`;
            }
        }
    </script>
</body>
</html>
"""

# --- ROUTES ---
@app.route('/')
def home():
    return html_code

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get("message")
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
            reply = response.choices[0].message.content
            return jsonify({"reply": reply})
        except Exception as e:
            print(f"Model error: {e}")
            continue 
            
    return jsonify({"reply": "System Error: Unable to reach Groq API."}), 500

# --- RENDER DEPLOYMENT FIX ---
if __name__ == '__main__':
    # This ensures Render can bind to the correct port and host to clear the 521 Error
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
    
