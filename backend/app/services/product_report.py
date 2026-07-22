"""
Product fortune report — long-form FO text from user saju.

v3: warmer narrative arc, less meta jargon, multi-paragraph sections.
Deterministic by product_id + chart seed.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from app.services.saju_engine import SajuResult
from app.services.saju_report import STEM_NATURE, _elems, _pillars_line, _strong, _t, _weak

NARRATIVE_VERSION = 3


def _seed(*parts: Any) -> int:
    s = 2166136261
    for p in parts:
        for ch in str(p):
            s ^= ord(ch)
            s = (s * 16777619) & 0x7FFFFFFF
    return s


def _pick(seed: int, options: list[str]) -> str:
    return options[seed % len(options)] if options else ""


def _join_paras(*parts: str) -> str:
    return "\n\n".join(p.strip() for p in parts if p and p.strip())


def build_product_report(
    product: dict[str, Any],
    result: SajuResult,
    birth: date,
    gender: str,
    *,
    display_name: str = "",
    partner: SajuResult | None = None,
    partner_name: str = "",
    partner_birth: date | None = None,
) -> dict[str, Any]:
    name = display_name or "회원"
    t = _t(result)
    seed = _seed(
        product.get("id"),
        result.day_master,
        _pillars_line(result),
        birth.isoformat(),
        gender,
        product.get("copy_version", NARRATIVE_VERSION),
        NARRATIVE_VERSION,
    )
    nature = STEM_NATURE.get(result.day_master, "균형 잡힌")
    cat = product.get("category_id") or "theme"
    tone = product.get("tone") or "light"
    year = 2026
    age = max(1, year - birth.year)
    chart_facts = getattr(result, "chart_facts", None)
    gko = "남" if gender == "male" else "여"
    pillars = _pillars_line(result)
    strong = _strong(result)
    weak = _weak(result)
    elems = _elems(result)
    title = product.get("title") or "주제 운세"

    header = {
        "product_id": product["id"],
        "product_title": title,
        "category_id": cat,
        "category_label": product.get("category_label"),
        "display_name": name,
        "gender": gender,
        "birth": birth.isoformat(),
        "day_master": result.day_master,
        "day_master_nature": nature,
        "pillars_line": pillars,
        "elements_line": elems,
        "tone": tone,
        "narrative_version": NARRATIVE_VERSION,
    }

    # ── Intro: personal, short meta ──────────────────────────────────────
    tone_open = {
        "light": f"{name}님, 가벼운 마음으로 읽어도 됩니다. 다만 한 줄만 챙겨 가셔도 충분해요.",
        "warm": f"{name}님의 흐름을 따뜻하게, 그러나 현실적으로 짚어 볼게요.",
        "serious": f"{name}님, 이번 해석은 감정보다 선택 기준을 선명히 하는 데 초점을 둡니다.",
        "direct": f"{name}님께 바로 말씀드릴게요. 핵심만 남기고 실행 가능한 문장으로 정리합니다.",
        "narrative": f"{name}님의 이야기 한 페이지를 펼칩니다. 장면마다 선택지가 있습니다.",
    }
    open_line = tone_open.get(tone, tone_open["warm"])

    intro = _join_paras(
        open_line,
        (
            f"일간 {result.day_master}({nature}) · 원국 {pillars}. "
            f"오행은 {elems}이며, 상대적으로 강한 쪽은 {strong}, 보완이 필요한 쪽은 {weak}입니다. "
            f"{gko}성 · 약 {age}세 전후, {year}년 전후의 ‘{t['mood']}’ 기운과 겹쳐 읽습니다."
        ),
        (
            f"「{title}」은 이 주제를 깊게 파는 패키지입니다. "
            f"상세 사주의 오늘·신년·토정·부자되기 탭과 역할이 다르니, "
            f"기본 흐름은 탭에서, 주제 디테일은 아래에서 보시면 됩니다."
        ),
    )

    if chart_facts and chart_facts.get("agreement"):
        intro += (
            f"\n\n원국 계산은 상용 가능(MIT) 엔진 교차 확인을 거쳤습니다. "
            f"문장은 FortuneOne 규칙으로 생성한 참고용 해석입니다."
        )
    else:
        intro += "\n\n문장은 FortuneOne 규칙으로 생성한 참고용 해석이며, 결정권은 언제나 본인에게 있습니다."

    section_titles = list(
        product.get("result_sections")
        or ["핵심 요약", "상황 읽기", "관계·환경", "실천 제안", "마무리"]
    )

    # ── Phrase banks ─────────────────────────────────────────────────────
    chart_lines = [
        f"일간 {result.day_master}의 {t['adj']} 기운이 이번 구간의 기본 톤을 잡습니다.",
        f"원국 {pillars}에서 이미 읽히는 결은, 같은 입력으로는 골격이 잘 바뀌지 않는다는 뜻입니다.",
        f"강점({strong})을 앞에 두고 약점({weak})은 환경·루틴으로 메우는 편이 오래 갑니다.",
        f"가치의 중심을 ‘{t['virtue']}’에 두면, 선택의 흔들림이 줄어듭니다.",
        f"{name}님에게 자연스러운 리듬은 ‘{t['mood']}’ 쪽에 가깝습니다.",
    ]
    life_lines = [
        f"일·역할에서는 {t['career']} 포지션이 잘 맞을 수 있습니다. 속도보다 마감 품질이 점수입니다.",
        f"관계에서는 {t['love']} 태도가 호감을 키우고, 추측성 대화는 신뢰를 깎기 쉽습니다.",
        f"돈의 감각은 {t['wealth']} 쪽이 기본입니다. 규모보다 회수·기록이 먼저일 때가 많습니다.",
        f"몸과 리듬은 {t['body']} 관련 과로를 피하면 예방이 됩니다.",
        f"사람 사이에서는 {t['social']} 역할이 자연스럽고, 억지로 다른 캐릭터를 쓰면 피로가 큽니다.",
    ]
    practice_lines = [
        f"지금 바로 쓸 수 있는 한 가지는 “{_pick(seed, ['주 1회 점검 메모','오전 핵심 업무 배치','지출 상한 숫자화','말하기 전 한 호흡','구체적 도움 요청','미룬 일 하나 끝내기','감사 한 줄 남기기'])}”입니다.",
        f"한 달 동안 ‘{_pick(seed + 1, ['관계','일','돈','건강','학습','휴식'])}’ 지표 하나만 숫자나 한 줄로 추적해 보세요.",
        "갈등 순간에는 “사실 → 느낌 → 요청” 순서로 말하면 오해가 줄기 쉽습니다.",
        "큰 계약·이직·이사 전에는 24시간 숙고 규칙을 두면 충동 결정이 줄어듭니다.",
        f"색·방향 힌트({t['color']} · {t['dir']})는 공간이나 일정에 소량만 반영해도 충분합니다.",
        "중요한 결정은 감정이 고조된 직후보다, 한 템포 뒤가 대체로 낫습니다.",
    ]
    close_lines = [
        "해석은 참고일 뿐이고, 마지막 결정권은 언제나 본인에게 있습니다.",
        "같은 사주·같은 상품으로 다시 열어도 골격 문장은 동일하게 유지됩니다.",
        "불안할수록 루틴을 단순화하는 편이, 운을 ‘기다리는’ 것보다 도움이 됩니다.",
        "긴 고민 한 번보다, 짧은 실천 한 줄이 다음 장면을 바꿉니다.",
        "완벽보다 반복 가능한 작은 약속이 길합니다.",
    ]

    cat_story: dict[str, list[str]] = {
        "newyear": [
            f"{year}년 키워드는 ‘{t['mood']}’로 읽힙니다. 상반기는 정리, 하반기는 선택적 확장 비중을 조절해 보세요.",
            "달력에 ‘밀기 / 쉬기 / 점검’만 표시해 두어도 충동 결정이 눈에 띄게 줄어듭니다.",
            "신년 탭의 로드맵과 겹치는 부분은 방향 확인용, 이 패키지는 실행 디테일용으로 나누어 쓰시면 됩니다.",
        ],
        "love": [
            f"애정 표현은 {t['love']} 쪽이 잘 통합니다. 상대 속도를 무시하면 호감이 빨리 식기 쉽습니다.",
            "만남은 우연처럼 보여도, 준비된 일정이 문을 엽니다. 소개·모임 횟수보다 질의 밀도를 올려 보세요.",
            "이별이나 재정리는 감정의 끝이 아니라, 다음 인연을 위한 경계 설정이기도 합니다.",
            "호감이 있을 때일수록 확인 질문 한 번이 추측 열 번보다 낫습니다.",
        ],
        "marriage": [
            "배우자 상은 ‘완벽한 사람’보다 ‘생활 루틴이 맞는 사람’에 가깝게 읽는 편이 현실적입니다.",
            "혼인 전후 재정·주거·가족 경계 세 가지는 말로만이 아니라 짧게라도 합의해 두면 갈등이 줄기 쉽습니다.",
            "부자되기 탭의 재물 호흡과 함께 보면, 가정 경제의 템포를 맞추기 좋습니다.",
            "사랑은 감정이지만 동거는 운영입니다. 둘 다 존중될 때 관계가 오래 갑니다.",
        ],
        "compat": [
            "두 사람의 차이는 ‘틀린 점’이 아니라 분업 재료입니다. 강점을 겹치지 않게 나누어 보세요.",
            "말의 속도와 사과 타이밍만 맞춰도 체감 궁합이 올라가는 경우가 많습니다.",
            "상대 프로필이 있으면 일간·오행 대비가 더 구체화됩니다. 없으면 태도 가이드로 읽어 주세요.",
            "잘 맞는 날보다, 어긋난 날의 복구 규칙이 관계를 지킵니다.",
        ],
        "money": [
            f"재물은 {t['wealth']} 태도가 기본입니다. 올해는 불려 쓰기보다 누수 차단이 점수에 가까운 구간일 수 있습니다.",
            "문서·보증·동업은 기회처럼 보여도, 손안의 현금 범위에서만 검토하세요.",
            "부자되기 탭의 월 등급·일자 캘린더와 함께 보면 ‘언제 줄이고 언제 움직일지’가 선명해집니다.",
            "수익 아이디어보다 먼저, 고정 지출 한 줄을 줄이는 편이 체감이 큽니다.",
        ],
        "career": [
            f"일터에서는 {t['career']} 포지션이 잘 맞을 수 있습니다. 성과는 속도보다 마감 품질과 기록입니다.",
            "이직·전환은 감정의 정점이 아니라, 대안이 준비된 뒤가 안전합니다.",
            "상사·동료와의 마찰은 업무 기준을 짧은 문장으로 맞추면 상당 부분 예방됩니다.",
            "평가 시즌 전에는 ‘한 줄 성과 로그’만 있어도 협상력이 달라집니다.",
        ],
        "life": [
            "초년의 습관, 중년의 선택, 말년의 정리가 한 줄로 이어집니다.",
            "인생풀이 탭과 겹치는 골격은 ‘기질’이고, 이 패키지는 구간별 실천을 더 촘촘히 둡니다.",
            "건강·관계·일 중 한 분기에 하나만 올려도 충분합니다. 세 개를 동시에 고치려 하면 다 놓칩니다.",
            "긴 인생에서 반복되는 패턴을 한 문장으로 적어 두면, 같은 함정을 피하기 쉽습니다.",
        ],
        "theme": [
            "한 주제에 초점을 좁힐수록 조언이 실행 가능해집니다.",
            "사람·돈·시간 중 하나만 바꿔도 결과가 달라질 수 있습니다. 세 개를 한꺼번에 흔들지 마세요.",
            "짧은 메모로 시작·중간·끝을 남기면 다음에 같은 실수를 줄입니다.",
            "오늘의 작은 경계 설정이 한 달 뒤의 여유를 만듭니다.",
        ],
        "free": [
            "체험용 요약입니다. 더 깊은 구간은 유료 패키지에서 이어집니다.",
            "오늘의 태도 하나가 분위기를 바꿉니다. 거창한 계획보다 한 줄 실천이 먼저입니다.",
        ],
    }
    cat_pool = cat_story.get(cat, cat_story["theme"])

    # ── Build sections with narrative roles ──────────────────────────────
    n = len(section_titles)
    bodies: list[dict[str, str]] = []
    for i, sec_title in enumerate(section_titles):
        s = seed + i * 31
        role = "open" if i == 0 else "close" if i == n - 1 else "mid"
        if n >= 4 and i == n - 2:
            role = "action"

        focus_by_cat: dict[str, list[str]] = {
            "love": [t["love"], t["mood"], t["social"], "경계와 속도", "표현과 경청"],
            "marriage": [t["love"], t["wealth"], "생활 루틴", "가정 경제", t["social"]],
            "compat": [t["social"], t["love"], "분업과 역할", "말의 속도", t["mood"]],
            "money": [t["wealth"], "누수 차단", "기록과 회수", t["career"], t["mood"]],
            "career": [t["career"], "마감 품질", t["social"], "평가와 기록", t["mood"]],
            "newyear": [t["mood"], t["virtue"], "상반기 정리", "선택적 확장", t["career"]],
            "life": [t["mood"], t["virtue"], t["body"], "습관과 선택", t["career"]],
            "theme": [t["mood"], t["virtue"], t["love"], t["wealth"], t["career"]],
            "free": [t["mood"], "오늘의 태도", t["virtue"]],
        }
        focus = _pick(s + 3, focus_by_cat.get(cat, focus_by_cat["theme"]))
        chart = _pick(s, chart_lines)
        life = _pick(s + 5, life_lines)
        practice = _pick(s + 7, practice_lines)
        close = _pick(s + 11, close_lines)
        story = _pick(s + 9, cat_pool)
        story2 = _pick(s + 17, cat_pool)

        partner_bit = ""
        if partner is not None and cat in ("compat", "love", "marriage"):
            pn = partner_name or "상대"
            partner_bit = (
                f"{pn}님(일간 {partner.day_master}, {_pillars_line(partner)})과 나란히 보면, "
                f"강점({strong} vs {_strong(partner)})을 역할로 나누는 편이 마찰을 줄입니다. "
                f"같은 일을 둘이 다 하려는 순간이 가장 피곤한 구간입니다."
            )

        detail_extra = _pick(
            s + 23,
            [
                (
                    f"{name}님의 경우, 강점({strong})을 ‘속도’로만 쓰면 과열되고 "
                    f"‘품질·기록’으로 쓰면 평가와 관계가 안정되는 편입니다. "
                    f"약점({weak})은 숨길 대상이 아니라, 환경 설계로 메울 항목입니다."
                ),
                (
                    f"같은 사주라도 수면·일정·사람 배치가 바뀌면 체감 운이 달라집니다. "
                    f"해석을 운명 선언으로 읽기보다, 이번 주 실험할 변수 하나로 번역해 보세요."
                ),
                (
                    f"‘{focus}’가 잘 안 풀릴 때는 더 세게 밀기보다 기준을 문장으로 적는 편이 낫습니다. "
                    f"기준이 없으면 감정 파도에 결정을 맡기게 됩니다."
                ),
                (
                    f"오행 분포({elems})는 균형 점수가 아니라 사용 설명서에 가깝습니다. "
                    f"강한 쪽을 과시하고 약한 쪽을 방치하면, 장기적으로 같은 함정에 빠지기 쉽습니다."
                ),
            ],
        )
        scene = _pick(
            s + 29,
            [
                (
                    f"실제 장면으로 옮기면 이렇습니다. 중요한 대화·계약·고백 전에는 "
                    f"‘원하는 결과 한 줄’과 ‘절대 하지 않을 말 한 줄’을 메모하세요. "
                    f"{t['color']} 계열 소품이나 {t['dir']} 방향 자리를 고르는 것은 보조일 뿐입니다."
                ),
                (
                    f"일주일 단위로 점검할 질문: 나는 속도를 냈는가, 기록을 남겼는가, "
                    f"사람을 소모했는가. 세 가지 중 하나만 개선해도 체감이 바뀝니다."
                ),
                (
                    f"운이 좋아 보이는 날일수록 규모를 키우기 쉽습니다. "
                    f"그럴 때일수록 손안의 자원(시간·돈·체력) 상한을 숫자로 정해 두세요."
                ),
            ],
        )

        if role == "open":
            body = _join_paras(
                f"먼저 ‘{sec_title}’부터 보겠습니다. 이 구간의 키워드는 ‘{focus}’ 쪽에 가깝습니다.",
                chart,
                story,
                life,
                detail_extra,
                scene,
                partner_bit,
            )
        elif role == "action":
            body = _join_paras(
                f"‘{sec_title}’에서는 말이 아니라 행동 단위로 정리합니다.",
                practice,
                story,
                (
                    f"{name}님의 약점 쪽({weak})을 하루 루틴 한 줄로만 보완해도, "
                    f"강한 쪽({strong})이 과열되지 않고 오래 갑니다."
                ),
                detail_extra,
                scene,
                _pick(s + 41, practice_lines),
                partner_bit,
            )
        elif role == "close":
            body = _join_paras(
                f"마지막 ‘{sec_title}’입니다. 오늘 챙길 문장만 남기겠습니다.",
                practice,
                close,
                story2,
                detail_extra,
                (
                    f"다시 읽고 싶을 때는 내 구매·다시보기에서 기간 안에 열 수 있습니다. "
                    f"결정이 필요할 때만 펼쳐 보셔도 충분합니다. "
                    f"불안이 커질수록 리포트를 여러 번 사는 것보다, 메모한 실천 한 줄을 반복하는 편이 낫습니다."
                ),
                scene,
            )
        else:
            body = _join_paras(
                f"‘{sec_title}’ 구간입니다. 초점 키워드는 ‘{focus}’입니다.",
                chart if i % 2 == 0 else life,
                story,
                practice if i % 3 == 0 else story2,
                detail_extra,
                scene if i % 2 == 1 else _pick(s + 37, practice_lines),
                partner_bit if i % 2 == 1 else "",
                close if i == n // 2 else life if i % 2 == 0 else "",
            )

        # Length floor for commercial long-form feel (~3x earlier short stamps)
        if len(body) < 520:
            body = _join_paras(
                body,
                (
                    f"정리하면, {name}님에게 유효한 태도는 ‘{t['mood']}’ 기운을 과시가 아니라 "
                    f"지속 가능한 루틴으로 쓰는 것입니다. "
                    f"오행({elems}) 기준으로 한 기운만 밀어붙이기보다 약한 쪽을 생활 습관으로 메우면 "
                    f"선택이 덜 흔들립니다. 이 구간(‘{sec_title}’)에서 가져갈 한 줄만 메모해 두세요."
                ),
            )

        bodies.append({"id": f"s{i + 1}", "title": sec_title, "body": body})

    preview_src = bodies[0]["body"] if bodies else intro
    preview = preview_src.replace("\n\n", " ")[:240] + ("…" if len(preview_src) > 240 else "")

    return {
        "product": {
            "id": product["id"],
            "title": title,
            "subtitle": product.get("subtitle"),
            "price_krw": product.get("price_krw"),
            "category_id": cat,
            "category_label": product.get("category_label"),
        },
        "header": header,
        "intro": intro,
        "sections": bodies,
        "preview": preview,
        "role_guide": {
            "this_product": "스토어 주제 심화 패키지",
            "free_tabs": "상세 사주 탭 — 오늘/신년/토정/부자되기/오행/인생풀이 기본 제공",
            "note": product.get("diff_from_free_tabs")
            or "탭은 기본 리포트, 스토어는 주제별 심화입니다.",
        },
        "partner": (
            {
                "display_name": partner_name or "상대",
                "day_master": partner.day_master,
                "pillars_line": _pillars_line(partner),
                "birth": partner_birth.isoformat() if partner_birth else None,
            }
            if partner
            else None
        ),
        "disclaimer": (
            "FortuneOne 규칙 기반 해석입니다. 엔터테인먼트·자기성찰 목적이며 "
            "투자·법률·의료 자문이 아닙니다. 결정권은 본인에게 있습니다."
        ),
        "engine_note": (
            "원국 fact: sajupy(MIT) + lunar_python/6tail(MIT) 교차 확인. "
            f"문장: FortuneOne narrative v{NARRATIVE_VERSION}."
        ),
        "chart_facts": chart_facts,
    }
