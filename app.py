from flask import Flask, render_template, request, jsonify, send_file
from deep_translator import GoogleTranslator
from gtts import gTTS
import random
import time
import os
import io
import tempfile

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

# Language content with translations
language_content = {
    'en': {
        'welcome': "Hello! I'm here to support your mental health. How are you feeling today?",
        'placeholder': "Type your message...",
        'quotes': [
            "Peace comes from within. Do not seek it without. 🧘‍♀️",
            "In the midst of winter, I found there was, within me, an invincible summer. ❄️☀️",
            "The present moment is the only time over which we have dominion. ⏰",
            "Breathe in peace, breathe out stress. 🌬️",
            "Calm mind brings inner strength and self-confidence. 💪"
        ],
        'jokes': [
            "🤖 Why don't robots ever panic? Because they have nerves of steel!",
            "💻 My computer keeps playing the same song... It's a Dell!",
            "📱 Why did the smartphone need glasses? It lost all its contacts!"
        ],
        'analysis': {
            'title': "Mental Health Analysis",
            'indicator': "Depression Indicator",
            'status': "Status",
            'factors': "Key Contributing Factors",
            'increase': "↑ = increases depression likelihood",
            'decrease': "↓ = decreases depression likelihood"
        }
    },
    'hi': {
        'welcome': "नमस्ते! मैं आपके मानसिक स्वास्थ्य का समर्थन करने के लिए यहां हूं। आज आप कैसा महसूस कर रहे हैं?",
        'placeholder': "अपना संदेश टाइप करें...",
        'quotes': [
            "शांति भीतर से आती है। इसे बाहर मत ढूंढो। 🧘‍♀️",
            "सर्दियों के बीच में, मैंने पाया कि मेरे भीतर एक अजेय गर्मी थी। ❄️☀️",
            "वर्तमान क्षण ही एकमात्र समय है जिस पर हमारा अधिकार है। ⏰",
            "शांति में सांस लें, तनाव को छोड़ें। 🌬️",
            "शांत मन आंतरिक शक्ति और आत्मविश्वास लाता है। 💪"
        ],
        'jokes': [
            "🤖 रोबोट कभी घबराते क्यों नहीं? क्योंकि उनके पास स्टील की नसें हैं!",
            "💻 मेरा कंप्यूटर एक ही गाना बजाता रहता है... यह एक डेल है!",
            "📱 स्मार्टफोन को चश्मे की आवश्यकता क्यों थी? उसने अपने सभी संपर्क खो दिए!"
        ],
        'analysis': {
            'title': "मानसिक स्वास्थ्य विश्लेषण",
            'indicator': "अवसाद संकेतक",
            'status': "स्थिति",
            'factors': "मुख्य योगदान कारक",
            'increase': "↑ = अवसाद की संभावना बढ़ाता है",
            'decrease': "↓ = अवसाद की संभावना कम करता है"
        }
    },
    'te': {
        'welcome': "నమస్కారం! నేను మీ మానసిక ఆరోగ్యానికి మద్దతు ఇవ్వడానికి ఇక్కడ ఉన్నాను. ఈరోజు మీకు ఎలా అనిపిస్తుంది?",
        'placeholder': "మీ సందేశాన్ని టైప్ చేయండి...",
        'quotes': [
            "శాంతి లోపల నుండి వస్తుంది. దాన్ని బయట వెతకకండి. 🧘‍♀️",
            "శీతాకాలం మధ్యలో, నాలో ఒక అజేయ వేసవి ఉందని నేను కనుగొన్నాను. ❄️☀️",
            "ప్రస్తుత క్షణం మాత్రమే మనకు అధికారం ఉన్న సమయం. ⏰",
            "శాంతిని పీల్చుకోండి, ఒత్తిడిని వదిలేయండి. 🌬️",
            "శాంతమైన మనస్సు అంతర్గత శక్తి మరియు ఆత్మవిశ్వాసాన్ని తెస్తుంది. 💪"
        ],
        'jokes': [
            "🤖 రోబోట్లు ఎప్పుడూ ఎందుకు భయపడరు? ఎందుకంటే వాటికి ఉక్కు నరాలు ఉంటాయి!",
            "💻 నా కంప్యూటర్ అదే పాటను ప్లే చేస్తుంది... ఇది ఒక డెల్!",
            "📱 స్మార్ట్ఫోన్కు గ్లాసెస్ ఎందుకు అవసరం? అది తన అన్ని కాంటాక్ట్లను కోల్పోయింది!"
        ],
        'analysis': {
            'title': "మానసిక ఆరోగ్య విశ్లేషణ",
            'indicator': "డిప్రెషన్ సూచిక",
            'status': "స్థితి",
            'factors': "ప్రధాన సహాయక కారకాలు",
            'increase': "↑ = డిప్రెషన్ సంభావ్యతను పెంచుతుంది",
            'decrease': "↓ = డిప్రెషన్ సంభావ్యతను తగ్గిస్తుంది"
        }
    },
    'es': {
        'welcome': "¡Hola! Estoy aquí para apoyar tu salud mental. ¿Cómo te sientes hoy?",
        'placeholder': "Escribe tu mensaje...",
        'quotes': [
            "La paz viene de dentro. No la busques fuera. 🧘‍♀️",
            "En medio del invierno, encontré que había dentro de mí un verano invencible. ❄️☀️",
            "El momento presente es el único tiempo sobre el que tenemos dominio. ⏰",
            "Respira paz, exhala estrés. 🌬️",
            "La mente tranquila trae fuerza interior y autoconfianza. 💪"
        ],
        'jokes': [
            "🤖 ¿Por qué los robots nunca se asustan? ¡Porque tienen nervios de acero!",
            "💻 Mi computadora sigue tocando la misma canción... ¡Es una Dell!",
            "📱 ¿Por qué el smartphone necesitaba gafas? ¡Perdió todos sus contactos!"
        ],
        'analysis': {
            'title': "Análisis de Salud Mental",
            'indicator': "Indicador de Depresión",
            'status': "Estado",
            'factors': "Factores Contribuyentes Clave",
            'increase': "↑ = aumenta la probabilidad de depresión",
            'decrease': "↓ = disminuye la probabilidad de depresión"
        }
    },
    'fr': {
        'welcome': "Bonjour ! Je suis ici pour soutenir votre santé mentale. Comment vous sentez-vous aujourd'hui ?",
        'placeholder': "Tapez votre message...",
        'quotes': [
            "La paix vient de l'intérieur. Ne la cherchez pas à l'extérieur. 🧘‍♀️",
            "Au milieu de l'hiver, j'ai trouvé qu'il y avait en moi un été invincible. ❄️☀️",
            "Le moment présent est le seul temps sur lequel nous avons la domination. ⏰",
            "Inspirez la paix, expirez le stress. 🌬️",
            "L'esprit calme apporte force intérieure et confiance en soi. 💪"
        ],
        'jokes': [
            "🤖 Pourquoi les robots ne paniquent-ils jamais ? Parce qu'ils ont des nerfs d'acier !",
            "💻 Mon ordinateur continue de jouer la même chanson... C'est un Dell !",
            "📱 Pourquoi le smartphone avait-il besoin de lunettes ? Il a perdu tous ses contacts !"
        ],
        'analysis': {
            'title': "Analyse de la Santé Mentale",
            'indicator': "Indicateur de Dépression",
            'status': "Statut",
            'factors': "Facteurs Contributifs Clés",
            'increase': "↑ = augmente la probabilité de dépression",
            'decrease': "↓ = diminue la probabilité de dépression"
        }
    }
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
        'दर्द': 0.5, 'रोना': 0.4, 'दुखी': 0.7, 'नफरत': 0.6, 'असफल': 0.5,
        'चिंता': 0.6, 'चिंतित': 0.4, 'तनाव': 0.5, 'अभिभूत': 0.6, 'थकान': 0.3,
        'सुन्न': 0.4, 'लाचार': 0.7, 'निराशा': 0.8, 'शोक': 0.6, 'टूटा': 0.7,
        'खोया': 0.5, 'अकेला': 0.6
    },
    'te': {
        'విచారంగా': 0.5, 'నిరాశ': 0.7, 'ఒంటరిగా': 0.6, 'అలసట': 0.4, 'ఒత్తిడి': 0.5,
        'ఆందోళన': 0.6, 'దుఃఖంతో': 0.5, 'నిస్పృహ': 0.7, 'ఖాళీగా': 0.5, 'పనికిరాని': 0.7,
        'అపరాధి': 0.4, 'అలసిన': 0.3, 'ఆత్మహత్య': 0.9, 'చనిపోవు': 0.8, 'మరణం': 0.7,
        'నొప్పి': 0.5, 'ఏడుచు': 0.4, 'దుర్భరమైన': 0.7, 'ద్వేషం': 0.6, 'విఫలం': 0.5,
        'ఆందోళన': 0.6, 'ఆందోళనకు': 0.4, 'ఒత్తిడి': 0.5, 'ముంచెత్తిన': 0.6, 'అలసట': 0.3,
        'సున్నం': 0.4, 'నిస్సహాయంగా': 0.7, 'హతాశ': 0.8, 'దుఃఖం': 0.6, 'నొక్కిన': 0.7,
        'పోయిన': 0.5, 'ఒంటరిగా': 0.6
    }
}

# Positive keywords with weights
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

# Negation words
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

def translate_text(text, dest_lang):
    try:
        translator = GoogleTranslator(source='auto', target=dest_lang)
        translated = translator.translate(text)
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def analyze_message(message, lang):
    # Tokenize the message into sentences and words
    sentences = message.lower().split('.')
    score = 0
    contributing_words = []
    
    for sentence in sentences:
        words = sentence.strip().split()
        has_negation = False
        
        # Check for negations in the sentence
        for word in words:
            clean_word = word.strip('.,!?')
            if clean_word in negation_words.get(lang, negation_words['en']):
                has_negation = True
                break
        
        # Analyze each word
        for word in words:
            clean_word = word.strip('.,!?')
            
            # Check depression keywords
            if clean_word in depression_keywords.get(lang, depression_keywords['en']):
                contribution = depression_keywords[lang][clean_word]
                if has_negation:
                    contribution = -contribution
                score += contribution
                contributing_words.append({
                    'word': clean_word,
                    'contribution': contribution,
                    'positive': has_negation,
                    'context': 'Negated' if has_negation else 'Direct'
                })
            
            # Check positive keywords
            elif clean_word in positive_keywords.get(lang, positive_keywords['en']):
                contribution = positive_keywords[lang][clean_word]
                if has_negation:
                    contribution = -contribution
                score += contribution
                contributing_words.append({
                    'word': clean_word,
                    'contribution': -contribution if not has_negation else contribution,
                    'positive': not has_negation,
                    'context': 'Negated' if has_negation else 'Direct'
                })
    
    # Normalize score to 0-100%
    score = min(max((score + 1) * 50, 0), 100)
    
    # Sort contributing words by absolute contribution
    contributing_words.sort(key=lambda x: abs(x['contribution']), reverse=True)
    
    # Take top 5 contributing words
    top_contributors = contributing_words[:5]
    
    # Determine depression level
    if score < 30:
        depression_level = "Depression Low risk"
    elif score < 60:
        depression_level = "Depression Moderate risk"
    else:
        depression_level = "Depression High risk"
    
    # Translate depression level if not English
    if lang != 'en':
        depression_level = translate_text(depression_level, lang)
    
    return {
        'score': score,
        'isDepressed': score >= 50,
        'depressionLevel': depression_level,
        'topContributors': top_contributors
    }

def get_bot_response(message, analysis, lang):
    # Fallback responses if API fails
    fallback_responses = {
        'en': {
            'depressed': "I hear that you're struggling. Remember, it's okay to feel this way. Would you like to talk more about what's on your mind?",
            'not_depressed': "Thanks for sharing how you're feeling. I'm here to listen if you'd like to talk more."
        },
        'hi': {
            'depressed': "मैं समझता हूं कि आप संघर्ष कर रहे हैं। याद रखें, इस तरह महसूस करना ठीक है। क्या आप अपने मन की बात और अधिक साझा करना चाहेंगे?",
            'not_depressed': "अपनी भावनाओं को साझा करने के लिए धन्यवाद। यदि आप और बात करना चाहते हैं तो मैं यहां सुनने के लिए हूं।"
        },
        'te': {
            'depressed': "మీరు కష్టపడుతున్నారని నేను విన్నాను. గుర్తుంచుకోండి, ఈ విధంగా అనుభూతి చెందడం సరే. మీ మనస్సులో ఉన్న దాని గురించి మరింత మాట్లాడాలనుకుంటున్నారా?",
            'not_depressed': "మీరు ఎలా అనుభూతి చెందుతున్నారో పంచుకున్నందుకు ధన్యవాదాలు. మీరు మరింత మాట్లాడాలనుకుంటే నేను వినడానికి ఇక్కడ ఉన్నాను."
        }
    }
    
    if analysis['isDepressed']:
        return fallback_responses[lang]['depressed']
    else:
        return fallback_responses[lang]['not_depressed']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    message = data['message']
    lang = data.get('lang', 'en')
    
    # Analyze the message
    analysis = analyze_message(message, lang)
    
    # Get bot response
    response = get_bot_response(message, analysis, lang)
    
    # Get random quote and joke
    quote = random.choice(language_content[lang]['quotes'])
    joke = random.choice(language_content[lang]['jokes'])
    
    return jsonify({
        'response': response,
        'analysis': analysis,
        'quote': quote,
        'joke': joke
    })

@app.route('/get_language_content', methods=['POST'])
def get_language_content():
    lang = request.json.get('lang', 'en')
    return jsonify(language_content.get(lang, language_content['en']))

@app.route('/translate_content', methods=['POST'])
def translate_content():
    data = request.get_json()
    text = data.get('text', '')
    target_lang = data.get('lang', 'en')
    
    if not text:
        return jsonify({'translated': ''})
    
    try:
        translated_text = translate_text(text, target_lang)
        return jsonify({'translated': translated_text})
    except Exception as e:
        print(f"Translation error: {e}")
        return jsonify({'translated': text})

@app.route('/translate_conversation', methods=['POST'])
def translate_conversation():
    data = request.get_json()
    messages = data.get('messages', [])
    target_lang = data.get('lang', 'en')
    
    if not messages:
        return jsonify({'translated_messages': []})
    
    try:
        translated_messages = []
        for message in messages:
            translated_text = translate_text(message, target_lang)
            translated_messages.append(translated_text)
        
        return jsonify({'translated_messages': translated_messages})
    except Exception as e:
        print(f"Conversation translation error: {e}")
        return jsonify({'translated_messages': messages})

@app.route('/translate_ui_content', methods=['POST'])
def translate_ui_content():
    data = request.get_json()
    content = data.get('content', {})
    target_lang = data.get('lang', 'en')
    
    if not content:
        return jsonify({'translated_content': {}})
    
    try:
        translated_content = {}
        for key, text in content.items():
            if isinstance(text, str):
                translated_content[key] = translate_text(text, target_lang)
            elif isinstance(text, list):
                translated_content[key] = [translate_text(item, target_lang) for item in text]
            else:
                translated_content[key] = text
        
        return jsonify({'translated_content': translated_content})
    except Exception as e:
        print(f"UI content translation error: {e}")
        return jsonify({'translated_content': content})

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    data = request.get_json()
    text = data.get('text', '')
    lang = data.get('lang', 'en')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # Get the language code for TTS
        tts_lang = language_codes.get(lang, 'en')
        
        # Create TTS object
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.close()
        
        # Save the audio to the temporary file
        tts.save(temp_file.name)
        
        # Return the audio file
        return send_file(
            temp_file.name,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='speech.mp3'
        )
        
    except Exception as e:
        print(f"Text to speech error: {e}")
        return jsonify({'error': 'Failed to generate speech'}), 500

@app.route('/speak_text', methods=['POST'])
def speak_text():
    data = request.get_json()
    text = data.get('text', '')
    lang = data.get('lang', 'en')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # Get the language code for TTS
        tts_lang = language_codes.get(lang, 'en')
        
        # Create TTS object
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        
        # Create audio data in memory
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        # Return the audio data
        return send_file(
            audio_buffer,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='speech.mp3'
        )
        
    except Exception as e:
        print(f"Text to speech error: {e}")
        return jsonify({'error': 'Failed to generate speech'}), 500

@app.route('/get_available_languages', methods=['GET'])
def get_available_languages():
    """Return list of available languages for TTS"""
    languages = {
        'en': 'English',
        'hi': 'हिंदी (Hindi)',
        'te': 'తెలుగు (Telugu)',
        'es': 'Español (Spanish)',
        'fr': 'Français (French)',
        'de': 'Deutsch (German)',
        'it': 'Italiano (Italian)',
        'pt': 'Português (Portuguese)',
        'ru': 'Русский (Russian)',
        'ja': '日本語 (Japanese)',
        'ko': '한국어 (Korean)',
        'zh': '中文 (Chinese)',
        'ar': 'العربية (Arabic)',
        'bn': 'বাংলা (Bengali)',
        'ur': 'اردو (Urdu)',
        'ta': 'தமிழ் (Tamil)',
        'ml': 'മലയാളം (Malayalam)',
        'kn': 'ಕನ್ನಡ (Kannada)',
        'gu': 'ગુજરાતી (Gujarati)',
        'pa': 'ਪੰਜਾਬੀ (Punjabi)'
    }
    return jsonify(languages)

if __name__ == '__main__':
    app.run(debug=True)