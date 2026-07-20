"""Topic-based long-form daily fortunes."""

from __future__ import annotations

from datetime import date
from typing import Any

from app.services.saju_engine import ELEMENT_KO, STEM_ELEMENT, SajuResult

TOPICS = {
    "love": "연애·관계",
    "money": "재물·기회",
    "work": "일·학업",
    "health": "건강·컨디션",
}


def build_topic_fortune(result: SajuResult, topic: str, as_of: date | None = None) -> dict[str, Any]:
    if topic not in TOPICS:
        raise ValueError("unknown topic")
    d = as_of or date.today()
    el = STEM_ELEMENT.get(result.day_master, "earth")
    el_ko = ELEMENT_KO.get(el, el)
    scores = result.daily.scores
    seed = d.toordinal() + ord(result.day_master[0]) + hash(topic) % 97

    score_map = {
        "love": scores.get("love", 60),
        "money": scores.get("money", 60),
        "work": scores.get("overall", 60),
        "health": scores.get("health", 60),
    }
    score = score_map[topic]

    templates: dict[str, dict[str, str]] = {
        "love": {
            "headline": f"일간 {result.day_master}의 관계 기운이 {el_ko} 톤으로 흐릅니다",
            "flow": (
                f"오늘의 애정·관계 운은 {score}점 구간입니다. "
                f"가까운 사람과의 대화에서 {el_ko} 특유의 리듬—느리지도 급하지도 않은 템포—이 잘 맞습니다. "
                f"오해는 대개 ‘추측’에서 생기니, 짧은 확인 질문이 관계를 부드럽게 만듭니다. "
                f"솔로라면 무리한 어필보다 공통 관심사에서의 자연스러운 만남이 유리하고, "
                f"커플·배우자라면 작은 배려 한 가지가 큰 안도감을 줍니다."
            ),
            "do": (
                "진심 어린 안부 메시지, 경청 후 한 줄 공감, 함께하는 가벼운 산책. "
                "감정을 사실-느낌-요청 순으로 말해 보세요."
            ),
            "dont": (
                "심야의 감정 논쟁, SNS 집착 확인, 상대를 시험하는 말. "
                "오늘은 ‘이기고 지는’ 대화 대신 ‘이해하려 하는’ 태도가 이득입니다."
            ),
            "message": "관계는 점수가 아니라 회복 속도입니다. 오늘 한 번의 따뜻한 확인이면 충분합니다.",
            "action": "소중한 이에게 짧은 감사 인사 보내기",
        },
        "money": {
            "headline": f"재물 흐름은 {el_ko} 기운과 맞물려 움직입니다",
            "flow": (
                f"금전·기회 운 {score}점. 큰 횡재보다 ‘새는 돈 막기’와 ‘준비된 기회’가 핵심입니다. "
                f"계약·결제는 한 번 더 숫자를 확인하고, 충동 소비 대신 목록 구매를 권합니다. "
                f"수입 아이디어는 오후에 메모해 두고 저녁에 현실성을 검토하세요."
            ),
            "do": "고정비 점검, 견적 비교, 비상금 이체, 포트폴리오·이력 한 줄 업데이트.",
            "dont": "검증 없는 투자 권유, 감정으로 하는 큰 결제, 보증·연대 약속.",
            "message": "오늘 버는 것보다 오늘 지키면, 한 달 뒤 여유가 됩니다.",
            "action": "불필요한 구독 1개 해지 검토",
        },
        "work": {
            "headline": f"일·학업에서 {result.day_master} 일간의 집중력이 빛날 수 있습니다",
            "flow": (
                f"성과·집중 운 {score}점. 오전에는 깊은 작업, 오후에는 소통·조율이 잘 맞습니다. "
                f"완성도 100%를 기다리기보다 ‘제출 가능한 80%’를 먼저 내보내는 날이 효율적입니다. "
                f"회의가 있다면 결론 문장을 미리 적어 두세요."
            ),
            "do": "우선순위 3개 적기, 방해 앱 끄기, 피드백 요청 한 번, 짧은 휴식 타이머.",
            "dont": "멀티태스킹 과다, 밤샘 강행, 비교로 인한 자기비난.",
            "message": "오늘 한 칸만 전진해도, 주간 목표의 뼈대가 됩니다.",
            "action": "가장 중요한 일 25분 집중 블록",
        },
        "health": {
            "headline": f"컨디션은 {el_ko} 균형을 회복하는 쪽이 유리합니다",
            "flow": (
                f"건강·에너지 운 {score}점. 몸보다 마음이 먼저 피로를 알릴 수 있습니다. "
                f"수분, 가벼운 스트레칭, 수면 리듬이 컨디션의 절반입니다. "
                f"과한 카페인·야식은 내일 집중력을 깎습니다."
            ),
            "do": "물 자주 마시기, 10분 걷기, 취침 전 스크린 줄이기, 따뜻한 식사.",
            "dont": "무리한 고강도 운동 강행, 끼니 거르기, 감정 폭식으로 스트레스 해소.",
            "message": "건강은 거창한 결심보다 작은 루틴의 합입니다.",
            "action": "오늘 취침 시각 정하기",
        },
    }
    t = templates[topic]
    color = result.daily.lucky.get("color", "청색")
    return {
        "topic": topic,
        "title": f"오늘의 {TOPICS[topic]} 운세",
        "score": score,
        "headline": t["headline"],
        "date": d.isoformat(),
        "day_master": result.day_master,
        "sections": [
            {"id": "flow", "title": "흐름", "body": t["flow"]},
            {"id": "do", "title": "하면 좋은 것", "body": t["do"]},
            {"id": "dont", "title": "피하면 좋은 것", "body": t["dont"]},
            {"id": "message", "title": "한 마디", "body": t["message"]},
        ],
        "lucky": {"color": color, "action": t["action"]},
        "_seed": seed,
    }
