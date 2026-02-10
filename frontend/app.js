const API_BASE = 'http://localhost:8000';

let currentSessionId = null;
let isProcessing = false;
let simulationActive = false;
let currentInputMode = 'text'; // 'text' or 'speech'
let recognition = null;
let isRecording = false;
let finalTranscript = '';  // Track transcript across recognition restarts

// Bidirectional communication variables
let currentMode = 'nonverbal-to-verbal';
let gestures = {};
let commonPhrases = {};

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
        item.innerHTML = `
            <div class="message-student">
                <div class="message-bubble">${message}</div>
            </div>
            <div class="message-meta" style="text-align: right;">You • ${new Date().toLocaleTimeString()}</div>
        `;
    } else if (type === 'teacher') {
        const intent = metadata.intent ? ` • ${metadata.intent}` : '';
        const confidence = metadata.confidence ? ` (${(metadata.confidence * 100).toFixed(0)}%)` : '';
        item.innerHTML = `
            <div class="message-teacher">
                <div class="message-bubble">${message}</div>
            </div>
            <div class="message-meta" style="text-align: left;">Teacher • ${new Date().toLocaleTimeString()}${intent}${confidence}</div>
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
    console.log('Loading conversation history for session:', sessionId);
    
    try {
        const response = await fetch(`${API_BASE}/session/${sessionId}`);
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
        
        // Clear and rebuild conversation
        conversationDisplay.innerHTML = '';
        
        if (data.messages && data.messages.length > 0) {
            // Messages are returned newest first, so reverse them
            const messages = data.messages.reverse();
            
            messages.forEach(msg => {
                // Add student message
                addConversationMessage('student', msg.input_text);
                
                // Add teacher response
                addConversationMessage('teacher', msg.output_text, {
                    intent: msg.intent
                });
            });
            
            console.log(`Loaded ${messages.length} conversation pairs`);
        } else {
            conversationDisplay.innerHTML = '<div style="padding: 15px; color: #999; text-align: center;">No messages yet. Start the conversation!</div>';
        }
        
    } catch (error) {
        console.error('Error loading conversation history:', error);
    }
}

// Restore session on page load
window.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded');
    
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
    if (currentInputMode === 'text') {
        return document.getElementById('student-input').value;
    } else {
        return document.getElementById('speech-transcript').textContent;
    }
}

function clearCurrentInput() {
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
            headers: {
                'Content-Type': 'application/json'
            }
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
    console.log('simulationActive:', simulationActive);
    console.log('currentSessionId:', currentSessionId);
    
    if (!input.trim()) {
        showNotification('Please enter a message or select a token', 'warning');
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
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
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
// BIDIRECTIONAL COMMUNICATION FEATURES
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
                const bidirectionalView = document.getElementById('bidirectional-view');
                const singleDirectionView = document.getElementById('single-direction-view');
                
                if (currentMode === 'bidirectional' || currentMode === 'verbal-to-nonverbal') {
                    bidirectionalView.style.display = 'block';
                    singleDirectionView.style.display = 'none';
                } else {
                    bidirectionalView.style.display = 'none';
                    singleDirectionView.style.display = 'block';
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
        if (verbalReceived) {
            verbalReceived.innerHTML = `
                <div style="background: #edf2f7; padding: 15px; border-radius: 8px; margin-top: 10px;">
                    <div style="font-size: 24px; margin-bottom: 10px;">${input}</div>
                    <div style="color: #2d3748; font-size: 16px;">${data.communication_result.output}</div>
                    <div style="color: #718096; font-size: 12px; margin-top: 8px;">
                        Intent: ${data.communication_result.intent} (${(data.communication_result.confidence * 100).toFixed(0)}%)
                    </div>
                </div>
            `;
        }
        
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
        if (gestureOutput) {
            gestureOutput.className = 'gesture-display';
            gestureOutput.textContent = data.gesture_sequence;
        }
        
        const translationInfo = document.getElementById('translation-info');
        if (translationInfo) {
            translationInfo.textContent = `Translation method: ${data.method} - ${data.explanation}`;
        }
        
        // Display in non-verbal user's received area
        const nonverbalReceived = document.getElementById('nonverbal-received');
        if (nonverbalReceived) {
            nonverbalReceived.className = 'gesture-display';
            nonverbalReceived.innerHTML = `
                <div style="font-size: 32px; margin-bottom: 10px;">${data.gesture_sequence}</div>
                <div style="font-size: 14px; color: #718096;">"${text}"</div>
            `;
        }
        
        // Clear input
        document.getElementById('verbal-input').value = '';
        
        showNotification('Message translated and sent!', 'success');
    } catch (error) {
        console.error('Error sending verbal message:', error);
        showNotification('Failed to translate message', 'error');
    }
}

// Initialize bidirectional features when page loads
window.addEventListener('DOMContentLoaded', async () => {
    // Load gestures and phrases
    await loadGestures();
    await loadPhrases();
    
    // Setup mode switching
    setupModeSwitching();
    
    // Setup bidirectional controls
    setupBidirectionalControls();
    
    // Initialize gesture palette and phrases
    renderGesturePalette();
    renderPhrasesLibrary();
});
