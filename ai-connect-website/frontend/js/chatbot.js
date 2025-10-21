// ===================================
//   Chatbot Widget Functionality
// ===================================

class ChatbotWidget {
    constructor() {
        this.isOpen = false;
        this.isTyping = false;
        this.messageHistory = [];
        this.settings = {
            soundEnabled: true,
            typingIndicators: true,
            responseStyle: 'balanced'
        };
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSettings();
        this.loadChatHistory();
        this.initializeMainChatbot();
    }

    bindEvents() {
        // Floating widget toggle
        const toggle = document.getElementById('chatbot-toggle');
        const close = document.getElementById('chatbot-close');
        
        if (toggle) {
            toggle.addEventListener('click', () => this.toggleWidget());
        }
        
        if (close) {
            close.addEventListener('click', () => this.closeWidget());
        }

        // Send message events
        const sendBtn = document.getElementById('chatbot-send');
        const input = document.getElementById('chatbot-input');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            
            input.addEventListener('input', () => this.handleInputChange());
        }

        // Main chatbot page events
        this.initMainChatbotEvents();
    }

    initMainChatbotEvents() {
        // Main chatbot input
        const mainInput = document.getElementById('main-chat-input');
        const mainSendBtn = document.getElementById('main-send-btn');
        
        if (mainInput) {
            mainInput.addEventListener('input', () => {
                this.updateCharCounter(mainInput, 'main-char-count');
                this.toggleSendButton(mainSendBtn, mainInput.value.trim());
            });
            
            mainInput.addEventListener('keydown', (e) => {
                this.handleInputKeydown(e);
            });
        }
        
        if (mainSendBtn) {
            mainSendBtn.addEventListener('click', () => this.sendMainMessage());
        }

        // Settings panel
        const settingsToggle = document.querySelector('[onclick*=\"toggleSettings\"]');
        if (settingsToggle) {
            settingsToggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleSettings();
            });
        }
    }

    toggleWidget() {
        const container = document.getElementById('chatbot-container');
        const toggle = document.getElementById('chatbot-toggle');
        
        if (container) {
            this.isOpen = !this.isOpen;
            container.classList.toggle('active', this.isOpen);
            
            if (this.isOpen) {
                this.focusInput();
                this.markMessagesAsRead();
            }
            
            // Animate toggle button
            if (toggle) {
                toggle.style.transform = this.isOpen ? 'rotate(180deg)' : 'rotate(0deg)';
            }
        }
    }

    closeWidget() {
        const container = document.getElementById('chatbot-container');
        const toggle = document.getElementById('chatbot-toggle');
        
        if (container) {
            this.isOpen = false;
            container.classList.remove('active');
            
            if (toggle) {
                toggle.style.transform = 'rotate(0deg)';
            }
        }
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input?.value.trim();
        
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input
        input.value = '';
        this.handleInputChange();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send to backend
            const response = await this.callChatbotAPI(message);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add bot response
            this.addMessage(response, 'bot');
            
            // Play sound if enabled
            if (this.settings.soundEnabled) {
                this.playNotificationSound();
            }
            
        } catch (error) {
            console.error('Chatbot error:', error);
            this.hideTypingIndicator();
            this.addMessage('I apologize, but I\\'m having trouble connecting right now. Please try again in a moment.', 'bot');
        }
        
        // Save conversation
        this.saveChatHistory();
    }

    async sendMainMessage() {
        const input = document.getElementById('main-chat-input');
        const message = input?.value.trim();
        
        if (!message) return;
        
        // Add user message to main chat
        this.addMainMessage(message, 'user');
        
        // Clear input and reset height
        input.value = '';
        input.style.height = 'auto';
        this.updateCharCounter(input, 'main-char-count');
        this.toggleSendButton(document.getElementById('main-send-btn'), '');
        
        // Hide quick actions
        const quickActions = document.getElementById('quick-actions');
        if (quickActions && quickActions.children.length > 0) {
            quickActions.style.display = 'none';
        }
        
        // Show typing indicator
        this.showMainTypingIndicator();
        
        try {
            // Send to backend
            const response = await this.callChatbotAPI(message);
            
            // Hide typing indicator
            this.hideMainTypingIndicator();
            
            // Add bot response
            this.addMainMessage(response, 'bot');
            
        } catch (error) {
            console.error('Chatbot error:', error);
            this.hideMainTypingIndicator();
            this.addMainMessage('I apologize, but I\\'m having trouble connecting right now. Please try again in a moment.', 'bot');
        }
    }

    async callChatbotAPI(message) {
        const response = await fetch('/api/chatbot/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                history: this.messageHistory.slice(-10), // Send last 10 messages for context
                settings: this.settings
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to get response from chatbot');
        }
        
        const data = await response.json();
        return data.response;
    }

    addMessage(message, sender) {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        if (sender === 'bot') {
            messageDiv.innerHTML = `
                <div class=\"message-avatar\">
                    <i class=\"fas fa-robot\"></i>
                </div>
                <div class=\"message-content\">
                    <p>${this.formatMessage(message)}</p>
                    <span class=\"message-time\">${this.getCurrentTime()}</span>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class=\"message-content\">
                    <p>${this.formatMessage(message)}</p>
                    <span class=\"message-time\">${this.getCurrentTime()}</span>
                </div>
            `;
        }
        
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom(messagesContainer);
        
        // Add to history
        this.messageHistory.push({
            message: message,
            sender: sender,
            timestamp: Date.now()
        });
        
        // Animate message appearance
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(20px)';
        setTimeout(() => {
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
            messageDiv.style.transition = 'all 0.3s ease';
        }, 10);
    }

    addMainMessage(message, sender) {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}-message`;
        
        if (sender === 'bot') {
            messageDiv.innerHTML = `
                <div class=\"message-avatar\">
                    <i class=\"fas fa-robot\"></i>
                </div>
                <div class=\"message-content\">
                    <div class=\"message-text\">${this.formatMessage(message)}</div>
                    <div class=\"message-time\">${this.getCurrentTime()}</div>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class=\"message-content\">
                    <div class=\"message-text\">${this.formatMessage(message)}</div>
                    <div class=\"message-time\">${this.getCurrentTime()}</div>
                </div>
                <div class=\"message-avatar user-avatar\">
                    <i class=\"fas fa-user\"></i>
                </div>
            `;
        }
        
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom(messagesContainer);
        
        // Add to history
        this.messageHistory.push({
            message: message,
            sender: sender,
            timestamp: Date.now()
        });
    }

    showTypingIndicator() {
        if (!this.settings.typingIndicators) return;
        
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class=\"typing-animation\">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom(messagesContainer);
        
        this.isTyping = true;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
        this.isTyping = false;
    }

    showMainTypingIndicator() {
        if (!this.settings.typingIndicators) return;
        
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message bot-message typing-indicator';
        typingDiv.id = 'main-typing-indicator';
        typingDiv.innerHTML = `
            <div class=\"message-avatar\">
                <i class=\"fas fa-robot\"></i>
            </div>
            <div class=\"typing-animation\">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom(messagesContainer);
    }

    hideMainTypingIndicator() {
        const typingIndicator = document.getElementById('main-typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    handleInputChange() {
        const input = document.getElementById('chatbot-input');
        const sendBtn = document.getElementById('chatbot-send');
        
        if (input && sendBtn) {
            const hasText = input.value.trim().length > 0;
            sendBtn.disabled = !hasText;
            sendBtn.style.opacity = hasText ? '1' : '0.6';
        }
    }

    handleInputKeydown(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.sendMainMessage();
        }
    }

    adjustTextareaHeight(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
    }

    updateCharCounter(input, counterId) {
        const counter = document.getElementById(counterId);
        if (counter && input) {
            counter.textContent = input.value.length;
        }
    }

    toggleSendButton(button, value) {
        if (button) {
            const hasText = value.length > 0;
            button.disabled = !hasText;
            button.style.opacity = hasText ? '1' : '0.6';
        }
    }

    formatMessage(message) {
        // Basic message formatting
        return message
            .replace(/\\n/g, '<br>')
            .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
            .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }

    getCurrentTime() {
        return new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    scrollToBottom(container) {
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }

    focusInput() {
        const input = document.getElementById('chatbot-input');
        if (input) {
            setTimeout(() => input.focus(), 100);
        }
    }

    markMessagesAsRead() {
        // Mark messages as read (could be used for notifications)
        // Implementation depends on notification system
    }

    playNotificationSound() {
        if (!this.settings.soundEnabled) return;
        
        // Create a simple notification sound
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.1);
    }

    // Settings Management
    toggleSettings() {
        const panel = document.getElementById('settings-panel');
        if (panel) {
            panel.classList.toggle('active');
        }
    }

    loadSettings() {
        const savedSettings = localStorage.getItem('ai-connect-chatbot-settings');
        if (savedSettings) {
            this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
        }
        
        // Apply saved settings to UI
        const responseStyleSelect = document.getElementById('response-style');
        if (responseStyleSelect) {
            responseStyleSelect.value = this.settings.responseStyle;
        }
        
        const soundCheckbox = document.getElementById('sound-enabled');
        if (soundCheckbox) {
            soundCheckbox.checked = this.settings.soundEnabled;
        }
        
        const typingCheckbox = document.getElementById('typing-indicators');
        if (typingCheckbox) {
            typingCheckbox.checked = this.settings.typingIndicators;
        }
    }

    saveSettings() {
        localStorage.setItem('ai-connect-chatbot-settings', JSON.stringify(this.settings));
    }

    // Chat History Management
    saveChatHistory() {
        // Only keep last 50 messages
        const historyToSave = this.messageHistory.slice(-50);
        localStorage.setItem('ai-connect-chat-history', JSON.stringify(historyToSave));
    }

    loadChatHistory() {
        const savedHistory = localStorage.getItem('ai-connect-chat-history');
        if (savedHistory) {
            this.messageHistory = JSON.parse(savedHistory);
            
            // Restore messages to widget (not main chat)
            const messagesContainer = document.getElementById('chatbot-messages');
            if (messagesContainer && this.messageHistory.length > 0) {
                // Clear existing messages except welcome message
                const welcomeMessage = messagesContainer.querySelector('.welcome-message');
                messagesContainer.innerHTML = '';
                if (welcomeMessage) {
                    messagesContainer.appendChild(welcomeMessage);
                }
                
                // Restore last few messages
                this.messageHistory.slice(-5).forEach(msg => {
                    if (msg.sender && msg.message) {
                        this.addMessage(msg.message, msg.sender);
                    }
                });
            }
        }
    }

    clearChat() {
        // Clear widget chat
        const messagesContainer = document.getElementById('chatbot-messages');
        if (messagesContainer) {
            const welcomeMessage = messagesContainer.querySelector('.welcome-message');
            messagesContainer.innerHTML = '';
            if (welcomeMessage) {
                messagesContainer.appendChild(welcomeMessage);
            }
        }
        
        // Clear main chat
        const mainMessagesContainer = document.getElementById('chat-messages');
        if (mainMessagesContainer) {
            const welcomeMessage = mainMessagesContainer.querySelector('.welcome-message');
            mainMessagesContainer.innerHTML = '';
            if (welcomeMessage) {
                mainMessagesContainer.appendChild(welcomeMessage);
            }
            
            // Show quick actions again
            const quickActions = document.getElementById('quick-actions');
            if (quickActions) {
                quickActions.style.display = 'grid';
            }
        }
        
        // Clear history
        this.messageHistory = [];
        localStorage.removeItem('ai-connect-chat-history');
    }

    exportChat() {
        if (this.messageHistory.length === 0) {
            alert('No conversation to export.');
            return;
        }
        
        const chatText = this.messageHistory
            .map(msg => `[${new Date(msg.timestamp).toLocaleString()}] ${msg.sender}: ${msg.message}`)
            .join('\\n');
        
        const blob = new Blob([chatText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai-connect-chat-${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }

    // Quick Actions
    sendQuickMessage(message) {
        const mainInput = document.getElementById('main-chat-input');
        if (mainInput) {
            mainInput.value = message;
            this.sendMainMessage();
        } else {
            // Fallback to widget
            const widgetInput = document.getElementById('chatbot-input');
            if (widgetInput) {
                widgetInput.value = message;
                this.sendMessage();
                this.toggleWidget(); // Open widget if not already open
            }
        }
    }

    // File Upload (placeholder for future implementation)
    handleFileUpload() {
        const modal = document.getElementById('file-upload-modal');
        if (modal) {
            modal.style.display = 'block';
        }
        alert('File upload feature coming soon!');
    }

    // Emoji Picker
    toggleEmojiPicker() {
        const picker = document.getElementById('emoji-picker');
        if (picker) {
            picker.style.display = picker.style.display === 'block' ? 'none' : 'block';
        }
    }

    insertEmoji(emoji) {
        const input = document.getElementById('main-chat-input') || document.getElementById('chatbot-input');
        if (input) {
            const cursorPos = input.selectionStart;
            const textBefore = input.value.substring(0, cursorPos);
            const textAfter = input.value.substring(cursorPos);
            input.value = textBefore + emoji + textAfter;
            input.selectionStart = input.selectionEnd = cursorPos + emoji.length;
            input.focus();
            
            // Trigger input event
            input.dispatchEvent(new Event('input'));
        }
        
        // Hide emoji picker
        this.toggleEmojiPicker();
    }

    initializeMainChatbot() {
        // Initialize main chatbot page specific functionality
        if (document.querySelector('.chatbot-interface')) {
            this.setupMainChatbotEventListeners();
        }
    }

    setupMainChatbotEventListeners() {
        // Settings panel events
        document.addEventListener('change', (e) => {
            if (e.target.id === 'response-style') {
                this.settings.responseStyle = e.target.value;
                this.saveSettings();
            } else if (e.target.id === 'sound-enabled') {
                this.settings.soundEnabled = e.target.checked;
                this.saveSettings();
            } else if (e.target.id === 'typing-indicators') {
                this.settings.typingIndicators = e.target.checked;
                this.saveSettings();
            }
        });

        // Close modals when clicking outside
        document.addEventListener('click', (e) => {
            const modal = document.getElementById('file-upload-modal');
            if (modal && e.target === modal) {
                modal.style.display = 'none';
            }
            
            const emojiPicker = document.getElementById('emoji-picker');
            if (emojiPicker && !e.target.closest('.emoji-btn') && !e.target.closest('#emoji-picker')) {
                emojiPicker.style.display = 'none';
            }
            
            const settingsPanel = document.getElementById('settings-panel');
            if (settingsPanel && !e.target.closest('.control-btn') && !e.target.closest('#settings-panel')) {
                settingsPanel.classList.remove('active');
            }
        });
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add chatbot styles
    const chatbotStyles = document.createElement('style');
    chatbotStyles.textContent = `
        .typing-animation {
            display: flex;
            gap: 4px;
            padding: 10px;
        }
        
        .typing-animation span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--primary-color);
            animation: typing 1.4s infinite ease-in-out both;
        }
        
        .typing-animation span:nth-child(1) { animation-delay: -0.32s; }
        .typing-animation span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }
        
        .chat-message {
            display: flex;
            gap: var(--spacing-md);
            margin-bottom: var(--spacing-lg);
            align-items: flex-start;
        }
        
        .chat-message.user-message {
            flex-direction: row-reverse;
        }
        
        .message-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        
        .chat-message .message-avatar {
            background: var(--primary-color);
            color: var(--text-light);
        }
        
        .chat-message .user-avatar {
            background: var(--secondary-color);
            color: var(--text-light);
        }
        
        .chat-message .message-content {
            background: var(--bg-secondary);
            padding: var(--spacing-md);
            border-radius: var(--border-radius-lg);
            max-width: 70%;
            border: 1px solid var(--border-color);
        }
        
        .chat-message.user-message .message-content {
            background: var(--primary-color);
            color: var(--text-light);
        }
        
        .message-text {
            margin-bottom: var(--spacing-xs);
        }
        
        .message-time {
            font-size: var(--font-size-xs);
            opacity: 0.7;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 10000;
            align-items: center;
            justify-content: center;
        }
        
        .modal-content {
            background: var(--bg-card);
            border-radius: var(--border-radius-lg);
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow: auto;
        }
        
        .modal-header {
            padding: var(--spacing-lg);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .modal-close {
            background: none;
            border: none;
            font-size: var(--font-size-lg);
            cursor: pointer;
            color: var(--text-muted);
        }
        
        .modal-body {
            padding: var(--spacing-lg);
        }
        
        .file-drop-zone {
            border: 2px dashed var(--border-color);
            border-radius: var(--border-radius);
            padding: var(--spacing-2xl);
            text-align: center;
            cursor: pointer;
            transition: var(--transition-base);
        }
        
        .file-drop-zone:hover {
            border-color: var(--primary-color);
            background: var(--primary-light);
        }
        
        .emoji-picker {
            position: absolute;
            bottom: 100%;
            right: 0;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            padding: var(--spacing-md);
            display: none;
            box-shadow: var(--shadow-lg);
        }
        
        .emoji-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: var(--spacing-xs);
        }
        
        .emoji {
            font-size: var(--font-size-lg);
            cursor: pointer;
            padding: var(--spacing-xs);
            border-radius: var(--border-radius);
            text-align: center;
            transition: var(--transition-base);
        }
        
        .emoji:hover {
            background: var(--bg-secondary);
        }
    `;
    document.head.appendChild(chatbotStyles);
    
    // Initialize chatbot
    window.chatbot = new ChatbotWidget();
});

// Global functions for HTML onclick handlers
window.sendQuickMessage = function(message) {
    if (window.chatbot) {
        window.chatbot.sendQuickMessage(message);
    }
};

window.clearChat = function() {
    if (window.chatbot) {
        window.chatbot.clearChat();
    }
};

window.exportChat = function() {
    if (window.chatbot) {
        window.chatbot.exportChat();
    }
};

window.toggleSettings = function() {
    if (window.chatbot) {
        window.chatbot.toggleSettings();
    }
};

window.handleFileUpload = function() {
    if (window.chatbot) {
        window.chatbot.handleFileUpload();
    }
};

window.toggleEmojiPicker = function() {
    if (window.chatbot) {
        window.chatbot.toggleEmojiPicker();
    }
};

window.insertEmoji = function(emoji) {
    if (window.chatbot) {
        window.chatbot.insertEmoji(emoji);
    }
};

window.adjustTextareaHeight = function(textarea) {
    if (window.chatbot) {
        window.chatbot.adjustTextareaHeight(textarea);
    }
};

window.handleInputKeydown = function(event) {
    if (window.chatbot) {
        window.chatbot.handleInputKeydown(event);
    }
};

window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
};