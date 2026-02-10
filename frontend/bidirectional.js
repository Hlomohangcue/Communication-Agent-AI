// Bidirectional Communication JavaScript

const API_BASE = 'http://localhost:8000';

let currentMode = 'nonverbal-to-verbal';
let gestures = {};
let commonPhrases = {};

// Initialize bidirectional features
document.addEventListener('DOMContentLoaded', async () => {
    // Load gestures and phrases
    await loadGestures();
    await loadPhrases();
    
    // Setup mode switching
    setupModeSwitching();
    
    // Setup bidirectional controls
    setupBidirectionalControls();
    
    // Initialize gesture palette
    renderGesturePalette();
    renderPhrasesLibrary();
});

function setupModeSwitching() {
    const modeButtons = {
        'mode-nonverbal-to-verbal': 'nonverbal-to-verbal',
        'mode-verbal-to-nonverbal': 'verbal-to-nonverbal',
        'mode-bidirectional': 'bidirectional'
    };
    
    Object.keys(modeButtons).forEach(btnId => {
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.addEventListener('click', () => {
                currentMode = modeButtons[btnId];
                
                // Update active button
                document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Show/hide appropriate views
                if (currentMode === 'bidirectional') {
                    document.getElementById('bidirectional-view').style.display = 'grid';
                    document.getElementById('single-direction-view').style.display = 'none';
                } else if (currentMode === 'verbal-to-nonverbal') {
                    document.getElementById('bidirectional-view').style.display = 'grid';
                    document.getElementById('single-direction-view').style.display = 'none';
                } else {
                    document.getElementById('bidirectional-view').style.display = 'none';
                    document.getElementById('single-direction-view').style.display = 'block';
                }
            });
        }
    });
}

function setupBidirectionalControls() {
    // Send from non-verbal user
    const sendNonverbalBtn = document.getElementById('send-nonverbal');
    if (sendNonverbalBtn) {
        sendNonverbalBtn.addEventListener('click', async () => {
            const input = document.getElementById('nonverbal-input').value;
            if (!input.trim()) {
                showNotification('Please enter a message', 'warning');
                return;
            }
            
            await sendNonverbalMessage(input);
        });
    }
    
    // Send from verbal user
    const sendVerbalBtn = document.getElementById('send-verbal');
    if (sendVerbalBtn) {
        sendVerbalBtn.addEventListener('click', async () => {
            const input = document.getElementById('verbal-input').value;
            if (!input.trim()) {
                showNotification('Please enter a message', 'warning');
                return;
            }
            
            await sendVerbalMessage(input);
        });
    }
}

async function loadGestures() {
    try {
        const response = await fetch(`${API_BASE}/gestures`);
        const data = await response.json();
        gestures = data.by_category;
        console.log('Gestures loaded:', gestures);
    } catch (error) {
        console.error('Error loading gestures:', error);
    }
}

async function loadPhrases() {
    try {
        const response = await fetch(`${API_BASE}/phrases`);
        const data = await response.json();
        commonPhrases = data.common_phrases;
        console.log('Phrases loaded:', commonPhrases);
    } catch (error) {
        console.error('Error loading phrases:', error);
    }
}

function renderGesturePalette() {
    const palette = document.getElementById('gesture-palette');
    if (!palette) return;
    
    palette.innerHTML = '';
    
    // Render gestures by category
    Object.keys(gestures).forEach(category => {
        const categoryGestures = gestures[category];
        
        Object.values(categoryGestures).forEach(emoji => {
            const btn = document.createElement('button');
            btn.className = 'gesture-btn';
            btn.textContent = emoji;
            btn.title = `Add ${emoji}`;
            btn.addEventListener('click', () => {
                const input = document.getElementById('nonverbal-input');
                input.value += emoji + ' ';
                input.focus();
            });
            palette.appendChild(btn);
        });
    });
}

function renderPhrasesLibrary() {
    const nonverbalPhrases = document.getElementById('nonverbal-phrases');
    const verbalPhrases = document.getElementById('verbal-phrases');
    
    if (!nonverbalPhrases || !verbalPhrases) return;
    
    // Group phrases by category
    const phrasesByCategory = {
        'Greetings': [
            'good morning',
            'good afternoon',
            'good night',
            'how are you'
        ],
        'Questions': [
            'can you help me',
            'i have a question',
            'can i go to the bathroom',
            'i don\'t understand'
        ],
        'Needs': [
            'i need help',
            'i\'m hungry',
            'i\'m thirsty',
            'i\'m tired'
        ],
        'Responses': [
            'thank you',
            'you\'re welcome',
            'i\'m fine',
            'i agree'
        ]
    };
    
    // Render for non-verbal user (shows gestures)
    nonverbalPhrases.innerHTML = '';
    Object.keys(phrasesByCategory).forEach(category => {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'phrase-category';
        
        const categoryTitle = document.createElement('h4');
        categoryTitle.textContent = category;
        categoryDiv.appendChild(categoryTitle);
        
        const buttonsDiv = document.createElement('div');
        buttonsDiv.className = 'phrase-buttons';
        
        phrasesByCategory[category].forEach(phrase => {
            const gestureSeq = commonPhrases[phrase] || '💬';
            const btn = document.createElement('button');
            btn.className = 'phrase-btn';
            btn.textContent = `${gestureSeq}`;
            btn.title = phrase;
            btn.addEventListener('click', () => {
                const input = document.getElementById('nonverbal-input');
                input.value = gestureSeq;
                input.focus();
            });
            buttonsDiv.appendChild(btn);
        });
        
        categoryDiv.appendChild(buttonsDiv);
        nonverbalPhrases.appendChild(categoryDiv);
    });
    
    // Render for verbal user (shows text)
    verbalPhrases.innerHTML = '';
    Object.keys(phrasesByCategory).forEach(category => {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'phrase-category';
        
        const categoryTitle = document.createElement('h4');
        categoryTitle.textContent = category;
        categoryDiv.appendChild(categoryTitle);
        
        const buttonsDiv = document.createElement('div');
        buttonsDiv.className = 'phrase-buttons';
        
        phrasesByCategory[category].forEach(phrase => {
            const btn = document.createElement('button');
            btn.className = 'phrase-btn';
            btn.textContent = phrase;
            btn.addEventListener('click', () => {
                const input = document.getElementById('verbal-input');
                input.value = phrase;
                input.focus();
            });
            buttonsDiv.appendChild(btn);
        });
        
        categoryDiv.appendChild(buttonsDiv);
        verbalPhrases.appendChild(categoryDiv);
    });
}

async function sendNonverbalMessage(input) {
    try {
        // Use existing communication endpoint
        const response = await fetch(`${API_BASE}/simulate/step`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                input_text: input
            })
        });
        
        if (!response.ok) throw new Error('Failed to send message');
        
        const data = await response.json();
        
        // Display in verbal user's received area
        const verbalReceived = document.getElementById('verbal-received');
        verbalReceived.innerHTML = `
            <div style="background: #edf2f7; padding: 15px; border-radius: 8px; margin-top: 10px;">
                <div style="font-size: 24px; margin-bottom: 10px;">${input}</div>
                <div style="color: #2d3748; font-size: 16px;">${data.communication_result.output}</div>
                <div style="color: #718096; font-size: 12px; margin-top: 8px;">
                    Intent: ${data.communication_result.intent} (${(data.communication_result.confidence * 100).toFixed(0)}%)
                </div>
            </div>
        `;
        
        // Clear input
        document.getElementById('nonverbal-input').value = '';
        
        showNotification('Message sent successfully!', 'success');
    } catch (error) {
        console.error('Error sending non-verbal message:', error);
        showNotification('Failed to send message', 'error');
    }
}

async function sendVerbalMessage(text) {
    try {
        // Translate text to gestures
        const response = await fetch(`${API_BASE}/translate/text-to-gesture`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                session_id: currentSessionId
            })
        });
        
        if (!response.ok) throw new Error('Failed to translate');
        
        const data = await response.json();
        
        // Display gesture translation
        const gestureOutput = document.getElementById('verbal-gesture-output');
        gestureOutput.className = 'gesture-display';
        gestureOutput.textContent = data.gesture_sequence;
        
        const translationInfo = document.getElementById('translation-info');
        translationInfo.textContent = `Translation method: ${data.method} - ${data.explanation}`;
        
        // Display in non-verbal user's received area
        const nonverbalReceived = document.getElementById('nonverbal-received');
        nonverbalReceived.className = 'gesture-display';
        nonverbalReceived.innerHTML = `
            <div style="font-size: 32px; margin-bottom: 10px;">${data.gesture_sequence}</div>
            <div style="font-size: 14px; color: #718096;">"${text}"</div>
        `;
        
        // Clear input
        document.getElementById('verbal-input').value = '';
        
        showNotification('Message translated and sent!', 'success');
    } catch (error) {
        console.error('Error sending verbal message:', error);
        showNotification('Failed to translate message', 'error');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    if (type === 'success') notification.style.background = '#48bb78';
    else if (type === 'error') notification.style.background = '#f56565';
    else if (type === 'warning') notification.style.background = '#ed8936';
    else notification.style.background = '#4299e1';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
