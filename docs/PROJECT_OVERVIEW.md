# Project Overview

## Problem

People who communicate using different methods may need a simple way to exchange
basic messages. A conventional text-only interface can be inaccessible or
inconvenient for some users, while recognizing a hand pose or emoji does not by
itself establish its intended meaning.

## Intended users

The prototype is intended for demonstration and exploration by verbal and
non-verbal communicators, caregivers, educators, and developers. It is not a
clinical, accessibility-certified, or sign-language translation product.

## Objectives

- Explore a browser interface with text, speech, emoji/token input, and webcam
  hand-pose interaction.
- Demonstrate authenticated conversation sessions and persisted history.
- Connect input interpretation and response generation through FastAPI services
  and optional AI assistance.
- Provide a separate, collector-labelled MediaPipe landmark collection path as a
  foundation for future model research.

## Proposed solution

The browser sends communication requests to a FastAPI application. SQLite stores
users, sessions, messages, and operational data. Optional Gemini-backed agents
can interpret input and generate responses; local rule/template fallbacks allow
some flows to run without the provider. The webcam path uses MediaPipe hand
detection and a current heuristic classifier to label selected generic poses.

The dataset collector is separate from recognition: an authorized collector
selects the label and recording hand, and the collection endpoint returns
MediaPipe landmarks without applying the heuristic gesture labeler.

## Current prototype scope

Implemented scope includes account authentication, session-based conversation,
emoji-oriented text-to-gesture output, browser speech input where supported,
webcam detection/heuristic gesture display, and SQLite persistence. A protected
landmark dataset collection interface and JSONL export tool are also present.

There is no trained gesture-recognition model, no validated SASL training
dataset, and no qualified linguistic validation. Existing mappings between
generic gestures and meanings are simplified examples, not sign-language
semantics. The dataset collector has automated coverage but has not been
physically tested on webcam hardware. No public deployment is configured or
verified.
