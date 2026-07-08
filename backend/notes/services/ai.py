import json

from django.conf import settings
from openai import OpenAI

from .web_search import verify_claim
from ..models import Note

SYSTEM_PROMPT = """You are a clinical reference assistant. You will be given the text of a \
document a medical practitioner uploaded (e.g. notes about a food, herb, or remedy). Read it \
carefully and produce a structured note a practitioner can scan at a glance during a patient visit.

Respond with a JSON object with exactly these keys:
- "title": the food/remedy/subject the note is about (short, e.g. "Ginger")
- "subject": same as title, used for search matching
- "conditions": an array of short condition/symptom names this food/remedy helps with or \
prevents (e.g. ["Nausea", "Inflammation"]). Use plain, common medical terms.
- "summary": a 1-2 sentence summary a practitioner can read in a few seconds
- "content": a fuller explanation (3-6 sentences) covering the supporting detail from the \
document, including any cautions or dosage notes if present

If the document does not clearly relate to a food/remedy and conditions it helps with, do your \
best to extract whatever medically relevant subject and summary you can."""

# Keeps token usage/cost bounded; a few thousand words is plenty of context for a summary note.
MAX_INPUT_CHARS = 12000


def _placeholder(filename: str, reason: str) -> dict:
    title = filename.rsplit('.', 1)[0] or filename
    return {
        'title': title,
        'subject': title,
        'conditions': ['Pending AI review'],
        'summary': f'AI summarization was not completed ({reason}).',
        'content': (
            f'Uploaded file: {filename}. {reason}. '
            'Edit this note manually, or retry the upload once resolved.'
        ),
        'verification': Note.VERIFICATION_UNVERIFIED,
        'verification_note': '',
    }


def _draft_from_document(text: str, filename: str) -> dict:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': text[:MAX_INPUT_CHARS]},
        ],
    )
    result = json.loads(response.choices[0].message.content)
    return {
        'title': result.get('title') or filename,
        'subject': result.get('subject') or result.get('title') or filename,
        'conditions': result.get('conditions') or [],
        'summary': result.get('summary') or '',
        'content': result.get('content') or '',
    }


def summarize_document(text: str, filename: str) -> dict:
    """Summarize an uploaded document's text into the note shape the frontend expects.

    Falls back to a clear placeholder (rather than raising) whenever summarization can't
    happen, so a PDF upload always results in a usable note. A successful draft is then
    cross-checked against the web (see services/web_search.py) before being returned, so the
    result always carries a `verification` status the UI can flag to the practitioner.
    """
    if not text.strip():
        return _placeholder(filename, 'no readable text was found in the PDF')

    if not settings.OPENAI_API_KEY:
        return _placeholder(filename, 'OPENAI_API_KEY is not configured')

    try:
        draft = _draft_from_document(text, filename)
    except Exception as exc:  # noqa: BLE001 — any failure here must degrade gracefully
        return _placeholder(filename, f'the AI request failed ({exc.__class__.__name__})')

    check = verify_claim(draft)
    if check is None:
        return {**draft, 'verification': Note.VERIFICATION_UNVERIFIED, 'verification_note': 'Web verification was unavailable.'}
    if check.get('verified'):
        return {**draft, 'verification': Note.VERIFICATION_WEB_CONFIRMED, 'verification_note': ''}

    corrected = check.get('corrected') or {}
    return {
        'title': corrected.get('title') or draft['title'],
        'subject': corrected.get('subject') or draft['subject'],
        'conditions': corrected.get('conditions') or draft['conditions'],
        'summary': corrected.get('summary') or draft['summary'],
        'content': corrected.get('content') or draft['content'],
        'verification': Note.VERIFICATION_AI_CORRECTED,
        'verification_note': check.get('note', ''),
    }
