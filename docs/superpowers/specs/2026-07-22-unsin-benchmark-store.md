# Unsin 샘플 벤치마크 → FortuneOne 스토어

**Date:** 2026-07-22  
**Status:** Implemented (catalog + mock pay + saju-based results)

## 무엇을 가져왔나 (구조)

샘플: `docs/scrabexample` (운세의 신 크롤, 111p / 결제 109)

| 샘플 구조 | FO 구현 |
|-----------|---------|
| 상단 카테고리 메뉴 (신년/연애/궁합/금전/…) | `/store` 카테고리 칩 + Header 「스토어」 |
| 상품 리스트 · 가격 | `product_catalog.json` 110종 |
| 상품 상세 (소개·구성·결제 안내) | `/store/[id]` |
| 결제 (구매자·약관·수단) | `/store/[id]/checkout` **모의결제** |
| 결제 후 결과 | `/store/[id]/result` — **선택 사주 프로필 기반** |

## 무엇을 복제하지 않나

- 상용 **본문 카피·슬로건** 미복제
- 제목은 용어 치환 후 FO 표기 (`rewrite_title`)
- 결과 문장 = `product_report.py` 시드 템플릿 (추후 교체 가능)

## 플로우

1. 사용자 사주 프로필 등록 (`/profiles`)
2. 스토어 상품 선택
3. 체크아웃에서 **프로필 지정** (+ 궁합형 상대 프로필)
4. 모의 결제 → `ContentUnlock product:{id}`
5. 결과 API가 해당 프로필로 원국 계산 후 섹션 생성

## 오픈소스 엔진 “Top 합산” 의견

**방향에 동의.** 단 “별점 Top4 코드를 그대로 합치면 풍성해진다”보다:

### 권장 아키텍처 (2층)

1. **Fact layer (합의 가능한 사실)**  
   - 원국 4주, 음력 변환, 오행 카운트, 십성, (가능하면) 지장간·신살 라벨  
   - 여러 라이브러리 결과가 **일치하면 채택**, 불일치 시 primary + `warnings[]`  
   - 후보: `sajupy`(현재) · JS `hoonsikim/saju` 로직 포팅 · `bazica`/gracefullight saju 등 **라이선스 확인 후**

2. **Narrative layer (상품별 문체)**  
   - 상품 `tone`: roadmap / narrative / practical / deep  
   - 섹션 템플릿 풀을 **카테고리×톤**으로 분리 → 같은 원국이어도 상품마다 다른 글  
   - 중복 느낌 해소의 핵심은 여기 (엔진 N개 합산만으로는 부족)

### 하지 말 것

- 라이선스 불명 상용 문구/타 사이트 결과 HTML 스크랩 본문 사용  
- 엔진마다 다른 절기 기준으로 사용자에게 서로 모순된 “정답” 남발 (경고 없이)

### 단계

| Phase | 내용 |
|-------|------|
| 지금 | sajupy + FO 템플릿 + 상품 110 구조 |
| 다음 | fact adapter 인터페이스 + 2nd engine cross-check |
| 이후 | 상품별 장문 코퍼스(자체 작성) · LLM 선택 보강 |

## 파일

- Catalog build: `docs/scrabexample/_build_catalog.py`
- Data: `backend/app/data/product_catalog.json`
- API: `/api/store/*`
- Web: `/store`, `/store/[id]`, checkout, result
