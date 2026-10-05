# Field Break

Hacktoberfest Open-Source AI Challenge — Week 1: Touch Grass

Field Break turns a small amount of free time into one simple outdoor micro-adventure, then explicitly tells the user to put the screen away.

## Open-source AI core

The app is designed for the open-weight Apertus 1.5 model through an OpenAI-compatible endpoint. The provider/model are environment-configurable, so the project can switch to another open-weight deployment without changing the UI.

Run with real model inference by setting:

OPEN_MODEL_API_KEY
OPEN_MODEL_API_URL=https://api.publicai.co/v1/chat/completions
OPEN_MODEL_NAME=swiss-ai/apertus-v1.5-8b

Without a key, the prototype runs a clearly labelled deterministic demo-policy; it never pretends that fallback output is model inference.

## Why open innovation matters

The planning layer is not locked to one proprietary model or API. An open-weight model can be self-hosted, swapped, audited, or moved closer to the user's data. For a tiny tool whose purpose is to get you away from the screen, that simplicity matters.

## Safety

Field Break never invents live weather, closures, trail status, or medical advice. It only uses the context the user supplies and prefers local, reversible, low-cost activities.

## Run

python3 server.py

Then open http://127.0.0.1:8791

## Tests

python3 -m unittest discover -s tests -v

## Author

Omar Baró · Unfire
