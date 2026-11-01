# Interview Demonstration Guide

This sequence demonstrates the current AI-assisted communication prototype
without presenting its outputs as validated sign-language translation. Allow
approximately 5–8 minutes, plus time to create a local account.

## Preparation

- Start the local API using [Installation and Setup](INSTALLATION_AND_SETUP.md).
- Open `/ui`, sign up, and sign in before the interview.
- Prepare an internet-connected webcam-equipped browser if demonstrating vision.
- For Gemini-backed responses, configure a valid `GEMINI_API_KEY` before
  starting the API. Without one, demonstrate the available local
  rule/template fallback and say that it is a fallback.
- Do not enable the dataset collector unless the collector account is
  intentionally authorized. It is not required for the regular dashboard demo.
- Confirm camera and microphone permissions in advance. No physical device
  checks are implied by this guide.

## Suggested walkthrough

### 1. Introduce the problem

Explain that users who communicate through different methods may need a simple
way to exchange basic messages. Position this project as a prototype exploring
text, emoji, speech, and generic hand-pose interaction.

### 2. Log in

Open the login page, create or use a demo account, and sign in. Explain that
protected API calls use JWT authentication and that user/session data is stored
in SQLite.

### 3. Tour the dashboard

Show the two communication modes, text/symbol input, conversation area, and
history/log panels. Explain that the interface and conversation flow are
prototype functionality and do not provide certified accessibility or clinical
support.

### 4. Demonstrate a conversation

Start a simulation, enter a short simple message or select an emoji/token, and
submit it. Show the response and history. This does not require a webcam.

With `GEMINI_API_KEY` configured and network access, explain that agents may use
Gemini. Without it, show the rule/template response and identify it as a
fallback. Avoid claiming all responses are produced by an AI model.

### 5. Demonstrate text-to-emoji output

Switch to verbal-to-non-verbal mode and enter a short phrase such as “I need
water” or “hello.” Show the emoji sequence and describe the current
phrase/keyword mapping. For an unmatched message, Gemini may be used when
configured; otherwise a generic fallback may be returned. This is
text-to-emoji representation, not sign-language translation.

### 6. Demonstrate webcam hand detection and current gesture recognition

This step **requires a working webcam**, browser permission, and successful
MediaPipe/OpenCV runtime initialization. Switch to webcam mode, start the
camera, and hold a supported pose such as an open palm or fist in view. Show
the detected label and automatic interpretation if the app accepts a stable
transition.

Describe the actual mechanism: MediaPipe detects hands and landmarks; current
labels are assigned by hand-written finger/coordinate heuristics, and wave
depends on a threshold-based movement tracker. The displayed confidence comes
from handedness detection, not a trained gesture classifier.

If the webcam is unavailable, skip this live step rather than presenting a
mock result as physical validation. Explain the pipeline from source code
instead.

### 7. Explain limitations

State clearly that the system is an AI-assisted hand-gesture communication
prototype, not a complete sign-language translator. Gesture meanings are
generic mappings, the recognition engine is not trained, and no validated
SASL dataset or qualified linguistic validation is available.

### 8. Discuss future work

Describe the collector-labelled landmark dataset as preparation for future
research. Explain the intended next steps: physical collector verification,
consented multi-participant data, participant-separated evaluation, a
confidence-calibrated landmark model with unknown rejection, and a separate
temporal model for movement gestures. These are future work, not current
capabilities.

## External service and hardware requirements

| Demonstration | Webcam needed | Gemini key/network needed |
|---|---:|---:|
| Login, dashboard, SQLite conversation flow | No | No |
| Rule/template conversational fallback | No | No |
| Gemini-enhanced conversation or complex text-to-emoji | No | Yes, for live provider use |
| Browser speech input | Microphone | No |
| Webcam detection and heuristic labels | Yes | No |
| Dataset collection | Yes, plus collector allowlist | No |

No hosted deployment is provided by this guide. A local demo should be clearly
identified as local and should not be described as a public or production
deployment.
