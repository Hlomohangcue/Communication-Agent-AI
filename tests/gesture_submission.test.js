const test = require('node:test');
const assert = require('node:assert/strict');
const { GestureSubmissionState } = require('../frontend/gesture_submission.js');

const gesture = (name, confidence = 0.9) => ({
    hands_detected: 1,
    gestures: [{ gesture: name, confidence }],
    confidence: 0.9,
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

test('neutral frame resets the latch and permits the same gesture again', () => {
    const submitter = createSubmitter();
    return submitter.observe(gesture('fist'))
        .then(() => submitter.observe(gesture('fist')))
        .then(() => submitter.observe({ hands_detected: 0, gestures: [], confidence: 0 }))
        .then(() => submitter.observe(gesture('fist')))
        .then(() => submitter.observe(gesture('fist')))
        .then(() => assert.equal(submitter.submissions, 2));
});

test('different stable gesture is accepted after its own stability threshold', () => {
    const submitter = createSubmitter();
    return submitter.observe(gesture('fist'))
        .then(() => submitter.observe(gesture('fist')))
        .then(() => submitter.observe(gesture('wave')))
        .then(() => {
            assert.equal(submitter.submissions, 1);
            return submitter.observe(gesture('wave'));
        })
        .then(() => assert.equal(submitter.submissions, 2));
});

test('low confidence and failed frame responses do not release an accepted gesture latch', () => {
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
    await assert.rejects(
        state.submit(decision.gestureNames, async () => {
            throw new Error('HTTP 503');
        }),
        /HTTP 503/
    );

    assert.equal(state.processing, false);
    assert.equal(state.observe(gesture('fist')).accepted, false);
    assert.equal(await state.submit(['fist'], async () => {}), false);
});

test('overlapping submissions are blocked by the processing lock', async () => {
    const state = new GestureSubmissionState(2, 0.55);
    state.observe(gesture('fist'));
    const decision = state.observe(gesture('fist'));

    let finishFirstSubmission;
    const firstSubmission = state.submit(decision.gestureNames, () => new Promise((resolve) => {
        finishFirstSubmission = resolve;
    }));
    assert.equal(await state.submit(['wave'], async () => {}), false);

    finishFirstSubmission();
    assert.equal(await firstSubmission, true);
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
});

test('old frame response cannot submit after a new detection session starts', async () => {
    const state = new GestureSubmissionState(2, 0.55);
    const oldGeneration = state.startDetection();
    let resolveResponse;
    const response = new Promise((resolve) => {
        resolveResponse = resolve;
    });
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

    state.handleFrameResult(newGeneration, result, (frameResult) => {
        state.observe(frameResult);
        const decision = state.observe(frameResult);
        if (decision.accepted) {
            submissions += 1;
        }
    });
    assert.equal(submissions, 1);
});
