(function (root, factory) {
    const api = factory();
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
    if (root) {
        root.GestureSubmissionState = api.GestureSubmissionState;
        root.isVideoFrameReady = api.isVideoFrameReady;
        root.isFrameDataValid = api.isFrameDataValid;
        root.getGestureDiagnosticDetails = api.getGestureDiagnosticDetails;
    }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    function isVideoFrameReady(video, minimumReadyState = 2) {
        return Boolean(
            video &&
            typeof video.readyState === 'number' &&
            video.readyState >= minimumReadyState &&
            Number.isFinite(video.videoWidth) &&
            video.videoWidth > 0 &&
            Number.isFinite(video.videoHeight) &&
            video.videoHeight > 0
        );
    }

    function isFrameDataValid(frameData) {
        if (typeof frameData !== 'string') {
            return false;
        }

        const prefix = 'data:image/jpeg;base64,';
        if (!frameData.startsWith(prefix)) {
            return false;
        }

        const payload = frameData.slice(prefix.length);
        return payload.length > 0 &&
            payload.length % 4 === 0 &&
            /^[A-Za-z0-9+/]+={0,2}$/.test(payload);
    }

    function getGestureDiagnosticDetails(result) {
        const gestures = result && Array.isArray(result.gestures) ? result.gestures : [];
        return {
            handsDetected: result && Number.isFinite(result.hands_detected)
                ? result.hands_detected
                : null,
            detectedHands: gestures.map((gesture) => ({
                hand: gesture && typeof gesture.hand === 'string' ? gesture.hand : null,
                gesture: gesture && typeof gesture.gesture === 'string' ? gesture.gesture : null,
                confidence: gesture && Number.isFinite(gesture.confidence)
                    ? gesture.confidence
                    : null,
                movement_direction: gesture && typeof gesture.movement_direction === 'string'
                    ? gesture.movement_direction
                    : null,
                movement_displacement: gesture && Number.isFinite(gesture.movement_displacement)
                    ? gesture.movement_displacement
                    : null,
                movement_velocity: gesture && Number.isFinite(gesture.movement_velocity)
                    ? gesture.movement_velocity
                    : null,
                wrist_movement_direction: gesture && typeof gesture.wrist_movement_direction === 'string'
                    ? gesture.wrist_movement_direction
                    : null,
                wrist_movement_displacement: gesture && Number.isFinite(gesture.wrist_movement_displacement)
                    ? gesture.wrist_movement_displacement
                    : null,
                wrist_movement_velocity: gesture && Number.isFinite(gesture.wrist_movement_velocity)
                    ? gesture.wrist_movement_velocity
                    : null,
                dynamic_gesture_confidence: gesture && Number.isFinite(gesture.dynamic_gesture_confidence)
                    ? gesture.dynamic_gesture_confidence
                    : null,
            })),
        };
    }

    class GestureSubmissionState {
        constructor(stableThreshold = 2, confidenceThreshold = 0.55) {
            this.stableThreshold = stableThreshold;
            this.confidenceThreshold = confidenceThreshold;
            this.lastSuccessfullySubmittedGestureKey = null;
            this.lastStableGestureKey = null;
            this.lastObservedGesture = null;
            this.consecutiveMatches = 0;
            this.transitionSequence = 0;
            this.handledTransitions = new Set();
            this.processing = false;
            this.processingGeneration = null;
            this.inFlightGestureKey = null;
            this.inFlightTransitionId = null;
            this.pendingSubmissions = [];
            this.frameProcessing = false;
            this.frameProcessingGeneration = null;
            this.generation = 0;
            this.detectionActive = false;
        }

        observe(result) {
            if (result && result.error) {
                this.resetStability();
                return {
                    accepted: false,
                    gestureNames: [],
                    reason: 'invalid-frame',
                };
            }

            const gestures = result && Array.isArray(result.gestures) ? result.gestures : [];
            const gestureNames = gestures
                .map((gesture) => typeof gesture?.gesture === 'string' ? gesture.gesture.trim() : '')
                .filter(Boolean);

            if (result && result.hands_detected === 0 && Array.isArray(result.gestures) && result.gestures.length === 0) {
                this.resetStability();
                return {
                    accepted: false,
                    gestureNames: [],
                    noHand: true,
                    reason: 'no-hand-detection',
                };
            }

            if (result && typeof result.hands_detected === 'number' && result.hands_detected > 0) {
                // Continue with validated gesture data below.
            } else {
                this.resetStability();
                return {
                    accepted: false,
                    gestureNames,
                    reason: 'invalid-frame',
                };
            }

            if (
                !gestureNames.length ||
                !result ||
                typeof result.confidence !== 'number' ||
                !Number.isFinite(result.confidence) ||
                result.confidence < this.confidenceThreshold ||
                gestureNames.length !== gestures.length ||
                gestures.some((gesture) =>
                    !gesture ||
                    typeof gesture !== 'object' ||
                    typeof gesture.gesture !== 'string' ||
                    !gesture.gesture.trim() ||
                    typeof gesture.confidence !== 'number' ||
                    !Number.isFinite(gesture.confidence) ||
                    gesture.confidence < this.confidenceThreshold ||
                    gesture.confidence > 1
                )
            ) {
                this.resetStability();
                return {
                    accepted: false,
                    gestureNames,
                    reason: 'invalid-frame',
                };
            }

            const currentGesture = gestureNames.join(',');
            if (this.lastObservedGesture !== currentGesture) {
                this.lastObservedGesture = currentGesture;
                this.consecutiveMatches = 1;
            } else {
                this.consecutiveMatches += 1;
            }

            const stable = this.consecutiveMatches >= this.stableThreshold;
            const isNewTransition = stable && currentGesture !== this.lastStableGestureKey;
            if (isNewTransition) {
                this.lastStableGestureKey = currentGesture;
                this.transitionSequence += 1;
            }

            return {
                accepted: isNewTransition,
                gestureNames,
                transitionId: isNewTransition ? this.transitionSequence : null,
                reason: isNewTransition
                    ? 'gesture-transition'
                    : stable
                        ? 'gesture-already-observed'
                        : 'awaiting-stability',
            };
        }

        beginFrameRequest(generation = this.generation) {
            if (this.frameProcessing && this.frameProcessingGeneration === generation) {
                return false;
            }

            this.frameProcessing = true;
            this.frameProcessingGeneration = generation;
            return true;
        }

        finishFrameRequest(generation = this.frameProcessingGeneration) {
            if (this.frameProcessingGeneration === generation) {
                this.frameProcessing = false;
                this.frameProcessingGeneration = null;
            }
        }

        beginSubmission(gestureNames, generation = this.generation, transitionId = null) {
            const gestureKey = gestureNames.join(',');
            if (this.processing || !this.isCurrentGeneration(generation)) {
                return false;
            }

            this.processing = true;
            this.processingGeneration = generation;
            this.inFlightGestureKey = gestureKey;
            this.inFlightTransitionId = transitionId;
            return true;
        }

        submit(gestureNames, action, generation = this.generation, transitionId = null) {
            if (!this.isCurrentGeneration(generation)) {
                return Promise.resolve(false);
            }

            const resolvedTransitionId = transitionId ?? ++this.transitionSequence;
            if (this.handledTransitions.has(resolvedTransitionId)) {
                return Promise.resolve(false);
            }
            this.handledTransitions.add(resolvedTransitionId);

            return new Promise((resolve, reject) => {
                this.pendingSubmissions.push({
                    gestureNames,
                    action,
                    generation,
                    transitionId: resolvedTransitionId,
                    resolve,
                    reject,
                });
                this.drainSubmissions();
            });
        }

        drainSubmissions() {
            if (this.processing) {
                return;
            }

            while (this.pendingSubmissions.length > 0) {
                const submission = this.pendingSubmissions.shift();
                if (!this.isCurrentGeneration(submission.generation)) {
                    submission.resolve(false);
                    continue;
                }
                if (!this.beginSubmission(
                    submission.gestureNames,
                    submission.generation,
                    submission.transitionId
                )) {
                    submission.resolve(false);
                    continue;
                }

                this.runSubmission(submission);
                return;
            }
        }

        async runSubmission(submission) {
            let succeeded = false;
            let failure = null;
            try {
                succeeded = (await submission.action()) !== false;
            } catch (error) {
                failure = error;
            } finally {
                this.completeSubmission(
                    submission.gestureNames,
                    submission.generation,
                    submission.transitionId,
                    succeeded
                );
                if (failure) {
                    submission.reject(failure);
                } else {
                    submission.resolve(succeeded);
                }
                this.drainSubmissions();
            }
            return succeeded;
        }

        completeSubmission(gestureNames, generation, transitionId, succeeded) {
            if (
                this.processingGeneration !== generation ||
                this.inFlightTransitionId !== transitionId
            ) {
                return false;
            }

            if (succeeded && this.isCurrentGeneration(generation)) {
                this.lastSuccessfullySubmittedGestureKey = gestureNames.join(',');
            }

            this.processing = false;
            this.processingGeneration = null;
            this.inFlightGestureKey = null;
            this.inFlightTransitionId = null;
            return true;
        }

        finishSubmission(generation = this.processingGeneration) {
            if (this.processingGeneration === generation) {
                this.processing = false;
                this.processingGeneration = null;
                this.inFlightGestureKey = null;
                this.inFlightTransitionId = null;
            }
        }

        startDetection() {
            if (this.detectionActive) {
                return this.generation;
            }

            this.generation += 1;
            this.resetStability();
            this.detectionActive = true;
            return this.generation;
        }

        stopDetection() {
            this.generation += 1;
            this.resetStability();
            this.detectionActive = false;
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
            this.resetStability();
        }
    }

    return {
        GestureSubmissionState,
        isVideoFrameReady,
        isFrameDataValid,
        getGestureDiagnosticDetails,
    };
}));
