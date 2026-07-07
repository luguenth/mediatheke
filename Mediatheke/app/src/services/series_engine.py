"""Unified series detection engine.

Two-tier approach:
  1. Rule-based:     named-group regex rules (series_rules.py)
  2. Similarity:     cluster unresolved items by normalized title prefix

Items still unresolved after both tiers become candidates for the LLM
fallback in openai.py.
"""
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from ..mediaitem.model import MediaItem
from ..mediaitem.schemas import MediaItemSeries
from .series_rules import RULES, SeriesRule


# ──────────────────────────── Result type ────────────────────────────


@dataclass
class Classification:
    media_item_id: int
    title: str
    series_name: str
    season_number: int = 0
    episode_number: int = 0
    episode_title: str = ""
    source: str = ""  # "rule:<id>" or "similarity"


# ──────────────────────────── Helpers ────────────────────────────────


def _channel_matches(rule: SeriesRule, item_channel: str) -> bool:
    if "*" in rule.channels:
        return True
    return (item_channel or "").strip().lower() in rule.channels


def _to_int(value: str | None) -> int:
    if value is None:
        return 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def _clean_series_name(name: str) -> str:
    """Strip leading/trailing whitespace and common punctuation."""
    return name.strip(" \t-–:_").strip()


# Topic names that are too generic to be series names.
_STOP_WORDS: set[str] = {
    "fernsehfilme und serien - serien",
    "aktuelles und gesellschaft - reportagen und recherchen",
    "aktuelles",
    "folge",
    "serie",
    "serien",
    "zdfinfo",
    "zdfinfo - die einzeldokus",
    "zdfinfo doku",
}


def _is_valid_series_name(name: str) -> bool:
    if not name or len(name) < 2:
        return False
    if name.lower() in _STOP_WORDS:
        return False
    if len(name) > 100:
        return False
    return True


# ─────────────────────────── Tier 1: Rules ───────────────────────────


def classify_by_rules(item: MediaItem) -> Classification | None:
    """Try each rule in order; return the first match or None."""
    for rule in RULES:
        if not _channel_matches(rule, item.channel):
            continue
        match = rule.pattern.search(item.title)
        if not match:
            continue

        groups = match.groupdict()

        if rule.series_from == "topic":
            series_name = item.topic or ""
        else:
            series_name = groups.get("series", "")

        series_name = _clean_series_name(series_name)
        if not _is_valid_series_name(series_name):
            continue  # extracted name is garbage; try next rule

        episode_num = _to_int(groups.get("episode"))
        # Skip year patterns (e.g. "Auskreuzung (2011)") — not episode numbers.
        if 1900 <= episode_num <= 2099:
            continue

        return Classification(
            media_item_id=item.id,
            title=item.title,
            series_name=series_name,
            season_number=_to_int(groups.get("season")) or rule.default_season,
            episode_number=episode_num,
            episode_title=(groups.get("episode_title") or "").strip(),
            source=f"rule:{rule.id}",
        )
    return None


# ───────────────────────── Tier 2: Similarity ────────────────────────
#
# For items that no rule matched, normalise the title by stripping episode
# markers, season markers, variant suffixes, and trailing subtitles.
# Items that share the same normalised core (and had something stripped)
# are almost certainly episodes of the same series.

# Markers that contain a number — these are the real episode/season signals.
_NUMBER_MARKERS: list[re.Pattern] = [
    re.compile(r"\s*\(\d+/\d+\)\s*"),          # (3/7)
    re.compile(r"\s*\(\d+\)\s*$"),             # (5) at end
    re.compile(r"\s*Folge\s+\d+(/\d+)?\s*"),   # Folge 12 / Folge 12/24
    re.compile(r"\s*Staffel\s+\d+.*$", re.IGNORECASE),
    re.compile(r"\s*Season\s+\d+.*$", re.IGNORECASE),
    re.compile(r"\s*Saison\s+\d+.*$", re.IGNORECASE),
    re.compile(r"\s*\(S\d+/E\d+\)\s*"),        # (S01/E05)
    re.compile(r"\s*#\d+\s*"),                 # #001
    re.compile(r"\s*Episode\s+\d+\s*"),
]

# Subtitle-only marker — applied for normalisation but doesn't qualify an
# item for similarity on its own (no number = probably a coincidence).
_SUBTITLE_MARKER = re.compile(r"\s*-\s*[^-]+$")  # trailing " - subtitle"

_VARIANT_MARKERS = re.compile(
    r"\s*\((?:OV|UT|OmU|OmDU|O\.?m\.?U\.?)\)\s*",
    re.IGNORECASE,
)


def _strip_markers(title: str) -> str:
    """Strip episode/season markers and variant suffixes. Preserves case."""
    result = _VARIANT_MARKERS.sub(" ", title)
    for pattern in _NUMBER_MARKERS:
        result = pattern.sub("", result)
    result = _SUBTITLE_MARKER.sub("", result)
    return _clean_series_name(result)


def _normalize(title: str) -> tuple[str, bool]:
    """Return (normalised_core_lowercased, has_number_marker).

    has_number_marker is True only when the original title contained a
    number-based episode/season marker. Titles with only a subtitle suffix
    (no number) return False — they're usually coincidental matches.
    """
    stripped = _strip_markers(title)
    has_number_marker = any(p.search(title) for p in _NUMBER_MARKERS)
    return stripped.lower(), has_number_marker


def classify_by_similarity(items: list[MediaItem]) -> list[Classification]:
    """Cluster unresolved items by normalised title.

    Two passes:
      1. Core-based: group items that share the same normalised title core
         (episode/season markers stripped). Only items with a number marker
         are considered; groups with 2+ members become a series.
      2. Suffix-based: for items still unresolved, extract the segment after
         the first `` - `` as a candidate series name. This handles the format
         ``[Episode Subtitle] - [Series Name] (N)`` where the series name is a
         suffix rather than a prefix.
    """
    classified_ids: set[int] = set()
    results: list[Classification] = []

    # ── Pass 1: Core-based grouping ──────────────────────────────────
    # Group by (normalized_title, topic). Same title core but different
    # topic is almost certainly a coincidence, not the same series.
    groups: dict[tuple[str, str], list[MediaItem]] = defaultdict(list)
    for item in items:
        core, has_number_marker = _normalize(item.title)
        if not has_number_marker:
            continue
        if not _is_valid_series_name(core):
            continue
        topic = (item.topic or "").strip().lower()
        groups[(core, topic)].append(item)

    for _core, members in groups.items():
        if len(members) < 2:
            continue
        # Use original-cased stripped title from the first member.
        series_name = _strip_markers(members[0].title)
        if not _is_valid_series_name(series_name):
            continue
        for item in members:
            classified_ids.add(item.id)
            results.append(Classification(
                media_item_id=item.id,
                title=item.title,
                series_name=series_name,
                season_number=0,
                episode_number=0,
                source="similarity",
            ))

    # ── Pass 2: Suffix-based grouping ───────────────────────────────
    remaining = [item for item in items if item.id not in classified_ids]
    results.extend(_group_by_suffix(remaining))

    return results


def _group_by_suffix(items: list[MediaItem]) -> list[Classification]:
    """Group items whose series name appears as a suffix after the first `` - ``.

    Handles the format ``[Episode Subtitle] - [Series Name] (N)`` where the
    series name comes after the first regular-hyphen separator, not before
    the episode marker.

    Rules:
      - Extract the suffix after the first `` - ``.
      - Strip number/variant markers to get the clean series name.
      - Group by (normalised_suffix, topic).
      - Require at least one item in the group to have a number marker.
      - Include items without number markers if they share the same suffix.
    """
    suffix_map: dict[tuple[str, str], list[tuple[str, MediaItem, bool]]] = defaultdict(list)

    for item in items:
        title = item.title
        # Find the first regular-hyphen separator surrounded by optional whitespace.
        m = re.search(r"\s*-\s*", title)
        if not m:
            continue
        rest = title[m.end():]
        # Strip number & variant markers (NOT the subtitle marker).
        cleaned = _VARIANT_MARKERS.sub(" ", rest)
        for pat in _NUMBER_MARKERS:
            cleaned = pat.sub("", cleaned)
        suffix = cleaned.strip()
        if not _is_valid_series_name(suffix):
            continue
        has_number = any(p.search(title) for p in _NUMBER_MARKERS)
        # Normalise hyphens and en-dashes for grouping.
        norm_key = suffix.replace("–", "-").strip().lower()
        topic = (item.topic or "").strip().lower()
        suffix_map[(norm_key, topic)].append((suffix, item, has_number))

    results: list[Classification] = []
    for (_norm_key, _topic), members in suffix_map.items():
        if len(members) < 2:
            continue
        numbered = [m for m in members if m[2]]
        if not numbered:
            continue  # at least one item must have a number marker
        # Use the first member's original-cased suffix as the series name.
        series_name = members[0][0]
        for _, item, _ in members:
            results.append(Classification(
                media_item_id=item.id,
                title=item.title,
                series_name=series_name,
                season_number=0,
                episode_number=0,
                source="similarity",
            ))
    return results


# ──────────────────────────── Pipeline ───────────────────────────────


def classify(items: list[MediaItem]) -> list[Classification]:
    """Full classification: rules → similarity.

    Returns classifications for all matched items. Unmatched items are
    omitted (they become candidates for the LLM fallback in openai.py).
    """
    classifications: list[Classification] = []
    unresolved: list[MediaItem] = []

    for item in items:
        result = classify_by_rules(item)
        if result:
            classifications.append(result)
        else:
            unresolved.append(item)

    classifications.extend(classify_by_similarity(unresolved))
    return classifications


def to_media_item_series(
    classifications: Iterable[Classification],
) -> list[MediaItemSeries]:
    """Convert engine results to the MediaItemSeries schema for DB persistence."""
    return [
        MediaItemSeries(
            media_item_id=c.media_item_id,
            title=c.title,
            season_number=c.season_number,
            episode_number=c.episode_number,
            series_name=c.series_name,
        )
        for c in classifications
    ]
