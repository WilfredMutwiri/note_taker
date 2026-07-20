import json

from django.conf import settings
from openai import OpenAI

from .web_search import RESPONSE_SHAPE, _as_list, verify_claim
from ..models import Note

SYSTEM_PROMPT = """You are a clinical reference assistant. You will be given the text of a \
document a medical practitioner uploaded — it may be about a food/herb/remedy, or about a \
disease/condition. Read it carefully, first decide which one it is, and produce a structured \
note a practitioner can scan at a glance during a patient visit.

""" + RESPONSE_SHAPE

# RESPONSE_SHAPE escapes its literal JSON braces (`{{`/`}}`) for reuse inside the other two
# templates below, which go through `.format()`; this one doesn't, so unescape them back here.
SYSTEM_PROMPT = SYSTEM_PROMPT.format()

# Keeps token usage/cost bounded; a few thousand words is plenty of context for a summary note.
MAX_INPUT_CHARS = 12000


def _placeholder(filename: str, reason: str) -> dict:
    title = filename.rsplit('.', 1)[0] or filename
    return {
        'type': Note.TYPE_FOOD,
        'title': title,
        'subject': title,
        'summary': f'AI summarization was not completed ({reason}).',
        'content': [
            f'Uploaded file: {filename}. {reason}.',
            'Edit this note manually, or retry the upload once resolved.',
        ],
        'conditions': ['Pending AI review'],
        'cautions': [],
        'alternatives': [],
        'dosage': '',
        'superiorFoods': [],
        'otherFoods': [],
        'verification': Note.VERIFICATION_UNVERIFIED,
        'verification_note': '',
    }


def _draft_from_document(text: str, filename: str) -> dict | None:
    """Returns None when the document isn't about a food/remedy or disease/condition —
    this platform's only two note types (see RESPONSE_SHAPE's not_relevant instruction)."""
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
    if result.get('type') == 'not_relevant':
        return None

    note_type = result.get('type') if result.get('type') in ('food', 'disease') else 'food'
    return {
        'type': note_type,
        'title': result.get('title') or filename,
        'subject': result.get('subject') or result.get('title') or filename,
        'summary': result.get('summary') or '',
        'content': _as_list(result.get('content')),
        'cautions': _as_list(result.get('cautions')),
        'conditions': result.get('conditions') or [],
        'alternatives': _as_list(result.get('alternatives')),
        'dosage': result.get('dosage') or '',
        'superiorFoods': result.get('superiorFoods') or [],
        'otherFoods': result.get('otherFoods') or [],
    }


def summarize_document(text: str, filename: str) -> dict | None:
    """Summarize an uploaded document's text into the note shape the frontend expects.

    Returns None if the document clearly isn't about a food/remedy or disease/condition —
    callers should reject the upload rather than create a note (this platform only stores
    notes on those two topics). Otherwise falls back to a clear placeholder (rather than
    raising) whenever summarization can't happen for other reasons, so a PDF upload always
    results in a usable note. A successful draft is then cross-checked against the web (see
    services/web_search.py) before being returned, so the result always carries a
    `verification` status the UI can flag to the practitioner.
    """
    if not text.strip():
        return _placeholder(filename, 'no readable text was found in the PDF')

    if not settings.OPENAI_API_KEY:
        return _placeholder(filename, 'OPENAI_API_KEY is not configured')

    try:
        draft = _draft_from_document(text, filename)
    except Exception as exc:  # noqa: BLE001 — any failure here must degrade gracefully
        return _placeholder(filename, f'the AI request failed ({exc.__class__.__name__})')

    if draft is None:
        return None

    check = verify_claim(draft)
    if check is None:
        return {**draft, 'verification': Note.VERIFICATION_UNVERIFIED, 'verification_note': 'Web verification was unavailable.'}
    if check.get('verified'):
        return {**draft, 'verification': Note.VERIFICATION_WEB_CONFIRMED, 'verification_note': ''}

    corrected = check.get('corrected') or draft
    return {
        **corrected,
        'verification': Note.VERIFICATION_AI_CORRECTED,
        'verification_note': check.get('note', ''),
    }
