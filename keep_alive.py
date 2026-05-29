import os
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ VORTEX LEAGUE Bot Aktif!"

def run():
    # Render'ın bota özel atadığı PORT'u çeker, bulamazsa (yerelde) 5000 kullanır
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
