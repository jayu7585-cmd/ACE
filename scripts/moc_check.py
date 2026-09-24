#!/usr/bin/env python3
"""MOC(Map of Contents) 정합성 점검.

페이지 frontmatter의 `moc:`(소속 선언)와 MOC 페이지의 큐레이션 영역(「## 자동 목록」 앞까지)을 대조한다.

1. MOC 미배정 지식 페이지
2. 존재하지 않는 MOC를 가리키는 `moc:` 값
3. 큐레이션 누락: 페이지는 MOC X 소속이라 선언했는데 X의 지도에 링크가 없음
4. 역방향 누락: MOC X의 지도가 링크한 페이지의 `moc:`에 X가 없음
5. 홈에 연결되지 않은 MOC
6. 너무 커진 MOC (분할 후보)
7. 새 MOC 후보: 미배정 페이지가 같은 태그로 여럿 모인 경우

사용법: python3 scripts/moc_check.py [--split 40] [--cluster 5]
"""
import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
KNOWLEDGE = {"concept", "theory", "topic", "person", "application", "synthesis"}
HOME = "홈"
LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
CODE_RE = re.compile(r"```.*?```|`[^`\n]*`|<!--.*?-->", re.S)
GENERIC_TAGS = {"moc", "hub", "jdm", "인물", "교육적용"}


def split_frontmatter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[3:end], text[end + 4:]
    return "", text


def field(fm, key):
    m = re.search(rf"^{key}:\s*(.*?)\s*(#.*)?$", fm, re.M)
    return m.group(1).strip() if m else ""


def list_field(fm, key):
    """인라인 목록(key: [a, b])과 여러 줄 목록(key:\\n  - a)을 모두 읽는다."""
    lines, out, inside = fm.splitlines(), [], False
    for line in lines:
        m = re.match(rf"^{key}:\s*(.*)$", line)
        if m:
            inside = True
            out.append(re.sub(r"\s#.*$", "", m.group(1)))
        elif inside and re.match(r"^\s+-\s*", line):
            out.append(line)
        else:
            inside = False
    return " ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", type=int, default=40, help="큐레이션 링크 수가 이보다 많으면 분할 후보")
    ap.add_argument("--cluster", type=int, default=5, help="같은 태그의 미배정 페이지가 이만큼이면 새 MOC 후보")
    args = ap.parse_args()

    pages = {}
    for p in WIKI.rglob("*.md"):
        fm, body = split_frontmatter(p.read_text(encoding="utf-8"))
        pages[p] = (fm, body)

    names = {}
    for p, (fm, _) in pages.items():
        names[p.stem] = p
        names[p.relative_to(WIKI).with_suffix("").as_posix()] = p
        title = field(fm, "title")
        if title:
            names.setdefault(title, p)
        for a in re.findall(r"[^\[\],]+", field(fm, "aliases")):
            if a.strip().strip("\"'"):
                names.setdefault(a.strip().strip("\"'"), p)

    resolve = lambda t: names.get(t.strip()) or names.get(t.strip().removesuffix(".md"))
    rel = lambda p: p.relative_to(WIKI).with_suffix("").as_posix()
    mocs = {p for p, (fm, _) in pages.items() if field(fm, "type") == "moc"}

    def curated_links(p):
        body = pages[p][1]
        cut = body.find("## 자동 목록")
        area = CODE_RE.sub("", body if cut == -1 else body[:cut])
        return {resolve(t) for t in LINK_RE.findall(area)} - {None}

    curated = {m: curated_links(m) for m in mocs}
    declared = {}
    out = defaultdict(list)

    for p, (fm, _) in pages.items():
        kind = field(fm, "type")
        targets = LINK_RE.findall(list_field(fm, "moc"))
        declared[p] = set()
        for t in targets:
            hit = resolve(t)
            if hit is None or hit not in mocs:
                out["missing_moc"].append(f"{rel(p)} → [[{t}]]")
            else:
                declared[p].add(hit)
        if kind in KNOWLEDGE and not declared[p]:
            out["unassigned"].append(p)

    for p, ms in declared.items():
        for m in ms:
            if p not in curated[m]:
                out["not_curated"].append(f"[[{rel(m)}]] 지도에 [[{rel(p)}]] 없음")

    for m, links in curated.items():
        for p in links:
            if p in mocs or p.stem in {"index", "log", "overview"}:
                continue
            if field(pages[p][0], "type") == "dashboard":
                continue
            if m not in declared.get(p, set()):
                out["not_declared"].append(f"{rel(p)}: moc에 [[{m.stem}]] 추가 필요")
        n = len([p for p in links if p not in mocs])
        if n > args.split and m.stem != HOME:
            out["too_big"].append(f"{rel(m)} ({n}개)")

    home = next((m for m in mocs if m.stem == HOME), None)
    if home:
        for m in mocs:
            if m != home and m not in curated[home]:
                out["not_home"].append(rel(m))

    by_tag = defaultdict(list)
    for p in out["unassigned"]:
        for t in re.findall(r"[^\[\],\s]+", field(pages[p][0], "tags")):
            if t.strip("\"'") not in GENERIC_TAGS:
                by_tag[t.strip("\"'")].append(p)
    for tag, ps in sorted(by_tag.items(), key=lambda x: -len(x[1])):
        if len(ps) >= args.cluster:
            out["new_moc"].append(f"#{tag}: {len(ps)}개 ({', '.join(p.stem for p in ps[:5])}…)")

    titles = [
        ("unassigned", "MOC 미배정 지식 페이지", lambda p: rel(p)),
        ("missing_moc", "존재하지 않는 MOC 참조", str),
        ("not_curated", "큐레이션 누락 (지도에 링크 추가 필요)", str),
        ("not_declared", "역방향 누락 (페이지 moc 필드 보완 필요)", str),
        ("not_home", "홈에 연결되지 않은 MOC", str),
        ("too_big", f"분할 후보 MOC (큐레이션 링크 {args.split}개 초과)", str),
        ("new_moc", f"새 MOC 후보 (같은 태그의 미배정 페이지 {args.cluster}개 이상)", str),
    ]
    print(f"# MOC check — MOC {len(mocs)}개, 페이지 {len(pages)}개")
    for key, title, fmt in titles:
        out[key].sort(key=str)
        print(f"\n## {title}: {len(out[key])}")
        for item in out[key]:
            print("  - " + fmt(item))
    return 0


if __name__ == "__main__":
    sys.exit(main())
