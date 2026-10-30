(function (root, factory) {
    const api = factory();
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
    if (root) {
        root.GestureSubmissionState = api.GestureSubmissionState;
    }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    class GestureSubmissionState {
        constructor(stableThreshold = 2, confidenceThreshold = 0.55) {
            this.stableThreshold = stableThreshold;
            this.confidenceThreshold = confidenceThreshold;
            this.lastAcceptedGesture = null;
            this.lastObservedGesture = null;
            this.consecutiveMatches = 0;
            this.processing = false;
            this.generation = 0;
        }

        observe(result) {
            if (result && result.error) {
                this.resetStability();
                return { accepted: false, gestureNames: [] };
            }

            const gestures = result && Array.isArray(result.gestures) ? result.gestures : [];
            const gestureNames = gestures
                .map((gesture) => typeof gesture?.gesture === 'string' ? gesture.gesture.trim() : '')
                .filter(Boolean);

            if (result && result.hands_detected === 0) {
                this.recordNeutral();
                return { accepted: false, gestureNames: [], neutral: true };
            }

            if (
                !gestureNames.length ||
                !result ||
                typeof result.confidence !== 'number' ||
                !Number.isFinite(result.confidence) ||
                result.confidence < this.confidenceThreshold ||
                gestures.some((gesture) =>
                    typeof gesture.confidence !== 'number' ||
                    !Number.isFinite(gesture.confidence) ||
                    gesture.confidence < this.confidenceThreshold ||
                    gesture.confidence > 1
                )
            ) {
                this.resetStability();
                return { accepted: false, gestureNames };
            }

            const currentGesture = gestureNames.join(',');
            if (this.lastObservedGesture !== currentGesture) {
                this.lastObservedGesture = currentGesture;
                this.consecutiveMatches = 1;
            } else {
                this.consecutiveMatches += 1;
            }

            return {
                accepted:
                    this.consecutiveMatches >= this.stableThreshold &&
                    this.lastAcceptedGesture !== currentGesture,
                gestureNames,
            };
        }

        beginSubmission(gestureNames) {
            const gestureKey = gestureNames.join(',');
            if (this.processing || this.lastAcceptedGesture === gestureKey) {
                return false;
            }

            this.lastAcceptedGesture = gestureKey;
            this.processing = true;
            return true;
        }

        async submit(gestureNames, action) {
            if (!this.beginSubmission(gestureNames)) {
                return false;
            }

            try {
                await action();
                return true;
            } finally {
                this.finishSubmission();
            }
        }

        finishSubmission() {
            this.processing = false;
        }

        recordNeutral() {
            this.lastAcceptedGesture = null;
            this.resetStability();
        }

        startDetection() {
            this.generation += 1;
            this.recordNeutral();
            return this.generation;
        }

        stopDetection() {
            this.generation += 1;
            this.recordNeutral();
            return this.generation;
        }

        isCurrentGeneration(generation) {
            return generation === this.generation;
        }

        handleFrameResult(generation, result, handler) {
            if (!this.isCurrentGeneration(generation)) {
                return false;
            }

            handler(result);
            return true;
        }

        resetStability() {
            this.lastObservedGesture = null;
            this.consecutiveMatches = 0;
        }

        reset() {
            this.recordNeutral();
        }
    }

    return { GestureSubmissionState };
}));
