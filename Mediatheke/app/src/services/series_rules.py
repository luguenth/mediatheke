"""Series detection rules.

Each rule uses named regex groups to extract series metadata from a title.
Named groups the engine recognises:
  - series:        the series name (used when series_from == "series")
  - season:        season number (optional)
  - episode:       episode number (required)
  - episode_title: episode subtitle (optional, extracted but not persisted)

series_from:
  - "series": use the "series" named group from the match
  - "topic":  use the MediaItem's topic field

channels: list of channel names (lowercase, case-insensitive match),
          or ["*"] for all channels.

Rules are evaluated top-to-bottom; first match wins.
Order specific (channel-scoped, anchored) → general (all channels).
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SeriesRule:
    id: str
    pattern: re.Pattern
    series_from: str  # "series" or "topic"
    channels: tuple[str, ...] = ("*",)
    default_season: int = 0


def _rule(
    id: str,
    pattern: str,
    series_from: str,
    channels: tuple = ("*",),
    default_season: int = 0,
) -> SeriesRule:
    return SeriesRule(
        id=id,
        pattern=re.compile(pattern),
        series_from=series_from,
        channels=tuple(c.lower() for c in channels),
        default_season=default_season,
    )


RULES: list[SeriesRule] = [
    # ── All channels: "Series Name Staffel N (ep/total)" — most specific, try first ──
    _rule(
        "all_staffel_parens",
        r"(?P<series>.+?)\s*Staffel (?P<season>\d+) \((?P<episode>\d+)/(?:\d+)\)",
        "series",
    ),
    _rule(
        "all_season_parens",
        r"(?P<series>.+?)\s*Season (?P<season>\d+) \((?P<episode>\d+)/(?:\d+)\)",
        "series",
    ),
    _rule(
        "all_saison_parens",
        r"(?P<series>.+?)\s*Saison (?P<season>\d+) \((?P<episode>\d+)/(?:\d+)\)",
        "series",
    ),
    _rule(
        "all_saison_parens_nospace",
        r"(?P<series>.+?)\s*saison (?P<season>\d+)\((?P<episode>\d+)/(?:\d+)\)",
        "series",
    ),
    _rule(
        "all_saison_parens_ut",
        r"(?P<series>.+?)\s*Saison (?P<season>\d+) \((?P<episode>\d+)/(?:\d+)\).*Untertitel\)",
        "series",
    ),
    _rule(
        "all_parens_ut",
        r"(?P<series>.+?)\s*\((?P<episode>\d+)/(?:\d+)\).*Untertitel\)",
        "series",
    ),

    # ── ARTE: "Series Name (ep/total)" with optional " - Episode Title" ──
    _rule(
        "arte_series_episode_in_parens",
        r"^(?P<series>.+?)\s*\((?P<episode>\d+)/(?:\d+)\)"
        r"(?:\s*-\s*(?P<episode_title>.+))?\s*$",
        "series",
        channels=("arte.de",),
    ),

    # ── ARD: "Staffel N,Folge M" (topic-based) ──
    _rule(
        "ard_staffel_folge",
        r"Staffel (?P<season>\d+),Folge (?P<episode>\d+)",
        "topic",
        channels=("ard",),
    ),
    _rule(
        "ard_s_e",
        r"\(S(?P<season>\d+)/E(?P<episode>\d+)\)",
        "topic",
        channels=("ard",),
    ),
    _rule(
        "all_s_e",
        r"\(S(?P<season>\d+)/E(?P<episode>\d+)\)",
        "topic",
    ),
    _rule(
        "ard_hash_number",
        r"#(?P<episode>\d+)",
        "topic",
        channels=("ard",),
    ),
    _rule(
        "all_hash_number",
        r"#(?P<episode>\d+)",
        "topic",
    ),

    # ── SRF: "Staffel N, Folge M" (topic-based) ──
    _rule(
        "srf_staffel_folge",
        r"Staffel (?P<season>\d+), Folge (?P<episode>\d+)",
        "topic",
        channels=("srf",),
    ),

    # ── HR ──
    _rule(
        "hr_staffel_folge_range",
        r"Staffel (?P<season>\d+), Folge (?P<episode>\d+)-\d+",
        "topic",
        channels=("hr",),
    ),
    _rule(
        "hr_staffel_folge_title",
        r"(?P<series>.+?)\s*Staffel (?P<season>\d+), Folge (?P<episode>\d+)",
        "series",
        channels=("hr",),
    ),
    _rule(
        "hr_folge_n",
        r"Folge (?P<episode>\d+)",
        "topic",
        channels=("hr",),
    ),
    _rule(
        "hr_folge_n_total",
        r"(?P<series>.+?)\s*Folge (?P<episode>\d+)/(?:\d+)",
        "series",
        channels=("hr",),
    ),
    _rule(
        "hr_parens_n_total",
        r"\((?P<episode>\d+)/(?:\d+)\)",
        "topic",
        channels=("hr",),
    ),

    # ── ZDF: "Series Name (N)" ──
    _rule(
        "zdf_parens_n",
        r"^(?P<series>[^\-–]+?)\s*\((?P<episode>\d+)\)\s*$",
        "series",
        channels=("zdf",),
    ),
    _rule(
        "all_parens_n",
        r"^(?P<series>[^\-–]+?)\s*\((?P<episode>\d+)\)\s*$",
        "series",
    ),
    _rule(
        "all_parens_n_topic",
        r"\((?P<episode>\d+)\)\s*$",
        "topic",
    ),

    # ── All channels: generic "(ep/total)" — title-based ──
    _rule(
        "all_parens_ep_total_title",
        r"^(?P<series>.+?)\s*\((?P<episode>\d+)/(?:\d+)\)",
        "series",
    ),

    # ── All channels: "Staffel N" (without episode number) ──
    _rule(
        "all_staffel_only",
        r"(?P<series>.+?)\s*Staffel (?P<season>\d+)(?:\s|$)",
        "series",
    ),

    # ── All channels: "Teil N" ──
    _rule(
        "all_teil_n",
        r"^(?P<series>.+?),?\s*Teil (?P<episode>\d+)",
        "series",
    ),

    # ── All channels: "Folge N" / "Episode N" (topic-based) ──
    _rule(
        "all_folge_n",
        r"Folge (?P<episode>\d+)",
        "topic",
    ),
    _rule(
        "all_episode_n",
        r"Episode (?P<episode>\d+)",
        "topic",
    ),
]
