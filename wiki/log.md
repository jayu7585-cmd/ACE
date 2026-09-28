---
type: log
title: 작업 로그
---

# 작업 로그 (Log)

> append-only. 새 항목은 맨 아래에 추가한다.
> 최근 5개: `grep "^## \[" wiki/log.md | tail -5`

## [2026-09-24] schema | 볼트 초기화
- LLM Wiki 구조 생성: `raw/`, `wiki/`, `templates/`, `outputs/`, `scripts/`
- `CLAUDE.md` 스키마 초안 작성
- 생성 페이지: [[index]], [[overview]]

## [2026-09-24] schema | ingest 스킬 등록
- `.claude/skills/wiki-ingest/SKILL.md` 생성 (`/wiki-ingest`)
- 미처리 자료 탐지 스크립트 `.claude/skills/wiki-ingest/scripts/pending.py` 추가
- `CLAUDE.md` 4.1절·8절·디렉토리 구조에 스킬 참조 반영

## [2026-09-24] schema | query·lint 스킬 등록
- `.claude/skills/wiki-query/SKILL.md` 생성 (`/wiki-query`) + 보조 검색 `scripts/search.py`
- `.claude/skills/wiki-lint/SKILL.md` 생성 (`/wiki-lint`) + 장부 정합성 점검 `scripts/deep_check.py`
- `scripts/wiki_lint.py`: `outputs/` 파일 링크를 실제 파일 존재로 확인하도록 수정
- `CLAUDE.md` 4.2·4.3절, 디렉토리 구조, `README.md`에 스킬 안내 반영

## [2026-09-24] schema | MOC 체계 도입
- 생성: [[홈]], [[판단과 의사결정 MOC]], [[선택 설계와 행동 개입 MOC]], [[학습과학과 인지 MOC]], [[진로 진학 의사결정 MOC]], [[교육 현장 적용 MOC]], [[연구자 MOC]], [[자료 MOC]], [[작업 대시보드]]
- `templates/moc.md` 추가, 모든 페이지 템플릿에 `moc:` 필드 추가
- `scripts/moc_check.py` 추가 (양방향 일치, 미배정, 분할·신설 후보 점검)
- `/wiki-ingest` 7단계, `/wiki-query` 5단계, `/wiki-lint` 1·2·3단계에 MOC 갱신 반영
- `CLAUDE.md` 3.5절 신설, index.md에 Maps 섹션 추가, 홈·대시보드 책갈피 등록

## [2026-09-24] schema | 사람용 운영 지침 mi.md 추가
- `mi.md` 생성: 운영 루틴(매 세션·매일·매주·매월), 자료 선별 기준, ingest 참여 방법, 질문 유형, 승인 원칙, 탐색 순서, 규칙 개정 방법, 명령 요약
- `CLAUDE.md` 1절·디렉토리 구조, `README.md`에 연결

## [2026-09-26] query | 교육학 발달·학습이론 연구 동향
- 질문: 교육학(발달이론 및 학습이론)에 관한 논문 동향을 알려 주세요.
- 근거 판정: 부족 (위키에 source 없음, 위키 밖 일반 지식으로 잠정 답변)
- 생성: [[syntheses/2026-09-26-교육학-발달·학습이론-연구동향]]
- 갱신: [[index]]
- MOC: [[학습과학과 인지 MOC]], [[판단과 의사결정 MOC]] (관련 종합·적용, 열린 질문)
- 열린 질문: 유창성 착각 교정의 발달 단계별 효과, AI 튜터와 ICAP, 청소년 위험 감수 모형 비교
