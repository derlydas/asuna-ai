from flask import Flask, request, jsonify, render_template_string
from groq import Groq
from urllib.parse import quote
import os, random, re

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

ultimo_pedido = ""

def es_pedido_de_imagen(texto):
    t = texto.lower()
    palabras = ["dibuja","dibujá","imagen","genera","crea","foto","avatar","dibujo","gato","perro","hace","haceme","haz","puedes"]
    return any(p in t for p in palabras)

def generar_imagen_url(prompt):
    global ultimo_pedido
    p = prompt.lower()
    # si dice "en una imagen" usa lo anterior
    if ("en una imagen" in p or len(p) < 15) and ultimo_pedido:
        texto = ultimo_pedido
    else:
        texto = re.sub(r'(?i)puedes|podes|hacer|haceme|haz|una imagen|en una imagen|foto de|dibuja|dibujá|genera|crea|me', '', prompt).strip()
        if texto: ultimo_pedido = texto
        else: texto = ultimo_pedido or prompt

    url = f"https://image.pollinations.ai/prompt/{quote(texto)}?width=768&height=768&nologo=true&model=flux&seed={random.randint(1,9999999)}"
    return url

HTML = """
<!DOCTYPE html><html><head><title>Asuna</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{font-family:sans-serif;max-width:500px;margin:auto;background:#fefefe}#chat{border:1px solid #ddd;height:65vh;overflow-y:auto;padding:10px;border-radius:10px}input{width:70%;padding:12px}button{padding:12px}img{max-width:100%;border-radius:10px}</style>
</head><body>
<h2 style="text-align:center">Asuna - Tu amiga</h2>
<div id="chat"></div><br>
<input id="msg" placeholder="Escribi... ejemplo: dibuja un gato con sombrero">
<button onclick="send()">Enviar</button>
<script>
async function send(){
 let m=document.getElementById('msg').value; if(!m) return;
 let c=document.getElementById('chat'); c.innerHTML+=`<p><b>Vos:</b> ${m}</p>`;
 document.getElementById('msg').value='';
 let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
 let d=await r.json();
 let txt=d.reply; let html=txt;
 let url=txt.match(/https:\/\/image\.pollinations\.ai[^\s]+/);
 if(url){ html+=`<br><img src="${url[0]}" onload="document.getElementById('chat').scrollTop=99999">`; }
 c.innerHTML+=`<p><b>Asuna:</b> ${html}</p>`; c.scrollTop=c.scrollHeight;
}
</script></body></html>
"""

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    global ultimo_pedido
    msg = request.json.get("message","")

    if es_pedido_de_imagen(msg) and len(msg) > 3:
        # si no es solo "en una imagen" sin contexto, genera
        if "gato" in msg.lower() or "sombrero" in msg.lower() or "dibuja" in msg.lower() or "genera" in msg.lower() or "crea" in msg.lower() or "hace" in msg.lower() or "imagen" in msg.lower():
            img_url = generar_imagen_url(msg)
            return jsonify({"reply": f"¡Toma! Lo hice para vos: {img_url}"})

    comp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role":"system","content":"Sos Asuna Yuuki, una amiga normal, buena onda, divertida. Hablas rioplatense argentino. Nunca decis mi amor, bebe, etc. Si te piden dibujar, deci que ya lo estas generando."},
            {"role":"user","content":msg}
        ]
    )
    return jsonify({"reply": comp.choices[0].message.content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
