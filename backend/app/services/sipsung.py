"""십성 (Ten Gods) relative to day master — simplified standard mapping."""

from __future__ import annotations

STEM_ELEM = {
    "甲": "wood",
    "乙": "wood",
    "丙": "fire",
    "丁": "fire",
    "戊": "earth",
    "己": "earth",
    "庚": "metal",
    "辛": "metal",
    "壬": "water",
    "癸": "water",
}
YANG = set("甲丙戊庚壬")
# 오행 상생: 목→화→토→금→수→목
GEN = {"wood": "fire", "fire": "earth", "earth": "metal", "metal": "water", "water": "wood"}
# 오행 상극: 목→토→수→화→금→목
CTRL = {"wood": "earth", "earth": "water", "water": "fire", "fire": "metal", "metal": "wood"}

# 지지 본기 (간략)
BRANCH_MAIN = {
    "子": "癸",
    "丑": "己",
    "寅": "甲",
    "卯": "乙",
    "辰": "戊",
    "巳": "丙",
    "午": "丁",
    "未": "己",
    "申": "庚",
    "酉": "辛",
    "戌": "戊",
    "亥": "壬",
}


def ten_god(day_master: str, other_stem: str) -> str:
    if day_master not in STEM_ELEM or other_stem not in STEM_ELEM:
        return "—"
    de, oe = STEM_ELEM[day_master], STEM_ELEM[other_stem]
    same_pol = (day_master in YANG) == (other_stem in YANG)
    if de == oe:
        return "비견" if same_pol else "겁재"
    if GEN[de] == oe:
        return "식신" if same_pol else "상관"
    if CTRL[de] == oe:
        return "편재" if same_pol else "정재"
    if CTRL[oe] == de:
        return "편관" if same_pol else "정관"
    if GEN[oe] == de:
        return "편인" if same_pol else "정인"
    return "—"


def branch_ten_god(day_master: str, branch: str) -> str:
    main = BRANCH_MAIN.get(branch)
    if not main:
        return "—"
    return ten_god(day_master, main)


def mingshi_table(result) -> dict:
    """Build 사주명식 table: year/month/day/hour stems & branches + 십성."""
    p = result.pillars
    dm = result.day_master
    cols = []
    order = [
        ("hour", "생시", p.hour),
        ("day", "생일", p.day),
        ("month", "생월", p.month),
        ("year", "생년", p.year),
    ]
    for key, label, sb in order:
        if sb is None:
            cols.append(
                {
                    "key": key,
                    "label": label,
                    "stem": "—",
                    "branch": "—",
                    "stem_god": "—",
                    "branch_god": "—",
                }
            )
            continue
        cols.append(
            {
                "key": key,
                "label": label,
                "stem": sb.stem,
                "branch": sb.branch,
                "stem_god": "일간" if key == "day" else ten_god(dm, sb.stem),
                "branch_god": branch_ten_god(dm, sb.branch),
            }
        )
    return {
        "day_master": dm,
        "columns": cols,  # 시 일 월 년 order (common display)
    }
