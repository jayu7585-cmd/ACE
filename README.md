# ACE — LLM Wiki 볼트

이 볼트는 옵시디언 볼트이자 git 저장소로, **LLM Wiki** 패턴으로 운영합니다.
위키를 쓰고 관리하는 일은 Claude가 맡습니다. 사람은 자료를 고르고, 질문하고, 의미를 해석합니다.

| 계층 | 위치 | 소유자 |
|---|---|---|
| 원자료 (불변) | `raw/` | 사람 (추가만 함) |
| 위키 | `wiki/` | Claude |
| 스키마 | `CLAUDE.md` | 사람과 Claude가 함께 |

운영 루틴, 자료 선별 기준, 질문하는 법은 **[mi.md](mi.md)**(사람용 운영 지침)에 있습니다.

## 빠른 시작
1. 옵시디언에서 이 폴더를 볼트로 엽니다.
2. 자료를 `raw/`의 알맞은 하위 폴더에 넣습니다. 웹 글은 Web Clipper로 `raw/articles/`에 저장합니다.
3. Claude Code에 요청합니다. 자연어로 말해도 되고, 스킬을 직접 불러도 됩니다.
   | 작업 | 스킬 | 예 |
   |---|---|---|
   | 자료 통합 | `/wiki-ingest` | `/wiki-ingest raw/papers/xxx.pdf`, "raw에 새 자료 넣었어" |
   | 질의 | `/wiki-query` | `/wiki-query 전망이론과 기대효용이론 비교 저장` |
   | 점검 | `/wiki-lint` | `/wiki-lint`, "위키 점검해줘" |
4. 옵시디언에서 결과를 확인합니다.
   - **[[홈]]** (`wiki/maps/홈.md`, 책갈피에 등록됨): 영역별 MOC 지도로 들어가는 출발점
   - **[[작업 대시보드]]**: MOC 미배정·초안·상충 현황 (Dataview)
   - 그래프 뷰, `wiki/index.md`

## 권장 플러그인
Dataview, Templates(코어, 폴더: `templates`), Marp Slides, Obsidian Web Clipper(브라우저 확장)

## 최근 작업 확인
```bash
grep "^## \[" wiki/log.md | tail -5
python3 scripts/wiki_lint.py
python3 scripts/moc_check.py
```
