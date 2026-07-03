# Healnote

An AI-assisted note-taking platform for medical professionals. Practitioners write or upload (PDF) notes about foods/remedies and the conditions they help with; the platform's AI pre-summarizes uploaded documents so a practitioner can search by keyword (e.g. "apple") during a patient visit and instantly see relevant conditions and recommendations.

## Status

Frontend-only scaffold, built with React + Vite + Tailwind CSS. Data currently comes from an in-memory mock service (`src/api/`) that mirrors the shape of the future Django REST API, so it can be swapped for real network calls without touching components.

Not yet implemented: Django backend, OpenAI-based PDF summarization/cross-referencing, Cloudflare R2 file storage, authentication.

## Development

```bash
npm install
npm run dev
```
# note_taker
