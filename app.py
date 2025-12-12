from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
import tempfile
from dotenv import load_dotenv

# Charge la clé API
load_dotenv()

app = Flask(__name__)
CORS(app) # Important pour que Next.js puisse communiquer avec Python

app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Configuration Gemini
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("❌ ERREUR : Clé API manquante dans le fichier .env")
else:
    genai.configure(api_key=api_key)

@app.route('/', methods=['GET', 'POST'])
def home():
    # Petit check pour voir si le serveur est en ligne
    if request.method == 'GET':
        return jsonify({"status": "Online", "service": "Pure OCR"})

    if request.method == 'POST':
        if 'input' not in request.files:
            return jsonify({"success": False, "error": "Aucun fichier reçu"}), 400
        
        file = request.files['input']
        if file.filename == '':
            return jsonify({"success": False, "error": "Fichier vide"}), 400

        # Sauvegarde temporaire
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        try:
            # Envoi à l'IA
            sample_file = genai.upload_file(path=filepath)
            model = genai.GenerativeModel(model_name="models/gemini-flash-latest")
            
            # --- LE PROMPT SIMPLIFIÉ ---
            # On demande juste l'extraction brute, sans traduction ni blabla.
            prompt = "Extract all text from this image exactly as it appears."

            response = model.generate_content([prompt, sample_file])
            
            # On renvoie le texte pur
            return jsonify({
                "success": True, 
                "text": response.text
            })
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
            
        finally:
            # Nettoyage
            if os.path.exists(filepath):
                try: os.remove(filepath)
                except: pass

if __name__ == '__main__':
    # Configuration du port pour le Cloud (ou 5000 en local)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)