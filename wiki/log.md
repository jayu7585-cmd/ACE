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
