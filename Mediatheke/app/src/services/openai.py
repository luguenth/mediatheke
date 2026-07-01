import csv
import json
import logging
import os
import re
from dataclasses import dataclass
from openai import OpenAI

from ...core.config import settings
from ..mediaitem.model import MediaItem
from ..mediaitem.schemas import MediaItemSeries

_CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "series-formats.csv",
)


@dataclass(frozen=True)
class _FormatPattern:
    regex: re.Pattern
    series_identifier: str  # "topic" or "title"
    with_season: bool
    channel: str  # "all", "ard", "srf", "hr", "zdf", ...


def _load_patterns() -> list[_FormatPattern]:
    patterns: list[_FormatPattern] = []
    try:
        with open(_CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=";")
            next(reader)  # skip header
            for row in reader:
                if len(row) < 5 or not row[1].strip():
                    continue
                try:
                    patterns.append(
                        _FormatPattern(
                            regex=re.compile(row[1]),
                            series_identifier=row[2].strip(),
                            with_season=row[3].strip().lower() == "true",
                            channel=row[4].strip().lower(),
                        )
                    )
                except re.error as e:
                    logging.warning(f"Skipping invalid series regex {row[1]!r}: {e}")
    except FileNotFoundError:
        logging.warning(f"series-formats.csv not found at {_CSV_PATH}; regex pre-pass disabled")
    return patterns


# Load at import time so it's cached for the process lifetime.
_EPISODE_PATTERNS: list[_FormatPattern] = _load_patterns()


def _channel_matches(pattern_channel: str, item_channel: str) -> bool:
    if pattern_channel == "all":
        return True
    return (item_channel or "").strip().lower() == pattern_channel


def _extract_numbers(match: re.Match, with_season: bool) -> tuple[int, int]:
    """Return (season_number, episode_number) from a regex match.

    The CSV's season_digit and episode_digit columns tell us which capture
    groups hold the season and episode numbers, but they're 1-based and
    1-indexed past the implicit "0" placeholder for absent seasons. We
    sniff the first two groups when with_season is set, else only one.
    """
    groups = [g for g in match.groups() if g is not None]
    if with_season and len(groups) >= 2:
        return int(groups[0]), int(groups[1])
    return 0, int(groups[0])


def _classify_by_regex(item: MediaItem) -> MediaItemSeries | None:
    """If the title matches a curated pattern from series-formats.csv, tag it.

    Series name comes from the topic (Filmliste taxonomy) for "topic"
    patterns, and from the title minus the matched substring for "title"
    patterns. If we can't derive a sensible name we leave it empty and
    let the LLM fill it in.
    """
    for pat in _EPISODE_PATTERNS:
        if not _channel_matches(pat.channel, item.channel):
            continue
        match = pat.regex.search(item.title)
        if not match:
            continue
        season_number, episode_number = _extract_numbers(match, pat.with_season)

        if pat.series_identifier == "topic":
            series_name = item.topic or ""
        else:
            # Use the part of the title BEFORE the match as the series name.
            # This gives a consistent name across episodes (e.g. "Happiness")
            # instead of the old approach which kept the varying subtitle.
            series_name = item.title[:match.start()].strip(" -–:")
            if not series_name:
                series_name = item.topic or ""

        return MediaItemSeries(
            media_item_id=item.id,
            title=item.title,
            season_number=season_number,
            episode_number=episode_number,
            series_name=series_name,
        )
    return None


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


def _build_llm_prompt(items: list[MediaItem]) -> str:
    """Enhanced prompt with full context (title, description, topic) for LLM mode."""
    lines = [
        "You are given a list of TV show entries. For each entry, extract:",
        "- series_name: the series/show name",
        "- season_number: the season number (0 if unknown)",
        "- episode_number: the episode number (0 if unknown)",
        "- is_original_version: true if this is the original language version",
        "- language: the language of this entry (e.g. 'German', 'English', 'French')",
        "- has_subtitles: true if subtitles are available (e.g. 'mit Untertitel' in title)",
        "",
        "Use the title, description, and topic together to determine the series.",
        "The description often reveals whether this is the original or a dubbed version.",
        "If an entry is not part of a series, omit it from the output.",
        "",
        "Entries (id: title | topic | channel | description):",
    ]
    for item in items:
        desc = (item.description or "")[:200]
        lines.append(
            f"{item.id}: {item.title} | {item.topic} | {item.channel} | {desc}"
        )
    lines.append("")
    lines.append(
        'Return a JSON object of the form {"items": [...]}, where each item has '
        '"media_item_id" (int), "title" (str), "season_number" (int or 0 if unknown), '
        '"episode_number" (int or 0 if unknown), "series_name" (str), '
        '"is_original_version" (bool), "language" (str), "has_subtitles" (bool).'
    )
    return "\n".join(lines)


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


def _call_llm(items: list[MediaItem], prompt_builder) -> list[MediaItemSeries]:
    """Shared helper: send items to the LLM, parse and return the response."""
    if not items:
        return []

    client = _get_client()
    prompt = prompt_builder(items)
    messages = [
        {
            "role": "system",
            "content": "You return only valid JSON. No prose, no markdown fences.",
        },
        {"role": "user", "content": prompt},
    ]

    extra_body = _provider_routing()
    extra_body["reasoning"] = {"effort": "low"}

    logging.info(f"Sending {len(items)} items to {settings.openai_model}")

    try:
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
            return []

    content = response.choices[0].message.content
    return _parse_response(content)


def _run_llm_all(items: list[MediaItem]) -> list[MediaItemSeries]:
    """LLM-only path: skip regex, classify everything with full context."""
    return _call_llm(items, _build_llm_prompt)


def run_conversation(items: list[MediaItem], method: str = "regex") -> list[MediaItemSeries]:
    """Detect series membership.

    method='regex' (default): regex pre-pass for obvious patterns, LLM for the rest.
    method='llm':        skip regex, send everything to the LLM with full context.
    """
    if method == "llm":
        return _run_llm_all(items)

    # Original regex + LLM fallback path
    regex_results: list[MediaItemSeries] = []
    unresolved: list[MediaItem] = []
    for item in items:
        tagged = _classify_by_regex(item)
        if tagged:
            regex_results.append(tagged)
        else:
            unresolved.append(item)

    if not unresolved:
        return regex_results

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
            f"(regex tagged {len(regex_results)} upfront)"
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
            return regex_results

    content = response.choices[0].message.content
    return regex_results + _parse_response(content)
