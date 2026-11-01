from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import snfy
import os

app = Flask(__name__)
CORS(app) 

engine = snfy.SonifyEngine()

@app.route("/tts", methods=["POST"])
def tts():
    try:
        data = request.get_json()
        text = data.get("text", "").strip()
        emotion = data.get("emotion", "warm")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        audio_path = "temp_audio.wav"
        result = engine.synthesize(
            text=text,
            emotion=emotion,
            output_path=audio_path
        )

        return send_file(
            audio_path,
            mimetype="audio/wav",
            as_attachment=False
        )

    except Exception as e:
        print("TTS Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)