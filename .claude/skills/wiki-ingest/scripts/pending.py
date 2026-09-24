#!/usr/bin/env python3
"""raw/ 자료 중 아직 wiki/sources/ 페이지가 없는(ingest되지 않은) 파일을 나열한다.

source 페이지 frontmatter의 `raw:` 필드(문자열 또는 리스트)와 대조한다.
사용법: python3 .claude/skills/wiki-ingest/scripts/pending.py   (볼트 루트에서 실행)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RAW, SOURCES = ROOT / "raw", ROOT / "wiki" / "sources"
SKIP_DIRS = {"assets"}  # 첨부 이미지는 본문 자료와 함께 처리되므로 제외


def ingested_paths():
    done = set()
    for page in SOURCES.glob("*.md"):
        text = page.read_text(encoding="utf-8")
        end = text.find("\n---", 3)
        if not text.startswith("---") or end == -1:
            continue
        fm, in_raw = text[3:end], False
        for line in fm.splitlines():
            m = re.match(r"^raw:\s*(.*)$", line)
            if m:
                in_raw = True
                done.update(re.findall(r"raw/[^\"',\]\s]+", m.group(1)))
            elif in_raw and re.match(r"^\s*-\s*", line):
                done.update(re.findall(r"raw/[^\"',\]\s]+", line))
            else:
                in_raw = False
    return done


def main():
    done = ingested_paths()
    pending = [
        p.relative_to(ROOT).as_posix()
        for p in sorted(RAW.rglob("*"))
        if p.is_file()
        and not p.name.startswith(".")
        and p.relative_to(RAW).parts[0] not in SKIP_DIRS
        and p.relative_to(ROOT).as_posix() not in done
    ]
    print(f"# 미처리 자료: {len(pending)}건 (처리 완료 {len(done)}건)")
    for p in pending:
        print(f"  - {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
