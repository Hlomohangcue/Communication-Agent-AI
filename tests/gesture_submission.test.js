const test = require('node:test');
const assert = require('node:assert/strict');
const {
    GestureSubmissionState,
    isVideoFrameReady,
    isFrameDataValid,
    getGestureDiagnosticDetails,
} = require('../frontend/gesture_submission.js');

const gesture = (name, confidence = 0.9) => ({
    hands_detected: 1,
    gestures: [{ gesture: name, confidence }],
    confidence: 0.9,
});

const neutral = () => ({
    hands_detected: 0,
    gestures: [],
    emojis: [],
    confidence: 0,
});

function createSubmitter() {
    const state = new GestureSubmissionState(2, 0.55);
    let submissions = 0;

    return {
        state,
        get submissions() {
            return submissions;
        },
        observe(result) {
            const decision = state.observe(result);
            if (decision.accepted) {
                return state.submit(decision.gestureNames, async () => {
                    submissions += 1;
                });
            }
            return Promise.resolve(false);
        },
    };
}

test('stable gesture submits once and additional held frames do not resubmit', () => {
    const submitter = createSubmitter();
    return submitter.observe(gesture('fist')).then(() => {
        assert.equal(submitter.submissions, 0);
        return submitter.observe(gesture('fist'));
    }).then(() => {
        assert.equal(submitter.submissions, 1);
        return submitter.observe(gesture('fist'));
    }).then(() => submitter.observe(gesture('fist'))).then(() => {
        assert.equal(submitter.submissions, 1);
    });
});

test('diagnostic details preserve both same-label hands and their side and confidence', () => {
    const details = getGestureDiagnosticDetails({
        hands_detected: 2,
        gestures: [
            { hand: 'Left', gesture: 'wave', confidence: 0.91 },
            { hand: 'Right', gesture: 'wave', confidence: 0.87 },
        ],
    });

    assert.deepEqual(details, {
        handsDetected: 2,
        detectedHands: [
            {
                hand: 'Left',
                gesture: 'wave',
                confidence: 0.91,
                movement_direction: null,
                movement_displacement: null,
                movement_velocity: null,
                wrist_movement_direction: null,
                wrist_movement_displacement: null,
                wrist_movement_velocity: null,
                dynamic_gesture_confidence: null,
            },
            {
                hand: 'Right',
                gesture: 'wave',
                confidence: 0.87,
                movement_direction: null,
                movement_displacement: null,
                movement_velocity: null,
                wrist_movement_direction: null,
                wrist_movement_displacement: null,
                wrist_movement_velocity: null,
                dynamic_gesture_confidence: null,
            },
        ],
    });
});

test('diagnostic details include dynamic movement metrics when supplied', () => {
    const details = getGestureDiagnosticDetails({
        hands_detected: 1,
        gestures: [{
            hand: 'Left',
            gesture: 'wave',
            confidence: 0.9,
            movement_direction: 'left',
            movement_displacement: 0.7,
            movement_velocity: 1.2,
            wrist_movement_direction: 'left',
            wrist_movement_displacement: 0.6,
            wrist_movement_velocity: 1.1,
            dynamic_gesture_confidence: 0.85,
        }],
    });

    test('gesture submission transition guard submits one wave transition only', async () => {
        const submitter = createSubmitter();
        const wave = gesture('wave');
        await submitter.observe(wave);
        await submitter.observe(wave);
        for (let frame = 0; frame < 5; frame += 1) {
            await submitter.observe(wave);
        }

        assert.equal(submitter.submissions, 1);
    });

    assert.deepEqual(details.detectedHands[0], {
        hand: 'Left',
        gesture: 'wave',
        confidence: 0.9,
        movement_direction: 'left',
        movement_displacement: 0.7,
        movement_velocity: 1.2,
        wrist_movement_direction: 'left',
        wrist_movement_displacement: 0.6,
        wrist_movement_velocity: 1.1,
        dynamic_gesture_confidence: 0.85,
    });
});

test('one zero-hand frame does not permit a duplicate held gesture', async () => {
    const submitter = createSubmitter();
    await submitter.observe(gesture('fist'));
    await submitter.observe(gesture('fist'));
    const noHand = submitter.state.observe(neutral());
    assert.equal(noHand.reason, 'no-hand-detection');
    assert.equal(submitter.state.lastStableGestureKey, 'fist');
    await submitter.observe(gesture('fist'));
    assert.equal(submitter.submissions, 1);
});

test('repeated zero-hand frames do not permit a duplicate held gesture', async () => {
    const submitter = createSubmitter();
    await submitter.observe(gesture('fist'));
    await submitter.observe(gesture('fist'));
    for (let frame = 0; frame < 4; frame += 1) {
        submitter.state.observe(neutral());
    }
    await submitter.observe(gesture('fist'));

    assert.equal(submitter.submissions, 1);
    assert.equal(submitter.state.lastStableGestureKey, 'fist');
    assert.equal(submitter.state.lastSuccessfullySubmittedGestureKey, 'fist');
});

test('fist followed by thumbs-up submits both stable transitions', async () => {
    const submitter = createSubmitter();
    await submitter.observe(gesture('fist'));
    await submitter.observe(gesture('fist'));
    await submitter.observe(gesture('thumbs_up'));
    await submitter.observe(gesture('thumbs_up'));
    assert.equal(submitter.submissions, 2);
});

test('thumbs-up followed by peace submits both stable transitions', async () => {
    const submitter = createSubmitter();
    await submitter.observe(gesture('thumbs_up'));
    await submitter.observe(gesture('thumbs_up'));
    await submitter.observe(gesture('peace'));
    await submitter.observe(gesture('peace'));
    assert.equal(submitter.submissions, 2);
});

test('fist followed by thumbs-up followed by fist submits three transitions', async () => {
    const submitter = createSubmitter();
    await submitter.observe(gesture('fist'));
    await submitter.observe(gesture('fist'));
    await submitter.observe(gesture('thumbs_up'));
    await submitter.observe(gesture('thumbs_up'));
    await submitter.observe(gesture('fist'));
    await submitter.observe(gesture('fist'));
    assert.equal(submitter.submissions, 3);
});

test('holding a different stable gesture does not submit duplicates', async () => {
    const submitter = createSubmitter();
    await submitter.observe(gesture('thumbs_up'));
    await submitter.observe(gesture('thumbs_up'));
    for (let frame = 0; frame < 8; frame += 1) {
        await submitter.observe(gesture('thumbs_up'));
    }
    assert.equal(submitter.submissions, 1);
});

test('open palm is an ordinary stable gesture transition without held duplicates', async () => {
    const submitter = createSubmitter();
    await submitter.observe(gesture('fist'));
    await submitter.observe(gesture('fist'));
    await submitter.observe(gesture('open_palm'));
    await submitter.observe(gesture('open_palm'));
    for (let frame = 0; frame < 5; frame += 1) {
        await submitter.observe(gesture('open_palm'));
    }
    assert.equal(submitter.submissions, 2);
    assert.equal(submitter.state.lastSuccessfullySubmittedGestureKey, 'open_palm');
});

test('different gesture remains usable after a zero-hand interruption', async () => {
    const submitter = createSubmitter();
    await submitter.observe(gesture('fist'));
    await submitter.observe(gesture('fist'));
    submitter.state.observe(neutral());
    await submitter.observe(gesture('thumbs_up'));
    await submitter.observe(gesture('thumbs_up'));
    assert.equal(submitter.submissions, 2);
});

test('low confidence and failed frame responses do not create gesture transitions', () => {
    const submitter = createSubmitter();
    return submitter.observe(gesture('fist'))
        .then(() => submitter.observe(gesture('fist')))
        .then(() => submitter.observe({ ...gesture('fist'), confidence: 0.4 }))
        .then(() => submitter.observe({ error: 'frame processing failed' }))
        .then(() => submitter.observe(gesture('fist')))
        .then(() => submitter.observe(gesture('fist')))
        .then(() => assert.equal(submitter.submissions, 1));
});

test('rejects one low-confidence gesture even when aggregate confidence is high', () => {
    const state = new GestureSubmissionState(2, 0.55);
    const result = {
        hands_detected: 2,
        gestures: [
            { gesture: 'fist', confidence: 0.9 },
            { gesture: 'wave', confidence: 0.54 },
        ],
        confidence: 0.8,
    };

    assert.equal(state.observe(result).accepted, false);
    assert.equal(state.observe(result).accepted, false);
});

test('accepts multiple gestures only when every individual confidence meets threshold', () => {
    const state = new GestureSubmissionState(2, 0.55);
    const result = {
        hands_detected: 2,
        gestures: [
            { gesture: 'fist', confidence: 0.55 },
            { gesture: 'wave', confidence: 0.8 },
        ],
        confidence: 0.7,
    };

    assert.equal(state.observe(result).accepted, false);
    assert.equal(state.observe(result).accepted, true);
});

test('rejects missing and invalid individual confidence values', () => {
    const state = new GestureSubmissionState(2, 0.55);
    const invalidResults = [
        { hands_detected: 1, gestures: [{ gesture: 'fist' }], confidence: 0.9 },
        { hands_detected: 1, gestures: [{ gesture: 'fist', confidence: NaN }], confidence: 0.9 },
        { hands_detected: 1, gestures: [{ gesture: 'fist', confidence: Infinity }], confidence: 0.9 },
        { hands_detected: 1, gestures: [{ gesture: 'fist', confidence: '0.9' }], confidence: 0.9 },
        { hands_detected: 1, gestures: [{ gesture: 'fist', confidence: 1.01 }], confidence: 0.9 },
    ];

    for (const result of invalidResults) {
        assert.equal(state.observe(result).accepted, false);
        assert.equal(state.observe(result).accepted, false);
    }
});

test('API failure releases processing lock without resubmitting a held gesture', async () => {
    const state = new GestureSubmissionState(2, 0.55);
    state.observe(gesture('fist'));
    const decision = state.observe(gesture('fist'));
    let submissions = 0;
    await assert.rejects(
        state.submit(decision.gestureNames, async () => {
            throw new Error('HTTP 503');
        }),
        /HTTP 503/
    );

    assert.equal(state.processing, false);
    assert.equal(state.observe(gesture('fist')).accepted, false);
    assert.equal(state.lastSuccessfullySubmittedGestureKey, null);
    assert.equal(submissions, 0);

    state.observe(gesture('thumbs_up'));
    const newTransition = state.observe(gesture('thumbs_up'));
    assert.equal(newTransition.accepted, true);
    assert.equal(await state.submit(newTransition.gestureNames, async () => {
        submissions += 1;
    }, state.generation, newTransition.transitionId), true);
    assert.equal(submissions, 1);
    assert.equal(state.lastSuccessfullySubmittedGestureKey, 'thumbs_up');
});

test('failed and malformed observations reset stability without creating transitions', () => {
    const state = new GestureSubmissionState(2, 0.55);
    state.observe(gesture('fist'));
    const decision = state.observe(gesture('fist'));
    assert.equal(state.beginSubmission(decision.gestureNames), true);
    state.finishSubmission();

    state.observe(gesture('open_palm'));
    state.observe({ error: 'frame request failed', hands_detected: 0, gestures: [], emojis: [], confidence: 0 });
    state.observe({ hands_detected: 1, gestures: [] });

    assert.equal(state.lastStableGestureKey, 'fist');
    assert.equal(state.consecutiveMatches, 0);
});

test('different stable gesture is queued and submitted serially while another is in flight', async () => {
    const state = new GestureSubmissionState(2, 0.55);
    const generation = state.startDetection();
    const pending = [];
    let active = 0;
    let maximumActive = 0;

    const enqueueObservedGesture = (name) => {
        const decision = state.observe(gesture(name));
        if (!decision.accepted) {
            return Promise.resolve(false);
        }
        return state.submit(decision.gestureNames, () => new Promise((resolve) => {
            active += 1;
            maximumActive = Math.max(maximumActive, active);
            pending.push(() => {
                active -= 1;
                resolve(true);
            });
        }), generation, decision.transitionId);
    };

    const firstFrame = enqueueObservedGesture('fist');
    const firstSubmission = enqueueObservedGesture('fist');
    const secondFrame = enqueueObservedGesture('thumbs_up');
    const secondSubmission = enqueueObservedGesture('thumbs_up');

    assert.equal(pending.length, 1);
    assert.equal(state.pendingSubmissions.length, 1);
    pending.shift()();
    assert.equal(await firstFrame, false);
    assert.equal(await firstSubmission, true);
    assert.equal(pending.length, 1);
    pending.shift()();
    assert.equal(await secondFrame, false);
    assert.equal(await secondSubmission, true);
    assert.equal(maximumActive, 1);
    assert.equal(state.lastSuccessfullySubmittedGestureKey, 'thumbs_up');
});

test('stopped detection session ignores an outstanding frame response', async () => {
    const state = new GestureSubmissionState(2, 0.55);
    const generation = state.startDetection();
    let resolveResponse;
    const response = new Promise((resolve) => {
        resolveResponse = resolve;
    });
    let submissions = 0;

    state.stopDetection();
    resolveResponse(gesture('fist'));
    const result = await response;
    const handled = state.handleFrameResult(generation, result, (frameResult) => {
        const decision = state.observe(frameResult);
        if (decision.accepted) {
            submissions += 1;
        }
    });

    assert.equal(handled, false);
    assert.equal(submissions, 0);
    assert.equal(state.consecutiveMatches, 0);
});

test('old frame response cannot submit after a new detection session starts', async () => {
    const state = new GestureSubmissionState(2, 0.55);
    const oldGeneration = state.startDetection();
    let resolveResponse;
    const response = new Promise((resolve) => {
        resolveResponse = resolve;
    });
    state.stopDetection();
    const newGeneration = state.startDetection();
    resolveResponse(gesture('fist'));
    const result = await response;
    let submissions = 0;

    assert.notEqual(oldGeneration, newGeneration);
    assert.equal(
        state.handleFrameResult(oldGeneration, result, (frameResult) => {
            const decision = state.observe(frameResult);
            if (decision.accepted) {
                submissions += 1;
            }
        }),
        false
    );
    assert.equal(submissions, 0);
    assert.equal(state.consecutiveMatches, 0);

    state.handleFrameResult(newGeneration, result, (frameResult) => {
        state.observe(frameResult);
        const decision = state.observe(frameResult);
        if (decision.accepted) {
            submissions += 1;
        }
    });
    assert.equal(submissions, 1);
});

test('multiple start attempts create only one active detection generation', () => {
    const state = new GestureSubmissionState(2, 0.55);
    const firstGeneration = state.startDetection();

    assert.equal(state.startDetection(), firstGeneration);
    assert.equal(state.generation, firstGeneration);
    assert.equal(state.detectionActive, true);

    state.stopDetection();
    const restartedGeneration = state.startDetection();
    assert.notEqual(restartedGeneration, firstGeneration);
});

test('overlapping frame requests are blocked within a session', () => {
    const state = new GestureSubmissionState(2, 0.55);
    const generation = state.startDetection();

    assert.equal(state.beginFrameRequest(generation), true);
    assert.equal(state.beginFrameRequest(generation), false);
    state.finishFrameRequest(generation);
    assert.equal(state.frameProcessing, false);
});

test('multiple gestures are accepted only when every individual confidence meets threshold', () => {
    const submitter = createSubmitter();
    const mixed = {
        hands_detected: 2,
        gestures: [
            { gesture: 'open_palm', confidence: 0.9 },
            { gesture: 'wave', confidence: 0.9 },
        ],
        confidence: 0.9,
    };
    assert.equal(submitter.state.observe(mixed).accepted, false);
    assert.equal(submitter.state.observe(mixed).accepted, true);
});

test('stopping and restarting preserves the last gesture and stale response cannot alter it', () => {
    const state = new GestureSubmissionState(2, 0.55);
    const oldGeneration = state.startDetection();
    state.observe(gesture('fist'));
    const acceptedFist = state.observe(gesture('fist'));
    assert.equal(acceptedFist.accepted, true);
    return state.submit(acceptedFist.gestureNames, async () => true, oldGeneration, acceptedFist.transitionId)
        .then(() => {
            state.stopDetection();
            const newGeneration = state.startDetection();

            assert.notEqual(oldGeneration, newGeneration);
            assert.equal(state.lastStableGestureKey, 'fist');
            assert.equal(state.consecutiveMatches, 0);

            let staleDecision;
            assert.equal(
                state.handleFrameResult(oldGeneration, gesture('open_palm'), (result) => {
                    staleDecision = state.observe(result);
                }),
                false
            );
            assert.equal(staleDecision, undefined);
            assert.equal(state.lastStableGestureKey, 'fist');

            assert.equal(state.observe(gesture('fist')).accepted, false);
            assert.equal(state.observe(gesture('fist')).accepted, false);
            assert.equal(state.observe(gesture('thumbs_up')).accepted, false);
            assert.equal(state.observe(gesture('thumbs_up')).accepted, true);
            assert.equal(state.lastStableGestureKey, 'thumbs_up');
        });
});

test('video readiness and captured frame validation reject invalid camera frames', () => {
    assert.equal(isVideoFrameReady({ readyState: 1, videoWidth: 640, videoHeight: 480 }), false);
    assert.equal(isVideoFrameReady({ readyState: 2, videoWidth: 0, videoHeight: 480 }), false);
    assert.equal(isVideoFrameReady({ readyState: 2, videoWidth: 640, videoHeight: 0 }), false);
    assert.equal(isVideoFrameReady({ readyState: 2, videoWidth: 640, videoHeight: 480 }), true);
    assert.equal(isVideoFrameReady(null), false);

    assert.equal(isFrameDataValid('data:,'), false);
    assert.equal(isFrameDataValid('data:image/jpeg;base64,'), false);
    assert.equal(isFrameDataValid('data:image/jpeg;base64,%%%'), false);
    assert.equal(isFrameDataValid('data:image/jpeg;base64,/9j/4AAQSkZJRg=='), true);
});

test('stale frame completion cannot release a newer session frame lock', () => {
    const state = new GestureSubmissionState(2, 0.55);
    const oldGeneration = state.startDetection();
    assert.equal(state.beginFrameRequest(oldGeneration), true);

    state.stopDetection();
    const newGeneration = state.startDetection();
    assert.notEqual(newGeneration, oldGeneration);
    assert.equal(state.beginFrameRequest(newGeneration), true);

    state.finishFrameRequest(oldGeneration);
    assert.equal(state.frameProcessing, true);
    assert.equal(state.beginFrameRequest(newGeneration), false);

    state.finishFrameRequest(newGeneration);
    assert.equal(state.frameProcessing, false);
});

test('stale submission completion cannot block or unlock a newer session', async () => {
    const state = new GestureSubmissionState(2, 0.55);
    const oldGeneration = state.startDetection();
    let finishOldSubmission;
    const oldSubmission = state.submit(['fist'], () => new Promise((resolve) => {
        finishOldSubmission = resolve;
    }), oldGeneration);

    state.stopDetection();
    const newGeneration = state.startDetection();
    assert.equal(state.lastStableGestureKey, null);

    let finishNewSubmission;
    const newSubmission = state.submit(['wave'], () => new Promise((resolve) => {
        finishNewSubmission = resolve;
    }), newGeneration);

    assert.notEqual(oldGeneration, newGeneration);
    assert.equal(state.processingGeneration, oldGeneration);
    finishOldSubmission();
    await oldSubmission;
    assert.equal(state.processing, true);
    assert.equal(state.processingGeneration, newGeneration);

    finishNewSubmission();
    await newSubmission;
    assert.equal(state.processing, false);
});
