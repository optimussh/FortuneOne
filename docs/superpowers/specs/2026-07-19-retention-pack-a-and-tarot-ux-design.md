# FortuneOne Retention Pack A + Tarot Interactive UX Design

**Date:** 2026-07-19  
**Status:** Draft for review (구현 전 승인 대기)  
**Depends on:** Local MVP + member full report + SQLite auth  
**Repo:** FortuneOne  

---

## 1. Goal

사용자가 **다양한 운세 경험**을 하고, 앱에 **오래 머물며 자주 방문**하도록 한다.

이번 스펙 범위는 이전에 합의한 **A 묶음** + **타로 UX 고도화(카드 이미지 · 펼치기 · 직접 뽑기)** 이다.

### Success metrics (로컬/제품 관점)

| 지표 | 목표 감각 |
|------|-----------|
| 일 1회 방문 동기 | 홈/데일리 허브에서 30초 안에 “오늘 운세” 확인 |
| 세션 길이 | 타로 뽑기·주제 운세·일기 작성으로 체류 증가 |
| 재방문 | 스트릭·일일 타로 1회 제한으로 “내일 또” 유도 |
| 감정 | 타로가 “버튼 결과”가 아니라 “내가 고른 경험”으로 느껴질 것 |

---

## 2. In scope / Out of scope

### In scope (Pack A + Tarot UX)

1. **로그인 유저 데일리 허브** (홈 또는 `/today-hub`)
2. **출석 스트릭** + 오늘 운세 열람 기록
3. **운세 일기** (하루 한 줄~짧은 메모)
4. **주제별 운세 4종** (연애 / 재물 / 일·학업 / 건강)
5. **오늘의 타로 1장** (하루 1회, 회원 기준 권장 · 게스트는 세션/로컬 제한)
6. **타로 인터랙션 UX**
   - 덱 셔플 → 뒷면 카드 펼침(부채/격자)
   - 사용자가 원하는 장수만큼 **직접 터치로 선택**
   - 뒤집기 애니메이션 + **카드 이미지** 표시
   - 해석 텍스트

### Out of scope (이번 스펙 아님)

- 실제 푸시/PWA 알림
- AI 대화형 타로
- 유료 결제·복주머니 과금
- 네이티브 위젯
- 실사 라이선스 Rider-Waite 상용 이미지 구매 (아래 자산 정책 참고)

---

## 3. Product principles

1. **Habit first:** 매일 보는 화면이 가장 빠르고 예뻐야 한다.
2. **Agency:** 타로는 서버가 던져 주는 결과가 아니라 **내가 고른 카드**여야 한다.
3. **Light friction:** 스트릭·일일 한도는 “아쉬움” 수준이지 짜증 수준이 아니어야 한다.
4. **Works offline-ish for guest:** 게스트도 타로·주제 운세 체험 가능. 스트릭·일기는 회원 권장.
5. **SQLite local:** 출석·일기·일일 타로 기록은 SQLite에 저장 (기존 `fortuneone.db`).

---

## 4. Information architecture

```
/                     게스트: 사주 입력 + 기능 카드
                      회원: 데일리 허브로 리다이렉트 또는 허브 섹션 상단 고정

/hub  (or enhance /me)   데일리 허브 (회원 메인)
  - 오늘 총운 카드
  - 스트릭
  - 주제 운세 4버튼
  - 오늘의 타로 CTA
  - 일기 입력/보기
  - 상세 사주 리포트 링크 (/me 기존 탭 유지)

/topics/[slug]        연애|wealth|work|health 장문 운세

/tarot                인터랙티브 타로 (전면 개편)
/tarot/daily          오늘의 1장 전용 플로우 (선택: /tarot?mode=daily)

/journal              운세 일기 목록·작성 (또는 허브 모달)
```

**권장:**  
- 회원 로그인 후 기본 랜딩 = **`/hub`**  
- 기존 `/me` = 심층 사주 리포트(일운 장문·신년·오행·인생풀이) 유지  
- 허브에서 “내 상세 사주”로 연결

---

## 5. Feature specs

### 5.1 Daily Hub (`/hub`)

**대상:** 로그인 + 사주 프로필 보유 유저  
**미보유:** 사주 등록 온보딩 (기존 `/me` 온보딩 재사용)

**화면 블록 (위→아래)**

1. **인사 + 날짜**  
   - “좋은 아침, {label}님” / 양력 날짜
2. **오늘의 한 장 요약 카드**
   - 총운 점수 (크게)
   - 한 줄 요약 (기존 daily summary 또는 report daily overview 1문단 앞 2문장)
   - 행운 색 / 방향 / 숫자
   - CTA: “자세히 읽기” → `/me?tab=daily`
3. **스트릭 바**
   - 🔥 N일 연속
   - 오늘 체크 여부 (운세 열람 또는 허브 방문 시 체크 — 규칙 5.2)
4. **퀵 액션 그리드 (2×3)**
   - 주제: 연애 / 재물 / 일·학업 / 건강
   - 오늘의 타로
   - 일기 쓰기
5. **최근 일기 1건** 미리보기
6. **하단 링크:** 상세 사주 · 궁합 · 띠별

**게스트 홈:** 기존 사주 폼 유지 + “로그인하면 매일 운세·스트릭” 배너.

---

### 5.2 Streak (출석 스트릭)

**정의**

- **출석 인정 이벤트 (택1, 권장 = A):**  
  - **A (권장):** `/hub` 진입 또는 “오늘의 운세 요약” API 성공 시  
  - B: 주제 운세/타로/일기 중 아무 행동 1회  
- 하루 1회만 카운트 (KST 자정 기준)
- 어제 출석했고 오늘 출석 → streak +1  
- 어제 미출석 + 오늘 출석 → streak = 1  
- 연속 끊김 시 배지 히스토리는 유지, 숫자만 리셋

**데이터 모델**

```text
user_streaks
  user_id PK
  current_streak int
  longest_streak int
  last_checkin_date date  -- KST calendar date
  updated_at

user_checkins
  id
  user_id
  checkin_date date  -- unique (user_id, checkin_date)
  source str  -- hub | daily | tarot | journal
  created_at
```

**API**

- `POST /api/engagement/checkin` `{ "source": "hub" }` → `{ current_streak, longest_streak, already_checked_in_today }`
- `GET /api/engagement/streak` → 동일 필드 + 최근 7일 체크 배열

**UI**

- 허브 상단 🔥 N일
- 마일스톤 토스트: 3/7/30일 (로컬 알림 문구만)

---

### 5.3 Fortune Journal (운세 일기)

**목적:** 읽기만 하던 경험을 “기록”으로 바꿔 재방문.

**필드**

```text
fortune_journals
  id
  user_id
  entry_date date  -- unique per user per day (1일 1개 권장, 수정 가능)
  mood int 1-5 optional
  body text  max 1000
  linked_overall_score int optional  -- 그날 총운 스냅샷
  created_at, updated_at
```

**API (auth)**

- `GET /api/journal?limit=30`
- `GET /api/journal/{date}`
- `PUT /api/journal/{date}` upsert `{ mood?, body }`  
  - 서버가 당일 총운 점수를 프로필 기준으로 스냅샷 가능하면 저장

**UI**

- 허브: 오늘 일기 입력 박스 (textarea + 기분 이모지 5단)
- `/journal`: 달력 또는 리스트로 과거 열람
- 빈 날: “그날 운세 다시 보기” 링크 (optional)

**게스트:** 일기 비활성, 로그인 CTA.

---

### 5.4 Topic fortunes (주제별 운세)

**슬러그**

| slug | 한국어 | 해석 축 |
|------|--------|---------|
| `love` | 연애·관계 | 애정, 소통, 매력 |
| `money` | 재물·기회 | 수입, 지출, 계약 |
| `work` | 일·학업 | 성과, 집중, 커리어 |
| `health` | 건강·컨디션 | 에너지, 휴식, 몸 |

**동작**

1. 회원: primary 사주 프로필로 계산  
2. 게스트: 세션에 최근 사주 입력 있으면 사용, 없으면 생년월일 간단 입력 후 진행  
3. 응답: **장문 3~5 섹션** (기존 `saju_report` 스타일 템플릿 확장)

**API**

- `POST /api/fortune/topic`  
  ```json
  {
    "topic": "love",
    "solar_date": "1990-05-15",
    "hour": 12,
    "minute": 0,
    "gender": "female",
    "time_unknown": true
  }
  ```
- 회원 편의: `GET /api/profiles/primary/topic/{slug}` (프로필 로드 후 동일 엔진)

**응답 스키마**

```json
{
  "topic": "love",
  "title": "오늘의 연애·관계 운세",
  "score": 72,
  "headline": "한 줄 헤드라인",
  "sections": [
    { "id": "flow", "title": "흐름", "body": "..." },
    { "id": "do", "title": "하면 좋은 것", "body": "..." },
    { "id": "dont", "title": "피하면 좋은 것", "body": "..." },
    { "id": "message", "title": "한 마디", "body": "..." }
  ],
  "lucky": { "color": "...", "action": "..." }
}
```

**UI:** `/topics/love` 등, 읽기 좋은 타이포 + 다른 주제 전환 칩.

---

### 5.5 Daily tarot (오늘의 1장)

**규칙**

- **회원:** user_id + KST date 기준 하루 1회  
  - 이미 뽑았으면 결과 재열람만 가능 (다시 뽑기 비활성)
- **게스트:** `localStorage` 키 `tarot:daily:YYYY-MM-DD` 로 1회 제한 (우회 가능 — 제품상 허용, 카피: “로그인하면 기록 보존”)

**데이터**

```text
daily_tarot_draws
  id
  user_id
  draw_date date
  card_id str
  reversed bool
  question str
  meaning str
  created_at
  UNIQUE(user_id, draw_date)
```

**플로우:** 인터랙티브 타로와 동일 UX, `count=1`, `mode=daily`.

---

## 6. Tarot interactive UX (핵심 상세)

### 6.1 문제 (현재)

- 1/3/5장 버튼 → API 즉시 결과 → **텍스트만**, 뽑는 과정 없음
- 몰입· agenc y 부족

### 6.2 목표 UX (단계)

```
[1. Intent] 질문 입력(선택) + 스프레드 종류 선택
     ↓
[2. Shuffle] “카드를 섞는 중…” 애니메이션 1.0~1.5s
     ↓
[3. Fan/Grid] 뒷면 카드 N장 펼침 (기본 22 또는 12장 표시 — 아래 정책)
     ↓
[4. Pick] 사용자가 필요한 장수만큼 탭으로 선택 (선택 순서 = 포지션)
     ↓
[5. Reveal] 한 장씩 또는 한꺼번에 뒤집기 + 이미지 + 이름
     ↓
[6. Read] 포지션별 해석 + 종합 요약
```

### 6.3 스프레드 정의

| id | 이름 | 뽑을 장수 | 포지션 라벨 |
|----|------|-----------|-------------|
| `daily_one` | 오늘의 한 장 | 1 | 현재 |
| `three` | 과거·현재·미래 | 3 | 과거 / 현재 / 미래 |
| `five` | 상황 조언 | 5 | 상황 / 장애 / 조언 / 환경 / 결과 |
| `yesno` | 예·아니오 (optional) | 1 | 답 |

UI에서 기존 “1장/3장/5장”을 스프레드 카드로 교체.

### 6.4 펼쳐 보이는 덱 정책

- 전체 78장을 모두 깔면 모바일에서 너무 빽빽함.
- **권장 v1:** 화면에 **뒷면 카드 18장** 부채꼴/2행 그리드로 표시  
  - 서버 또는 클라이언트가 78장 중 18장을 셔플 샘플  
  - 사용자가 그중 `need` 장 선택  
  - 선택 후 서버에 `card_ids[]` 전달해 정·역·해석 확정  
- **대안 v1.1:** 78장 중 화면에 보이는 건 스크롤 가로 덱

**확정(이 스펙):** **18장 그리드 + 탭 선택** (모바일 우선).

### 6.5 선택 인터랙션

- 필요 장수 `need` = 스프레드 장수
- 카드 탭 → 선택 순서 배지 (1, 2, 3…)
- 다시 탭 → 선택 해제 (순서 재정렬)
- `need` 도달 시 “확정하고 뒤집기” 버튼 활성화
- 확정 후 선택 변경 불가 (다시 하려면 “다시 섞기”)

### 6.6 서버 계약 변경

**기존:** `POST /api/fortune/tarot` `{ count, question }` → 서버가 랜덤 드로우

**신규 (권장 이중 엔드포인트)**

1. `POST /api/fortune/tarot/shuffle`  
   ```json
   { "spread": "three", "question": "..." }
   ```  
   →  
   ```json
   {
     "session_id": "uuid",
     "spread": "three",
     "need": 3,
     "deck_face_down": [
       { "slot_id": "s0", "card_id": "major-0" },
       ...
     ]
   }
   ```  
   - `card_id`는 서버만 알고, 클라이언트에는 **slot_id만 보여도 됨** (치팅 방지 강화 시)  
   - **v1 단순화:** slot에 card_id를 내려주되 UI는 뒷면만 표시 (로컬 앱이므로 허용)

2. `POST /api/fortune/tarot/reveal`  
   ```json
   {
     "session_id": "uuid",
     "picked_slot_ids": ["s3", "s11", "s7"]
   }
   ```  
   →  
   ```json
   {
     "cards": [
       {
         "id": "major-6",
         "name": "연인",
         "arcana": "major",
         "reversed": false,
         "position": "과거",
         "meaning": "...",
         "image_key": "major-06",
         "image_url": "/tarot/major-06.svg"
       }
     ],
     "summary": "..."
   }
   ```

**세션 저장:** 메모리 또는 SQLite `tarot_sessions` (TTL 1시간). 서버 재시작 시 무효 → “다시 섞기”.

**Daily 모드:** reveal 성공 시 `daily_tarot_draws` insert, 중복 시 409 + 기존 결과 반환.

### 6.7 카드 이미지 자산 정책

**원칙:** 저작권 안전한 자체/오픈 에셋만 사용.

| 옵션 | 설명 | 권장 |
|------|------|------|
| **A. SVG 생성 세트** | 메이저 22 + 마이너 심볼 단순 일러스트 (숫자·문양·색) | **v1 권장** |
| B. 퍼블릭 도메인 스캔 | 일부 Rider-Waite PD 변형 | 라이선스 확인 필요 |
| C. 단색 플레이스홀더 + 이모지 | 최빠름, 퀄 낮음 | 임시만 |

**v1 구현**

- `frontend/public/tarot/` 또는 `backend` 정적 서빙
- 파일 키: `major-00.svg` … `major-21.svg`, `wands-01.svg` … (또는 메이저만 이미지, 마이너는 수트 패턴 템플릿 1장 + 오버레이 텍스트)
- **현실적 절충:**  
  - 메이저 22장: 개별 SVG  
  - 마이너 56장: 수트별 배경 4종 + 랭크 텍스트 오버레이 (컴포넌트 렌더)

**카드 뒷면:** `tarot/back.svg` 공통 1장 (브랜드 그라데이션 + 문양).

**이미지 컴포넌트**

```tsx
<TarotCardFace
  imageKey={card.image_key}
  name={card.name}
  reversed={card.reversed}
  size="md"
/>
```

- reversed: `transform: rotate(180deg)` + “역방향” 뱃지

### 6.8 애니메이션 (체감)

| 단계 | 모션 |
|------|------|
| Shuffle | 카드 살짝 흔들림 또는 스택 셔플 CSS 1.2s |
| Fan out | stagger로 18장 opacity/translate |
| Select | scale 1.05 + 링 하이라이트 + 순서 뱃지 |
| Flip | 3D rotateY 0→180 (뒷면→앞면) 0.45s, 선택 순서로 cascade |
| Reduced motion | `prefers-reduced-motion`: 즉시 표시 |

### 6.9 타로 화면 와이어 (텍스트)

```
┌─────────────────────────────┐
│ 타로                        │
│ [질문 입력…………]            │
│ ( 한 장 ) ( 3장 ) ( 5장 )   │
│      [ 카드 섞기 ]          │
└─────────────────────────────┘

섞은 후:
┌─────────────────────────────┐
│ 3장을 골라 주세요 (2/3)     │
│ 🂠 🂠 🂠 🂠 🂠 🂠          │
│ 🂠 🂠 🂠 🂠 🂠 🂠          │
│ 🂠 🂠 🂠 🂠 🂠 🂠          │
│   [ 선택 확정 · 뒤집기 ]    │
└─────────────────────────────┘

결과:
┌──────┐ ┌──────┐ ┌──────┐
│ img  │ │ img  │ │ img  │
│과거  │ │현재  │ │미래  │
│해석… │ │해석… │ │해석… │
└──────┘ └──────┘ └──────┘
종합 요약 …
[ 다시 섞기 ] [ 공유(후순위) ]
```

---

## 7. Data model summary (SQLite)

신규 테이블:

- `user_streaks`, `user_checkins`
- `fortune_journals`
- `daily_tarot_draws`
- `tarot_sessions` (optional)

기존:

- `user`, `fortune_profiles` 유지

마이그레이션: 로컬은 `create_all`로 충분. 파일 `backend/data/fortuneone.db`.

---

## 8. API summary

| Method | Path | Auth | 용도 |
|--------|------|------|------|
| POST | `/api/engagement/checkin` | Y | 출석 |
| GET | `/api/engagement/streak` | Y | 스트릭 조회 |
| GET/PUT | `/api/journal`, `/api/journal/{date}` | Y | 일기 |
| POST | `/api/fortune/topic` | N | 주제 운세 |
| GET | `/api/profiles/primary/topic/{slug}` | Y | 회원 주제 운세 |
| POST | `/api/fortune/tarot/shuffle` | N | 덱 펼침 |
| POST | `/api/fortune/tarot/reveal` | N* | 선택 공개 (*daily는 Y 권장) |
| GET | `/api/fortune/tarot/daily/today` | Y | 오늘 뽑기 여부·결과 |

레거시 `POST /api/fortune/tarot` 는 호환용 유지 또는 deprecate.

---

## 9. Frontend components (planned)

```
components/hub/DailyHub.tsx
components/hub/StreakBadge.tsx
components/hub/TopicGrid.tsx
components/journal/JournalEditor.tsx
components/tarot/TarotTable.tsx       // 전체 플로우 상태머신
components/tarot/ShuffleAnimation.tsx
components/tarot/CardGrid.tsx         // 뒷면 18장
components/tarot/TarotCardBack.tsx
components/tarot/TarotCardFace.tsx
components/tarot/RevealRow.tsx
public/tarot/back.svg
public/tarot/...
```

**상태머신 (`TarotTable`)**

`idle → shuffling → picking → revealing → done`

---

## 10. Implementation phases (for later plan)

| Phase | Deliverable | Verify |
|-------|-------------|--------|
| A0 | 스키마 + engagement/journal API + tests | pytest |
| A1 | `/hub` 데일리 허브 + 스트릭 연동 | 로그인 후 화면 |
| A2 | 주제 운세 API + `/topics/[slug]` 페이지 | 4 토픽 장문 |
| A3 | 운세 일기 UI | upsert + 목록 |
| T1 | 타로 이미지 에셋(메이저+수트 템플릿) + Face/Back 컴포넌트 | 시각 확인 |
| T2 | shuffle/reveal API + 세션 | 테스트 |
| T3 | 인터랙티브 타로 페이지 (pick UI + flip) | 수동 E2E |
| T4 | 일일 타로 1회 제한 + 허브 CTA | 두 번째 진입 시 재열람 |

각 페이즈마다 커밋·푸시 (FortuneOne 규칙).

---

## 11. Copy / UX notes (Korean)

- 스트릭: “연속 N일째 만나서 반가워요”
- 일일 타로 소진: “오늘의 카드는 이미 뽑았어요. 내일 다시 만나요.”
- 타로 pick: “직감으로 카드를 골라 보세요. 순서가 포지션이 됩니다.”
- 게스트 일기: “기록을 남기려면 로그인해 주세요”

---

## 12. Risks & decisions

| Risk | Mitigation |
|------|------------|
| 78장 풀 일러스트 공수 | 메이저 개별 + 마이너 템플릿 |
| 치팅(클라이언트가 card_id 봄) | 로컬 제품 허용; 이후 slot-only + 서버 맵 |
| 스트릭 집착 피로 | 마일스톤만 강조, 강압 카피 금지 |
| 허브 vs /me 중복 | 허브=짧고 매일, /me=길고 심층 |

**Open decision for user (기본값 이미 스펙에 박음):**

1. 출석 트리거 = 허브 방문 (A)  
2. 펼침 카드 수 = 18  
3. 이미지 = SVG 자체 에셋  

반대 의견 있으면 수정 후 구현.

---

## 13. Acceptance checklist

- [ ] 회원 로그인 시 데일리 허브에서 오늘 총운·스트릭·퀵액션 확인
- [ ] 출석 연속일 정상 증가/리셋 (KST)
- [ ] 주제 운세 4종이 장문으로 표시
- [ ] 일기 작성·수정·목록
- [ ] 타로: 섞기 → 뒷면 펼침 → 사용자 선택 → 뒤집기 + **이미지** + 해석
- [ ] 오늘의 타로 1회 제한 (회원)
- [ ] SQLite에 기록 영속
- [ ] pytest + 수동 브라우저 확인 (localhost:6100)

---

## 14. Next step after approval

1. 이 스펙 파일 승인  
2. `writing-plans` 로 `docs/superpowers/plans/YYYY-MM-DD-retention-pack-a-tarot.md` 태스크 분해  
3. Phase A0부터 구현·커밋·푸시  

**스펙 검토 요청:** 위 범위·타로 18장 픽·SVG 이미지 정책으로 진행해도 될지 알려 주세요. 수정 포인트(예: 펼침 78장, 게스트도 스트릭 등)가 있으면 반영한 뒤 구현 플랜으로 넘어갑니다.
