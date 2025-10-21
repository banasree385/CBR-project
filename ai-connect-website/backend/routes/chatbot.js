const express = require('express');
const router = express.Router();
const OpenAI = require('openai');

// Initialize OpenAI client
let openai = null;
if (process.env.OPENAI_API_KEY) {
    openai = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY
    });
} else {
    console.warn('⚠️  OpenAI API key not found. Chatbot will use mock responses.');
}

// ===================================
//   Chatbot Message Handler
// ===================================

router.post('/message', async (req, res) => {
    try {
        const { message, history = [], settings = {} } = req.body;
        
        // Validate input
        if (!message || typeof message !== 'string') {
            return res.status(400).json({
                error: 'Message is required and must be a string',
                code: 'INVALID_MESSAGE'
            });
        }
        
        if (message.length > 1000) {
            return res.status(400).json({
                error: 'Message is too long. Maximum 1000 characters allowed.',
                code: 'MESSAGE_TOO_LONG'
            });
        }
        
        // Log the request
        console.log(`💬 Chatbot request: "${message.substring(0, 50)}${message.length > 50 ? '...' : ''}"`);
        
        let response;
        
        if (openai) {
            // Use OpenAI API
            response = await generateOpenAIResponse(message, history, settings);
        } else {
            // Use mock response
            response = generateMockResponse(message);
        }
        
        res.json({
            response: response,
            timestamp: new Date().toISOString(),
            messageId: generateMessageId()
        });
        
    } catch (error) {
        console.error('Chatbot error:', error);
        
        // Handle different types of errors
        if (error.type === 'insufficient_quota') {
            return res.status(429).json({
                error: 'API quota exceeded. Please try again later.',
                code: 'QUOTA_EXCEEDED'
            });
        }
        
        if (error.type === 'invalid_request_error') {
            return res.status(400).json({
                error: 'Invalid request to AI service.',
                code: 'INVALID_REQUEST'
            });
        }
        
        res.status(500).json({
            error: 'I apologize, but I\'m experiencing technical difficulties. Please try again in a moment.',
            code: 'INTERNAL_ERROR'
        });
    }
});

// ===================================
//   OpenAI Integration
// ===================================

async function generateOpenAIResponse(message, history, settings) {
    try {
        // Build conversation context
        const messages = buildConversationContext(message, history, settings);
        
        // Configure model parameters based on settings
        const modelParams = getModelParameters(settings);
        
        const completion = await openai.chat.completions.create({
            model: 'gpt-3.5-turbo',
            messages: messages,
            max_tokens: modelParams.maxTokens,
            temperature: modelParams.temperature,
            top_p: modelParams.topP,
            frequency_penalty: 0.3,
            presence_penalty: 0.3,
            user: generateUserHash() // For abuse monitoring
        });
        
        if (completion.choices && completion.choices.length > 0) {
            return completion.choices[0].message.content.trim();
        } else {
            throw new Error('No response generated');
        }
        
    } catch (error) {
        console.error('OpenAI API error:', error);
        throw error;
    }
}

function buildConversationContext(currentMessage, history, settings) {
    const messages = [
        {
            role: 'system',
            content: getSystemPrompt(settings)
        }
    ];
    
    // Add recent conversation history (last 10 messages)
    const recentHistory = history.slice(-10);
    recentHistory.forEach(msg => {
        if (msg.sender === 'user') {
            messages.push({
                role: 'user',
                content: msg.message
            });
        } else if (msg.sender === 'bot') {
            messages.push({
                role: 'assistant',
                content: msg.message
            });
        }
    });
    
    // Add current message
    messages.push({
        role: 'user',
        content: currentMessage
    });
    
    return messages;
}

function getSystemPrompt(settings) {
    const basePrompt = `You are an AI assistant for AI Connect, a company that provides intelligent AI solutions. You are helpful, friendly, and knowledgeable about AI technology, machine learning, and digital transformation.

Key information about AI Connect:
- We provide AI chatbots and virtual assistants
- We offer both consumer and enterprise solutions
- We prioritize privacy, security, and ethical AI development
- We support multiple languages and platforms
- We help businesses automate customer service and improve productivity

Guidelines:
- Be conversational and approachable
- Provide accurate information about AI and technology
- If asked about competitors, be respectful but highlight AI Connect's strengths
- For technical support questions, provide helpful guidance
- If you don't know something specific about AI Connect, be honest
- Keep responses concise but informative
- Use emojis sparingly and appropriately`;

    // Adjust based on response style setting
    const style = settings.responseStyle || 'balanced';
    
    switch (style) {
        case 'creative':
            return basePrompt + '\n\nResponse style: Be more creative, engaging, and use varied language. Feel free to use analogies and examples.';
        case 'precise':
            return basePrompt + '\n\nResponse style: Be concise, factual, and direct. Focus on providing clear, actionable information.';
        default:
            return basePrompt + '\n\nResponse style: Maintain a balanced tone - friendly but professional, informative but accessible.';
    }
}

function getModelParameters(settings) {
    const style = settings.responseStyle || 'balanced';
    
    switch (style) {
        case 'creative':
            return {
                maxTokens: 300,
                temperature: 0.8,
                topP: 0.9
            };
        case 'precise':
            return {
                maxTokens: 200,
                temperature: 0.3,
                topP: 0.7
            };
        default:
            return {
                maxTokens: 250,
                temperature: 0.6,
                topP: 0.8
            };
    }
}

// ===================================
//   Mock Response System
// ===================================

function generateMockResponse(message) {
    const lowerMessage = message.toLowerCase();
    
    // FAQ responses
    const faqResponses = {
        'hello': 'Hello! Welcome to AI Connect! I\'m here to help you learn about our AI solutions. How can I assist you today?',
        'hi': 'Hi there! Thanks for visiting AI Connect. I\'m your AI assistant, ready to answer questions about our services and AI technology. What would you like to know?',
        'help': 'I\'m happy to help! I can assist you with:\n\n• Information about AI Connect\'s services\n• AI and chatbot technology questions\n• Technical support guidance\n• Business solutions and use cases\n\nWhat specific topic interests you?',
        'about ai connect': 'AI Connect is a leading provider of intelligent AI solutions! We specialize in:\n\n🤖 Advanced chatbots and virtual assistants\n🏢 Enterprise AI automation\n🔒 Privacy-focused AI development\n🌐 Multi-platform AI integration\n\nWe help businesses transform their customer experience and boost productivity through AI. Would you like to know more about any specific service?',
        'pricing': 'We offer flexible pricing plans to suit different needs:\n\n• **Starter Plan**: Perfect for small businesses\n• **Professional Plan**: Advanced features for growing companies\n• **Enterprise Plan**: Custom solutions with dedicated support\n\nFor detailed pricing information, I\'d recommend visiting our pricing page or contacting our sales team. Would you like me to help you determine which plan might be best for your needs?',
        'features': 'AI Connect offers powerful features including:\n\n✨ Natural language understanding\n🧠 Context-aware conversations\n🔄 Multi-language support\n📊 Analytics and insights\n🔌 Easy API integration\n🛡️ Enterprise-grade security\n\nWhich feature would you like to learn more about?',
        'security': 'Security is our top priority! AI Connect implements:\n\n🔐 End-to-end encryption\n🏛️ SOC 2 compliance\n🌍 GDPR compliance\n🛡️ Regular security audits\n🔒 Zero data retention policies (optional)\n\nYour conversations and data are always protected. Do you have specific security questions?',
        'integration': 'AI Connect integrates seamlessly with popular platforms:\n\n💻 Websites and web apps\n📱 Mobile applications\n💬 Slack, Microsoft Teams\n🛒 E-commerce platforms\n📧 Email systems\n☁️ Cloud platforms (AWS, Azure, GCP)\n\nWe also provide REST APIs and SDKs for custom integrations. What platform are you looking to integrate with?'
    };
    
    // Check for exact matches first
    for (const [key, response] of Object.entries(faqResponses)) {
        if (lowerMessage.includes(key)) {
            return response;
        }
    }
    
    // Contextual responses
    if (lowerMessage.includes('business') || lowerMessage.includes('enterprise')) {
        return 'AI Connect helps businesses of all sizes leverage AI technology! Our enterprise solutions include custom chatbots, automated customer support, and AI-powered analytics. We work with companies to understand their unique needs and implement AI solutions that drive real results. What type of business challenge are you looking to solve?';
    }
    
    if (lowerMessage.includes('api') || lowerMessage.includes('developer')) {
        return 'Great question! AI Connect provides comprehensive developer resources:\n\n📚 Detailed API documentation\n🔧 SDKs for popular languages\n🧪 Sandbox environment for testing\n💡 Code examples and tutorials\n🎯 Webhook support\n\nOur APIs are RESTful and easy to integrate. Would you like specific information about our developer tools?';
    }
    
    if (lowerMessage.includes('support') || lowerMessage.includes('contact')) {
        return 'We\'re here to help! AI Connect offers multiple support channels:\n\n💬 24/7 chat support (that\'s me!)\n📧 Email support: hello@aiconnect.com\n📞 Phone support for enterprise customers\n📖 Comprehensive documentation\n🎓 Video tutorials and guides\n\nWhat type of support do you need today?';
    }
    
    if (lowerMessage.includes('language') || lowerMessage.includes('multilingual')) {
        return 'AI Connect supports multiple languages including:\n\n🇺🇸 English • 🇪🇸 Spanish • 🇫🇷 French\n🇩🇪 German • 🇮🇹 Italian • 🇵🇹 Portuguese\n🇨🇳 Mandarin Chinese\n\nWe\'re continuously adding more languages based on user demand. Our AI can automatically detect the user\'s language and respond appropriately. Which languages are important for your use case?';
    }
    
    // Emotion and sentiment responses
    if (lowerMessage.includes('thank') || lowerMessage.includes('awesome') || lowerMessage.includes('great')) {
        return 'Thank you so much! I\'m delighted I could help. AI Connect is committed to providing excellent service and innovative AI solutions. Is there anything else you\'d like to know about our platform or AI technology in general?';
    }
    
    if (lowerMessage.includes('confused') || lowerMessage.includes('difficult') || lowerMessage.includes('complex')) {
        return 'I understand that AI technology can seem complex at first! That\'s exactly why AI Connect focuses on making AI accessible and easy to use. We provide step-by-step guidance, comprehensive documentation, and dedicated support to help you succeed. What specific aspect would you like me to explain more clearly?';
    }
    
    // Default responses with personality
    const defaultResponses = [
        'That\'s an interesting question! While I don\'t have specific information about that topic, I\'d be happy to help you with questions about AI Connect\'s services, AI technology, or how our platform can benefit your business. What would you like to explore?',
        'I appreciate your question! For the most accurate and detailed information about that topic, I\'d recommend checking our documentation or contacting our support team. In the meantime, I can help you with general AI Connect questions. What else can I assist you with?',
        'Thanks for reaching out! While I might not have the exact answer to that question, I\'m here to help with information about AI Connect\'s features, pricing, integrations, and AI technology in general. What aspect of our platform interests you most?',
        'Great question! AI Connect is constantly evolving, and I want to make sure you get the most up-to-date information. For specialized questions like this, our technical team would be the best resource. I can help you get connected with them, or answer other questions about our AI platform. How can I assist you further?'
    ];
    
    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
}

// ===================================
//   Utility Functions
// ===================================

function generateMessageId() {
    return 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function generateUserHash() {
    // Generate a hash for user identification (for abuse monitoring)
    // In production, you might want to use a more sophisticated approach
    return 'user_' + Math.random().toString(36).substr(2, 9);
}

// ===================================
//   Additional Endpoints
// ===================================

// Get chatbot capabilities
router.get('/capabilities', (req, res) => {
    res.json({
        features: [
            'Natural language understanding',
            'Context-aware conversations',
            'Multi-language support',
            'Customizable response styles',
            'Integration APIs',
            'Real-time responses'
        ],
        supportedLanguages: [
            'English', 'Spanish', 'French', 'German', 
            'Italian', 'Portuguese', 'Mandarin Chinese'
        ],
        responseStyles: [
            { value: 'balanced', label: 'Balanced', description: 'Professional yet friendly' },
            { value: 'creative', label: 'Creative', description: 'Engaging and varied language' },
            { value: 'precise', label: 'Precise', description: 'Concise and factual' }
        ],
        limits: {
            messageLength: 1000,
            dailyRequests: 1000,
            contextHistory: 10
        }
    });
});

// Get chatbot status
router.get('/status', (req, res) => {
    res.json({
        status: 'online',
        model: openai ? 'gpt-3.5-turbo' : 'mock',
        version: '1.0.0',
        uptime: process.uptime(),
        timestamp: new Date().toISOString()
    });
});

module.exports = router;