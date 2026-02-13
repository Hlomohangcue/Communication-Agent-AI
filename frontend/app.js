const API_BASE = 'https://8000-i1jp0gsn9.brevlab.com';

let currentSessionId = null;
let isProcessing = false;
let simulationActive = false;
let currentInputMode = 'text'; // 'text' or 'speech'
let recognition = null;
let isRecording = false;
let finalTranscript = '';  // Track transcript across recognition restarts
let authToken = null;  // Store auth token
let currentUser = null;  // Store current user info

// Communication mode variables
let currentMode = 'nonverbal-to-verbal';
let gestures = {};
let commonPhrases = {};

// Get auth token from storage
function getAuthToken() {
    return localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
}

// Get auth headers
function getAuthHeaders() {
    const token = getAuthToken();
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
}

// Check authentication on page load
async function checkAuthentication() {
    const token = getAuthToken();
    
    if (!token) {
        // No token, redirect to login
        window.location.href = 'login.html';
        return false;
    }
    
    try {
        const response = await fetch(`${API_BASE}/auth/me`, {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            // Token invalid, redirect to login
            localStorage.removeItem('authToken');
            sessionStorage.removeItem('authToken');
            window.location.href = 'login.html';
            return false;
        }
        
        currentUser = await response.json();
        console.log('Authenticated user:', currentUser);
        
        // Update user info in UI
        updateUserInfo();
        
        // Load user credits
        await loadUserCredits();
        
        return true;
    } catch (error) {
        console.error('Authentication check failed:', error);
        window.location.href = 'login.html';
        return false;
    }
}

// Update user info in UI
function updateUserInfo() {
    if (!currentUser) return;
    
    const userName = document.querySelector('.user-name');
    const userRole = document.querySelector('.user-role');
    
    if (userName) {
        userName.textContent = currentUser.name || 'User';
    }
    
    if (userRole) {
        if (currentMode === 'verbal-to-nonverbal') {
            userRole.textContent = 'Verbal Teacher';
        } else {
            userRole.textContent = 'Non-Verbal Communicator';
        }
    }
}

// Load user credits
async function loadUserCredits() {
    try {
        const response = await fetch(`${API_BASE}/auth/credits`, {
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('User credits:', data);
            
            // Display credits in UI
            if (data.plan === 'free') {
                const creditsDisplay = document.getElementById('credits-display');
                if (creditsDisplay) {
                    creditsDisplay.textContent = `${data.credits} messages left`;
                }
            }
        }
    } catch (error) {
        console.error('Failed to load credits:', error);
    }
}

// Logout function
function logout() {
    localStorage.removeItem('authToken');
    sessionStorage.removeItem('authToken');
    localStorage.removeItem('userId');
    sessionStorage.removeItem('userId');
    window.location.href = 'login.html';
}

// Common phrases for verbal to non-verbal communication
const COMMON_PHRASES = [
    // Greetings
    "Hello",
    "Hi",
    "Good morning",
    "Good afternoon",
    "Good night",
    "Goodbye",
    "See you tomorrow",
    
    // Polite Expressions
    "Please",
    "Thank you",
    "Yes",
    "No",
    "You're welcome",
    
    // Classroom Instructions
    "Please sit down",
    "Stand up",
    "Please be quiet",
    "Listen carefully",
    "Look at the board",
    "Open your books",
    "Read the page",
    "Write in your notebook",
    "Take out your pencils",
    "Put away your paper",
    
    // Questions & Help
    "Raise your hand if you have a question",
    "Do you have any questions",
    "Do you need help",
    "Can you repeat that",
    "Do you understand",
    "Show me your work",
    "Tell me your answer",
    
    // Time & Schedule
    "It's time to begin",
    "Let's start",
    "Time to stop",
    "We're done for today",
    "Time for a break",
    "Lunch time",
    "See you tomorrow",
    "Homework is due tomorrow",
    
    // Feedback & Encouragement
    "Good job",
    "Great job",
    "Excellent work",
    "Well done",
    "Keep trying",
    "You can do it",
    "That's correct",
    "Try again",
    
    // Classroom Management
    "Pay attention please",
    "Eyes on me",
    "Work with your partner",
    "Join your group",
    "Line up please",
    "Clean up your desk",
    "Put your things away",
    "Get ready to go",
    
    // Activities
    "Time to study",
    "Let's review",
    "Practice your reading",
    "Work on your art project",
    "Time to play",
    "Go to your seat",
    "Come to the front",
    
    // Basic Needs
    "You may go to the bathroom",
    "Are you hungry",
    "Do you need water",
    "Are you feeling tired",
    "Are you feeling sick",
    "Do you need a break",
    
    // Emotions & Feelings
    "Are you happy",
    "What's wrong",
    "Don't be sad",
    "It's okay",
    "I'm sorry",
    "Don't worry",
    "Are you angry",
    "Calm down please",
    
    // Common Responses
    "I understand",
    "I see",
    "That's right",
    "Not quite",
    "Let me help you",
    "Ask me if you need help",
    "Think about it",
    "Take your time"
];

// ASL (American Sign Language) emoji mappings
const ASL_MAPPINGS = {
    // Greetings
    'hello': '👋',
    'hi': '👋',
    'good morning': '☀️👋',
    'good afternoon': '🌤️👋',
    'good night': '🌙👋',
    'goodbye': '👋✌️',
    'see you': '👋',
    
    // Common classroom phrases
    'please': '🙏',
    'thank you': '🙏❤️',
    'yes': '👍',
    'no': '👎',
    'sit': '🪑',
    'sit down': '🪑⬇️',
    'stand': '🧍',
    'stand up': '🧍⬆️',
    'quiet': '🤫',
    'be quiet': '🤫',
    'listen': '👂',
    'look': '👀',
    'read': '📖',
    'write': '✍️',
    'open': '📖➡️',
    'close': '📖⬅️',
    'book': '📖',
    'books': '📚',
    'pencil': '✏️',
    'pencils': '✏️✏️',
    'paper': '📄',
    
    // Actions
    'raise hand': '🙋',
    'raise your hand': '🙋',
    'question': '❓',
    'questions': '❓❓',
    'answer': '💬',
    'help': '🆘',
    'work': '💼',
    'study': '📚',
    'learn': '🎓',
    'think': '🤔',
    'understand': '💡',
    'repeat': '🔄',
    'again': '🔄',
    
    // Time related
    'time': '⏰',
    'break': '☕',
    'lunch': '🍽️',
    'lunch time': '🍽️⏰',
    'tomorrow': '📅➡️',
    'today': '📅',
    'now': '⏰',
    'later': '⏰➡️',
    'begin': '▶️',
    'start': '▶️',
    'stop': '⏹️',
    'finish': '✅',
    'done': '✅',
    
    // Emotions & Feedback
    'good': '👍',
    'great': '👍⭐',
    'excellent': '⭐⭐⭐',
    'great job': '👍⭐',
    'well done': '👏',
    'happy': '😊',
    'sad': '😢',
    'sorry': '😔',
    
    // Classroom management
    'attention': '👀⚠️',
    'pay attention': '👀⚠️',
    'class': '👥',
    'partner': '👥',
    'group': '👥👥',
    'line up': '➡️➡️➡️',
    'clean up': '🧹',
    'homework': '📝🏠',
    'review': '🔄📚',
    
    // Common words
    'you': '👉',
    'me': '👈',
    'we': '👥',
    'they': '👉👥',
    'have': '🤲',
    'need': '🙏',
    'want': '🙏',
    'can': '💪',
    'do': '✅',
    'go': '➡️',
    'come': '⬅️',
    'take': '🤲',
    'give': '🤲➡️',
    'show': '👁️',
    'tell': '💬'
};

// Initialize speech recognition if available
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = true;  // Keep recording continuously
    recognition.interimResults = true;  // Show results as you speak
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;
    
    let restartTimeout = null;
    
    recognition.onstart = () => {
        console.log('Speech recognition started');
        if (isRecording) {
            document.getElementById('recording-status').textContent = '🔴 Recording... Speak now!';
            document.getElementById('recording-status').className = 'recording-status active';
        }
    };
    
    recognition.onresult = (event) => {
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Display both final and interim results
        const displayText = finalTranscript + interimTranscript;
        document.getElementById('speech-transcript').textContent = displayText;
        console.log('Transcript:', displayText);
    };
    
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        
        if (event.error === 'no-speech') {
            console.log('No speech detected, but continuing to listen...');
            // Don't stop on no-speech, the onend handler will restart
            return;
        }
        
        if (event.error === 'aborted') {
            console.log('Recognition aborted (user stopped)');
            // User manually stopped, don't show error
            return;
        }
        
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
            document.getElementById('recording-status').textContent = '❌ Microphone access denied';
            document.getElementById('recording-status').className = 'recording-status';
            
            showNotification(
                'Microphone access denied! Please:\n' +
                '1. Click the 🔒 lock icon in your browser address bar\n' +
                '2. Allow microphone access\n' +
                '3. Refresh the page and try again',
                'error'
            );
            stopRecording();
            return;
        }
        
        if (event.error === 'network') {
            console.log('Network error, will retry...');
            // Network errors can happen, let onend restart
            return;
        }
        
        // For other errors, show message but try to continue
        console.warn('Recognition error:', event.error);
        document.getElementById('recording-status').textContent = `⚠️ ${event.error} - retrying...`;
    };
    
    recognition.onend = () => {
        console.log('Speech recognition ended, isRecording:', isRecording);
        
        // Clear any pending restart
        if (restartTimeout) {
            clearTimeout(restartTimeout);
            restartTimeout = null;
        }
        
        // Automatically restart if still supposed to be recording
        if (isRecording) {
            console.log('Auto-restarting recognition in 100ms...');
            // Small delay before restart to avoid rapid restart loops
            restartTimeout = setTimeout(() => {
                if (isRecording) {  // Check again in case user stopped during delay
                    try {
                        recognition.start();
                        console.log('Recognition restarted successfully');
                    } catch (error) {
                        console.error('Error restarting recognition:', error);
                        // If already started, ignore the error
                        if (error.message && error.message.includes('already started')) {
                            console.log('Recognition already running, continuing...');
                        } else {
                            // For other errors, try again after a longer delay
                            console.log('Will retry restart in 500ms...');
                            restartTimeout = setTimeout(() => {
                                if (isRecording) {
                                    try {
                                        recognition.start();
                                    } catch (e) {
                                        console.error('Failed to restart after retry:', e);
                                        stopRecording();
                                        showNotification('Recording stopped due to error. Please try again.', 'error');
                                    }
                                }
                            }, 500);
                        }
                    }
                }
            }, 100);
        }
    };
    
    console.log('Speech recognition initialized');
} else {
    console.warn('Speech recognition not supported in this browser');
}

// Define functions first before they're used
function addWorkflowItem(agent, action) {
    console.log('addWorkflowItem called:', agent, action);
    const workflowDisplay = document.getElementById('workflow-display');
    
    if (!workflowDisplay) {
        console.error('workflow-display element not found!');
        return;
    }
    
    console.log('workflow-display found, adding item');
    
    const item = document.createElement('div');
    item.className = 'workflow-item';
    item.style.opacity = '0';
    item.innerHTML = `
        <div class="agent-name">${agent}</div>
        <div>${action}</div>
        <div style="font-size: 0.75rem; color: #718096; margin-top: 4px;">
            ${new Date().toLocaleTimeString()}
        </div>
    `;
    workflowDisplay.insertBefore(item, workflowDisplay.firstChild);
    
    console.log('Item added to workflow display');
    
    // Fade in animation
    setTimeout(() => {
        item.style.transition = 'opacity 0.3s';
        item.style.opacity = '1';
    }, 10);
    
    // Keep last 20 workflow items
    if (workflowDisplay.children.length > 20) {
        workflowDisplay.removeChild(workflowDisplay.lastChild);
    }
}

function addConversationMessage(type, message, metadata = {}) {
    console.log('=== ADD CONVERSATION MESSAGE ===');
    console.log('Type:', type);
    console.log('Message:', message);
    console.log('Metadata:', metadata);
    
    const conversationDisplay = document.getElementById('conversation-display');
    
    if (!conversationDisplay) {
        console.error('ERROR: conversation-display element not found!');
        return;
    }
    
    console.log('Conversation display found, current children:', conversationDisplay.children.length);
    
    const item = document.createElement('div');
    item.className = 'conversation-item';
    item.style.opacity = '0';
    
    if (type === 'student') {
        // Check if this is a gesture message (contains emojis or is from translation)
        const isGestureMessage = metadata.originalText || /[\u{1F300}-\u{1F9FF}]/u.test(message);
        
        let displayMessage = message;
        let metaInfo = `Non-Verbal User • ${new Date().toLocaleTimeString()}`;
        
        if (metadata.originalText) {
            // This is a translated gesture from verbal user
            metaInfo += ` • Translated from: "${metadata.originalText}"`;
        }
        
        item.innerHTML = `
            <div class="message-student">
                <div class="message-bubble">${displayMessage}</div>
            </div>
            <div class="message-meta" style="text-align: right;">${metaInfo}</div>
        `;
    } else if (type === 'teacher') {
        const intent = metadata.intent ? ` • ${metadata.intent}` : '';
        const confidence = metadata.confidence ? ` (${(metadata.confidence * 100).toFixed(0)}%)` : '';
        const gestures = metadata.gestures ? ` • Gestures: ${metadata.gestures}` : '';
        const method = metadata.method ? ` • ${metadata.method}` : '';
        
        item.innerHTML = `
            <div class="message-teacher">
                <div class="message-bubble">${message}</div>
            </div>
            <div class="message-meta" style="text-align: left;">Verbal User • ${new Date().toLocaleTimeString()}${intent}${confidence}${gestures}${method}</div>
        `;
    }
    
    conversationDisplay.appendChild(item);
    
    // Fade in animation
    setTimeout(() => {
        item.style.transition = 'opacity 0.3s';
        item.style.opacity = '1';
    }, 50);
    
    console.log('Message added! Total messages now:', conversationDisplay.children.length);
    
    // Auto-scroll to bottom
    setTimeout(() => {
        conversationDisplay.scrollTop = conversationDisplay.scrollHeight;
    }, 100);
    
    console.log('=== MESSAGE ADDED SUCCESSFULLY ===');
}

async function loadConversationHistory(sessionId) {
    console.log('=== LOAD CONVERSATION HISTORY CALLED ===');
    console.log('Session ID:', sessionId);
    console.log('Stack trace:', new Error().stack);
    console.log('Loading conversation history for session:', sessionId);
    
    try {
        const response = await fetch(`${API_BASE}/session/${sessionId}`, {
            headers: getAuthHeaders()
        });
        if (!response.ok) {
            console.error('Failed to load conversation history');
            return;
        }
        
        const data = await response.json();
        console.log('Conversation history loaded:', data);
        
        const conversationDisplay = document.getElementById('conversation-display');
        if (!conversationDisplay) {
            console.error('conversation-display not found');
            return;
        }
        
        console.log('⚠️ CLEARING CONVERSATION DISPLAY - Current message count:', conversationDisplay.children.length);
        
        // Clear and rebuild conversation
        conversationDisplay.innerHTML = '';
        
        if (data.messages && data.messages.length > 0) {
            // Messages are returned newest first, so reverse them
            const messages = data.messages.reverse();
            
            console.log(`Rebuilding conversation with ${messages.length} messages from database`);
            
            messages.forEach(msg => {
                // Check if this is a verbal-to-nonverbal message
                if (msg.intent === 'verbal_to_nonverbal_translation') {
                    // This is a teacher→student message with ASL translation
                    // input_text contains "[Teacher] ..." and output_text contains "[ASL] ..."
                    const teacherText = msg.input_text.replace('[Teacher] ', '');
                    const aslText = msg.output_text.replace('[ASL] ', '');
                    
                    console.log('Loading verbal→nonverbal message:', { teacherText, aslText });
                    
                    // Add teacher message first
                    addConversationMessage('teacher', teacherText);
                    
                    // Add ASL translation as student message
                    addConversationMessage('student', aslText, {
                        originalText: teacherText
                    });
                } else {
                    // Regular non-verbal to verbal message
                    console.log('Loading nonverbal→verbal message:', { input: msg.input_text, output: msg.output_text });
                    
                    // Add non-verbal user message (student)
                    addConversationMessage('student', msg.input_text);
                    
                    // Add verbal user response (teacher)
                    addConversationMessage('teacher', msg.output_text, {
                        intent: msg.intent
                    });
                }
            });
            
            console.log(`✅ Loaded ${messages.length} conversation pairs`);
        } else {
            conversationDisplay.innerHTML = '<div style="padding: 15px; color: #999; text-align: center;">No messages yet. Start the conversation!</div>';
        }
        
    } catch (error) {
        console.error('Error loading conversation history:', error);
    }
}

// Restore session on page load
window.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM Content Loaded');
    
    // Check authentication first
    const isAuthenticated = await checkAuthentication();
    if (!isAuthenticated) {
        return; // Will redirect to login
    }
    
    const savedSessionId = sessionStorage.getItem('sessionId');
    const savedIsActive = sessionStorage.getItem('isActive');
    
    if (savedSessionId && savedIsActive === 'true') {
        console.log('Restoring session:', savedSessionId);
        currentSessionId = savedSessionId;
        simulationActive = true;
        
        const startBtn = document.getElementById('start-sim');
        const stopBtn = document.getElementById('stop-sim');
        
        document.getElementById('session-id').textContent = `Session: ${currentSessionId.substring(0, 8)}... (Active)`;
        document.getElementById('session-id').style.color = '#48bb78';
        document.getElementById('session-id').style.fontWeight = 'bold';
        
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-block';
        
        document.getElementById('send-message').disabled = false;
        document.getElementById('student-input').disabled = false;
        
        addWorkflowItem('System', '🔄 Session restored - Ready to communicate');
        
        // Load existing conversation from database
        loadConversationHistory(savedSessionId);
    }
    
    // Attach event listeners
    console.log('Attaching event listeners...');
    
    const startBtn = document.getElementById('start-sim');
    const stopBtn = document.getElementById('stop-sim');
    const sendBtn = document.getElementById('send-message');
    const refreshBtn = document.getElementById('refresh-logs');
    const clearBtn = document.getElementById('clear-logs');
    
    console.log('Elements found:', {
        startBtn: !!startBtn,
        stopBtn: !!stopBtn,
        sendBtn: !!sendBtn,
        refreshBtn: !!refreshBtn,
        clearBtn: !!clearBtn
    });
    
    if (startBtn) {
        startBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Start button clicked');
            startSimulation();
        });
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Stop button clicked');
            stopSimulation();
        });
    }
    
    if (sendBtn) {
        console.log('Send button element:', sendBtn);
        console.log('Send button onclick:', sendBtn.onclick);
        console.log('Send button disabled:', sendBtn.disabled);
        
        sendBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('=== SEND MESSAGE BUTTON CLICKED ===');
            console.log('Event:', e);
            sendMessage();
        });
        
        console.log('Send button listener attached');
    } else {
        console.error('Send button not found!');
    }
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadLogs);
    }
    
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            document.getElementById('logs-display').innerHTML = '';
            showNotification('Logs cleared', 'info');
        });
    }
    
    // Mode toggle buttons
    const textModeBtn = document.getElementById('text-mode-btn');
    const speechModeBtn = document.getElementById('speech-mode-btn');
    const startRecordingBtn = document.getElementById('start-recording');
    const stopRecordingBtn = document.getElementById('stop-recording');
    
    if (textModeBtn) {
        textModeBtn.addEventListener('click', switchToTextMode);
    }
    
    if (speechModeBtn) {
        speechModeBtn.addEventListener('click', switchToSpeechMode);
    }
    
    if (startRecordingBtn) {
        startRecordingBtn.addEventListener('click', startRecording);
    }
    
    if (stopRecordingBtn) {
        stopRecordingBtn.addEventListener('click', stopRecording);
    }
    
    // Token buttons
    document.querySelectorAll('.token-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const token = btn.dataset.token;
            const input = document.getElementById('student-input');
            input.value += token + ' ';
            input.focus();
        });
    });
    
    // Enter key to send
    const studentInput = document.getElementById('student-input');
    if (studentInput) {
        studentInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                sendMessage();
            }
        });
    }
    
    console.log('Event listeners attached');
});

function switchToTextMode() {
    currentInputMode = 'text';
    document.getElementById('text-mode-btn').classList.add('active');
    document.getElementById('speech-mode-btn').classList.remove('active');
    document.getElementById('text-input-mode').style.display = 'block';
    document.getElementById('speech-input-mode').style.display = 'none';
    
    if (isRecording) {
        stopRecording();
    }
}

function switchToSpeechMode() {
    if (!recognition) {
        showNotification('Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.', 'error');
        return;
    }
    
    currentInputMode = 'speech';
    document.getElementById('text-mode-btn').classList.remove('active');
    document.getElementById('speech-mode-btn').classList.add('active');
    document.getElementById('text-input-mode').style.display = 'none';
    document.getElementById('speech-input-mode').style.display = 'block';
    
    // Show microphone permission info
    showNotification('Click "Start Recording" and allow microphone access when prompted.', 'info');
}

function startRecording() {
    if (!recognition) {
        showNotification('Speech recognition not available in this browser. Try Chrome or Edge.', 'error');
        return;
    }
    
    if (isRecording) {
        console.log('Already recording');
        return;
    }
    
    console.log('Starting recording...');
    isRecording = true;
    finalTranscript = '';  // Reset transcript for new recording
    
    // Clear previous transcript
    document.getElementById('speech-transcript').textContent = '';
    
    // Update UI
    document.getElementById('start-recording').style.display = 'none';
    document.getElementById('stop-recording').style.display = 'inline-block';
    document.getElementById('recording-status').textContent = '🎤 Initializing microphone...';
    document.getElementById('recording-status').className = 'recording-status active';
    
    try {
        recognition.start();
        console.log('Speech recognition start requested');
        showNotification('Recording started! Speak clearly into your microphone. Recording will continue until you click Stop.', 'success');
    } catch (error) {
        console.error('Error starting recognition:', error);
        if (error.message && error.message.includes('already started')) {
            console.log('Recognition already running');
            showNotification('Recording is already active!', 'info');
        } else {
            showNotification('Failed to start recording: ' + error.message, 'error');
            stopRecording();
        }
    }
}

function stopRecording() {
    console.log('Stopping recording...');
    isRecording = false;
    
    // Update UI
    document.getElementById('start-recording').style.display = 'inline-block';
    document.getElementById('stop-recording').style.display = 'none';
    document.getElementById('recording-status').textContent = '✓ Recording stopped';
    document.getElementById('recording-status').className = 'recording-status';
    
    if (recognition) {
        try {
            recognition.stop();
            console.log('Speech recognition stopped');
            
            const transcript = document.getElementById('speech-transcript').textContent;
            if (transcript.trim()) {
                showNotification('Recording stopped. Click "Send Message" to send.', 'info');
            } else {
                showNotification('Recording stopped. No speech detected.', 'warning');
            }
        } catch (error) {
            console.error('Error stopping recognition:', error);
        }
    }
}

function getCurrentInput() {
    if (currentMode === 'verbal-to-nonverbal') {
        // In verbal-to-nonverbal mode, get input from verbal teacher input
        const verbalInput = document.getElementById('verbal-teacher-input');
        return verbalInput ? verbalInput.value : '';
    } else {
        // In nonverbal-to-verbal mode, use existing logic
        if (currentInputMode === 'text') {
            return document.getElementById('student-input').value;
        } else {
            return document.getElementById('speech-transcript').textContent;
        }
    }
}

function clearCurrentInput() {
    if (currentMode === 'verbal-to-nonverbal') {
        const verbalInput = document.getElementById('verbal-teacher-input');
        if (verbalInput) {
            setTimeout(() => {
                verbalInput.value = '';
                verbalInput.focus();
            }, 500);
        }
    } else {
        if (currentInputMode === 'text') {
            setTimeout(() => {
                document.getElementById('student-input').value = '';
                document.getElementById('student-input').focus();
            }, 500);
        } else {
            finalTranscript = '';  // Clear the global transcript
            document.getElementById('speech-transcript').textContent = '';
        }
    }
}

async function checkStatus() {
    try {
        const response = await fetch(`${API_BASE}/`);
        const data = await response.json();
        document.getElementById('status-text').textContent = 'Connected';
        document.getElementById('status-indicator').style.background = '#48bb78';
        console.log('Backend connected:', data);
    } catch (error) {
        document.getElementById('status-text').textContent = 'Disconnected';
        document.getElementById('status-indicator').style.background = '#f56565';
        console.error('Backend connection error:', error);
    }
}

async function startSimulation() {
    console.log('=== START SIMULATION CLICKED ===');
    const startBtn = document.getElementById('start-sim');
    const stopBtn = document.getElementById('stop-sim');
    
    startBtn.disabled = true;
    startBtn.textContent = 'Starting...';
    
    console.log(`Before: simulationActive=${simulationActive}, sessionId=${currentSessionId}`);
    
    try {
        const response = await fetch(`${API_BASE}/simulate/start`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Simulation started:', data);
        
        currentSessionId = data.session_id;
        simulationActive = true;
        
        // Store in sessionStorage for persistence
        sessionStorage.setItem('sessionId', currentSessionId);
        sessionStorage.setItem('isActive', 'true');
        
        console.log(`After: simulationActive=${simulationActive}, sessionId=${currentSessionId}`);
        
        // Update UI
        const sessionIdElement = document.getElementById('session-id');
        sessionIdElement.textContent = `Session: ${currentSessionId.substring(0, 8)}... (Active)`;
        sessionIdElement.style.color = '#48bb78';
        sessionIdElement.style.fontWeight = 'bold';
        
        console.log('Session ID element updated:', sessionIdElement.textContent);
        
        // Hide start button, show stop button
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-block';
        
        console.log(`Buttons: start=${startBtn.style.display}, stop=${stopBtn.style.display}`);
        
        // Enable input controls
        document.getElementById('send-message').disabled = false;
        document.getElementById('student-input').disabled = false;
        document.getElementById('student-input').focus();
        
        addWorkflowItem('System', '✅ Simulation started - Ready to communicate');
        
        showNotification('Simulation is now ACTIVE! You can send messages anytime.', 'success');
        
        console.log('=== SIMULATION IS NOW ACTIVE ===');
        
        // Load conversation history if any
        loadConversationHistory(currentSessionId);
        
        // Verify state after 1 second
        setTimeout(() => {
            console.log(`State check: simulationActive=${simulationActive}, sessionId=${currentSessionId}`);
            console.log(`Start button display: ${startBtn.style.display}`);
            console.log(`Stop button display: ${stopBtn.style.display}`);
        }, 1000);
        
    } catch (error) {
        console.error('Error starting simulation:', error);
        showNotification('Failed to start simulation. Check console for details.', 'error');
        startBtn.disabled = false;
        startBtn.textContent = 'Start Simulation';
        startBtn.style.display = 'inline-block';
    }
}

function stopSimulation() {
    console.log('=== STOP SIMULATION CLICKED ===');
    const startBtn = document.getElementById('start-sim');
    const stopBtn = document.getElementById('stop-sim');
    
    if (!simulationActive) {
        console.log('No active simulation to stop');
        return;
    }
    
    console.log('Stopping simulation...');
    
    // Update state
    simulationActive = false;
    const oldSessionId = currentSessionId;
    currentSessionId = null;
    
    // Clear sessionStorage
    sessionStorage.removeItem('sessionId');
    sessionStorage.removeItem('isActive');
    
    console.log(`Session stopped: ${oldSessionId}`);
    console.log(`simulationActive = ${simulationActive}`);
    
    // Update UI
    document.getElementById('session-id').textContent = `Session: ${oldSessionId.substring(0, 8)}... (Stopped)`;
    document.getElementById('session-id').style.color = '#f56565';
    
    // Show start button, hide stop button
    stopBtn.style.display = 'none';
    startBtn.style.display = 'inline-block';
    startBtn.disabled = false;
    startBtn.textContent = 'Start Simulation';
    
    // Disable input controls
    document.getElementById('send-message').disabled = true;
    document.getElementById('student-input').disabled = true;
    document.getElementById('student-input').value = '';
    
    addWorkflowItem('System', '⏹️ Simulation stopped');
    
    showNotification('Simulation stopped. Start a new one to continue.', 'info');
    
    console.log('=== SIMULATION STOPPED ===');
}

async function sendMessage() {
    console.log('=== SEND MESSAGE CLICKED ===');
    const input = getCurrentInput();
    
    console.log('Input value:', input);
    console.log('Current mode:', currentMode);
    console.log('simulationActive:', simulationActive);
    console.log('currentSessionId:', currentSessionId);
    
    if (!input.trim()) {
        showNotification('Please enter a message or select a phrase', 'warning');
        return;
    }
    
    if (!simulationActive || !currentSessionId) {
        showNotification('Please start a simulation first', 'warning');
        return;
    }
    
    if (isProcessing) {
        showNotification('Please wait, processing previous message...', 'warning');
        return;
    }
    
    isProcessing = true;
    const sendBtn = document.getElementById('send-message');
    sendBtn.disabled = true;
    sendBtn.textContent = 'Processing...';
    
    try {
        console.log('Sending message to API:', input);
        
        if (currentMode === 'verbal-to-nonverbal') {
            // Verbal to Non-Verbal Mode: Translate to ASL
            console.log('Translating to ASL...');
            
            // Translate to ASL
            const aslTranslation = translateToASL(input);
            console.log('ASL Translation:', aslTranslation);
            
            // Save to database by sending to backend
            // We'll send the teacher's text as input and ASL as the "response"
            const requestBody = {
                session_id: currentSessionId,
                input_text: `[Teacher] ${input}`,  // Mark it as from teacher
                output_text: `[ASL] ${aslTranslation}`,  // Mark as ASL translation
                intent: 'verbal_to_nonverbal_translation',
                confidence: 1.0
            };
            
            console.log('Saving verbal-to-nonverbal message to database');
            
            try {
                // Save to database via a direct database call
                const saveResponse = await fetch(`${API_BASE}/save_message`, {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: JSON.stringify(requestBody)
                });
                
                if (saveResponse.ok) {
                    console.log('Message saved to database successfully');
                } else {
                    console.warn('Failed to save to database:', await saveResponse.text());
                }
            } catch (saveError) {
                console.error('Error saving to database:', saveError);
                // Continue anyway - message will still display locally
            }
            
            // Add teacher's verbal message to conversation
            addConversationMessage('teacher', input);
            addWorkflowItem('Teacher', `Said: "${input.substring(0, 30)}${input.length > 30 ? '...' : ''}"`);
            
            // Add ASL translation as student message
            addConversationMessage('student', aslTranslation, {
                originalText: input
            });
            
            addWorkflowItem('AI System', 'Translated to ASL gestures');
            addWorkflowItem('Non-Verbal Student', `Received: ${aslTranslation}`);
            
            showNotification('Message translated to ASL and saved!', 'success');
            
        } else {
            // Non-Verbal to Verbal Mode: Original behavior
            // Add student message to conversation
            addConversationMessage('student', input);
            
            // Show student input in workflow
            addWorkflowItem('Student', `Sent: "${input.substring(0, 30)}${input.length > 30 ? '...' : ''}"`);
            
            const requestBody = {
                session_id: currentSessionId,
                input_text: input
            };
            
            console.log('Request body:', requestBody);
            
            const response = await fetch(`${API_BASE}/simulate/step`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(requestBody)
            });
            
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Response error:', errorText);
                throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
            }
            
            const responseText = await response.text();
            console.log('Raw response text:', responseText);
            
            const data = JSON.parse(responseText);
            console.log('Parsed response data:', data);
            
            // Check if we have the expected data structure
            if (!data.communication_result) {
                console.error('Missing communication_result in response:', data);
                throw new Error('Invalid response format');
            }
            
            console.log('=== DISPLAYING RESULTS ===');
            console.log('Teacher output:', data.communication_result.output);
            
            // Add teacher message to conversation history
            console.log('Adding teacher message to conversation...');
            addConversationMessage('teacher', data.communication_result.output, {
                intent: data.communication_result.intent,
                confidence: data.communication_result.confidence
            });
            
            // Add workflow steps with delay for visibility
            if (data.simulation_steps && Array.isArray(data.simulation_steps)) {
                console.log('Adding workflow steps:', data.simulation_steps.length);
                for (let i = 0; i < data.simulation_steps.length; i++) {
                    await new Promise(resolve => setTimeout(resolve, 200));
                    const step = data.simulation_steps[i];
                    console.log('Adding step:', step);
                    addWorkflowItem(step.actor, step.action);
                }
            } else {
                console.warn('No simulation_steps in response');
            }
            
            // Show intent and confidence in workflow
            if (data.communication_result) {
                const result = data.communication_result;
                addWorkflowItem('AI System', 
                    `Detected: ${result.intent} (${(result.confidence * 100).toFixed(0)}% confidence)`
                );
            }
        }
        
        // Clear input based on mode
        clearCurrentInput();
        
        showNotification('Message processed successfully!', 'success');
        console.log('=== MESSAGE SENT SUCCESSFULLY ===');
        
    } catch (error) {
        console.error('Error sending message:', error);
        console.error('Error stack:', error.stack);
        showNotification('Failed to send message: ' + error.message, 'error');
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send Message';
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

async function loadLogs() {
    try {
        const url = currentSessionId 
            ? `${API_BASE}/logs?session_id=${currentSessionId}&limit=20`
            : `${API_BASE}/logs?limit=20`;
        
        console.log('Loading logs from:', url);
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Logs loaded:', data.logs.length);
        
        const logsDisplay = document.getElementById('logs-display');
        logsDisplay.innerHTML = '';
        
        if (data.logs.length === 0) {
            logsDisplay.innerHTML = '<div style="color: #999; padding: 10px;">No logs yet. Start sending messages!</div>';
            return;
        }
        
        data.logs.forEach(log => {
            const item = document.createElement('div');
            item.className = 'log-item';
            item.innerHTML = `
                <div><strong>${log.agent_name}</strong>: ${log.action}</div>
                <div class="timestamp">${new Date(log.created_at).toLocaleString()}</div>
            `;
            logsDisplay.appendChild(item);
        });
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

if (document.getElementById('status-text')) {
    checkStatus();
    setInterval(checkStatus, 10000);
}

if (document.getElementById('send-message')) {
    console.log('Initial state: send-message button found');
    const sendBtn = document.getElementById('send-message');
    const inputField = document.getElementById('student-input');
    console.log('Send button disabled:', sendBtn.disabled);
    console.log('Input field disabled:', inputField.disabled);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);


// ============================================
// MODE SWITCHING FEATURES
// ============================================

// Load gestures and phrases on page load
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

function setupModeSwitching() {
    const modeButtons = {
        'mode-nonverbal-to-verbal': 'nonverbal-to-verbal',
        'mode-verbal-to-nonverbal': 'verbal-to-nonverbal'
    };
    
    Object.keys(modeButtons).forEach(btnId => {
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.addEventListener('click', () => {
                currentMode = modeButtons[btnId];
                
                // Update active button
                document.querySelectorAll('.mode-selector .mode-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // IMPORTANT: We do NOT clear the conversation history when switching modes
                // The conversation display persists across mode changes
                
                // Update UI based on mode
                const simulationTitle = document.getElementById('simulation-title');
                const inputTitle = document.getElementById('input-title');
                const textInputMode = document.getElementById('text-input-mode');
                const commonPhrasesSection = document.getElementById('common-phrases-section');
                const speechInputMode = document.getElementById('speech-input-mode');
                const inputModeToggle = document.querySelector('.input-mode-toggle');
                const userRole = document.querySelector('.user-role');
                const userName = document.querySelector('.user-name');
                
                if (currentMode === 'verbal-to-nonverbal') {
                    // Verbal to Non-Verbal Mode
                    if (simulationTitle) simulationTitle.textContent = 'Verbal to Non-Verbal Communication';
                    if (inputTitle) inputTitle.textContent = 'Verbal Teacher Input';
                    if (userRole) userRole.textContent = 'Verbal Teacher';
                    if (userName) userName.textContent = 'Teacher User';
                    
                    // Hide emoji tokens and speech mode
                    if (textInputMode) textInputMode.style.display = 'none';
                    if (speechInputMode) speechInputMode.style.display = 'none';
                    if (inputModeToggle) inputModeToggle.style.display = 'none';
                    
                    // Show common phrases
                    if (commonPhrasesSection) {
                        commonPhrasesSection.style.display = 'block';
                        renderCommonPhrases();
                    }
                    
                    showNotification('Switched to Verbal → Non-Verbal mode. Output will be translated to ASL gestures.', 'info');
                } else {
                    // Non-Verbal to Verbal Mode
                    if (simulationTitle) simulationTitle.textContent = 'Non-Verbal to Verbal Communication';
                    if (inputTitle) inputTitle.textContent = 'Non-Verbal Student Input';
                    if (userRole) userRole.textContent = 'Non-Verbal Communicator';
                    if (userName) userName.textContent = 'Student User';
                    
                    // Show emoji tokens and speech toggle
                    if (textInputMode) textInputMode.style.display = 'block';
                    if (inputModeToggle) inputModeToggle.style.display = 'flex';
                    
                    // Hide common phrases
                    if (commonPhrasesSection) commonPhrasesSection.style.display = 'none';
                    
                    // Make sure speech mode is hidden by default
                    if (speechInputMode) speechInputMode.style.display = 'none';
                    
                    showNotification('Switched to Non-Verbal → Verbal mode', 'info');
                }
                
                console.log(`Mode switched to: ${currentMode}. Conversation history preserved.`);
            });
        }
    });
}

function renderCommonPhrases() {
    const container = document.getElementById('common-phrases-buttons');
    if (!container) return;
    
    container.innerHTML = '';
    
    COMMON_PHRASES.forEach(phrase => {
        const btn = document.createElement('button');
        btn.className = 'phrase-btn';
        btn.textContent = phrase;
        btn.type = 'button';
        btn.addEventListener('click', () => {
            const input = document.getElementById('verbal-teacher-input');
            if (input) {
                input.value = phrase;
                input.focus();
            }
        });
        container.appendChild(btn);
    });
}

function translateToASL(text) {
    if (!text || !text.trim()) return '';
    
    const lowerText = text.toLowerCase();
    let aslOutput = [];
    
    // Try to match phrases first (longer matches first)
    const sortedPhrases = Object.keys(ASL_MAPPINGS).sort((a, b) => b.length - a.length);
    
    let remainingText = lowerText;
    let matched = true;
    
    while (matched && remainingText.length > 0) {
        matched = false;
        remainingText = remainingText.trim();
        
        for (const phrase of sortedPhrases) {
            if (remainingText.startsWith(phrase)) {
                aslOutput.push(ASL_MAPPINGS[phrase]);
                remainingText = remainingText.substring(phrase.length);
                matched = true;
                break;
            }
        }
        
        // If no match found, skip one word
        if (!matched && remainingText.length > 0) {
            const nextSpace = remainingText.indexOf(' ');
            if (nextSpace > 0) {
                remainingText = remainingText.substring(nextSpace + 1);
                matched = true;
            } else {
                break;
            }
        }
    }
    
    // If we got some translations, return them
    if (aslOutput.length > 0) {
        return aslOutput.join(' ');
    }
    
    // Fallback: try word by word
    const words = lowerText.split(/\s+/);
    const translations = [];
    
    for (const word of words) {
        const cleanWord = word.replace(/[.,!?;:]/g, '');
        if (ASL_MAPPINGS[cleanWord]) {
            translations.push(ASL_MAPPINGS[cleanWord]);
        }
    }
    
    return translations.length > 0 ? translations.join(' ') : '🤷 (No direct ASL translation available)';
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
        // Add to conversation history immediately
        addConversationMessage('student', input);
        
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
        
        // Add teacher response to conversation history
        addConversationMessage('teacher', data.communication_result.output, {
            intent: data.communication_result.intent,
            confidence: data.communication_result.confidence
        });
        
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
        
        // Add verbal user's text message to conversation history (as teacher/verbal user)
        addConversationMessage('teacher', text, {
            method: `Translated to: ${data.gesture_sequence}`
        });
        
        // Add gesture translation as non-verbal user's view (as student)
        addConversationMessage('student', data.gesture_sequence, {
            originalText: text,
            translationMethod: data.method
        });
        
        // Clear input
        document.getElementById('verbal-input').value = '';
        
        showNotification('Message translated and sent!', 'success');
    } catch (error) {
        console.error('Error sending verbal message:', error);
        showNotification('Failed to translate message', 'error');
    }
}

// Initialize mode switching when page loads
window.addEventListener('DOMContentLoaded', async () => {
    // Setup mode switching
    setupModeSwitching();
    
    // Render common phrases (hidden by default)
    renderCommonPhrases();
});


// ===== WEBCAM GESTURE RECOGNITION =====

// Webcam variables
let webcamStream = null;
let isCapturing = false;
let captureInterval = null;

// Start webcam
async function startWebcam() {
    try {
        const video = document.getElementById('webcam');
        
        // Request webcam access
        webcamStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 }
            }
        });
        
        video.srcObject = webcamStream;
        
        // Update UI
        document.getElementById('startWebcamBtn').style.display = 'none';
        document.getElementById('stopWebcamBtn').style.display = 'inline-block';
        document.getElementById('captureBtn').style.display = 'inline-block';
        
        // Start automatic gesture detection
        startGestureDetection();
        
        console.log('Webcam started');
    } catch (error) {
        console.error('Error accessing webcam:', error);
        alert('Could not access webcam. Please check permissions.');
    }
}

// Stop webcam
function stopWebcam() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }
    
    stopGestureDetection();
    
    const video = document.getElementById('webcam');
    video.srcObject = null;
    
    // Update UI
    document.getElementById('startWebcamBtn').style.display = 'inline-block';
    document.getElementById('stopWebcamBtn').style.display = 'none';
    document.getElementById('captureBtn').style.display = 'none';
    document.getElementById('detectedGesture').textContent = 'No gestures detected';
    
    console.log('Webcam stopped');
}

// Start automatic gesture detection
function startGestureDetection() {
    isCapturing = true;
    
    // Capture and process frames every 500ms
    captureInterval = setInterval(() => {
        if (isCapturing) {
            processCurrentFrame();
        }
    }, 500);
}

// Stop gesture detection
function stopGestureDetection() {
    isCapturing = false;
    if (captureInterval) {
        clearInterval(captureInterval);
        captureInterval = null;
    }
}

// Process current webcam frame
async function processCurrentFrame() {
    try {
        const video = document.getElementById('webcam');
        const canvas = document.getElementById('canvas');
        const context = canvas.getContext('2d');
        
        // Set canvas size to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Draw current frame to canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert to base64
        const frameData = canvas.toDataURL('image/jpeg', 0.8);
        
        // Send to backend for processing
        const response = await fetch(`${API_BASE}/vision/process-frame`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                frame: frameData,
                session_id: currentSessionId
            })
        });
        
        const result = await response.json();
        
        // Update UI with detected gestures
        updateGestureDisplay(result);
        
    } catch (error) {
        console.error('Error processing frame:', error);
    }
}

// Update gesture display and populate input field
function updateGestureDisplay(result) {
    const overlay = document.getElementById('detectedGesture');
    
    if (result.error) {
        overlay.innerHTML = `<div style="color: #f56565;">⚠️ ${result.error}</div>`;
        return;
    }
    
    if (result.hands_detected > 0 && result.gestures.length > 0) {
        const gestureText = result.gestures.map(g => 
            `${g.gesture} (${(g.confidence * 100).toFixed(0)}%)`
        ).join(', ');
        
        const emojiText = result.emojis.join(' ');
        
        overlay.innerHTML = `
            <div>👋 Detected: ${gestureText}</div>
            <div>📝 Emojis: ${emojiText}</div>
        `;
        
        // AUTO-POPULATE INPUT FIELD (like speech-to-text)
        // Get the appropriate input field based on current mode
        const studentInput = document.getElementById('student-input');
        const verbalInput = document.getElementById('verbal-teacher-input');
        
        if (currentMode === 'nonverbal-to-verbal' && studentInput) {
            // Add emojis to student input (non-verbal user)
            const currentText = studentInput.value.trim();
            if (currentText) {
                studentInput.value = currentText + ' ' + emojiText;
            } else {
                studentInput.value = emojiText;
            }
            
            // Visual feedback
            studentInput.style.backgroundColor = '#e6ffed';
            setTimeout(() => {
                studentInput.style.backgroundColor = '';
            }, 300);
            
            console.log('✅ Gesture added to input:', emojiText);
        } else if (currentMode === 'verbal-to-nonverbal' && verbalInput) {
            // In verbal-to-nonverbal mode, gestures could be used as feedback
            // For now, just show in overlay
            console.log('Gesture detected in verbal-to-nonverbal mode:', emojiText);
        }
    } else {
        overlay.textContent = 'No gestures detected';
    }
}

// Capture gesture and send to AI
async function captureGesture() {
    try {
        const video = document.getElementById('webcam');
        const canvas = document.getElementById('canvas');
        const context = canvas.getContext('2d');
        
        // Set canvas size
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Capture frame
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const frameData = canvas.toDataURL('image/jpeg', 0.8);
        
        // Show loading
        showNotification('Processing gesture...', 'info');
        
        // Send to backend for full processing
        const response = await fetch(`${API_BASE}/vision/gesture-to-text`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                frame: frameData,
                session_id: currentSessionId
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Display detected gesture
            const gestureText = result.detected_gestures.map(g => g.gesture).join(', ');
            const emojiText = result.emojis.join(' ');
            
            // Add to input field
            const studentInput = document.getElementById('student-input');
            if (studentInput) {
                const currentText = studentInput.value.trim();
                if (currentText) {
                    studentInput.value = currentText + ' ' + emojiText;
                } else {
                    studentInput.value = emojiText;
                }
            }
            
            showNotification(`Gesture detected: ${gestureText} → ${emojiText}`, 'success');
        } else {
            showNotification('No gesture detected. Please try again.', 'warning');
        }
        
    } catch (error) {
        console.error('Error capturing gesture:', error);
        showNotification('Error processing gesture', 'error');
    }
}

// Clear gesture input
function clearGestureInput() {
    const studentInput = document.getElementById('student-input');
    const verbalInput = document.getElementById('verbal-teacher-input');
    
    if (currentMode === 'nonverbal-to-verbal' && studentInput) {
        studentInput.value = '';
        showNotification('Input cleared', 'info');
    } else if (currentMode === 'verbal-to-nonverbal' && verbalInput) {
        verbalInput.value = '';
        showNotification('Input cleared', 'info');
    }
}

// Toggle webcam section visibility
function toggleWebcam() {
    const section = document.getElementById('webcamSection');
    if (section.style.display === 'none') {
        section.style.display = 'block';
    } else {
        section.style.display = 'none';
        stopWebcam();
    }
}

// Add webcam mode button handler
document.addEventListener('DOMContentLoaded', function() {
    const webcamModeBtn = document.getElementById('webcam-mode-btn');
    if (webcamModeBtn) {
        webcamModeBtn.addEventListener('click', function() {
            // Hide other input modes
            document.getElementById('text-input-mode').style.display = 'none';
            document.getElementById('speech-input-mode').style.display = 'none';
            document.getElementById('webcamSection').style.display = 'block';
            
            // Update button states
            document.getElementById('text-mode-btn').classList.remove('active');
            document.getElementById('speech-mode-btn').classList.remove('active');
            document.getElementById('webcam-mode-btn').classList.add('active');
        });
    }
    
    // Update text mode button to hide webcam
    const textModeBtn = document.getElementById('text-mode-btn');
    if (textModeBtn) {
        textModeBtn.addEventListener('click', function() {
            document.getElementById('text-input-mode').style.display = 'block';
            document.getElementById('speech-input-mode').style.display = 'none';
            document.getElementById('webcamSection').style.display = 'none';
            stopWebcam();
            
            document.getElementById('text-mode-btn').classList.add('active');
            document.getElementById('speech-mode-btn').classList.remove('active');
            document.getElementById('webcam-mode-btn').classList.remove('active');
        });
    }
    
    // Update speech mode button to hide webcam
    const speechModeBtn = document.getElementById('speech-mode-btn');
    if (speechModeBtn) {
        speechModeBtn.addEventListener('click', function() {
            document.getElementById('text-input-mode').style.display = 'none';
            document.getElementById('speech-input-mode').style.display = 'block';
            document.getElementById('webcamSection').style.display = 'none';
            stopWebcam();
            
            document.getElementById('text-mode-btn').classList.remove('active');
            document.getElementById('speech-mode-btn').classList.add('active');
            document.getElementById('webcam-mode-btn').classList.remove('active');
        });
    }
});
