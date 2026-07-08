import json

from django.conf import settings
from openai import OpenAI

SEARCH_PROMPT_TEMPLATE = """You are a clinical reference assistant helping a medical practitioner \
who found nothing in their local notes for: "{query}"

Search the web for reliable information connecting this food, remedy, or condition to what it \
helps with or is helped by. If "{query}" names a condition, focus on foods/remedies that help it; \
if it names a food/remedy, focus on the conditions it helps with or prevents.

Respond with ONLY a raw JSON object (no markdown code fences, no prose before or after) with \
exactly these keys:
- "title": short subject name (the food/remedy)
- "subject": same as title
- "conditions": array of short condition/symptom names
- "summary": a 1-2 sentence summary a practitioner can read in a few seconds
- "content": a fuller 3-6 sentence explanation, including any cautions or dosage notes

If you cannot find anything medically relevant for "{query}", respond with exactly: {{"not_found": true}}"""

VERIFY_PROMPT_TEMPLATE = """You are a clinical fact-checker. A colleague drafted this note from an \
uploaded document, which has NOT yet been checked against outside sources:

Subject: {subject}
Claimed conditions helped/prevented: {conditions}
Summary: {summary}
Content: {content}

Search the web for reliable sources and check whether these claims are accurate. Minor phrasing \
differences don't count as inaccurate — only flag genuine factual problems (wrong conditions, \
unsafe/missing cautions, fabricated claims).

Respond with ONLY a raw JSON object (no markdown code fences, no prose):
- If the claims hold up: {{"verified": true}}
- If something is wrong and should be corrected: {{"verified": false, "corrected": {{"title": "...", \
"subject": "...", "conditions": ["..."], "summary": "...", "content": "..."}}, "note": "one short \
sentence explaining what was wrong and what changed"}}"""


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


def search_for_note(query: str) -> dict | None:
    """Search the web for a note-shaped answer when nothing local matches a query.

    Returns None if search is unavailable, fails, or turns up nothing relevant — callers
    should fall back to the normal "no results" behavior in that case.
    """
    result = _call_web_search(SEARCH_PROMPT_TEMPLATE.format(query=query))
    if not result or result.get('not_found'):
        return None
    if not result.get('title') or not result.get('conditions'):
        return None
    return {
        'title': result['title'],
        'subject': result.get('subject') or result['title'],
        'conditions': result['conditions'],
        'summary': result.get('summary', ''),
        'content': result.get('content', ''),
    }


def verify_claim(draft: dict) -> dict | None:
    """Cross-check a draft PDF summary against the web.

    Returns None if the check itself couldn't be performed (caller should treat the draft as
    unverified rather than falsely marking it confirmed). Otherwise returns
    {"verified": True} or {"verified": False, "corrected": {...}, "note": "..."}.
    """
    prompt = VERIFY_PROMPT_TEMPLATE.format(
        subject=draft.get('subject', ''),
        conditions=', '.join(draft.get('conditions', [])),
        summary=draft.get('summary', ''),
        content=draft.get('content', ''),
    )
    result = _call_web_search(prompt)
    if not result or 'verified' not in result:
        return None
    return result
