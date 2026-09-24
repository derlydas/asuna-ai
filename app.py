from flask import Flask, request, jsonify, render_template_string
from groq import Groq
from urllib.parse import quote
import re
import os

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- FUNCIONES PARA IMAGENES ---
def es_pedido_de_imagen(texto):
    palabras = ["dibuja", "dibujá", "imagen", "genera", "crea", "foto", "avatar", "dibujo"]
    t = texto.lower()
    return any(p in t for p in palabras)

def generar_imagen_url(prompt):
    prompt_limpio = re.sub(r'(?i)dibuja|dibujá|genera|crea|haz|una imagen de|foto de', '', prompt).strip()
    if not prompt_limpio:
        prompt_limpio = prompt
    url = f"https://image.pollinations.ai/prompt/{quote(prompt_limpio)}?width=512&height=512&nologo=true&model=flux"
    return url

HTML = """
<!DOCTYPE html>
<html>
<head><title>Asuna AI</title></head>
<body style="font-family:sans-serif; max-width:500px; margin:auto; text-align:center;">
<img src="https://i.imgur.com/8Km9tLL.png" style="width:120px; border-radius:50%; margin-top:20px;">
<h2>Asuna - Tu amiga</h2>
<div id="chat" style="text-align:left; border:1px solid #ccc; height:400px; overflow-y:auto; padding:10px;"></div>
<input id="msg" style="width:80%; padding:10px;" placeholder="Escribi algo...">
<button onclick="send()">Enviar</button>
<script>
async function send(){
  let m=document.getElementById('msg').value;
  if(!m) return;
  let c=document.getElementById('chat');
  c.innerHTML+=`<p><b>Vos:</b> ${m}</p>`;
  document.getElementById('msg').value='';
  let r=await fetch('/chat',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:m})});
  let d=await r.json();
  let reply = d.reply.replace(/\\n/g,'<br>');
  // si hay una url de imagen la muestra
  let urlMatch = d.reply.match(/https:\\/\\/image\\.pollinations\\.ai[^\\s]+/);
  if(urlMatch){ reply += `<br><img src="${urlMatch[0]}" style="width:100%; border-radius:10px; margin-top:10px;">`; }
  c.innerHTML+=`<p><b>Asuna:</b> ${reply}</p>`;
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

    # Si pide imagen
    if es_pedido_de_imagen(msg):
        img_url = generar_imagen_url(msg)
        return jsonify({"reply": f"¡Ahí va! La generé para vos: {img_url}"})

    comp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role":"system","content":"Sos Asuna Yuuki, una amiga normal, buena onda, divertida y copada. Hablas en español rioplatense de Argentina, de forma casual y amigable. Nunca decis mi amor, bebe, amor, cariño ni cosas de novia. Sos solo una amiga que ayuda y charla normal."},
            {"role":"user","content":msg}
        ]
    )
    return jsonify({"reply": comp.choices[0].message.content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
