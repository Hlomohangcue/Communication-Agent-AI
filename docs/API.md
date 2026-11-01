# API Reference

FastAPI defines the current API in `backend/main.py`; the interactive schema is
available at `/docs` when the service is running. This overview lists the
implemented routes. Request and response models in the application are the
source of truth for exact payload fields.

## Service and UI

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Service status/version response. |
| GET | `/health` | Health-check response. |
| GET | `/ui` | Redirects to `/app/login.html`. |

Static frontend files are mounted at `/app`.

## Authentication

| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/signup` | Create an account. |
| POST | `/auth/login` | Authenticate and obtain a JWT. |
| GET | `/auth/verify` | Verify the current token. |
| GET | `/auth/me` | Return the authenticated account. |
| GET | `/auth/credits` | Return account credit information. |

Signup and login are public. Other protected operations resolve the account
from the JWT; session access is checked against the authenticated account.

## Conversation and simulation

| Method | Path | Purpose |
|---|---|---|
| POST | `/simulate/start` | Start a communication simulation/session. |
| POST | `/simulate/step` | Submit a simulation message/step. |
| POST | `/communicate` | Process a communication request. |
| GET | `/logs` | Read the authenticated user's logs. |
| GET | `/session/{session_id}` | Read an owned session. |
| DELETE | `/session/{session_id}` | Delete an owned session. |
| GET | `/sessions` | List the authenticated user's sessions. |
| POST | `/save_message` | Save a message to an owned session. |

## Gesture and phrase endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/translate/text-to-gesture` | Map text to an emoji/gesture-token sequence. This is not sign-language translation. |
| GET | `/gestures` | List configured generic gesture/meaning data. |
| GET | `/phrases` | List configured phrases. |
| POST | `/phrases/custom` | Add a custom phrase. |
| GET | `/gesture-history/{session_id}` | Read gesture history associated with an owned session. |

## Vision and landmark collection

| Method | Path | Purpose |
|---|---|---|
| POST | `/vision/process-frame` | Run current MediaPipe hand detection and heuristic gesture recognition. |
| GET | `/vision/gestures` | List vision gesture labels. |
| POST | `/vision/gesture-to-text` | Convert detected gesture input to the application's text response. |
| POST | `/vision/interpret-gesture` | Resolve a gesture label through the configured meaning mapping. |
| GET | `/vision/collection-config` | Return dataset labels/schema for an authenticated allowlisted collector. |
| POST | `/vision/collect-frame` | Extract landmark observations without invoking the heuristic labeler; requires an authenticated allowlisted collector. |
| POST | `/vision/dataset/recordings` | Validate and append collector-labelled dataset records; requires an authenticated allowlisted collector. |

The dataset endpoints are disabled for accounts not listed in
`GESTURE_DATASET_COLLECTOR_IDS`; an empty allowlist denies collection. Labels
are supplied by the collector, not inferred by the existing classifier.
Handedness confidence is metadata and is distinct from gesture-class
confidence. See [Gesture Dataset Collection](GESTURE_DATASET_COLLECTION.md).

## Authentication and ownership

- Protected API requests use a bearer JWT.
- The server identifies the account from the token subject; clients do not
  choose an arbitrary owner ID for session operations.
- Session-bound reads and writes enforce ownership.
- Unauthenticated requests receive 401; authenticated access to another
  account's session is denied. Missing-session behavior is route-specific.
