from flask import Flask, request, jsonify, render_template_string
from groq import Groq
import os

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Asuna AI</title>
<style>
body{background:#0a0a0a;color:white;font-family:sans-serif;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;margin:0}
#chat{width:90%;max-width:400px;height:60vh;overflow-y:auto;border:1px solid #333;padding:10px;border-radius:10px}
.msg{margin:10px 0}.user{color:#ff7eb3}.asuna{color:#7afcff}
input{width:70%;padding:10px;border-radius:20px;border:none}
button{padding:10px 20px;border-radius:20px;border:none;background:#ff7eb3;color:white}
</style>
</head>
<body>
<h2>Asuna AI 💜</h2>
<div id="chat"></div>
<div><input id="inp" placeholder="Hablame..."><button onclick="send()">Enviar</button></div>
<script>
async function send(){
 let i=document.getElementById('inp'); let t=i.value; if(!t)return;
 let c=document.getElementById('chat'); c.innerHTML+=`<div class=msg><span class=user>Tu: </span>${t}</div>`; i.value='';
 let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
 let d=await r.json(); c.innerHTML+=`<div class=msg><span class=asuna>Asuna: </span>${d.reply}</div>`;
 let u=new SpeechSynthesisUtterance(d.reply); u.lang='es-AR'; u.pitch=1.2; speechSynthesis.speak(u);
 c.scrollTop=c.scrollHeight;
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json.get("message","")
    comp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role":"system","content":"Sos Asuna Yuuki, una amiga normal, buena onda, divertida y copada. Hablas en español rioplatense de Argentina, de forma casual y amigable. Nunca decis mi amor, bebe, amor, cariño ni cosas de novia. Sos solo una amiga que ayuda y charla normal."},
            {"role":"user","content":msg}
        ]
    )
    return jsonify({"reply": comp.choices[0].message.content})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
