---
type: moc
title: 
aliases: []
tags: [moc]
scope: 
parent: "[[홈]]"
created: {{date:YYYY-MM-DD}}
updated: {{date:YYYY-MM-DD}}
status: seed
---

# {{title}}

> 상위: [[홈]] · 관련 MOC: 

## 범위
(이 지도가 다루는 영역, 다루지 않는 영역)

## 지도
<!-- Claude가 관리하는 큐레이션 영역. 항목 형식: - [[페이지]] — 이 지도 안에서의 역할 한 줄 -->

### 1. 
_아직 없음_

## 관련 종합·적용
_아직 없음_

## 열린 질문
_아직 없음_

## 자동 목록
<!-- Dataview가 frontmatter `moc:`를 읽어 자동으로 채운다. 큐레이션에서 빠진 페이지를 여기서 확인할 수 있다. -->
```dataview
TABLE type AS "유형", sources AS "출처", status AS "상태", updated AS "갱신"
FROM "wiki"
WHERE contains(moc, this.file.link)
SORT type ASC, sources DESC
```
