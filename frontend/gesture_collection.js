(function (root, factory) {
    const api = factory();
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
    if (root) {
        root.GestureRecording = api.GestureRecording;
    }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    const MIN_DYNAMIC_OBSERVATIONS = 5;

    function createSampleId() {
        if (globalThis.crypto && typeof globalThis.crypto.randomUUID === 'function') {
            return globalThis.crypto.randomUUID();
        }
        return `sample-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    }

    class GestureRecording {
        constructor(context, sampleIdFactory = createSampleId) {
            this.context = { ...context };
            this.sampleIdFactory = sampleIdFactory;
            this.observations = [];
            this.stopped = false;
            this.discarded = false;
        }

        addObservation(observation) {
            if (this.stopped || this.discarded) {
                throw new Error('Cannot add observations to a stopped recording');
            }
            if (
                !observation ||
                observation.hand_side !== this.context.handSide ||
                !Array.isArray(observation.landmarks) ||
                observation.landmarks.length !== 21
            ) {
                return false;
            }
            this.observations.push({
                timestamp: observation.timestamp,
                timestamp_ms: observation.timestamp_ms,
                handedness_confidence: observation.handedness_confidence,
                landmarks: observation.landmarks,
            });
            return true;
        }

        stop() {
            this.stopped = true;
        }

        get observationCount() {
            return this.observations.length;
        }

        get sampleCount() {
            if (this.context.sampleType === 'dynamic') {
                return this.observations.length >= MIN_DYNAMIC_OBSERVATIONS ? 1 : 0;
            }
            return this.observations.length;
        }

        toRecords() {
            if (!this.stopped) {
                throw new Error('Stop the recording before saving it');
            }
            if (this.discarded) {
                return [];
            }
            if (!this.observations.length) {
                throw new Error('No matching hand observations were captured');
            }

            const common = {
                dataset_version: this.context.datasetVersion,
                participant_id: this.context.participantId,
                recording_session_id: this.context.recordingSessionId,
                gesture_label: this.context.gestureLabel,
                hand_side: this.context.handSide,
                feature_version: this.context.featureVersion,
                sample_type: this.context.sampleType,
            };

            if (this.context.sampleType === 'dynamic') {
                if (this.observations.length < MIN_DYNAMIC_OBSERVATIONS) {
                    throw new Error(
                        `Dynamic recordings require at least ${MIN_DYNAMIC_OBSERVATIONS} observations`
                    );
                }
                return [{
                    ...common,
                    sample_id: this.sampleIdFactory(),
                    timestamp: this.observations[0].timestamp,
                    landmarks: this.observations.map((observation) => ({ ...observation })),
                }];
            }

            return this.observations.map((observation) => ({
                ...common,
                sample_id: this.sampleIdFactory(),
                timestamp: observation.timestamp,
                handedness_confidence: observation.handedness_confidence,
                landmarks: observation.landmarks,
            }));
        }

        discard() {
            this.discarded = true;
            this.stopped = true;
            this.observations = [];
        }
    }

    return { GestureRecording, MIN_DYNAMIC_OBSERVATIONS };
}));
