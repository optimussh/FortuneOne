"""Shared types for pillar fact engines (commercial-safe adapters only)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"


@dataclass
class PillarFact:
    stem: str
    branch: str

    @property
    def pair(self) -> str:
        return f"{self.stem}{self.branch}"

    def as_dict(self) -> dict[str, str]:
        return {"stem": self.stem, "branch": self.branch}


@dataclass
class EngineChart:
    """Normalized four-pillar chart from one licensed engine."""

    engine_id: str
    license: str  # e.g. MIT
    package: str
    year: PillarFact
    month: PillarFact
    day: PillarFact
    hour: PillarFact | None
    extra: dict[str, Any] = field(default_factory=dict)
    ok: bool = True
    error: str | None = None

    def pillars_dict(self) -> dict[str, Any]:
        return {
            "year": self.year.as_dict(),
            "month": self.month.as_dict(),
            "day": self.day.as_dict(),
            "hour": self.hour.as_dict() if self.hour else None,
        }

    def signature(self) -> str:
        h = self.hour.pair if self.hour else "--"
        return f"{self.year.pair}|{self.month.pair}|{self.day.pair}|{h}"


@dataclass
class ChartFacts:
    """Merged commercial-safe fact layer."""

    primary_engine: str
    year: PillarFact
    month: PillarFact
    day: PillarFact
    hour: PillarFact | None
    day_master: str
    engines: list[EngineChart]
    agreement: bool
    warnings: list[str] = field(default_factory=list)
    licenses: list[dict[str, str]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "primary_engine": self.primary_engine,
            "pillars": {
                "year": self.year.as_dict(),
                "month": self.month.as_dict(),
                "day": self.day.as_dict(),
                "hour": self.hour.as_dict() if self.hour else None,
            },
            "day_master": self.day_master,
            "agreement": self.agreement,
            "warnings": self.warnings,
            "licenses": self.licenses,
            "engines": [
                {
                    "engine_id": e.engine_id,
                    "license": e.license,
                    "package": e.package,
                    "ok": e.ok,
                    "error": e.error,
                    "signature": e.signature() if e.ok else None,
                    "pillars": e.pillars_dict() if e.ok else None,
                    "extra": e.extra,
                }
                for e in self.engines
            ],
        }


def split_pair(pair: str) -> PillarFact:
    pair = (pair or "").strip()
    if len(pair) >= 2 and pair[0] in STEMS and pair[1] in BRANCHES:
        return PillarFact(stem=pair[0], branch=pair[1])
    raise ValueError(f"invalid pillar pair: {pair!r}")
