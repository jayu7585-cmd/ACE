#!/usr/bin/env python3
"""wiki/ 페이지를 검색어로 찾아 관련도 순으로 나열한다 (index.md 보조용 단순 검색).

점수: 제목·파일명 일치 10점, aliases 일치 8점, tags 일치 5점, 본문 등장 1회당 1점(최대 10점).
사용법: python3 .claude/skills/wiki-query/scripts/search.py 손실회피 "loss aversion" [-n 15]
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
WIKI = ROOT / "wiki"
SKIP = {"index", "log"}


def split_frontmatter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[3:end], text[end + 4:]
    return "", text


def field(fm, key):
    m = re.search(rf"^{key}:\s*(.*)$", fm, re.M)
    return m.group(1).strip() if m else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("terms", nargs="+")
    ap.add_argument("-n", type=int, default=15)
    args = ap.parse_args()
    terms = [t.lower() for t in args.terms]

    results = []
    for p in WIKI.rglob("*.md"):
        if p.stem in SKIP:
            continue
        fm, body = split_frontmatter(p.read_text(encoding="utf-8"))
        title = (field(fm, "title") + " " + p.stem).lower()
        aliases, tags = field(fm, "aliases").lower(), field(fm, "tags").lower()
        body_l = body.lower()
        score, hits = 0, []
        for t in terms:
            s = 0
            if t in title:
                s += 10
            if t in aliases:
                s += 8
            if t in tags:
                s += 5
            s += min(body_l.count(t), 10)
            if s:
                hits.append(t)
            score += s
        if score:
            results.append((score, len(hits), p, fm))

    results.sort(key=lambda r: (-r[1], -r[0]))
    print(f"# 검색: {' '.join(args.terms)} — {len(results)}건")
    for score, _, p, fm in results[: args.n]:
        meta = f"{field(fm, 'type') or '?'}, sources: {field(fm, 'sources') or '-'}, {field(fm, 'status') or '-'}"
        print(f"  {score:3d}  {p.relative_to(WIKI).with_suffix('').as_posix()}  ({meta})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
