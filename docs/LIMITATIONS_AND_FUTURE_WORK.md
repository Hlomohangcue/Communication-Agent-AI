# Limitations and Future Work

## Current limitations

### Heuristic gesture classification

Static labels are assigned by hand-written finger-extension and coordinate
rules. Fixed image-space thresholds are sensitive to hand orientation, camera
position, occlusion, and individual variation. The current webcam `confidence`
field is MediaPipe handedness confidence, not classifier confidence. A successful
test of the rules is not evidence of real-world recognition accuracy.

### No trained recognition model

The repository does not include a trained or validated gesture-recognition
model, model weights, training pipeline, class calibration, or confidence-based
unknown rejection. The project currently cannot substantiate model-level
precision or recall claims.

### No validated SASL data or interpretation

The current generic gesture labels and emoji meanings are not validated SASL
signs or linguistic translations. The repository has no validated SASL training
dataset, suitable annotations, or qualified linguistic review. It should not be
presented as SASL recognition. Generic labels should also not be represented as
validated ASL signs.

### Dynamic gesture recognition

Wave uses thresholded horizontal motion and an open-palm/raised-hand heuristic.
It is not a temporal machine-learning model and may be affected by camera motion,
tracking interruption, pose classification, or movement that resembles waving.
The tracker uses handedness for stream association rather than a learned,
validated identity model.

### Dataset collection

The collector stores 21 MediaPipe x/y/z landmark coordinates with
collector-supplied labels and timestamps. Its API and validation tests use
mocked landmark extraction. The full page and endpoints have not been
physically verified with a webcam or participants. Current records include
pseudonymous participant/session identifiers but do not capture a comprehensive
condition inventory for camera, lighting, or recording environment. The
collector allowlist is configured by account IDs; an application-wide collector
role system does not exist.

### Conversational AI and deployment

Gemini requires configuration and network access. Local fallbacks are
rule/template behavior, not equivalent language understanding. Browser speech
recognition is browser-dependent. Deployment templates exist, but no public
deployment, domain, TLS, target-server, persistence recovery, or device matrix
has been validated.

## Future work

1. Manually verify the collection UI with physical webcams, permissions, and
   multiple camera conditions before treating it as operational.
2. Define collection consent, annotation guidance, quality review, and privacy
   controls; gather genuinely labelled samples from multiple participants and
   conditions.
3. Use participant-separated train/validation/test data. Keep all records from a
   participant in one split to prevent identity leakage.
4. Train and evaluate static landmark models against a baseline, report
   per-class precision/recall and a confusion matrix, calibrate thresholds, and
   measure unknown false acceptance before changing the recognition engine.
5. Evaluate movement gestures with a separate temporal sequence model and
   event-level metrics, including hard-negative movement cases.
6. Only consider SASL research with validated SASL datasets, appropriate
   linguistic annotations, consent, and qualified signer/educator review.
7. Conduct device/browser testing and security/deployment review before
   presenting the app as publicly available.

These are proposals, not implemented product capabilities. No model is trained
or validated by this repository at the current stage.
