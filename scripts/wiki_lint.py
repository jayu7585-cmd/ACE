#!/usr/bin/env python3
"""LLM Wiki 기계적 점검: 깨진 링크, 고아 페이지, frontmatter 누락, index 미등재.

사용법: python3 scripts/wiki_lint.py   (볼트 루트에서 실행)
내용 차원의 점검(모순, 낡은 주장 등)은 Claude가 CLAUDE.md 4.3절에 따라 수행한다.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
REQUIRED = ("type", "title", "created", "updated", "status")
SPECIAL = {"index", "log", "overview"}
LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
CODE_RE = re.compile(r"```.*?```|`[^`\n]*`", re.S)


def links(text):
    """코드 블록·인라인 코드 안의 예시 링크는 제외한다."""
    return [t.strip() for t in LINK_RE.findall(CODE_RE.sub("", text))]


def frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    keys = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if m:
            keys[m.group(1)] = m.group(2).strip()
    return keys


def main():
    pages = {p: p.read_text(encoding="utf-8") for p in WIKI.rglob("*.md")}
    # 링크 해석용 이름표: 파일명, wiki/ 기준 상대경로, aliases
    names = {}
    for p, text in pages.items():
        rel = p.relative_to(WIKI).with_suffix("").as_posix()
        names[p.stem] = p
        names[rel] = p
        fm = frontmatter(text) or {}
        for a in re.findall(r"[^\[\],]+", fm.get("aliases", "")):
            if a.strip():
                names[a.strip()] = p

    inbound = {p: 0 for p in pages}
    broken, missing_fm = [], []
    for p, text in pages.items():
        fm = frontmatter(text)
        if p.stem not in SPECIAL and (fm is None or any(k not in fm for k in REQUIRED)):
            missing_fm.append(p)
        for target in links(text):
            if target.startswith(("raw/", "outputs/")):
                if not (ROOT / target).exists():
                    broken.append((p, target))
                continue
            hit = names.get(target) or names.get(target.removesuffix(".md"))
            if hit is None:
                broken.append((p, target))
            elif hit != p:
                inbound[hit] += 1

    index_text = pages.get(WIKI / "index.md", "")
    indexed = set(links(index_text))
    orphans = [p for p, n in inbound.items() if n == 0 and p.stem not in SPECIAL]
    unindexed = [
        p for p in pages
        if p.stem not in SPECIAL
        and p.stem not in indexed
        and p.relative_to(WIKI).with_suffix("").as_posix() not in indexed
    ]

    def show(title, items, fmt):
        print(f"\n## {title}: {len(items)}")
        for it in items:
            print("  - " + fmt(it))

    rel = lambda p: p.relative_to(ROOT).as_posix()
    print(f"# Wiki lint — 페이지 {len(pages)}개")
    show("깨진 링크", broken, lambda x: f"{rel(x[0])} → [[{x[1]}]]")
    show("고아 페이지 (들어오는 링크 없음)", orphans, rel)
    show("index 미등재", unindexed, rel)
    show("frontmatter 누락/불완전", missing_fm, rel)
    return 1 if (broken or orphans or unindexed or missing_fm) else 0


if __name__ == "__main__":
    sys.exit(main())
