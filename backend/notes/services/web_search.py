import json

from django.conf import settings
from openai import OpenAI

# Shared response contract for both the search-fallback and verification prompts below.
# All keys are always present (empty string/array when not applicable to the classified
# type) rather than conditionally present — simpler and more robust to parse.
RESPONSE_SHAPE = """Respond with ONLY a raw JSON object (no markdown code fences, no prose before or \
after) with exactly these keys, ALL always present:
- "type": either "food" or "disease" — classify the subject first
- "title": short subject name
- "subject": same as title, used for search matching
- "summary": a 1-2 sentence summary a practitioner can read in a few seconds
- "content": a fuller 3-6 sentence explanation

If type is "food", also fill in (leave the disease-only fields below as "" / []):
- "conditions": array of short condition/symptom names this food/remedy helps with or prevents
- "superiorBenefits": the single most important, best-evidenced benefit (a short sentence or two)
- "otherBenefits": other secondary benefits (a short sentence or two)
- "dosage": how to take it for maximum benefit — typical amount, form, timing
- "cautions": safety notes, contraindications, or who should avoid/limit it

If type is "disease", also fill in (leave "conditions", "superiorBenefits", "otherBenefits", \
"dosage", "cautions" as "" / []):
- "superiorFoods": array of up to 3 of the single best foods/remedies for managing this disease \
— REQUIRED, must not be omitted or left empty for a disease
- "otherFoods": array of other helpful foods/remedies beyond the top 3 — REQUIRED for a disease

Your JSON object MUST include every single key listed above, every time, with no exceptions. \
Never omit a key. Use "" or [] only for the keys that don't apply to the type you classified — \
never omit a key entirely, and never leave superiorFoods/otherFoods empty when type is "disease", \
or conditions empty when type is "food"."""

SEARCH_PROMPT_TEMPLATE = """You are a clinical reference assistant helping a medical practitioner \
who found nothing in their local notes for: "{query}"

Search the web for reliable information. First decide: is "{query}" a food/remedy, or a \
disease/condition?

""" + RESPONSE_SHAPE + """

If you cannot find anything medically relevant for "{query}", respond with exactly: {{"not_found": true}}"""

VERIFY_PROMPT_TEMPLATE = """You are a clinical fact-checker. A colleague drafted this note, which \
has NOT yet been checked against outside sources:

Type: {type}
Title/subject: {subject}
{claims}
Summary: {summary}
Content: {content}

Search the web for reliable sources and check whether these claims are accurate. Minor phrasing \
differences don't count as inaccurate — only flag genuine factual problems (wrong conditions/foods, \
unsafe/missing cautions, fabricated claims).

If the claims hold up, respond with ONLY: {{"verified": true}}

If something is wrong and should be corrected, respond with ONLY a raw JSON object (no markdown \
code fences, no prose) of the form {{"verified": false, "note": "one short sentence explaining what \
was wrong and what changed", "corrected": {{...}}}} where "corrected" is a full replacement note \
with the SAME type ("{type}") and follows this exact shape:

""" + RESPONSE_SHAPE


def _parse_json_response(text):
    cleaned = text.strip()
    if cleaned.startswith('```'):
        cleaned = cleaned.strip('`')
        if '\n' in cleaned:
            cleaned = cleaned.split('\n', 1)[1]
    return json.loads(cleaned)


def _call_web_search(prompt):
    if not settings.OPENAI_API_KEY:
        return None
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.responses.create(
            model=settings.OPENAI_MODEL,
            tools=[{'type': 'web_search'}],
            input=prompt,
        )
        return _parse_json_response(response.output_text)
    except Exception:  # noqa: BLE001 — web search is best-effort; caller degrades gracefully
        return None


def _note_shape_from_result(result):
    note_type = result.get('type') if result.get('type') in ('food', 'disease') else 'food'
    return {
        'type': note_type,
        'title': result.get('title') or '',
        'subject': result.get('subject') or result.get('title') or '',
        'summary': result.get('summary') or '',
        'content': result.get('content') or '',
        'conditions': result.get('conditions') or [],
        'superiorBenefits': result.get('superiorBenefits') or '',
        'otherBenefits': result.get('otherBenefits') or '',
        'dosage': result.get('dosage') or '',
        'cautions': result.get('cautions') or '',
        'superiorFoods': result.get('superiorFoods') or [],
        'otherFoods': result.get('otherFoods') or [],
    }


def search_for_note(query: str) -> dict | None:
    """Search the web for a note-shaped answer when nothing local matches a query.

    Returns None if search is unavailable, fails, or turns up nothing relevant — callers
    should fall back to the normal "no results" behavior in that case.
    """
    result = _call_web_search(SEARCH_PROMPT_TEMPLATE.format(query=query))
    if not result or result.get('not_found'):
        return None
    if not result.get('title'):
        return None
    return _note_shape_from_result(result)


def verify_claim(draft: dict) -> dict | None:
    """Cross-check a draft note (from a PDF) against the web.

    Returns None if the check itself couldn't be performed (caller should treat the draft as
    unverified rather than falsely marking it confirmed). Otherwise returns
    {"verified": True} or {"verified": False, "corrected": {...same shape as draft...}, "note": "..."}.
    """
    if draft.get('type') == 'disease':
        claims = (
            f"Claimed top 3 foods for management: {', '.join(draft.get('superiorFoods', []))}\n"
            f"Claimed other helpful foods: {', '.join(draft.get('otherFoods', []))}"
        )
    else:
        claims = (
            f"Claimed conditions helped/prevented: {', '.join(draft.get('conditions', []))}\n"
            f"Claimed superior benefit: {draft.get('superiorBenefits', '')}\n"
            f"Claimed other benefits: {draft.get('otherBenefits', '')}\n"
            f"Claimed dosage: {draft.get('dosage', '')}\n"
            f"Claimed cautions: {draft.get('cautions', '')}"
        )

    prompt = VERIFY_PROMPT_TEMPLATE.format(
        type=draft.get('type', 'food'),
        subject=draft.get('subject', ''),
        claims=claims,
        summary=draft.get('summary', ''),
        content=draft.get('content', ''),
    )
    result = _call_web_search(prompt)
    if not result or 'verified' not in result:
        return None
    if result.get('corrected'):
        result['corrected'] = _note_shape_from_result(result['corrected'])
    return result
