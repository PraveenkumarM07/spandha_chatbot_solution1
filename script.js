// Mental Health Chatbot JavaScript

class MentalHealthChatbot {
    constructor() {
        this.currentLanguage = 'en';
        this.lastBotMessage = '';
        this.recognition = null;
        this.isListening = false;
        
        this.initializeElements();
        this.initializeEventListeners();
        this.initializeSpeechRecognition();
        this.loadLanguageContent();
    }

    initializeElements() {
        this.messagesContainer = document.getElementById('messages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.voiceBtn = document.getElementById('voiceBtn');
        this.speakBtn = document.getElementById('speakBtn');
        this.languageSelect = document.getElementById('languageSelect');
        this.loading = document.getElementById('loading');
    }

    initializeEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        this.voiceBtn.addEventListener('click', () => this.toggleVoiceRecognition());
        this.speakBtn.addEventListener('click', () => this.speakLastMessage());
        this.languageSelect.addEventListener('change', (e) => this.changeLanguage(e.target.value));
    }

    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = this.getRecognitionLanguage();

            this.recognition.onstart = () => {
                this.isListening = true;
                this.voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
                this.voiceBtn.style.background = 'linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)';
            };

            this.recognition.onend = () => {
                this.isListening = false;
                this.voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
                this.voiceBtn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
            };

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.messageInput.value = transcript;
                this.sendMessage();
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.showMessage('bot', 'Sorry, I had trouble understanding your voice. Please try again or type your message.');
            };
        } else {
            this.voiceBtn.style.display = 'none';
        }
    }

    getRecognitionLanguage() {
        const langMap = {
            'en': 'en-US',
            'hi': 'hi-IN',
            'te': 'te-IN',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'it': 'it-IT',
            'pt': 'pt-PT',
            'ru': 'ru-RU',
            'ja': 'ja-JP',
            'ko': 'ko-KR',
            'zh': 'zh-CN',
            'ar': 'ar-SA'
        };
        return langMap[this.currentLanguage] || 'en-US';
    }

    toggleVoiceRecognition() {
        if (!this.recognition) return;

        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.recognition.lang = this.getRecognitionLanguage();
            this.recognition.start();
        }
    }

    changeLanguage(lang) {
        this.currentLanguage = lang;
        this.loadLanguageContent();
        if (this.recognition) {
            this.recognition.lang = this.getRecognitionLanguage();
        }
    }

    loadLanguageContent() {
        const content = this.getLanguageContent();
        document.querySelector('.header p').textContent = content.subtitle;
        this.messageInput.placeholder = content.placeholder;
        
        // Update welcome message
        const welcomeMsg = document.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.innerHTML = `
                <h3>${content.welcome.title}</h3>
                <p>${content.welcome.message1}</p>
                <p>${content.welcome.message2}</p>
                <p>${content.welcome.message3}</p>
            `;
        }
    }

    getLanguageContent() {
        const content = {
            'en': {
                subtitle: 'Your Mental Health Companion',
                placeholder: 'Type your message here...',
                welcome: {
                    title: 'Welcome to Spandha! 🌟',
                    message1: "I'm here to listen and support you on your mental health journey.",
                    message2: "Feel free to share what's on your mind - I'm here to help! 💙",
                    message3: "You can type your message or use the voice button to speak."
                }
            },
            'hi': {
                subtitle: 'आपका मानसिक स्वास्थ्य साथी',
                placeholder: 'यहाँ अपना संदेश लिखें...',
                welcome: {
                    title: 'स्पंदना में आपका स्वागत है! 🌟',
                    message1: "मैं आपकी मानसिक स्वास्थ्य यात्रा में सुनने और सहायता करने के लिए यहाँ हूँ।",
                    message2: "बेझिझक साझा करें कि आपके मन में क्या है - मैं मदद के लिए यहाँ हूँ! 💙",
                    message3: "आप अपना संदेश टाइप कर सकते हैं या बोलने के लिए वॉइस बटन का उपयोग कर सकते हैं।"
                }
            },
            'te': {
                subtitle: 'మీ మానసిక ఆరోగ్య సహచరుడు',
                placeholder: 'ఇక్కడ మీ సందేశం టైప్ చేయండి...',
                welcome: {
                    title: 'స్పందనకు స్వాగతం! 🌟',
                    message1: "మీ మానసిక ఆరోగ్య ప్రయాణంలో వినడానికి మరియు మద్దతు ఇవ్వడానికి నేను ఇక్కడ ఉన్నాను.",
                    message2: "మీ మనసులో ఉన్నది పంచుకోండి - నేను సహాయం చేయడానికి ఇక్కడ ఉన్నాను! 💙",
                    message3: "మీరు మీ సందేశాన్ని టైప్ చేయవచ్చు లేదా మాట్లాడటానికి వాయిస్ బటన్‌ను ఉపయోగించవచ్చు."
                }
            }
        };
        return content[this.currentLanguage] || content['en'];
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Show user message
        this.showMessage('user', message);
        this.messageInput.value = '';
        this.showLoading(true);

        try {
            // Simulate API call with local processing
            const response = await this.processMessage(message);
            this.showLoading(false);
            
            // Show bot response
            this.showMessage('bot', response.response, response.analysis, response.quote, response.joke);
            this.lastBotMessage = response.response;
            
        } catch (error) {
            this.showLoading(false);
            this.showMessage('bot', 'I apologize, but I encountered an error. Please try again.');
            console.error('Error:', error);
        }
    }

    async processMessage(message) {
        // Simulate processing delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Simple local analysis
        const analysis = this.analyzeMessage(message);
        const response = this.generateResponse(analysis);
        const quote = this.getMotivationalQuote();
        const joke = this.getJoke();

        return { response, analysis, quote, joke };
    }

    analyzeMessage(message) {
        const depressionKeywords = [
            'sad', 'depressed', 'hopeless', 'lonely', 'empty', 'worthless', 'tired', 'anxious',
            'worried', 'stressed', 'overwhelmed', 'helpless', 'despair', 'grief', 'lost', 'alone'
        ];
        
        const positiveKeywords = [
            'happy', 'joy', 'good', 'great', 'excited', 'love', 'hope', 'better', 'improve',
            'progress', 'peace', 'calm', 'relaxed', 'content', 'grateful', 'thankful'
        ];

        const words = message.toLowerCase().split(/\s+/);
        let score = 0;
        let contributors = [];

        words.forEach(word => {
            if (depressionKeywords.includes(word)) {
                score += 0.5;
                contributors.push({ word, positive: false });
            } else if (positiveKeywords.includes(word)) {
                score -= 0.3;
                contributors.push({ word, positive: true });
            }
        });

        const normalizedScore = Math.min(Math.max((score + 1) * 50, 0), 100);
        
        let riskLevel = 'Low Risk';
        if (normalizedScore >= 60) riskLevel = 'High Risk';
        else if (normalizedScore >= 30) riskLevel = 'Moderate Risk';

        return {
            score: Math.round(normalizedScore),
            isDepressed: normalizedScore >= 50,
            riskLevel,
            topContributors: contributors.slice(0, 3)
        };
    }

    generateResponse(analysis) {
        const responses = {
            high: [
                "I hear you're going through a difficult time. Your feelings are valid, and it's brave of you to share.",
                "Thank you for trusting me with your feelings. Remember, you're not alone in this journey.",
                "It sounds like you're carrying a heavy burden. Would you like to talk more about what's on your mind?"
            ],
            moderate: [
                "I notice you might be feeling some stress. It's completely normal to have ups and downs.",
                "Thanks for sharing how you're feeling. Sometimes talking about our emotions can be really helpful.",
                "It sounds like you're dealing with some challenges. How can I best support you right now?"
            ],
            low: [
                "I'm glad you're reaching out. How are you taking care of yourself today?",
                "Thanks for sharing with me. What's been going well for you lately?",
                "It's great that you're checking in with your mental health. What brings you here today?"
            ]
        };

        let category = 'low';
        if (analysis.score >= 60) category = 'high';
        else if (analysis.score >= 30) category = 'moderate';

        return responses[category][Math.floor(Math.random() * responses[category].length)];
    }

    getMotivationalQuote() {
        const quotes = [
            "Peace comes from within. Do not seek it without. 🧘‍♀️",
            "In the midst of winter, I found there was, within me, an invincible summer. ❄️☀️",
            "The present moment is the only time over which we have dominion. ⏰",
            "Breathe in peace, breathe out stress. 🌬️",
            "Calm mind brings inner strength and self-confidence. 💪",
            "You are stronger than you think and more capable than you imagine. 🌟",
            "Every small step forward is progress worth celebrating. 🎉",
            "Your mental health is just as important as your physical health. 💚"
        ];
        return quotes[Math.floor(Math.random() * quotes.length)];
    }

    getJoke() {
        const jokes = [
            "🤖 Why don't robots ever panic? Because they have nerves of steel!",
            "💻 My computer keeps playing the same song... It's a Dell!",
            "📱 Why did the smartphone need glasses? It lost all its contacts!",
            "🧠 Why did the brain go to therapy? It had too many thoughts to process!",
            "☕ How does a penguin build its house? Igloos it together!",
            "🌟 Why don't scientists trust atoms? Because they make up everything!"
        ];
        return jokes[Math.floor(Math.random() * jokes.length)];
    }

    showMessage(sender, content, analysis = null, quote = null, joke = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = content;

        if (sender === 'bot' && analysis) {
            // Add analysis card
            const analysisCard = document.createElement('div');
            analysisCard.className = 'analysis-card';
            
            const riskClass = analysis.riskLevel.toLowerCase().replace(' ', '-');
            analysisCard.innerHTML = `
                <div class="risk-indicator risk-${riskClass}">${analysis.riskLevel}</div>
                <p><strong>Analysis Score:</strong> ${analysis.score}%</p>
                ${analysis.topContributors.length > 0 ? 
                    `<p><strong>Key words:</strong> ${analysis.topContributors.map(c => c.word).join(', ')}</p>` : ''}
            `;
            messageContent.appendChild(analysisCard);

            // Add quote
            if (quote) {
                const quoteCard = document.createElement('div');
                quoteCard.className = 'quote-card';
                quoteCard.innerHTML = `<strong>💭 Inspiration:</strong> ${quote}`;
                messageContent.appendChild(quoteCard);
            }

            // Add joke
            if (joke) {
                const jokeCard = document.createElement('div');
                jokeCard.className = 'joke-card';
                jokeCard.innerHTML = `<strong>😄 A little humor:</strong> ${joke}`;
                messageContent.appendChild(jokeCard);
            }
        }

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);

        // Remove welcome message if it exists
        const welcomeMessage = this.messagesContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        this.messagesContainer.appendChild(messageDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    showLoading(show) {
        this.loading.classList.toggle('show', show);
        if (show) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }

    speakLastMessage() {
        if (!this.lastBotMessage) {
            this.showMessage('bot', 'No messages to read yet.');
            return;
        }

        if ('speechSynthesis' in window) {
            // Cancel any ongoing speech
            speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(this.lastBotMessage);
            utterance.lang = this.getRecognitionLanguage();
            utterance.rate = 0.8;
            utterance.pitch = 1;
            
            speechSynthesis.speak(utterance);
        } else {
            this.showMessage('bot', 'Text-to-speech is not supported in your browser.');
        }
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new MentalHealthChatbot();
});