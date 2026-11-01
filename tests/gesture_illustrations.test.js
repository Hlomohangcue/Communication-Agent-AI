const test = require('node:test');
const assert = require('node:assert/strict');
const {
    renderGestureIllustration,
    getSupportedGestureIllustrations,
} = require('../frontend/gesture_illustrations.js');

test('every configured gesture has a named local SVG illustration', () => {
    const gestures = getSupportedGestureIllustrations();

    assert.equal(gestures.length, 18);
    for (const { gesture, label } of gestures) {
        const svg = renderGestureIllustration(gesture);
        assert.match(svg, /^<svg class="gesture-illustration"/);
        assert.ok(svg.includes(`aria-label="${label} hand illustration"`));
        assert.ok(svg.includes('<path'));
    }
});

test('renderer preserves distinct poses for the priority gestures', () => {
    const fist = renderGestureIllustration('fist');
    const wave = renderGestureIllustration('wave');
    const peace = renderGestureIllustration('peace');
    const rockOn = renderGestureIllustration('rock_on');
    const pointingUp = renderGestureIllustration('pointing_up');
    const thumbsDown = renderGestureIllustration('thumbs_down');

    assert.notEqual(fist, wave);
    assert.notEqual(peace, rockOn);
    assert.notEqual(pointingUp, thumbsDown);
    assert.equal(renderGestureIllustration('unverified_sign'), '');
});
