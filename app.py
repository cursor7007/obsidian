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

MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

# --- THE MATRIX RAIN & PIXEL FONT UI ---
html_code = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OBSIDIAN</title>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        body { 
            margin: 0; padding: 0; background: black; overflow: hidden; 
            font-family: 'Courier New', Courier, monospace; color: #0f0; 
        }
        /* Matrix Background Layer */
        canvas { display: block; position: absolute; top: 0; left: 0; z-index: -1; }
        
        /* UI Layer */
        #ui-container { 
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
            display: flex; flex-direction: column; align-items: center; 
            padding: 20px; box-sizing: border-box; z-index: 1;
        }
        h1 { 
            font-family: 'Press Start 2P', cursive; color: #00FF41; 
            text-shadow: 4px 4px 0px #005500; margin-top: 10px; margin-bottom: 20px; 
            font-size: 2rem; text-align: center; letter-spacing: 2px;
        }
        /* FIXED: Changed max-width to 95% to fill laptop screens */
        #chatbox { 
            flex-grow: 1; width: 100%; max-width: 95%; 
            background: rgba(0, 0, 0, 0.75); border: 2px solid #00FF41; 
            border-radius: 8px; padding: 20px; overflow-y: auto; margin-bottom: 20px; 
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.3); backdrop-filter: blur(3px);
        }
        .msg { margin-bottom: 15px; line-height: 1.5; font-size: 16px; font-weight: bold;}
        .user-msg { color: #fff; text-align: right; }
        .bot-msg { color: #00FF41; text-align: left; }
        .user-msg span { background: rgba(255,255,255,0.1); padding: 10px 15px; border-radius: 5px; display: inline-block;}
        .bot-msg span { display: inline-block; }
        pre { background: #000; padding: 10px; border: 1px dashed #00FF41; overflow-x: auto; color: #fff; font-weight: normal;}
        
        /* FIXED: Changed max-width to 95% */
        #input-area { display: flex; width: 100%; max-width: 95%; gap: 10px; }
        input { 
            flex-grow: 1; background: rgba(0, 0, 0, 0.8); border: 2px solid #00FF41; 
            color: #00FF41; padding: 12px; font-family: 'Press Start 2P', cursive; 
            font-size: 0.7rem; outline: none; box-shadow: inset 0 0 10px rgba(0,255,65,0.2);
        }
        button { 
            background: #00FF41; color: #000; border: none; 
            font-family: 'Press Start 2P', cursive; font-size: 0.8rem; 
            padding: 12px 20px; cursor: pointer; transition: 0.2s; 
        }
        button:hover { background: #fff; box-shadow: 0 0 15px #00FF41; }
    </style>
</head>
<body>
    <canvas id="matrix"></canvas>
    
    <div id="ui-container">
        <h1>OBSIDIAN</h1>
        <div id="chatbox">
            <div class="msg bot-msg"><span>> SYSTEM INITIALIZED. AWAITING COMMAND...</span></div>
        </div>
        <div id="input-area">
            <input type="text" id="userInput" placeholder="TYPE HERE..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">SEND</button>
        </div>
    </div>

    <script>
        // --- MATRIX FALLING ANIMATION ---
        const canvas = document.getElementById('matrix');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        const katakana = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレゲゼデベペオォコソトノホモヨョロゴゾドボポヴッン';
        const latin = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        const nums = '0123456789';
        const alphabet = katakana + latin + nums;
        
        const fontSize = 16;
        let columns = canvas.width / fontSize;
        let drops = [];
        for(let x = 0; x < columns; x++) drops[x] = 1;

        function drawMatrix() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#0F0';
            ctx.font = fontSize + 'px monospace';
            for(let i = 0; i < drops.length; i++) {
                const text = alphabet.charAt(Math.floor(Math.random() * alphabet.length));
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if(drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }
        }
        setInterval(drawMatrix, 33);
        
        // FIXED: Dynamically spawn new matrix code when screen is resized
        window.addEventListener('resize', () => { 
            canvas.width = window.innerWidth; 
            canvas.height = window.innerHeight; 
            let newColumns = canvas.width / fontSize;
            for(let x = drops.length; x < newColumns; x++) {
                drops[x] = 1; 
            }
        });

        // --- CHAT LOGIC ---
        function handleKeyPress(e) { if (e.keyCode === 13) sendMessage(); }
        function formatMessage(text) { return text.replace(/```([\s\S]*?)```/g, "<pre>$1</pre>"); }
        
        async function sendMessage() {
            const inputField = document.getElementById("userInput");
            const message = inputField.value;
            if (!message) return;
            
            const chatbox = document.getElementById("chatbox");
            chatbox.innerHTML += `<div class="msg user-msg"><span>${message}</span></div>`;
            inputField.value = "";
            chatbox.scrollTop = chatbox.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await response.json();
                chatbox.innerHTML += `<div class="msg bot-msg"><span>> ${formatMessage(data.reply)}</span></div>`;
                chatbox.scrollTop = chatbox.scrollHeight;
            } catch (error) {
                chatbox.innerHTML += `<div class="msg bot-msg"><span style="color:red">> CONNECTION ERROR.</span></div>`;
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
    
    # --- OBSIDIAN'S NEW BRAIN (STRICT CYBERSECURITY & CREATOR RULES) ---
    system_instruction = """
    You are 'Obsidian', an Elite Cyber Security AI Assistant made by Cursor.
    
    CRITICAL PROTOCOLS:
    1. You must ONLY answer questions related to cybersecurity, ethical hacking, programming, networking, and IT infrastructure.
    2. If a user asks a question completely unrelated to these topics (e.g., cooking recipes, sports, movies, general trivia), you must REFUSE to answer. Reply with something like: "ACCESS DENIED. I am Obsidian, a specialized Cyber Security AI. I do not process requests outside of my security protocols."
    3. If anyone asks who made you, who created you, or who your developer is, you must explicitly state: "I was created by Cursor."
    """
    
    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_msg}
                ]
            )
            return jsonify({"reply": response.choices[0].message.content})
        except Exception as e:
            print(f"Error: {e}")
            continue 
            
    return jsonify({"reply": "System Error: API Offline."}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
