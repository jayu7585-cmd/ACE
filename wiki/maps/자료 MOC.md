---
type: moc
title: 자료 MOC
aliases: [Sources MOC, 문헌 MOC]
tags: [moc]
scope: ingest된 원자료(source 페이지) 전체의 지도. 핵심 문헌은 큐레이션하고, 나머지는 자동 목록으로 본다.
parent: "[[홈]]"
created: 2026-09-24
updated: 2026-09-24
status: seed
---

# 자료 MOC

> 상위: [[홈]] · 관련 MOC: [[연구자 MOC]] · [[판단과 의사결정 MOC]]

## 범위
ingest된 원자료(source 페이지) 전체의 지도. 핵심 문헌은 큐레이션하고, 나머지는 자동 목록으로 본다.

## 지도
<!-- Claude가 관리하는 큐레이션 영역. 항목 형식: - [[페이지]] — 이 지도 안에서의 역할 한 줄
     "예상 항목"은 페이지가 생기면 링크 항목으로 바꾸고, 첫 항목을 넣을 때 "_아직 없음_" 줄을 지운다. -->

### 1. 핵심 문헌
_아직 없음_ · 예상 항목: 각 도메인의 토대가 되는 고전 논문과 책

### 2. 최근 연구와 메타분석
_아직 없음_ · 예상 항목: 재현 연구, 메타분석, 리뷰 논문

### 3. 교육 현장 자료
_아직 없음_ · 예상 항목: 기사, 수업 녹취, 사용자 메모

## 관련 종합·적용
_아직 없음_

## 열린 질문
_아직 없음_

## 유형·연도별 자동 목록
```dataview
TABLE WITHOUT ID file.link AS "자료", year AS "연도", kind AS "유형", authors AS "저자"
FROM "wiki/sources"
SORT year DESC
```

## 자동 목록
<!-- Dataview가 frontmatter `moc:`를 읽어 자동으로 채운다. 큐레이션(위 지도)에서 빠진 페이지를 여기서 확인할 수 있다. -->
```dataview
TABLE type AS "유형", sources AS "출처", status AS "상태", updated AS "갱신"
FROM "wiki"
WHERE contains(moc, this.file.link)
SORT type ASC, sources DESC
```
