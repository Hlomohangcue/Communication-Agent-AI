const test = require('node:test');
const assert = require('node:assert/strict');
const { GestureRecording } = require('../frontend/gesture_collection.js');

const makeObservation = (index, side = 'Left') => ({
    hand_side: side,
    timestamp: `2026-10-30T12:00:0${index}.000Z`,
    timestamp_ms: 1000 + index * 200,
    handedness_confidence: 0.9,
    landmarks: Array.from({ length: 21 }, () => ({ x: 0.2, y: 0.3, z: 0.1 })),
});

const context = (sampleType = 'static') => ({
    participantId: 'participant-1',
    recordingSessionId: 'recording-1',
    gestureLabel: sampleType === 'dynamic' ? 'wave' : 'open_palm',
    handSide: 'Left',
    sampleType,
    featureVersion: 'mediapipe_hand_landmarks_xyz_v1',
    datasetVersion: 1,
});

test('static recording creates one collector-labelled sample per observation', () => {
    const recording = new GestureRecording(context(), () => 'static-sample');
    assert.equal(recording.addObservation(makeObservation(0)), true);
    assert.equal(recording.addObservation(makeObservation(1)), true);
    recording.stop();

    const records = recording.toRecords();
    assert.equal(records.length, 2);
    assert.equal(records[0].gesture_label, 'open_palm');
    assert.equal(records[0].sample_type, 'static');
    assert.equal(records[0].sample_id, 'static-sample');
    assert.equal(records[0].handedness_confidence, 0.9);
    assert.equal(records[0].landmarks.length, 21);
    assert.equal(records[0].dataset_version, 1);
});

test('dynamic recording stores an ordered landmark sequence as one sample', () => {
    const recording = new GestureRecording(context('dynamic'), () => 'wave-sample');
    for (let index = 0; index < 5; index += 1) {
        recording.addObservation(makeObservation(index));
    }
    recording.stop();

    const [record] = recording.toRecords();
    assert.equal(record.sample_type, 'dynamic');
    assert.equal(record.gesture_label, 'wave');
    assert.equal(record.sample_id, 'wave-sample');
    assert.equal(record.landmarks.length, 5);
    assert.deepEqual(
        record.landmarks.map((observation) => observation.timestamp_ms),
        [1000, 1200, 1400, 1600, 1800]
    );
    assert.equal(record.landmarks[0].landmarks.length, 21);
});

test('recording cancellation discards buffered data and prevents saving', () => {
    const recording = new GestureRecording(context());
    recording.addObservation(makeObservation(0));
    recording.discard();

    assert.equal(recording.observationCount, 0);
    assert.deepEqual(recording.toRecords(), []);
    assert.throws(() => recording.addObservation(makeObservation(1)), /stopped recording/);
});

test('wrong hand observations are ignored and incomplete dynamic recordings cannot save', () => {
    const recording = new GestureRecording(context('dynamic'));
    assert.equal(recording.addObservation(makeObservation(0, 'Right')), false);
    recording.addObservation(makeObservation(0));
    recording.stop();

    assert.throws(() => recording.toRecords(), /at least 5 observations/);
});
