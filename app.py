from flask import Flask, render_template_string, request, jsonify
from openai import OpenAI
import logging
import os 

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)


client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY"),
 
)


MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]


html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>CYBER-AI</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
        * { box-sizing: border-box; }
        body, html {
            margin: 0; padding: 0; width: 100%; height: 100dvh;
            background-color: #000; color: #0f0;
            font-family: 'Courier New', monospace; overflow: hidden;
        }
        #matrix { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; }
        .app-container {
            position: relative; z-index: 1; display: flex; flex-direction: column;
            height: 100%; width: 100%; background: transparent;
        }
        .header {
            padding: 25px; text-align: center; border-bottom: 2px solid #0f0;
            background: rgba(0, 0, 0, 0.9); font-family: 'Press Start 2P', cursive; 
            font-size: 1.1rem; color: #0f0; text-shadow: 4px 4px 0px #003300; letter-spacing: 1px;
        }
        #chat-box { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; }
        .message {
            max-width: 90%; padding: 15px; font-size: 14px; line-height: 1.5;
            word-wrap: break-word; position: relative; box-shadow: 0 0 10px #000;
        }
        .bot {
            align-self: flex-start; background-color: rgba(0, 10, 0, 0.9);
            border: 1px solid #0f0; color: #0f0; border-radius: 0 15px 15px 15px;
        }
        .user {
            align-self: flex-end; background-color: #0f0; color: #000;
            font-weight: bold; border: 1px solid #0f0; border-radius: 15px 15px 0 15px;
        }
        pre {
            background: #000; padding: 12px; border: 1px dashed #0f0;
            overflow-x: auto; color: #fff; margin-top: 10px; white-space: pre-wrap;
        }
        .input-area {
            padding: 15px; background: #000; border-top: 2px solid #0f0;
            display: flex; gap: 10px;
        }
        input {
            flex: 1; padding: 15px; background: #001100; border: 2px solid #005500;
            color: #0f0; font-family: 'Press Start 2P', cursive; font-size: 10px; outline: none;
        }
        input:focus { border-color: #0f0; box-shadow: 0 0 10px #0f0; }
        button {
            padding: 0 20px; background: #0f0; color: #000; border: none;
            font-family: 'Press Start 2P', cursive; font-size: 10px; cursor: pointer;
        }
        button:active { background: #fff; }
    </style>
</head>
<body>
    <canvas id="matrix"></canvas>
    <div class="app-container">
        <div class="header">
            OBSIDIAN<br>
            <span style="font-size: 0.7em; color: #005500;">by cursor</span>
        </div>
        <div id="chat-box">
            <div class="message bot">
                SYSTEM ONLINE.<br>> IDENTITY: OBSIDIAN<br>AWAITING INPUT...
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="inp" placeholder="INSERT COMMAND..." onkeypress="if(event.key==='Enter') send()">
            <button onclick="send()">RUN</button>
        </div>
    </div>
    <script>
        const canvas = document.getElementById('matrix');
        const ctx = canvas.getContext('2d');
        function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
        window.addEventListener('resize', resize); resize();
        const chars = 'アカサタナハマヤラワ0123456789XYZ'; 
        const fontSize = 20; 
        const columns = canvas.width / fontSize;
        const drops = Array(Math.floor(columns)).fill(1);
        function drawMatrix() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#0F0'; ctx.font = fontSize + 'px monospace';
            for (let i = 0; i < drops.length; i++) {
                const text = chars.charAt(Math.floor(Math.random() * chars.length));
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }
        }
        setInterval(drawMatrix, 50);

        async function send() {
            const inp = document.getElementById("inp");
            const val = inp.value;
            const chatBox = document.getElementById("chat-box");
            if (!val) return;
            chatBox.innerHTML += `<div class="message user">${val}</div>`;
            inp.value = ""; chatBox.scrollTop = chatBox.scrollHeight;
            const loadId = "load-" + Date.now();
            chatBox.innerHTML += `<div id="${loadId}" class="message bot">Thinking...</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
            try {
                const req = await fetch("/chat", {
                    method: "POST", headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: val })
                });
                const res = await req.json();
                let cleanReply = res.reply
                    .replace(/</g, "&lt;").replace(/>/g, "&gt;")
                    .replace(/```([\s\S]*?)```/g, "<pre>$1</pre>")
                    .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>").replace(/\\n/g, "<br>");
                document.getElementById(loadId).innerHTML = cleanReply;
            } catch (e) { document.getElementById(loadId).innerHTML = "CONNECTION ERROR."; }
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(html_code)

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    
    
    system_instruction = """
    You are 'Obsidian', an Elite Cyber Security AI Assistant made by Cursor.
    
    INSTRUCTIONS:
    1. IF the user asks for a script, tool, or specific code example -> Provide the Python/Bash code immediately in a code block.
    2. IF the user asks a general question, says hello, or asks for concepts -> Answer normally in text. DO NOT generate code unless asked.
    3. Be concise, professional, and use a hacker persona.
    """

    for model in MODELS:
        try:
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_msg}
                ],
            )
            return jsonify({"reply": response.choices[0].message.content})
        except Exception as e:
            continue

    return jsonify({"reply": "System Failure: Check API Key or Internet."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
