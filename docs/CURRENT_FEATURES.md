# Current Features and Verification Status

This document describes code currently in the repository. Automated tests are
not equivalent to browser, device, webcam, microphone, or production validation.

## Implemented and automatically tested

| Capability | Evidence and scope |
|---|---|
| Account signup/login and JWT-protected routes | FastAPI routes use bcrypt/JWT; API and session-ownership tests cover authentication responses, session ownership, and access outcomes. |
| SQLite sessions and message history | The database layer stores users, sessions, messages, logs, credits, and gesture sequences. Session tests cover create/read/save/history/delete and ownership boundaries. |
| Simulation and conversation coordinator | Coordinator invokes non-verbal, intent, speech, and context agents. Tests exercise selected agent fallback behavior and endpoint paths. This does not establish production-quality conversation accuracy. |
| Gesture-to-meaning mappings | `GestureMeaningService` has unit tests for known labels, multiple labels, and ambiguous fist meanings. Its meanings are application mappings, not validated linguistic semantics. |
| Text-to-emoji/gesture-sequence mapping | `GestureAgent` phrase and keyword paths have unit tests. These return emoji sequences, not translated signs. |
| Static heuristic rule behavior and dynamic wave thresholds | The source implements static pose heuristics and a wave threshold tracker. Dynamic tracker tests cover threshold, timing, stream isolation, and hand-side edge cases. They use synthetic test landmarks; they are not real-world accuracy tests. |
| Frontend gesture submission stability and duplicate protection | Node tests cover stable transitions, individual confidence checks, interruptions, failed submissions, and stale request/session behavior in the submission state module. |
| Dataset record validation and participant-disjoint splitting | Tests cover static/dynamic JSONL records, coordinates, identifiers, labels, sequence timestamps, duplicates, and participant separation. Export tests check split output and disjoint participants. |
| API frame validation and landmark serialization | Tests cover invalid frame handling and mocked MediaPipe landmark metadata, including 21-point serialization and separate two-hand observations. These tests do not access a physical camera. |

## Implemented but not physically verified

| Capability | Verification boundary |
|---|---|
| Dashboard authentication and browser interaction | Frontend code is present; no end-to-end browser demonstration is established by the automated test suite. |
| Webcam capture and live heuristic recognition | Browser `getUserMedia`, JPEG frame transfer, MediaPipe detection, and display paths are implemented. They require a working webcam, permissions, and a compatible runtime; no physical webcam test is claimed here. |
| Browser speech recognition | Uses browser `SpeechRecognition`/`webkitSpeechRecognition` APIs where available. Hardware, permissions, locale, and browser behavior require manual testing. |
| Dataset collection page and live collection flow | Collector UI and APIs are implemented and covered through unit/API tests with mocked landmark extraction. They have not been physically verified with a webcam or participants. |
| Docker/container deployment and public access | Dockerfile and Compose configuration exist, but no deployment or target-host validation has been performed. |

## Partially implemented

| Capability | Current scope and gap |
|---|---|
| Gesture recognition | Static labels use hand-written geometric/finger-count rules. `confidence` from webcam results reflects handedness detection, not a learned gesture-class confidence. There is no trained gesture model or calibrated unknown rejection. |
| Dynamic gestures | Wave uses a threshold-based tracker gated by an open-palm/raised-hand heuristic. It is not a trained sequence classifier. |
| Text-to-gesture communication | The app maps phrases/keywords to emoji tokens, may use Gemini for complex input, and falls back to generic emoji output. It does not generate verified sign-language sequences. |
| External AI | Gemini is an optional dependency on a configured API key and network. Agents use rule/template fallbacks when unavailable or when calls fail. Fallbacks are reduced in capability. |
| Freemium/credits | User records, credits, and per-message deductions in the simulation flow exist. The repository does not implement a verified payment, billing, or subscription-purchase integration. |
| Dataset program | Versioned landmark records and participant-grouped export exist. The collector does not provide a complete research/consent workflow, comprehensive lighting/camera metadata, annotation review, or an evaluated dataset. |

## Not implemented

- A trained or validated static or temporal gesture-recognition model.
- Validated ASL or SASL recognition/translation.
- A validated sign-language vocabulary, grammar, or sentence translation system.
- Qualified linguistic validation or validated SASL annotations.
- Public hosting, target-domain configuration, and production deployment validation.
- Cross-device accuracy or accessibility certification.

The test suite's passing status means the tested code paths passed their
automated assertions. It does not prove webcam accuracy, model quality, language
validation, or deployment readiness.
