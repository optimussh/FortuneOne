# -*- coding: utf-8 -*-
"""
Polish product catalog for FO product quality:
- re-tag categories (money/career/love/etc.)
- rewrite titles + detail copy (no commercial scrape body)
- expand result section labels
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "product_catalog.json"

# keyword buckets — first match wins by priority score
CAT_DEFS: list[tuple[str, str, list[str], int]] = [
    # id, label, keywords, priority weight
    ("free", "무료·체험", ["무료"], 100),
    (
        "money",
        "재물·금전",
        [
            "재물", "금전", "돈", "부자", "재테크", "투자", "모으", "유실", "재산",
            "수입", "지출", "주식", "부동산", "월급", "연봉", "복권", "재성",
            "경제", "풍요", "부유", "빚", "대출", "사업 수익", "재복", "재운",
            "금운", "돈복", "부귀", "재물운", "금전운", "부적", "로또",
        ],
        95,
    ),
    (
        "career",
        "직장·사업",
        [
            "직장", "사업", "동업", "상사", "부하", "이직", "취업", "승진", "회사",
            "직업", "업무", "커리어", "창업", "조직", "동료", "면접", "명예", "출세",
            "퇴사", "연봉 협상", "진로", "업무운", "직장운", "사업운",
        ],
        88,
    ),
    (
        "newyear",
        "신년·연간",
        ["2026", "신년", "올해", "연간", "12개월", "토정", "세운", "월별", "한 해", "세배"],
        80,
    ),
    (
        "marriage",
        "결혼·배우자",
        ["결혼", "배우자", "신랑", "신부", "웨딩", "혼인", "약혼", "혼기", "시댁", "처가"],
        75,
    ),
    (
        "compat",
        "궁합·관계",
        ["궁합", "두 사람", "우리 둘", "호흡", "상성", "케미", "둘의"],
        70,
    ),
    (
        "love",
        "연애·인연",
        [
            "연애", "사랑", "인연", "만남", "짝", "고백", "이별", "재회", "솔로", "썸",
            "연인", "애정", "이성", "첫사랑", "소개팅", "그 사람", "상대", "남자", "여자",
            "마음", "감정", "로맨스",
        ],
        60,
    ),
    (
        "life",
        "평생·사주풀이",
        ["평생", "사주", "인생", "명리", "기질", "성격", "팔자", "총운", "운명", "타고난"],
        55,
    ),
    (
        "theme",
        "테마·기타",
        ["자녀", "꿈", "혈액", "별자리", "타로", "주간", "월간", "오늘", "건강", "가족"],
        40,
    ),
]

SECTION_BY_CAT: dict[str, list[str]] = {
    "newyear": [
        "한 해 총평",
        "상반기 흐름",
        "하반기 흐름",
        "월별 포인트 맵",
        "기회 구간",
        "주의 구간",
        "인간·직장 연결",
        "실천 로드맵",
    ],
    "love": [
        "인연의 결",
        "끌림 패턴",
        "만남 시기",
        "표현·소통",
        "오해·갈등 포인트",
        "관계 회복 팁",
        "정리·거리 두기",
        "한 달 실천 체크",
    ],
    "marriage": [
        "배우자 상",
        "혼인 흐름",
        "가정 안정 조건",
        "갈등 조율",
        "시기별 조언",
        "재정·생활 호흡",
        "함께 키울 습관",
        "장기 로드맵",
    ],
    "compat": [
        "기질 비교",
        "보완 포인트",
        "충돌 포인트",
        "감정 온도차",
        "대화 운영법",
        "생활 리듬",
        "함께할 실천",
        "장기 호흡",
    ],
    "money": [
        "재물 그릇",
        "수입 리듬",
        "지출·누수",
        "투자 태도",
        "문서·계약",
        "사람·동업",
        "지키는 습관",
        "올해 우선순위",
    ],
    "career": [
        "일 기질",
        "역할 궁합",
        "조직 호흡",
        "전환 타이밍",
        "성장 루트",
        "성과 루틴",
        "관계 리스크",
        "다음 분기 액션",
    ],
    "life": [
        "기질 구조",
        "초년 흐름",
        "중년 흐름",
        "말년 흐름",
        "강점 활용",
        "보완 포인트",
        "인간관계 기본",
        "평생 테마",
    ],
    "theme": [
        "핵심 요약",
        "상세 해석 1",
        "상세 해석 2",
        "환경·타이밍",
        "주의 포인트",
        "기회 포인트",
        "실천 제안",
        "한 줄 메모",
    ],
    "free": ["간단 요약", "오늘의 팁", "주의 한 가지"],
}

# FO title templates by category — {theme} filled from source signals
TITLE_BANK: dict[str, list[str]] = {
    "newyear": [
        "2026 연간 흐름 리포트",
        "한 해 세운 가이드",
        "신년 로드맵 풀이",
        "12개월 운 리듬 맵",
        "연간 기회·주의 체크",
        "2026 상하반기 전략",
        "세운 기반 실천 플랜",
        "연간 명리 브리핑",
        "새해 방향 설정 리포트",
        "한 해 총운·월운 패키지",
        "2026 흐름 압축 해석",
        "연간 선택 가이드",
        "신년 테마 리딩",
    ],
    "love": [
        "인연 결 읽기",
        "끌림 패턴 분석",
        "만남 타이밍 힌트",
        "애정 소통 스타일",
        "마음 거리 조절법",
        "솔로 구간의 기회",
        "재회·정리 가이드",
        "이성 운 리듬",
        "소개팅·만남 전 체크",
        "감정 기복 다루기",
        "인연의 문 열기",
        "관계 온도 맞추기",
        "연애 흐름 브리핑",
        "호감 신호 해석",
        "애정운 실천 노트",
    ],
    "marriage": [
        "배우자 상 스케치",
        "혼인 흐름 리포트",
        "가정 안정의 조건",
        "결혼 시기 힌트",
        "부부 호흡 가이드",
        "혼기 전후 체크",
        "배우자 인연 맵",
        "가정 재정 호흡",
        "결혼 결정 전 점검",
        "동반 생활 루틴",
        "배우자 궁합 브리프",
        "혼인 로드맵",
    ],
    "compat": [
        "두 사람 기질 비교",
        "상성·호흡 리포트",
        "보완과 충돌 맵",
        "대화 온도 맞추기",
        "장기 동반 가이드",
        "관계 운영 매뉴얼",
        "케미 분석 브리핑",
        "함께할 때 실천표",
    ],
    "money": [
        "재물 그릇 진단",
        "수입·지출 리듬",
        "지키는 재테크 태도",
        "문서·계약 주의보",
        "재물 누수 점검",
        "올해 금전 우선순위",
        "현금흐름 가이드",
        "투자 규모 조절법",
    ],
    "career": [
        "일 기질 진단",
        "조직 역할 궁합",
        "이직·전환 타이밍",
        "성과 루틴 설계",
        "상사·동료 호흡",
        "커리어 성장 루트",
        "사업 확장 체크",
        "분기 액션 플랜",
    ],
    "life": [
        "평생 기질 구조",
        "초중말 인생 흐름",
        "타고난 강점 활용",
        "보완 포인트 처방",
        "인간관계 기본기",
        "생활 리듬 설계",
        "팔자 흐름 다시 읽기",
        "평생 테마 리포트",
    ],
    "theme": [
        "테마 집중 풀이",
        "상황별 힌트 모음",
        "타이밍 브리핑",
        "선택 전 체크리스트",
        "환경 맞추기 가이드",
        "단기 흐름 해석",
        "주제별 실천 노트",
        "한 주제 심화 리딩",
    ],
    "free": [
        "무료 간단 브리핑",
        "오늘 참고 한 줄",
        "체험용 요약 운세",
    ],
}

ROLE_NOTE = (
    "상세 사주 탭(오늘·신년·토정·부자되기)은 기본 제공 리포트이고, "
    "스토어 상품은 주제를 더 깊게 파는 유료(모의) 패키지입니다."
)


def _h(s: str) -> int:
    x = 2166136261
    for ch in s:
        x ^= ord(ch)
        x = (x * 16777619) & 0x7FFFFFFF
    return x


def _pick(seed: int, options: list[str]) -> str:
    return options[seed % len(options)] if options else ""


def score_category(title: str, source_title: str) -> tuple[str, str]:
    text = f"{source_title} {title}"
    best = ("theme", "테마·기타", -1)
    for cid, label, keys, weight in CAT_DEFS:
        hits = sum(1 for k in keys if k in text)
        if hits == 0:
            continue
        score = hits * 10 + weight
        if cid == "marriage" and any(k in text for k in ["결혼", "배우자", "혼인", "혼기", "웨딩"]):
            score += 40
        if cid == "money" and any(k in text for k in ["재물", "금전", "부자", "재테크", "재운", "금운"]):
            score += 35
        if cid == "career" and any(k in text for k in ["직장", "직업", "사업", "이직", "승진", "진로"]):
            score += 35
        # "직업" inside marriage titles (배우자 직업) → prefer marriage if 결혼 present
        if cid == "career" and any(k in text for k in ["결혼", "배우자", "혼인", "혼기"]):
            score -= 50
        if score > best[2]:
            best = (cid, label, score)
    return best[0], best[1]


def fo_title(cat: str, idx: int, source: str) -> str:
    """FO-owned title only — no leftover commercial phrasing, no cross-cat tags."""
    bank = TITLE_BANK.get(cat) or TITLE_BANK["theme"]
    base = bank[idx % len(bank)]
    # uniquify within category when bank wraps
    if idx >= len(bank):
        return f"{base} #{idx // len(bank) + 1}"
    return base


def subtitle_for(cat: str, title: str, label: str) -> str:
    seed = _h(title + cat)
    hooks = {
        "newyear": [
            f"{label} · 한 해 선택 기준을 세우는 연간 심화",
            f"{label} · 상·하반기 리듬과 실행 우선순위",
            f"{label} · 월별 밀고 쉴 구간을 한눈에",
        ],
        "love": [
            f"{label} · 끌림·표현·정리까지 패턴으로 읽기",
            f"{label} · 오늘의 점수 대신 ‘왜 반복되는지’",
            f"{label} · 만남 전·썸·정리 구간에 바로 쓰는 문장",
        ],
        "marriage": [
            f"{label} · 배우자 상·생활 루틴·가정 경제 호흡",
            f"{label} · 혼인 전후 결정 전 체크리스트형",
            f"{label} · 장기 동반을 전제로 한 현실 조언",
        ],
        "compat": [
            f"{label} · 두 사람 기질 비교와 운영 매뉴얼",
            f"{label} · 충돌 포인트와 복구 규칙까지",
            f"{label} · 상대 프로필 연동 시 더 선명",
        ],
        "money": [
            f"{label} · 재물 그릇·누수·지키는 습관 중심",
            f"{label} · 부자되기 캘린더와 짝을 이루는 태도 심화",
            f"{label} · 큰 지출·계약 전 한 번 더 보는 리포트",
        ],
        "career": [
            f"{label} · 역할 궁합·전환 타이밍·성과 루틴",
            f"{label} · 이직·승진·사업 확장 전 참고용",
            f"{label} · 조직 안 포지션을 선명히",
        ],
        "life": [
            f"{label} · 초·중·말 흐름과 평생 테마",
            f"{label} · 기질 구조를 깊게 다시 읽기",
            f"{label} · 인생풀이 탭보다 구간별 실천이 촘촘",
        ],
        "theme": [
            f"{label} · 한 질문에 초점을 모은 집중 풀이",
            f"{label} · 상황·타이밍·실천까지 한 패키지",
            f"{label} · 짧고 깊게, 바로 쓰는 조언",
        ],
        "free": [
            f"{label} · 맛보기 요약 · 깊은 주제는 스토어에서",
            f"{label} · 가볍게 시작하는 첫 리포트",
        ],
    }
    return _pick(seed, hooks.get(cat, hooks["theme"]))


def diff_from_free_tabs(cat: str, title: str) -> str:
    """Category-specific comparison vs free /me tabs — not the same generic line."""
    seed = _h(title + "diff" + cat)
    base = (
        "상세 사주 탭의 오늘·신년·토정·부자되기·오행·인생풀이는 로그인 후 기본으로 볼 수 있는 리포트입니다. "
        f"「{title}」은 그중 한 주제를 깊게 파고, 결제(모의) 후 내 사주 프로필로 다시 생성되는 스토어 패키지입니다."
    )
    extra = {
        "newyear": (
            " 신년 탭이 ‘한 해 테마 스케치’라면, 이 상품은 상·하반기 전략·월 리듬·실행 우선순위를 "
            "로드맵 문장으로 더 촘촘히 적습니다. 매일 바뀌는 일운 대신, 분기 단위 결정을 돕습니다."
        ),
        "love": (
            " 오늘의 연애 점수나 토정의 애정 한 줄과 달리, 끌림 패턴·표현 습관·만남/정리 타이밍·한 달 실천까지 "
            "관계 운영 관점으로 풀어 드립니다. ‘지금 기분’보다 ‘왜 같은 장면이 반복되는지’에 가깝습니다."
        ),
        "marriage": (
            " 신년·토정의 가정·인연 요약보다 배우자 상, 혼인 전후 조건, 생활·재정 호흡, 갈등 조율 규칙을 "
            "장기 동반 전제로 다룹니다. 결혼·동거·가족 경계 결정 전 체크리스트로 쓰기 좋습니다."
        ),
        "compat": (
            " 한 사람 기준 기본 탭과 달리, 두 사람 기질 대비·충돌/보완·대화 운영·복구 규칙을 중심으로 합니다. "
            "상대 프로필을 함께 고르면 일간·오행 대비가 더 선명해집니다."
        ),
        "money": (
            " 부자되기 탭이 월 등급·일자 캘린더(언제 줄이고 움직일지)라면, 이 상품은 재물 그릇·누수·계약·동업 태도·"
            "지키는 습관 같은 ‘어떻게 다루는지’에 집중합니다. 둘을 같이 보면 시기+태도가 맞춰집니다."
        ),
        "career": (
            " 일운·신년의 직장 한 줄보다 역할 궁합, 조직 호흡, 이직·전환 타이밍, 성과 루틴, 관계 리스크를 "
            "의사결정용 문장으로 정리합니다. 면접·이직·승진·창업 전 참고용입니다."
        ),
        "life": (
            " 인생풀이 탭과 골격은 비슷하지만, 상품별로 초·중·말 구간·강점 처방·관계 기본기를 "
            "더 긴 섹션으로 나눕니다. ‘나는 어떤 사람인가’를 한 번 제대로 정리하고 싶을 때 적합합니다."
        ),
        "theme": (
            " 기본 탭이 넓게 훑는다면, 이 패키지는 제목이 가리키는 상황 하나에 초점을 모아 "
            "환경·타이밍·주의·실천을 한 번에 담습니다. 질문 하나를 끝내는 용도로 쓰기 좋습니다."
        ),
        "free": (
            " 무료 체험 요약입니다. 깊이 있는 주제 해석·긴 실천 로드맵은 유료(모의) 스토어 상품에서 이어집니다."
        ),
    }
    cta = _pick(
        seed,
        [
            " 결과는 웹 7일·메일 링크 30일 다시보기할 수 있어, 결정이 필요할 때마다 펼쳐 보시면 됩니다.",
            " 결제 후 내 구매·다시보기에서 기간 안에 다시 열 수 있습니다.",
            " 같은 사주·같은 상품이면 골격 문장이 안정적으로 유지됩니다.",
        ],
    )
    return base + extra.get(cat, extra["theme"]) + cta


def intro_blurbs(cat: str, title: str) -> list[str]:
    """Long, topic-specific product page copy (~3x previous)."""
    seed = _h(title + cat)
    s2 = seed // 7

    hook = {
        "newyear": _pick(
            seed,
            [
                f"올해를 ‘대충 지나가는 한 해’로 두지 않으려면, 방향보다 먼저 리듬이 필요합니다. 「{title}」은 회원님 사주 원국(양력·시진 반영)을 기준으로 2026년 전후 흐름을 로드맵처럼 풀어, 언제 밀고 언제 쉬고 언제 점검할지 문장으로 남깁니다.",
                f"신년 운세를 읽고도 ‘그래서 이번 달에 뭘 하지?’가 남았다면 「{title}」이 그 빈칸을 채웁니다. 원국의 일간·오행 강약을 바탕으로 상·하반기 비중, 기회 구간, 주의 구간을 실행 가능한 언어로 정리합니다.",
                f"계획은 많은데 우선순위가 흔들릴 때 「{title}」을 열어 보세요. 한 해 총평만으로 끝내지 않고, 월 리듬·인간·일 연결·실천 로드맵까지 이어서 적어 의사결정 피로를 줄입니다.",
            ],
        ),
        "love": _pick(
            seed,
            [
                f"호감은 있는데 타이밍이 안 맞거나, 같은 이별 패턴이 반복된다면 점수보다 패턴이 먼저입니다. 「{title}」은 회원님 사주로 끌림의 결, 표현 방식, 만남·정리 구간, 한 달 실천까지 이야기형으로 풀어 ‘다음에 같은 장면’을 줄이는 데 초점을 둡니다.",
                f"오늘의 연애운이 좋아도 말실수 한 번에 분위기가 꺾일 수 있습니다. 「{title}」은 원국 기반 애정 기질을 읽어, 상대 속도를 존중하는 소통법·오해 포인트·거리 조절 규칙을 구체적으로 담습니다.",
                f"솔로 구간이 길거나 썸이 늘 애매하게 끝난다면 「{title}」에서 인연의 문과 준비된 일정, 확인 질문의 힘을 함께 점검해 보세요. 감정에 휩쓸리기 전, 스스로 쓰는 관계 매뉴얼이 생깁니다.",
            ],
        ),
        "marriage": _pick(
            seed,
            [
                f"결혼은 로맨스의 끝이 아니라 생활 운영의 시작입니다. 「{title}」은 배우자 상·혼인 흐름·가정 안정 조건·재정·갈등 조율을 장기 동반 관점으로 정리해, ‘설레는 사람’과 ‘함께 살아질 사람’의 간극을 현실적으로 보여 줍니다.",
                f"혼인·동거·가족 경계 결정 전에 감만으로 밀고 나가기 불안하다면 「{title}」을 기준점 삼아 보세요. 사주 원국으로 배우자 이미지와 생활 루틴 궁합, 시기별 조언을 체크리스트처럼 제공합니다.",
                f"시댁·처가·돈·주거 — 결혼 후 갈등의 대부분이 여기서 시작됩니다. 「{title}」은 그 세 축을 미리 문장으로 합의할 수 있게, 가정 경제 호흡과 함께 키울 습관까지 이어서 적습니다.",
            ],
        ),
        "compat": _pick(
            seed,
            [
                f"사랑하는 사람과도 ‘말의 온도’가 다르면 매일 소모전이 됩니다. 「{title}」은 두 사람(본인+상대 프로필) 기질을 나란히 놓고 보완·충돌·대화 운영·복구 규칙을 제시해, 틀린 점이 아니라 분업 재료로 읽게 돕습니다.",
                f"궁합 점수 하나로 관계를 판단하기보다, 어긋난 날 어떻게 복구할지가 더 중요합니다. 「{title}」은 감정 온도차·생활 리듬·장기 호흡을 운영 매뉴얼 톤으로 정리합니다.",
                f"연인·부부·파트너십 — 같이 갈 사람이 정해졌다면 다음은 운영입니다. 「{title}」에서 강점 분배와 사과 타이밍, 함께할 실천표를 확인해 보세요.",
            ],
        ),
        "money": _pick(
            seed,
            [
                f"돈은 ‘얼마나 버느냐’보다 ‘어디서 새고, 어떤 태도로 지키느냐’에서 갈립니다. 「{title}」은 사주 재물 그릇·수입 리듬·지출 누수·문서·동업 리스크를 다뤄, 부자되기 탭의 월·일 캘린더와 짝을 이루는 태도 심화 리포트입니다.",
                f"투자·계약·보증 앞에서 마음이 급해질 때 「{title}」을 한 번 펼쳐 보세요. 손안의 현금 범위, 기록 습관, 올해 금전 우선순위를 원국 기준으로 차분히 짚어 충동 결정을 줄입니다.",
                f"수입은 늘었는데 통장이 그대로라면 누수 점검이 먼저입니다. 「{title}」은 지키는 재테크 태도·현금흐름·사람/동업 포인트를 실천 문장으로 남깁니다.",
            ],
        ),
        "career": _pick(
            seed,
            [
                f"열심히 하는데 평가가 안 따라오거나, 이직 타이밍만 고민 중이라면 역할 궁합을 다시 볼 때입니다. 「{title}」은 일 기질·조직 호흡·전환 시점·성과 루틴·관계 리스크를 의사결정용으로 정리합니다.",
                f"면접·연봉 협상·퇴사·창업 전, 감정의 정점보다 대안이 준비된 뒤가 안전합니다. 「{title}」은 회원님 사주로 맞는 포지션과 분기 액션을 구체화합니다.",
                f"상사·동료와의 마찰은 업무 기준 문장만 맞춰도 상당 부분 예방됩니다. 「{title}」에서 성장 루트와 다음 분기 우선순위를 확인해 보세요.",
            ],
        ),
        "life": _pick(
            seed,
            [
                f"짧은 운세로는 안 풀리는 ‘나는 왜 이런 선택을 반복하지?’가 있다면 「{title}」이 맞습니다. 초년·중년·말년 흐름과 기질 구조, 강점 처방, 평생 테마를 길게 읽어 자기 이해의 기준선을 만듭니다.",
                f"인생풀이 탭을 봤어도 구간별 실천이 Vague했다면 「{title}」에서 더 촘촘한 섹션으로 다시 정리해 보세요. 건강·관계·일 중 한 분기에 하나만 올려도 충분하다는 메시지와 함께 갑니다.",
                f"팔자를 바꾸기보다, 타고난 결을 잘 쓰는 편이 빠릅니다. 「{title}」은 원국 기반으로 강점을 앞에, 약점을 루틴으로 메우는 전략을 담습니다.",
            ],
        ),
        "theme": _pick(
            seed,
            [
                f"질문이 하나인데 정보가 너무 많으면 오히려 결정이 흐려집니다. 「{title}」은 그 주제 하나에 초점을 모아 핵심·환경·타이밍·주의·실천을 한 패키지로 제공합니다.",
                f"지금 당장 선택해야 하는 상황이라면 「{title}」처럼 좁고 깊은 리포트가 유리합니다. 사주 원국에 상황을 겹쳐, 바로 쓸 수 있는 체크리스트형 문장을 남깁니다.",
                f"넓게 훑는 기본 탭과 달리 「{title}」은 제목이 가리키는 장면만 확대합니다. 짧은 시간에 결론에 가까이 가고 싶을 때 선택하세요.",
            ],
        ),
        "free": _pick(
            seed,
            [
                f"「{title}」은 부담 없이 맛보는 체험 요약입니다. 사주 프로필만 있으면 짧게 오늘의 태도 힌트를 확인할 수 있고, 더 깊은 주제는 스토어 유료(모의) 패키지로 이어집니다.",
                f"처음 FortuneOne을 쓰는 분이라면 「{title}」으로 결과 톤을 먼저 느껴 보세요. 원국 기반 문장이 어떻게 나오는지 확인한 뒤, 필요한 주제만 골라 결제하시면 됩니다.",
            ],
        ),
    }.get(cat, None)

    if hook is None:
        hook = f"「{title}」은 회원님 사주 원국을 바탕으로 한 주제 심화 리포트입니다."

    what_you_get = {
        "newyear": (
            "구성은 한 해 총평 → 상·하반기 → 월 포인트 → 기회/주의 구간 → 인간·일과 연결 → 실천 로드맵 순입니다. "
            "읽은 뒤 ‘올해 내가 지키면 좋은 세 가지’가 남도록, 추상적 미학보다 실행 언어를 우선합니다. "
            "분기 초·중요한 계약·이사·이직 전에 다시 펼쳐 보시기 좋습니다."
        ),
        "love": (
            "인연의 결·끌림 패턴·만남 시기·표현·오해·회복·정리·한 달 체크까지 이어집니다. "
            "상대를 탓하기보다, 내가 조절 가능한 태도·질문·일정에 초점을 둡니다. "
            "고백·소개팅·재회·이별 정리 직전에 읽으면 말이 과해지는 구간을 줄일 수 있습니다."
        ),
        "marriage": (
            "배우자 상, 혼인 흐름, 가정 안정, 갈등 조율, 시기, 재정·생활, 습관, 장기 로드맵을 담습니다. "
            "완벽한 배우자 찾기보다 생활 루틴이 맞는 사람을 고르는 현실 감각을 강조합니다. "
            "웨딩·동거·가족 합의 전 체크리스트로 활용하세요."
        ),
        "compat": (
            "기질 비교 → 보완/충돌 → 감정 온도 → 대화법 → 생활 리듬 → 공동 실천 → 장기 호흡 순서입니다. "
            "점수 경쟁이 아니라 ‘어떻게 같이 살지’에 무게를 둡니다. 상대 사주를 함께 넣으면 대비가 또렷해집니다."
        ),
        "money": (
            "재물 그릇, 수입 리듬, 누수, 투자 태도, 문서·계약, 사람·동업, 지키는 습관, 올해 우선순위를 다룹니다. "
            "대박 약속이 아니라 손실을 줄이고 기록을 남기는 쪽이 운을 돕습니다. "
            "큰 지출·동업·대출 전에 한 섹션만이라도 다시 읽어 보세요."
        ),
        "career": (
            "일 기질, 역할 궁합, 조직 호흡, 전환 타이밍, 성장 루트, 성과 루틴, 관계 리스크, 분기 액션을 제공합니다. "
            "열정만으로 밀어붙이기보다 마감 품질·한 줄 성과 로그·대안 준비가 점수입니다."
        ),
        "life": (
            "기질 구조와 초·중·말 흐름, 강점·보완, 관계 기본, 평생 테마를 긴 호흡으로 읽습니다. "
            "하루 운세와 다른 ‘자기 사용 설명서’에 가깝습니다."
        ),
        "theme": (
            "핵심 요약부터 환경·타이밍·주의·기회·실천·한 줄 메모까지, 한 주제에 필요한 층을 빠짐없이 쌓습니다. "
            "다른 상품과 겹치는 일반론보다 제목 장면의 디테일을 남기는 것이 목표입니다."
        ),
        "free": (
            "간단 요약·오늘의 팁·주의 한 가지 정도로 짧게 구성됩니다. "
            "깊이가 필요하면 연애·재물·직장·결혼 등 스토어 주제를 골라 주세요."
        ),
    }.get(cat, "주제 섹션을 따라 읽으면 핵심 → 맥락 → 실천 순으로 정리됩니다.")

    vs_tabs = {
        "newyear": (
            "상세 사주 탭의 신년·토정이 ‘한 해 스케치’라면, 이 상품은 같은 해를 실행 단위로 쪼갭니다. "
            "일운은 매일 보고, 이 리포트는 분기 결정이 필요할 때 꺼내 쓰는 용도로 역할이 나뉩니다."
        ),
        "love": (
            "탭의 오늘 애정·토정 인연 한 줄은 분위기 파악용이고, 이 패키지는 관계 패턴 운영용입니다. "
            "둘을 같이 보면 ‘오늘 컨디션’과 ‘장기 습관’이 동시에 잡힙니다."
        ),
        "marriage": (
            "기본 탭이 넓게 가정을 스치듯 다룬다면, 여기서는 배우자·혼인·생활 경제만 깊게 파고듭니다. "
            "결혼 관련 결정만 따로 모아야 할 때 적합합니다."
        ),
        "compat": (
            "기본 탭은 한 사람 중심, 이 상품은 두 사람 운영 중심입니다. "
            "상대 프로필을 연결하면 교차 해석이 더 풍부해집니다."
        ),
        "money": (
            "부자되기 탭 = 언제(월·일 캘린더). 이 상품 = 어떻게(태도·누수·계약). "
            "시기와 태도를 같이 맞출 때 재물 판단이 덜 흔들립니다."
        ),
        "career": (
            "일운·신년의 직장 문장은 짧은 힌트이고, 여기서는 이직·역할·성과 루틴을 길게 설계합니다. "
            "커리어 분기점이 가까울수록 가치가 큽니다."
        ),
        "life": (
            "인생풀이 탭과 결은 잇되, 섹션을 더 나누고 실천 처방을 늘린 심화판에 가깝습니다."
        ),
        "theme": (
            "기본 탭이 전방위라면, 이 상품은 제목 한 줄에 해당하는 장면만 확대한 집중 패키지입니다."
        ),
        "free": (
            "기본 탭과 스토어 유료 상품 사이의 입문용 브릿지입니다."
        ),
    }.get(cat, ROLE_NOTE)

    why_pay = _pick(
        s2,
        [
            (
                f"「{title}」을 결제(모의)하는 이유는 단순합니다. 고민을 검색창에 반복하기보다, "
                f"내 사주 기준으로 고정된 문장을 갖고 있으면 같은 불안을 덜 되뇌게 됩니다. "
                f"결과는 웹 7일·이메일 링크 30일 다시보기할 수 있어, 결정 전날 밤에도 다시 펼칠 수 있습니다."
            ),
            (
                f"막연한 ‘잘 될 거야’ 대신, 내가 조절할 수 있는 행동 단위가 필요할 때 「{title}」이 도움이 됩니다. "
                f"프로필을 고르는 순간 원국이 고정되고, 같은 입력으로는 골격이 안정적으로 유지됩니다. "
                f"운세를 소비가 아니라 의사결정 메모로 쓰고 싶은 분께 맞춰져 있습니다."
            ),
            (
                f"친구 조언·숏폼 운세는 자극은 크지만 내 원국과 무관할 때가 많습니다. "
                f"「{title}」은 회원님 생년월일·시진·성별을 반영한 맞춤 문장이라, 읽고 난 뒤 메모 한 줄이 남습니다. "
                f"그 한 줄이 충동 소비·충동 고백·충동 퇴사를 한 번 더 멈추게 합니다."
            ),
        ],
    )

    how = (
        f"이용 방법: 로그인 → 사주 프로필 선택(필요 시 상대 프로필) → 결제(모의) → 즉시 결과. "
        f"원국 fact는 MIT 상용 가능 엔진(sajupy + lunar_python 교차)으로 검증하고, "
        f"해석 문장은 FortuneOne 자체 템플릿(v3)으로 생성합니다. "
        f"상용 운세 사이트의 문구를 복제하지 않으며, 엔터테인먼트·자기성찰 목적의 참고용입니다. "
        f"투자·법률·의료 자문이 아니며 결정권은 언제나 본인에게 있습니다."
    )

    close = _pick(
        seed + 3,
        [
            f"지금 이 주제가 가장 마음에 걸린다면, 「{title}」부터 읽고 나머지를 줄이세요. 한 번에 모든 운세를 사는 것보다 한 주제의 실행이 삶을 바꿉니다.",
            f"「{title}」은 두려움을 키우기 위한 상품이 아니라, 선택의 기준을 짧게 남기기 위한 패키지입니다. 편안한 마음으로 천천히 읽어 주세요.",
            f"읽은 뒤 실천 한 줄만 메모해도 충분합니다. 「{title}」이 그 한 줄의 초안이 되어 드립니다.",
        ],
    )

    # free: shorter but still richer than before
    if cat == "free":
        return [
            hook,
            what_you_get,
            vs_tabs,
            how,
            "마음에 드는 주제가 생기면 스토어에서 연애·결혼·재물·직장 심화 패키지를 이어서 보시면 됩니다.",
        ]

    return [
        hook,
        what_you_get,
        vs_tabs,
        why_pay,
        how,
        close,
    ]


def for_whom(cat: str, title: str) -> list[str]:
    seed = _h(title + "whom" + cat)
    banks: dict[str, list[str]] = {
        "newyear": [
            "올해 목표를 세웠지만 분기마다 우선순위가 흔들리는 분",
            "상반기·하반기에 힘을 어디에 둘지 정하고 싶은 분",
            "이사·이직·사업 확장 등 큰 일정을 한 해 리듬에 맞추고 싶은 분",
            "신년 운세는 읽었는데 실행 문장이 부족했던 분",
            "월별로 ‘밀기/쉬기/점검’만 표시해 두고 싶은 분",
            "감정적으로 바쁘게 보내기보다 로드맵으로 한 해를 운영하고 싶은 분",
            "토정·신년 탭과 별도로 연간 전략 문서를 갖고 싶은 분",
        ],
        "love": [
            "호감은 있는데 고백·만남 타이밍이 계속 어긋나는 분",
            "같은 유형의 이별·재회 패턴이 반복되어 지친 분",
            "썸·소개팅에서 말과 속도 조절이 어렵다고 느끼는 분",
            "솔로 구간을 ‘대기’가 아니라 ‘준비’로 바꾸고 싶은 분",
            "상대 눈치만 보다가 내 기준을 잃고 싶지 않은 분",
            "오늘의 연애 점수보다 관계 운영법을 알고 싶은 분",
            "이별 정리 후 다음 인연의 경계를 세우고 싶은 분",
        ],
        "marriage": [
            "혼인·약혼·동거를 앞두고 현실 체크리스트가 필요한 분",
            "배우자 상·생활 루틴 궁합이 궁금한 분",
            "시댁·처가·주거·재정 경계를 미리 합의하고 싶은 분",
            "설렘과 생활력 사이에서 결정이 어려운 분",
            "부부 갈등 패턴을 줄일 조율 규칙이 필요한 분",
            "가정 경제 호흡을 맞추며 장기 계획을 세우고 싶은 분",
            "결혼 후 ‘함께 키울 습관’을 구체적으로 남기고 싶은 분",
        ],
        "compat": [
            "연인·부부·파트너와 말의 온도 차이가 큰 분",
            "사랑하는데 같은 주제에서 반복 다툼이 나는 분",
            "두 사람 강점을 분업으로 나누고 싶은 분",
            "상대 사주를 넣어 비교 해석을 보고 싶은 분",
            "갈등 후 복구 규칙이 없어 관계가 소모되는 분",
            "장기 동반 여부를 감정 외 기준으로도 보고 싶은 분",
            "대화·생활 리듬·사과 타이밍을 맞추고 싶은 분",
        ],
        "money": [
            "수입 대비 통장이 늘지 않아 누수가 의심되는 분",
            "투자·계약·보증 전 한 번 더 기준이 필요한 분",
            "부자되기 캘린더와 함께 재물 태도를 다잡고 싶은 분",
            "동업·공동 투자 제안을 냉정히 검토하고 싶은 분",
            "충동 소비·과한 규모 확장 전에 멈추고 싶은 분",
            "지출 상한·기록 습관을 사주 기질에 맞게 설계하고 싶은 분",
            "올해 금전 우선순위 세 가지만 남기고 싶은 분",
        ],
        "career": [
            "이직·퇴사·창업 타이밍을 감정 말고 기준으로 보고 싶은 분",
            "열심히 하는데 평가·포지션이 안 맞는 느낌이 드는 분",
            "상사·동료 마찰을 업무 문장으로 줄이고 싶은 분",
            "승진·연봉 협상 전 성과 로그 전략이 필요한 분",
            "조직 안 역할 궁합을 점검하고 싶은 분",
            "다음 분기 액션 3개를 명확히 정하고 싶은 분",
            "사업 확장·채용 전 리스크를 한 번 더 보고 싶은 분",
        ],
        "life": [
            "짧은 운세로 해결되지 않는 자기 이해 질문이 있는 분",
            "초년·중년 전환기에서 방향을 재설정하고 싶은 분",
            "강점은 아는데 약점을 루틴으로 못 메우는 분",
            "인생풀이 탭보다 구간별 실천이 더 필요한 분",
            "관계·일·건강 중 우선순위를 정하고 싶은 분",
            "평생 테마를 한 문장으로 정리하고 싶은 분",
            "선택의 반복 패턴을 객관적으로 보고 싶은 분",
        ],
        "theme": [
            "지금 당장 한 가지 상황만 깊게 보고 싶은 분",
            "정보가 많아 결정이 흐려진 분",
            "기본 탭을 본 뒤 특정 주제만 보강하고 싶은 분",
            "체크리스트형 조언이 필요한 분",
            "짧은 시간에 결론에 가까이 가고 싶은 분",
            "제목에 해당하는 장면이 현재 고민과 일치하는 분",
        ],
        "free": [
            "FortuneOne 결과 톤을 먼저 느껴 보고 싶은 분",
            "결제 전 가볍게 체험하고 싶은 분",
            "사주 프로필 등록 후 첫 리포트를 열어 볼 분",
        ],
    }
    pool = banks.get(cat, banks["theme"])
    # pick 5-6 unique-ish lines in rotation
    n = 6 if cat != "free" else 3
    out = []
    for i in range(n):
        out.append(pool[(seed + i * 3) % len(pool)])
    # dedupe preserve order
    seen = set()
    uniq = []
    for x in out:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


def _extra_fo_products() -> list[dict]:
    """FO-authored products to balance money/career (sample site was love-heavy)."""
    extras = []
    money_titles = TITLE_BANK["money"]
    career_titles = TITLE_BANK["career"]
    for i, title in enumerate(money_titles):
        extras.append(
            {
                "id": f"fo_money_{i+1}",
                "source_cid": None,
                "source_url": "",
                "source_title": f"[FO] {title}",
                "category_id": "money",
                "category_label": "재물·금전",
                "title": title,
                "price_krw": 3900 + (i % 4) * 1000,
                "currency": "KRW",
                "needs_profile": True,
                "needs_partner": False,
                "is_free": False,
                "tone": "practical",
                "payment": {
                    "methods_mock": ["신용카드", "간편결제", "휴대폰"],
                    "result_view_days_web": 7,
                },
            }
        )
    for i, title in enumerate(career_titles):
        extras.append(
            {
                "id": f"fo_career_{i+1}",
                "source_cid": None,
                "source_url": "",
                "source_title": f"[FO] {title}",
                "category_id": "career",
                "category_label": "직장·사업",
                "title": title,
                "price_krw": 4200 + (i % 4) * 1000,
                "currency": "KRW",
                "needs_profile": True,
                "needs_partner": False,
                "is_free": False,
                "tone": "practical",
                "payment": {
                    "methods_mock": ["신용카드", "간편결제", "휴대폰"],
                    "result_view_days_web": 7,
                },
            }
        )
    # a few free + life + compat
    extras.append(
        {
            "id": "fo_free_1",
            "source_title": "[FO] free",
            "category_id": "free",
            "category_label": "무료·체험",
            "title": "무료 간단 브리핑",
            "price_krw": 0,
            "is_free": True,
            "needs_profile": True,
            "tone": "light",
        }
    )
    extras.append(
        {
            "id": "fo_compat_1",
            "source_title": "[FO] 궁합",
            "category_id": "compat",
            "category_label": "궁합·관계",
            "title": "관계 운영 매뉴얼",
            "price_krw": 5500,
            "needs_profile": True,
            "needs_partner": True,
            "tone": "analytical",
        }
    )
    return extras


def polish(catalog: dict) -> dict:
    products = list(catalog.get("products") or [])
    # drop previous FO extras on re-run
    products = [p for p in products if not str(p.get("id", "")).startswith("fo_")]
    products.extend(_extra_fo_products())
    counters: dict[str, int] = Counter()
    out = []
    for p in products:
        src = p.get("source_title") or p.get("title") or ""
        old_title = p.get("title") or src
        cat, label = score_category(old_title, src)
        counters[cat] += 1
        idx = counters[cat] - 1
        title = fo_title(cat, idx, src + old_title)
        sections = SECTION_BY_CAT.get(cat, SECTION_BY_CAT["theme"])
        # price keep; free if 0
        price = int(p.get("price_krw") or 0)
        is_free = price == 0 or cat == "free"
        needs_partner = cat == "compat" or "궁합" in src or "둘이" in title
        tone = {
            "newyear": "roadmap",
            "love": "narrative",
            "marriage": "narrative",
            "compat": "analytical",
            "money": "practical",
            "career": "practical",
            "life": "deep",
            "theme": "light",
            "free": "light",
        }.get(cat, "light")

        out.append(
            {
                **{
                    k: v
                    for k, v in p.items()
                    if k
                    not in (
                        "intro_blurbs",
                        "for_whom",
                        "diff_from_free_tabs",
                        "subtitle",
                    )
                },
                "title": title,
                "subtitle": subtitle_for(cat, title, label),
                "category_id": cat,
                "category_label": label,
                "result_sections": sections,
                "preview_sections": ["이런 분께", "구성", "기본 탭과 차이"],
                "intro_blurbs": intro_blurbs(cat, title),
                "for_whom": for_whom(cat, title),
                "diff_from_free_tabs": diff_from_free_tabs(cat, title),
                "tone": tone,
                "needs_partner": needs_partner,
                "is_free": is_free,
                "copy_version": 3,
            }
        )

    catalog["products"] = out
    catalog["content_quality"] = {
        "version": 3,
        "notes": [
            "Titles and long-form blurbs are FO-authored; source_title internal only.",
            "Per-category diff_from_free_tabs + purchase-oriented intros (~3x length).",
            "MIT engines for chart facts; narrative templates not scraped commercial copy.",
        ],
        "category_counts": dict(Counter(p["category_id"] for p in out)),
    }
    catalog["role_guide"] = {
        "free_tabs": {
            "daily": "오늘의 운세 — 매일 변하는 짧은 일운",
            "newyear": "2026 신년 — 연간 테마·로드맵(기본 제공)",
            "tojeong": "2026 토정 — 이야기형 종합·월별·영역",
            "wealth": "2026 부자되기 — 재물 전용 월등급·일자 캘린더",
            "five": "오행 — 기질·구조",
            "life": "인생풀이 — 초중말·평생",
        },
        "store": (
            "주제별 심화 패키지(결제/모의). 내 사주 프로필로 결과 생성. "
            "기본 탭이 ‘넓게’라면 스토어는 ‘한 주제를 깊게’."
        ),
        "summary": (
            "상세 사주 탭은 기본 제공, 스토어는 연애·결혼·재물·직장 등 주제 심화. "
            "상품마다 소개·이런분께·기본탭 차이가 다르게 작성됩니다."
        ),
    }
    return catalog


def main() -> None:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    polished = polish(data)
    CATALOG_PATH.write_text(
        json.dumps(polished, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # mirror to docs
    docs = ROOT.parent.parent.parent / "docs" / "superpowers" / "specs" / "2026-07-22-unsin-benchmark-catalog.json"
    if docs.parent.exists():
        docs.write_text(json.dumps(polished, ensure_ascii=False, indent=2), encoding="utf-8")
    print("category_counts", polished["content_quality"]["category_counts"])
    print("products", len(polished["products"]))
    print("sample titles:")
    for p in polished["products"][:8]:
        print(f"  [{p['category_id']}] {p['title']}")


if __name__ == "__main__":
    main()
