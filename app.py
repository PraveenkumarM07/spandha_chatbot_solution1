from flask import Flask, render_template, request, jsonify, send_file
from deep_translator import GoogleTranslator
from gtts import gTTS
import random
import time
import os
import io
import tempfile
import re

app = Flask(__name__)

# Language mapping for TTS
language_codes = {
    'en': 'en',
    'hi': 'hi',
    'te': 'te',
    'es': 'es',
    'fr': 'fr',
    'de': 'de',
    'it': 'it',
    'pt': 'pt',
    'ru': 'ru',
    'ja': 'ja',
    'ko': 'ko',
    'zh': 'zh',
    'ar': 'ar',
    'bn': 'bn',
    'ur': 'ur',
    'ta': 'ta',
    'ml': 'ml',
    'kn': 'kn',
    'gu': 'gu',
    'pa': 'pa'
}

# Depression keywords with weights
depression_keywords = {
    'en': {
        'sad': 0.3, 'depressed': 0.7, 'hopeless': 0.8, 'lonely': 0.5, 'empty': 0.6,
        'worthless': 0.75, 'guilty': 0.4, 'tired': 0.3, 'suicide': 0.9, 'die': 0.8,
        'death': 0.7, 'pain': 0.5, 'cry': 0.4, 'miserable': 0.7, 'hate': 0.6,
        'failure': 0.5, 'anxiety': 0.6, 'worried': 0.4, 'stress': 0.5, 'overwhelmed': 0.6,
        'fatigue': 0.3, 'numb': 0.4, 'helpless': 0.7, 'despair': 0.8, 'grief': 0.6,
        'heartbroken': 0.7, 'lost': 0.5, 'alone': 0.6
    },
    'hi': {
        'उदास': 0.5, 'निराश': 0.7, 'अकेला': 0.6, 'थकान': 0.4, 'तनाव': 0.5,
        'चिंता': 0.6, 'दुखी': 0.5, 'हताश': 0.7, 'खाली': 0.5, 'बेकार': 0.7,
        'दोषी': 0.4, 'थका': 0.3, 'आत्महत्या': 0.9, 'मरना': 0.8, 'मौत': 0.7,
        'दर्द': 0.5, 'रोना': 0.4, 'नफरत': 0.6, 'असफल': 0.5,
        'चिंतित': 0.4, 'अभिभूत': 0.6, 'सुन्न': 0.4, 'लाचार': 0.7, 'निराशा': 0.8, 
        'शोक': 0.6, 'टूटा': 0.7, 'खोया': 0.5
    },
    'te': {
        'విచారంగా': 0.5, 'నిరాశ': 0.7, 'ఒంటరిగా': 0.6, 'అలసట': 0.4, 'ఒత్తిడి': 0.5,
        'ఆందోళన': 0.6, 'దుఃఖంతో': 0.5, 'నిస్పృహ': 0.7, 'ఖాళీగా': 0.5, 'పనికిరాని': 0.7,
        'అపరాధి': 0.4, 'అలసిన': 0.3, 'ఆత్మహత్య': 0.9, 'చనిపోవు': 0.8, 'మరణం': 0.7,
        'నొప్పి': 0.5, 'ఏడుచు': 0.4, 'దుర్భరమైన': 0.7, 'ద్వేషం': 0.6, 'విఫలం': 0.5,
        'ఆందోళనకు': 0.4, 'ముంచెత్తిన': 0.6, 'సున్నం': 0.4, 'నిస్సహాయంగా': 0.7, 
        'హతాశ': 0.8, 'దుఃఖం': 0.6, 'నొక్కిన': 0.7, 'పోయిన': 0.5
    }
}

# Positive keywords
positive_keywords = {
    'en': {
        'happy': -0.5, 'joy': -0.6, 'good': -0.4, 'great': -0.5, 'excited': -0.4,
        'love': -0.7, 'hope': -0.6, 'better': -0.4, 'improve': -0.3, 'progress': -0.3,
        'peace': -0.5, 'calm': -0.4, 'relaxed': -0.4, 'content': -0.5, 'grateful': -0.6,
        'thankful': -0.5, 'optimistic': -0.6, 'confident': -0.5, 'proud': -0.4, 'success': -0.5
    },
    'hi': {
        'खुश': -0.5, 'आनंद': -0.6, 'अच्छा': -0.4, 'महान': -0.5, 'उत्साहित': -0.4,
        'प्रेम': -0.7, 'आशा': -0.6, 'बेहतर': -0.4, 'सुधार': -0.3, 'प्रगति': -0.3,
        'शांति': -0.5, 'शांत': -0.4, 'आराम': -0.4, 'संतुष्ट': -0.5, 'आभारी': -0.6,
        'धन्यवाद': -0.5, 'आशावादी': -0.6, 'आत्मविश्वास': -0.5, 'गर्व': -0.4, 'सफलता': -0.5
    },
    'te': {
        'సంతోషంగా': -0.5, 'ఆనందం': -0.6, 'మంచి': -0.4, 'గొప్ప': -0.5, 'ఉత్సాహంతో': -0.4,
        'ప్రేమ': -0.7, 'ఆశ': -0.6, 'మెరుగ్గా': -0.4, 'మెరుగుపరచు': -0.3, 'పురోగతి': -0.3,
        'శాంతి': -0.5, 'శాంతంగా': -0.4, 'విశ్రాంతి': -0.4, 'కంటెంట్': -0.5, 'కృతజ్ఞత': -0.6,
        'ధన్యవాదాలు': -0.5, 'ఆశావాదం': -0.6, 'ఆత్మవిశ్వాసం': -0.5, 'గర్వంగా': -0.4, 'విజయం': -0.5
    }
}

# Negation words (currently not used but kept for future enhancement)
negation_words = {
    'en': ['not', 'no', 'never', 'don\'t', 'doesn\'t', 'cant', 'cannot', 'won\'t', 'isnt', 'aren\'t'],
    'hi': ['नहीं', 'मत', 'कभी नहीं', 'न', 'मैं नहीं', 'नहीं करता'],
    'te': ['కాదు', 'ఏమాత్రం', 'ఎప్పుడూ', 'లేదు', 'నేను కాదు', 'చేయరు']
}

# Error messages
error_messages = {
    'en': {
        'voice_error': "Sorry, there was an error with voice recognition. Please try again.",
        'no_messages': "No messages to read yet.",
        'api_error': "Sorry, I'm having trouble connecting to the service. Please try again later."
    },
    'hi': {
        'voice_error': "क्षमा करें, ध्वनि पहचान में त्रुटि हुई। कृपया पुनः प्रयास करें।",
        'no_messages': "अभी तक कोई संदेश नहीं है।",
        'api_error': "क्षमा करें, मुझे सेवा से जुड़ने में परेशानी हो रही है। कृपया बाद में पुनः प्रयास करें।"
    },
    'te': {
        'voice_error': "క్షమించండి, వాయిస్ గుర్తింపులో లోపం ఏర్పడింది. దయచేసి మళ్లీ ప్రయత్నించండి.",
        'no_messages': "ఇంకా చదవడానికి సందేశాలు లేవు.",
        'api_error': "క్షమించండి, సేవకు కనెక్ట్ అవ్వడంలో నాకు ఇబ్బంది ఉంది. దయచేసి తర్వాత మళ్లీ ప్రయత్నించండి."
    }
}

# Load motivational quotes
def load_motivational_quotes():
    quotes = [
        "Peace comes from within. Do not seek it without. 🧘‍♀️",
        "In the midst of winter, I found there was, within me, an invincible summer. ❄️☀️",
        "The present moment is the only time over which we have dominion. ⏰",
        "Breathe in peace, breathe out stress. 🌬️",
        "Calm mind brings inner strength and self-confidence. 💪"
    ]
    try:
        if os.path.exists('motiv_quotes.txt'):
            with open('motiv_quotes.txt', 'r', encoding='utf-8') as f:
                file_quotes = [line.strip() for line in f.readlines() if line.strip()]
                if file_quotes:
                    quotes.extend(file_quotes)
    except Exception as e:
        print(f"Error loading quotes: {e}")
    return quotes

# Load jokes
def load_jokes():
    jokes = [
        "🤖 Why don't robots ever panic? Because they have nerves of steel!",
        "💻 My computer keeps playing the same song... It's a Dell!",
        "📱 Why did the smartphone need glasses? It lost all its contacts!"
    ]
    try:
        if os.path.exists('jokes.txt'):
            with open('jokes.txt', 'r', encoding='utf-8') as f:
                file_jokes = [line.strip() for line in f.readlines() if line.strip()]
                if file_jokes:
                    jokes.extend(file_jokes)
    except Exception as e:
        print(f"Error loading jokes: {e}")
    return jokes

# Initialize quotes and jokes
motivational_quotes = load_motivational_quotes()
jokes_list = load_jokes()

def translate_text(text, dest_lang):
    """Translate text to destination language with error handling"""
    if dest_lang == 'en' or not text:
        return text
    try:
        translator = GoogleTranslator(source='auto', target=dest_lang)
        translated = translator.translate(text)
        return translated if translated else text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def analyze_message(message, lang='en'):
    """Analyze message for depression indicators with improved error handling"""
    if not message or not isinstance(message, str):
        return {
            'score': 0,
            'isDepressed': False,
            'riskLevel': "Low Risk",
            'topContributors': []
        }
    
    # Clean and tokenize
    message_lower = message.lower().strip()
    words = re.findall(r'\b\w+\b', message_lower)
    
    if not words:
        return {
            'score': 0,
            'isDepressed': False,
            'riskLevel': "Low Risk",
            'topContributors': []
        }

    score = 0
    contributing_words = []

    # Get keywords for the specified language, fallback to English
    dep_words = depression_keywords.get(lang, depression_keywords['en'])
    pos_words = positive_keywords.get(lang, positive_keywords['en'])

    for word in words:
        if word in dep_words:
            contribution = dep_words[word]
            score += contribution
            contributing_words.append({
                'word': word,
                'contribution': contribution,
                'positive': False
            })
        elif word in pos_words:
            contribution = pos_words[word]
            score += contribution
            contributing_words.append({
                'word': word,
                'contribution': contribution,
                'positive': True
            })

    # Normalize score to 0-100%
    normalized_score = min(max((score + 1) * 50, 0), 100)

    # Sort and get top contributors
    contributing_words.sort(key=lambda x: abs(x['contribution']), reverse=True)
    top_contributors = contributing_words[:5]

    # Determine risk level
    if normalized_score < 30:
        risk_level = "Low Risk"
    elif normalized_score < 60:
        risk_level = "Moderate Risk"
    else:
        risk_level = "High Risk"

    return {
        'score': round(normalized_score, 2),
        'isDepressed': normalized_score >= 50,
        'riskLevel': risk_level,
        'topContributors': top_contributors
    }

def get_supportive_response(message, analysis, lang='en'):
    """Generate supportive response based on analysis"""
    responses = {
        'en': {
            'high': [
                "I hear you're going through a difficult time. Your feelings are valid, and it's brave of you to share.",
                "Thank you for trusting me with your feelings. Remember, you're not alone in this journey.",
                "It sounds like you're carrying a heavy burden. Would you like to talk more about what's on your mind?"
            ],
            'moderate': [
                "I notice you might be feeling some stress. It's completely normal to have ups and downs.",
                "Thanks for sharing how you're feeling. Sometimes talking about our emotions can be really helpful.",
                "It sounds like you're dealing with some challenges. How can I best support you right now?"
            ],
            'low': [
                "I'm glad you're reaching out. How are you taking care of yourself today?",
                "Thanks for sharing with me. What's been going well for you lately?",
                "It's great that you're checking in with your mental health. What brings you here today?"
            ]
        }
    }

    # Determine risk category
    score = analysis.get('score', 0)
    if score >= 60:
        risk_category = 'high'
    elif score >= 30:
        risk_category = 'moderate'
    else:
        risk_category = 'low'

    # Get response in English first
    response = random.choice(responses['en'][risk_category])
    
    # Translate if needed
    if lang != 'en':
        response = translate_text(response, lang)
    
    return response

@app.route('/')
def index():
    """Serve the main page"""
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error serving index page: {e}")
        return f"Error loading page: {str(e)}", 500

@app.route('/send_message', methods=['POST'])
def send_message():
    """Handle message sending and analysis"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        message = data.get('message', '').strip()
        lang = data.get('lang', 'en')

        if not message:
            return jsonify({'error': 'No message provided'}), 400

        # Validate language code
        if lang not in language_codes:
            lang = 'en'

        # Analyze message
        analysis = analyze_message(message, lang)

        # Get response
        response = get_supportive_response(message, analysis, lang)

        # Get random quote and joke
        quote = random.choice(motivational_quotes) if motivational_quotes else "Stay positive! 😊"
        joke = random.choice(jokes_list) if jokes_list else "Why did the computer go to therapy? It had too many bytes! 💻"

        # Translate if needed
        if lang != 'en':
            quote = translate_text(quote, lang)
            joke = translate_text(joke, lang)

        return jsonify({
            'response': response,
            'analysis': analysis,
            'quote': quote,
            'joke': joke,
            'status': 'success'
        })

    except Exception as e:
        print(f"Error in send_message: {e}")
        error_msg = error_messages.get(request.get_json().get('lang', 'en'), error_messages['en']).get('api_error', 'Internal server error')
        return jsonify({'error': error_msg}), 500

@app.route('/translate_content', methods=['POST'])
def translate_content():
    """Handle content translation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        text = data.get('text', '').strip()
        target_lang = data.get('lang', 'en')

        if not text:
            return jsonify({'translated': ''})

        # Validate language code
        if target_lang not in language_codes:
            target_lang = 'en'

        translated = translate_text(text, target_lang)
        return jsonify({'translated': translated, 'status': 'success'})

    except Exception as e:
        print(f"Translation error: {e}")
        return jsonify({'translated': data.get('text', ''), 'status': 'error'})

@app.route('/speak_text', methods=['POST'])
def speak_text():
    """Handle text-to-speech conversion"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        text = data.get('text', '').strip()
        lang = data.get('lang', 'en')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Validate and get language code for TTS
        tts_lang = language_codes.get(lang, 'en')

        # Create TTS with error handling
        try:
            tts = gTTS(text=text, lang=tts_lang, slow=False)
        except Exception as tts_error:
            print(f"TTS creation error: {tts_error}")
            # Fallback to English if the language is not supported
            tts = gTTS(text=text, lang='en', slow=False)

        # Create audio in memory
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        return send_file(
            audio_buffer,
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name='speech.mp3'
        )

    except Exception as e:
        print(f"TTS error: {e}")
        return jsonify({'error': 'Failed to generate speech'}), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files with error handling"""
    try:
        static_path = os.path.join('static', filename)
        if os.path.exists(static_path):
            return send_file(static_path)
        else:
            return '', 404
    except Exception as e:
        print(f"Static file error: {e}")
        return '', 404

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("Starting Mental Health Chatbot...")
    print(f"Loaded {len(motivational_quotes)} motivational quotes")
    print(f"Loaded {len(jokes_list)} jokes")
    
    app.run(host='0.0.0.0', port=5000, debug=True)