(() => {
    const API_BASE =
        window.API_BASE ||
        localStorage.getItem('apiBaseUrl') ||
        (window.location.origin || 'http://localhost:8000');
    const token = () => localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    const headers = () => ({
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...(token() ? { Authorization: `Bearer ${token()}` } : {}),
    });

    const video = document.getElementById('camera');
    const canvas = document.getElementById('frame');
    const participantInput = document.getElementById('participant-id');
    const labelSelect = document.getElementById('gesture-label');
    const handSelect = document.getElementById('hand-side');
    const startButton = document.getElementById('start-recording');
    const stopButton = document.getElementById('stop-recording');
    const saveButton = document.getElementById('save-recording');
    const discardButton = document.getElementById('discard-recording');
    const stopCameraButton = document.getElementById('stop-camera');
    const sampleCount = document.getElementById('sample-count');
    const status = document.getElementById('status');
    const sampleTypeText = document.getElementById('sample-type');
    const controls = [participantInput, labelSelect, handSelect];
    let config = null;
    let cameraStream = null;
    let recording = null;
    let isRecording = false;
    let context = null;

    function setStatus(message) {
        status.textContent = message;
    }

    function setRecordingControls(active) {
        controls.forEach((control) => { control.disabled = active; });
        startButton.disabled = active;
        stopButton.disabled = !active;
        stopCameraButton.disabled = active;
        updateRecordingSummary();
    }

    function updateRecordingSummary() {
        const observations = recording ? recording.observationCount : 0;
        const samples = recording ? recording.sampleCount : 0;
        sampleCount.textContent = `Captured samples: ${samples} (${observations} observations)`;
        saveButton.disabled = isRecording || !recording || samples === 0;
        discardButton.disabled = isRecording || !recording || observations === 0;
    }

    function selectedSampleType() {
        return config.dynamic_labels.includes(labelSelect.value) ? 'dynamic' : 'static';
    }

    function updateLabelDescription() {
        if (!config || !labelSelect.value) {
            return;
        }
        sampleTypeText.textContent = selectedSampleType() === 'dynamic'
            ? `Dynamic sequence: collect at least ${config.minimum_dynamic_observations} consecutive observations.`
            : 'Static pose: each captured frame becomes one labelled sample.';
    }

    async function authenticatedFetch(url, options = {}) {
        const response = await fetch(url, {
            ...options,
            headers: { ...headers(), ...(options.headers || {}) },
        });
        if (response.status === 401) {
            localStorage.removeItem('authToken');
            sessionStorage.removeItem('authToken');
            window.location.href = 'login.html';
            throw new Error('Authentication expired; sign in again.');
        }
        return response;
    }

    async function loadConfig() {
        if (!token()) {
            window.location.href = 'login.html';
            return;
        }
        const authResponse = await authenticatedFetch(`${API_BASE}/auth/me`);
        if (!authResponse.ok) {
            throw new Error('You must sign in as an authorised collector.');
        }
        const response = await authenticatedFetch(`${API_BASE}/vision/collection-config`);
        const result = await response.json();
        if (!response.ok) {
            throw new Error(
                result.detail || `Could not load collection settings (HTTP ${response.status}).`
            );
        }
        config = result;
        labelSelect.replaceChildren(...config.gesture_labels.map((label) => {
            const option = document.createElement('option');
            option.value = label;
            option.textContent = label;
            return option;
        }));
        updateLabelDescription();
    }

    async function ensureCamera() {
        if (cameraStream) {
            return;
        }
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('This browser does not support webcam capture.');
        }
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'user' },
            audio: false,
        });
        video.srcObject = cameraStream;
        await video.play();
    }

    function createId() {
        if (window.crypto && typeof window.crypto.randomUUID === 'function') {
            return window.crypto.randomUUID();
        }
        return `recording-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    }

    function startRecording() {
        const participantId = participantInput.value.trim();
        if (!participantInput.reportValidity() || !participantId) {
            return;
        }
        const sampleType = selectedSampleType();
        recording = new window.GestureRecording({
            participantId,
            recordingSessionId: createId(),
            gestureLabel: labelSelect.value,
            handSide: handSelect.value,
            sampleType,
            featureVersion: config.feature_version,
            datasetVersion: config.dataset_version,
        });
        isRecording = true;
        setRecordingControls(true);
        setStatus('Recording landmark observations. The classifier is not assigning labels.');
        captureLoop();
    }

    async function captureLoop() {
        context = canvas.getContext('2d');
        while (isRecording) {
            try {
                if (!video.videoWidth || !video.videoHeight) {
                    await new Promise((resolve) => window.setTimeout(resolve, 120));
                    continue;
                }
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
                const timestampMs = window.performance.now();
                const response = await authenticatedFetch(`${API_BASE}/vision/collect-frame`, {
                    method: 'POST',
                    body: JSON.stringify({
                        frame: canvas.toDataURL('image/jpeg', 0.85),
                        frame_timestamp_ms: timestampMs,
                    }),
                });
                const result = await response.json();
                if (!response.ok) {
                    throw new Error(result.detail || `Landmark extraction failed (HTTP ${response.status}).`);
                }
                if (result.error) {
                    throw new Error(result.error);
                }
                if (!isRecording) {
                    break;
                }

                const matches = (result.observations || [])
                    .filter((observation) => observation.hand_side === handSelect.value);
                if (matches.length === 1) {
                    recording.addObservation(matches[0]);
                    updateRecordingSummary();
                } else if (matches.length > 1) {
                    setStatus('Ambiguous handedness result; frame skipped to avoid merging hands.');
                }
                await new Promise((resolve) => window.setTimeout(resolve, 120));
            } catch (error) {
                if (isRecording) {
                    isRecording = false;
                    recording.stop();
                    setRecordingControls(false);
                    setStatus(error.message || 'Landmark capture failed.');
                }
            }
        }
    }

    function stopRecording() {
        if (!recording || !isRecording) {
            return;
        }
        isRecording = false;
        recording.stop();
        setRecordingControls(false);
        if (!recording.observationCount) {
            setStatus('No matching hand observations were captured. Adjust the hand or selected side and try again.');
        } else {
            setStatus(`Recording stopped: ${recording.observationCount} observations are ready to review.`);
        }
    }

    async function saveRecording() {
        if (!recording || isRecording) {
            return;
        }
        try {
            const records = recording.toRecords();
            saveButton.disabled = true;
            const response = await authenticatedFetch(`${API_BASE}/vision/dataset/recordings`, {
                method: 'POST',
                body: JSON.stringify({ records }),
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.detail || `Dataset save failed (HTTP ${response.status}).`);
            }
            setStatus(`Saved ${result.saved_count} ${result.saved_count === 1 ? 'sample' : 'samples'} to the dataset.`);
            recording = null;
            updateRecordingSummary();
        } catch (error) {
            setStatus(error.message || 'Could not save this recording.');
            updateRecordingSummary();
        }
    }

    function discardRecording() {
        if (!recording || isRecording) {
            return;
        }
        recording.discard();
        recording = null;
        updateRecordingSummary();
        setStatus('Recording discarded; no samples were saved.');
    }

    function stopCamera() {
        if (cameraStream) {
            cameraStream.getTracks().forEach((track) => track.stop());
            cameraStream = null;
            video.srcObject = null;
        }
    }

    labelSelect.addEventListener('change', updateLabelDescription);
    startButton.addEventListener('click', async () => {
        try {
            await ensureCamera();
            startRecording();
        } catch (error) {
            setStatus(error.message || 'Could not start webcam.');
        }
    });
    stopButton.addEventListener('click', stopRecording);
    saveButton.addEventListener('click', saveRecording);
    discardButton.addEventListener('click', discardRecording);
    stopCameraButton.addEventListener('click', () => {
        if (isRecording) {
            stopRecording();
        }
        stopCamera();
    });
    window.addEventListener('beforeunload', stopCamera);

    loadConfig().catch((error) => {
        setStatus(error.message || 'Could not initialize the collection page.');
        startButton.disabled = true;
    });
})();
