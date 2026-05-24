from flask import Flask, request, jsonify, send_file
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global config
VISION_ENDPOINT = None
VISION_KEY = None
TRANSLATOR_KEY = None
SPEECH_KEY = None
SPEECH_REGION = None
DOC_INTELLIGENCE_ENDPOINT = None
DOC_INTELLIGENCE_KEY = None
TEXT_ANALYTICS_ENDPOINT = None
TEXT_ANALYTICS_KEY = None

@app.route('/config', methods=['POST'])
def update_config():
    global VISION_ENDPOINT, VISION_KEY, TRANSLATOR_KEY, SPEECH_KEY, SPEECH_REGION, DOC_INTELLIGENCE_ENDPOINT, DOC_INTELLIGENCE_KEY, TEXT_ANALYTICS_ENDPOINT, TEXT_ANALYTICS_KEY
    data = request.json
    
    VISION_ENDPOINT = data.get('vision_endpoint')
    VISION_KEY = data.get('vision_key')
    TRANSLATOR_KEY = data.get('translator_key')
    SPEECH_KEY = data.get('speech_key')
    SPEECH_REGION = data.get('speech_region')
    DOC_INTELLIGENCE_ENDPOINT = data.get('doc_endpoint')
    DOC_INTELLIGENCE_KEY = data.get('doc_key')
    TEXT_ANALYTICS_ENDPOINT = data.get('text_analytics_endpoint')
    TEXT_ANALYTICS_KEY = data.get('text_analytics_key')
    
    return jsonify({"status": "success", "message": "Configuration Saved!"})

@app.route('/')
def home():
    return send_file('index.html')

# ===================== IMAGE ANALYSIS =====================
@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    if not VISION_ENDPOINT or not VISION_KEY:
        return jsonify({"error": "Vision config not set"}), 400

    file = request.files.get('image')
    if not file: return jsonify({"error": "No image"}), 400

    try:
        from azure.ai.vision.imageanalysis import ImageAnalysisClient
        from azure.ai.vision.imageanalysis.models import VisualFeatures
        from azure.core.credentials import AzureKeyCredential

        client = ImageAnalysisClient(endpoint=VISION_ENDPOINT, credential=AzureKeyCredential(VISION_KEY))
        image_data = file.read()

        result = client.analyze(image_data=image_data, visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ, VisualFeatures.TAGS])

        response = {
            "caption": result.caption.text if result.caption else "No caption",
            "tags": [tag.name for tag in (result.tags or [])],
            "text_extracted": []
        }

        if hasattr(result, 'read') and result.read and result.read.blocks:
            for block in result.read.blocks:
                for line in block.lines:
                    response["text_extracted"].append(line.text)

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===================== TRANSLATION =====================
@app.route('/translate', methods=['POST'])
def translate():
    if not TRANSLATOR_KEY:
        return jsonify({"error": "Translator config not set"}), 400

    data = request.json
    text = data.get('text')
    to_language = data.get('to', 'hi')

    try:
        from azure.ai.translation.text import TextTranslationClient
        from azure.core.credentials import AzureKeyCredential

        client = TextTranslationClient(credential=AzureKeyCredential(TRANSLATOR_KEY))
        response = client.translate(body=[text], to=[to_language])
        translated_text = response[0].translations[0].text

        return jsonify({"original": text, "translated": translated_text, "to": to_language})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===================== TEXT TO SPEECH =====================
@app.route('/speak', methods=['POST'])
def speak():
    if not SPEECH_KEY or not SPEECH_REGION:
        return jsonify({"error": "Speech config not set"}), 400

    data = request.json
    text = data.get('text')

    try:
        import azure.cognitiveservices.speech as speechsdk
        import base64

        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        speech_config.speech_synthesis_voice_name = "hi-IN-MadhurNeural"

        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            audio_base64 = base64.b64encode(result.audio_data).decode('utf-8')
            return jsonify({"audio": audio_base64})
        else:
            return jsonify({"error": "Speech synthesis failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===================== DOCUMENT INTELLIGENCE =====================
@app.route('/analyze-document', methods=['POST'])
def analyze_document():
    if not DOC_INTELLIGENCE_ENDPOINT or not DOC_INTELLIGENCE_KEY:
        return jsonify({"error": "Document Intelligence config not set"}), 400

    file = request.files.get('document')
    if not file: return jsonify({"error": "No document"}), 400

    try:
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.core.credentials import AzureKeyCredential

        client = DocumentIntelligenceClient(endpoint=DOC_INTELLIGENCE_ENDPOINT, credential=AzureKeyCredential(DOC_INTELLIGENCE_KEY))
        file_bytes = file.read()

        poller = client.begin_analyze_document("prebuilt-layout", file_bytes)
        result = poller.result()

        extracted = {
            "content": result.content[:1500] if result.content else "",
            "key_value_pairs": []
        }

        if result.key_value_pairs:
            for kvp in result.key_value_pairs:
                key = kvp.key.content if kvp.key else ""
                value = kvp.value.content if kvp.value else ""
                if key or value:
                    extracted["key_value_pairs"].append({"key": key, "value": value})

        return jsonify(extracted)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===================== TEXT ANALYTICS (Review Analyzer) =====================
@app.route('/analyze-review', methods=['POST'])
def analyze_review():
    if not TEXT_ANALYTICS_ENDPOINT or not TEXT_ANALYTICS_KEY:
        return jsonify({"error": "Text Analytics config not set"}), 400

    data = request.json
    text = data.get('text')

    try:
        from azure.ai.textanalytics import TextAnalyticsClient
        from azure.core.credentials import AzureKeyCredential

        client = TextAnalyticsClient(endpoint=TEXT_ANALYTICS_ENDPOINT, credential=AzureKeyCredential(TEXT_ANALYTICS_KEY))

        documents = [text]
        response = client.analyze_sentiment(documents)
        sentiment = response[0]

        key_phrases = client.extract_key_phrases(documents)
        phrases = key_phrases[0].key_phrases if key_phrases[0].key_phrases else []

        result = {
            "sentiment": sentiment.sentiment,
            "confidence": {
                "positive": round(sentiment.confidence_scores.positive, 3),
                "neutral": round(sentiment.confidence_scores.neutral, 3),
                "negative": round(sentiment.confidence_scores.negative, 3)
            },
            "key_phrases": phrases[:8]
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)