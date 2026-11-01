import asyncio
import os
import tempfile

from flask import Flask, request, send_file, jsonify, after_this_request
from flask_cors import CORS
import edge_tts

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Awaaz badalni ho to sirf yahan badlo:
#   en-IN-NeerjaNeural (female, Indian English, Hinglish ke liye best)
#   en-IN-PrabhatNeural (male)
#   hi-IN-SwaraNeural / hi-IN-MadhurNeural (Hindi, Devanagari text ke liye)
VOICE = os.environ.get("TTS_VOICE", "en-IN-NeerjaNeural")

STYLES = {
    "warm":    {"rate": "-5%",  "pitch": "+0Hz"},
    "calm":    {"rate": "-12%", "pitch": "-2Hz"},
    "excited": {"rate": "+5%",  "pitch": "+4Hz"},
}


async def synth(text, path, rate, pitch):
    await edge_tts.Communicate(text, VOICE, rate=rate, pitch=pitch).save(path)


@app.route("/")
def health():
    return "OK", 200


@app.route("/tts", methods=["POST"])
def tts():
    try:
        data = request.get_json(silent=True) or {}
        text = (data.get("text") or "").strip()[:1500]
        style = STYLES.get(data.get("emotion", "warm"), STYLES["warm"])

        if not text:
            return jsonify({"error": "No text provided"}), 400

        fd, audio_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)

        asyncio.run(synth(text, audio_path, style["rate"], style["pitch"]))

        @after_this_request
        def cleanup(response):
            try:
                os.remove(audio_path)
            except OSError:
                pass
            return response

        return send_file(audio_path, mimetype="audio/mpeg", as_attachment=False)

    except Exception as e:
        print("TTS Error:", e, flush=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
