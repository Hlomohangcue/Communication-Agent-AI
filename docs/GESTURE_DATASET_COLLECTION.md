# Gesture Landmark Dataset Collection

This is a collector-only path. It does not change or train the current recognition
engine, and it does not store raw video. Gesture labels come from the person
conducting each recording, not from heuristic predictions or illustrations.

## Requirements and access

An operator must authorize collector accounts before collection is available.
There is no collector role in the current user model, so set
`GESTURE_DATASET_COLLECTOR_IDS` to a comma-separated list of existing application
user IDs in `.env` and restart the API. Collection is disabled when the list is
empty. An authenticated user can find their own ID from the `/auth/me` response;
only include IDs belonging to trusted data collectors.

Then sign in with an authorized account and open
`/app/gesture-collection.html`, or use **Collect training data** in the dashboard's
webcam controls. The webcam requires a secure browser context (HTTPS or localhost).
The collector page's APIs require both the existing bearer-token authentication
and membership in the collector allowlist.

Enter a pseudonymous participant ID using letters, digits, underscores, or hyphens.
Do not enter names, email addresses, or other identifying information. Choose a
configured label and recording hand, then start and stop a recording. Review the
sample/observation counts before saving; discard deletes the unsaved in-memory
recording.

Default labels are `open_palm`, `fist`, `thumbs_up`, `wave`, and `unknown`.
`unknown` is manually assigned to real unsupported or ambiguous hand poses.
`wave` is configured as dynamic and must be recorded as at least five consecutive
observations. Other labels save one static sample per captured frame. Labels and
dynamic labels can be configured with `GESTURE_DATASET_LABELS` and
`GESTURE_DATASET_DYNAMIC_LABELS` in `.env`; labels must be lowercase snake_case.

## Storage format

The default append-only dataset is `data/gesture_dataset_v1.jsonl`, configurable
with `GESTURE_DATASET_PATH`. Each UTF-8 JSONL record has `dataset_version: 1`,
`sample_id`, `participant_id`, `recording_session_id`, collector-supplied
`gesture_label`, `hand_side`, `timestamp`, `feature_version`,
`sample_type`, and landmarks. Static records also contain the separate
`handedness_confidence`. Dynamic records store ordered landmark observations in
`landmarks`; each observation has its own timestamp, monotonic timestamp,
handedness confidence, and 21 x/y/z points. The feature version is
`mediapipe_hand_landmarks_xyz_v1`.

The collection endpoint only returns coordinates from MediaPipe's 21 hand
landmarks and handedness metadata. It does not call the heuristic classifier.
The dataset service validates labels, identifiers, timestamps, finite
coordinates, the exact landmark count, dynamic sequence length/order, and
duplicate sample IDs before appending. The dataset and generated split files are
ignored by Git by default.

## Export for future training

Collect records from at least three distinct participants, then run from the
repository root:

```powershell
python scripts\export_gesture_dataset.py --input data\gesture_dataset_v1.jsonl --output-dir data\gesture_splits
```

The command validates the JSONL records and writes `train.jsonl`,
`validation.jsonl`, `test.jsonl`, and `split_manifest.json`. Splits are assigned
by participant, never by individual sample, so a participant cannot appear in
more than one split. The default seed is `42`; use `--seed` to choose another
reproducible assignment. Existing split files are not overwritten unless
`--overwrite` is supplied.

The export is data preparation only: no model is trained or evaluated. Before
using the data for training, review consent, annotation consistency, class
coverage, participant diversity, and recording-condition metadata. In
particular, do not treat these generic labels as SASL signs.
