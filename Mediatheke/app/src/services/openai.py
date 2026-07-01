import json
import logging

from openai import OpenAI

from ...core.config import settings
from ..mediaitem.model import MediaItem
from ..mediaitem.schemas import MediaItemSeries
from .series_engine import classify, to_media_item_series


def _get_client() -> OpenAI:
    """Build an OpenAI-compatible client. base_url lets us hit OpenRouter."""
    kwargs = {"api_key": settings.openai_key}
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    return OpenAI(**kwargs)


def _provider_routing() -> dict:
    """Pin to a specific provider when requested via the OPENAI_PROVIDER env var.

    Cerebras on gpt-oss-120b gives ~2000 tok/s with ~1s first-token latency,
    which is dramatically faster than the default router. Trade-off is
    ~10x the cost of :floor routing.
    """
    name = (settings.openai_provider or "").strip().lower()
    if not name:
        return {}
    return {"provider": {"order": [name]}}


def _build_prompt(items: list[MediaItem]) -> str:
    """Build the prompt asking the LLM to identify series episodes."""
    lines = [
        "You are given a list of TV show entries. Identify which entries belong to the same series.",
        "For each series you find, return the series name, season number, and episode number.",
        "If an entry is not part of a series, omit it from the output.",
        "",
        "Entries (id: title | topic | channel | date | duration):",
    ]
    for item in items:
        lines.append(
            f"{item.id}: {item.title} | {item.topic} | {item.channel} | {item.date} | {item.duration}"
        )
    lines.append("")
    lines.append(
        'Return a JSON object of the form {"items": [...]}, where each item has '
        '"media_item_id" (int), "title" (str), "season_number" (int or 0 if unknown), '
        '"episode_number" (int or 0 if unknown), "series_name" (str).'
    )
    return "\n".join(lines)


def _parse_response(content: str) -> list[MediaItemSeries]:
    """Parse and validate the LLM's JSON response.

    Tolerant of markdown fences, leading prose, and trailing commentary.
    """
    if not content:
        return []

    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    if not text.startswith("{"):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]

    try:
        payload = json.loads(text)
        items = payload.get("items", [])
    except (json.JSONDecodeError, AttributeError, TypeError) as e:
        logging.error(f"Couldn't parse LLM response as JSON: {e}\nContent: {content[:500]}")
        return []

    results = []
    for item in items:
        try:
            results.append(
                MediaItemSeries(
                    media_item_id=item["media_item_id"],
                    title=item["title"],
                    episode_number=item.get("episode_number") or 0,
                    season_number=item.get("season_number") or 0,
                    series_name=item.get("series_name") or "",
                )
            )
        except Exception as e:
            logging.error(f"Couldn't validate series entry: {e}")
    return results


def run_conversation(items: list[MediaItem]) -> list[MediaItemSeries]:
    """Detect series membership.

    Two-tier engine (rules + title similarity) for the pre-pass, LLM for
    whatever the engine can't resolve.
    """
    classifications = classify(items)
    classified_ids = {c.media_item_id for c in classifications}
    unresolved = [item for item in items if item.id not in classified_ids]

    engine_results = to_media_item_series(classifications)

    if not unresolved:
        return engine_results

    client = _get_client()
    prompt = _build_prompt(unresolved)
    messages = [
        {
            "role": "system",
            "content": "You return only valid JSON. No prose, no markdown fences.",
        },
        {"role": "user", "content": prompt},
    ]

    # Reasoning models (e.g. gpt-oss) spend output budget on chain-of-thought
    # before the actual answer. Cap the reasoning effort so we don't run out
    # of tokens before the JSON response.
    extra_body = _provider_routing()
    extra_body["reasoning"] = {"effort": "low"}

    try:
        logging.info(
            f"Sending {len(unresolved)} items to {settings.openai_model} "
            f"(engine tagged {len(engine_results)} upfront)"
        )
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=4096,
            extra_body=extra_body,
        )
    except Exception as e:
        logging.warning(f"response_format rejected, retrying without: {e}")
        try:
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=0,
                max_tokens=4096,
                extra_body=extra_body,
            )
        except Exception as e2:
            logging.error(f"LLM request failed: {repr(e2)}")
            return engine_results

    content = response.choices[0].message.content
    return engine_results + _parse_response(content)
