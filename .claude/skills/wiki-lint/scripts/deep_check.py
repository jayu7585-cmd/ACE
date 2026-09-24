#!/usr/bin/env python3
"""wiki_lint.py가 보지 않는 '장부 정합성'과 '내용 점검 후보'를 찾는다.

1. frontmatter `sources:` 수 ↔ 본문의 실제 [[sources/...]] 링크 수 불일치
2. index.md 항목의 (sources: n, status) ↔ 페이지 frontmatter 불일치
3. 출처 링크가 하나도 없는 지식 페이지 (concept/theory/topic/person/application)
4. 링크 없이 언급된 페이지 제목·별칭 → 교차참조 후보
5. 미해결 콜아웃 목록: [!warning] 상충, [!question] 열린 질문
6. 오래된 seed 페이지 (updated가 N일 이상 지남)
7. 마지막 lint 이후 ingest 건수 (log.md 기준)

사용법: python3 .claude/skills/wiki-lint/scripts/deep_check.py [--stale-days 60]
"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
WIKI = ROOT / "wiki"
SPECIAL = {"index", "log", "overview"}
KNOWLEDGE = {"concept", "theory", "topic", "person", "application"}
LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
CODE_RE = re.compile(r"```.*?```|`[^`\n]*`|<!--.*?-->", re.S)


def split_frontmatter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[3:end], text[end + 4:]
    return "", text


def field(fm, key):
    m = re.search(rf"^{key}:\s*(.*?)\s*(#.*)?$", fm, re.M)
    return m.group(1).strip() if m else ""


def listval(v):
    return [a.strip().strip("\"'") for a in re.findall(r"[^\[\],]+", v) if a.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stale-days", type=int, default=60)
    args = ap.parse_args()

    pages = {}
    for p in WIKI.rglob("*.md"):
        fm, body = split_frontmatter(p.read_text(encoding="utf-8"))
        pages[p] = (fm, CODE_RE.sub("", body))
    rel = lambda p: p.relative_to(WIKI).with_suffix("").as_posix()
    out = {k: [] for k in ("count", "index", "nosrc", "mention", "warning", "question", "stale")}

    for p, (fm, body) in pages.items():
        if p.stem in {"index", "log"}:
            continue
        for tag, key in (("[!warning]", "warning"), ("[!question]", "question")):
            n = body.count(tag)
            if n:
                out[key].append(f"{rel(p)} ({n})")
        if p.stem in SPECIAL:
            continue
        kind = field(fm, "type")
        cited = {t.strip() for t in LINK_RE.findall(body) if t.strip().startswith("sources/")}
        declared = field(fm, "sources")
        if kind != "source" and declared.isdigit() and int(declared) != len(cited):
            out["count"].append(f"{rel(p)}: frontmatter {declared} ↔ 본문 인용 {len(cited)}")
        if kind in KNOWLEDGE and not cited:
            out["nosrc"].append(rel(p))
        upd = field(fm, "updated")
        if field(fm, "status") == "seed" and re.fullmatch(r"\d{4}-\d{2}-\d{2}", upd):
            age = (date.today() - date.fromisoformat(upd)).days
            if age >= args.stale_days:
                out["stale"].append(f"{rel(p)} ({age}일)")

    # index 항목 메타데이터 대조
    index = WIKI / "index.md"
    by_name = {}
    for p in pages:
        by_name[p.stem] = p
        by_name[rel(p)] = p
    if index in pages:
        for line in pages[index][1].splitlines():
            m = re.match(r"^\s*-\s*\[\[([^\]|#]+)[^\]]*\]\].*\(sources:\s*(\d+),\s*(\w+)\)", line)
            if not m or m.group(1).strip() not in by_name:
                continue
            fm = pages[by_name[m.group(1).strip()]][0]
            want = (field(fm, "sources"), field(fm, "status"))
            if (m.group(2), m.group(3)) != want and all(want):
                out["index"].append(
                    f"{m.group(1).strip()}: index ({m.group(2)}, {m.group(3)}) ↔ 페이지 ({want[0]}, {want[1]})")

    # 링크 없는 언급 (제목·별칭 2글자 이상)
    names = {}
    for p, (fm, _) in pages.items():
        if p.stem in SPECIAL or field(fm, "type") == "source":
            continue
        for n in [p.stem, field(fm, "title"), *listval(field(fm, "aliases"))]:
            if len(n) >= 2:
                names.setdefault(n, p)
    for p, (fm, body) in pages.items():
        if p.stem in {"index", "log"}:
            continue
        linked = {t.strip().split("/")[-1] for t in LINK_RE.findall(body)}
        plain = LINK_RE.sub("", body)
        seen = set()
        for n, target in names.items():
            if target == p or target in seen or target.stem in linked:
                continue
            pattern = re.escape(n) if re.search(r"[가-힣]", n) else rf"(?<![A-Za-z]){re.escape(n)}(?![A-Za-z])"
            if re.search(pattern, plain, re.I):
                seen.add(target)
                out["mention"].append(f"{rel(p)} → [[{rel(target)}]] (\"{n}\")")

    # 마지막 lint 이후 ingest 수
    log = (WIKI / "log.md").read_text(encoding="utf-8") if (WIKI / "log.md").exists() else ""
    heads = re.findall(r"^## \[(\d{4}-\d{2}-\d{2})\] (\w+) \|", log, re.M)
    last_lint = max((i for i, h in enumerate(heads) if h[1] == "lint"), default=-1)
    since = sum(1 for h in heads[last_lint + 1:] if h[1] == "ingest")

    titles = {
        "count": "sources 수 불일치",
        "index": "index 메타데이터 불일치",
        "nosrc": "출처 인용 없는 지식 페이지",
        "mention": "링크 없는 언급 (교차참조 후보)",
        "warning": "미해결 상충 콜아웃",
        "question": "열린 질문 콜아웃",
        "stale": f"{args.stale_days}일 이상 방치된 seed 페이지",
    }
    print(f"# Deep check — 페이지 {len(pages)}개, 마지막 lint 이후 ingest {since}건")
    for key, title in titles.items():
        print(f"\n## {title}: {len(out[key])}")
        for item in out[key]:
            print(f"  - {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
