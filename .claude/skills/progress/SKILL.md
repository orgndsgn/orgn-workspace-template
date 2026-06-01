---
name: progress
description: |
  프로젝트별 PROGRESS.md를 누적·갱신. 현재 상태/타임라인/원자료 인덱스/의사결정/Next를 한 파일에 모은다.
  raw/ 원자료(카톡·메일·통화·회의록)를 받으면 자동 분류·인덱싱하고, 데일리 노트와 양방향 링크.
  "progress 업데이트", "프로젝트 진척", "진행 상황 정리", "PROGRESS", "원자료 정리"를 언급하거나
  같은 프로젝트에서 일정량 작업이 누적되면 자동 제안.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# Progress

프로젝트별 시간축 SSOT(`PROGRESS.md`)를 만들고, 카톡·메일·통화·회의록 원자료를 `raw/` 폴더에 누적·인덱싱하며, 데일리 노트와 양방향으로 연결한다.

> 짝꿍 스킬: [`ripple`](../ripple/SKILL.md)이 프로젝트 파일 변경(T2)을 감지하면 이 스킬을 후속 제안한다. 거꾸로 이 스킬에서 위키 흡수 후보가 감지되면 [`wiki-ingest`](../wiki-ingest/SKILL.md)를 제안한다.

## 경로 규약

```
WORKSPACE_ROOT = ~/orgn-workspace  (모든 경로는 ./ 상대)
PROJECTS_DIR   = ./10-projects
TEMPLATE       = ./00-system/01-templates/progress-template.md
DAILY_DIR      = ./40-personal/41-daily
CACHE_DIR      = ./.cache/progress
WIKI_INDEX     = ./30-knowledge/00-wiki/index.md
```

- `.cache/`는 `.gitignore`에 등록되어 있음.
- 프로젝트 루트 탐지: 수정·언급된 파일이 `./10-projects/<slug>/...` 하위면 `<slug>`가 프로젝트.

---

## 진입 시 흐름 (요약)

```
1. 컨텍스트 수집     — 프로젝트 slug 확정
2. 자동 감지 점수    — S1~S5 평가
3. PROGRESS.md 확인  — 없으면 템플릿 초안
4. 원자료 처리       — S3 발동 시 raw/ 작성
5. 변경사항 합성     — 섹션 갱신, rolling 7일 → 타임라인 이동
6. 데일리 연동       — 양방향 링크
7. 위키 흡수 후보    — W1~W4 평가, 제안만
8. 결과 리포트
```

---

## Step 1: 프로젝트 slug 확정

다음 우선순위로 결정:

1. **사용자 명시** — "<프로젝트명> 프로그레스 업데이트" 같은 직접 지정
2. **현재 작업 파일 경로** — `git status --short`나 대화 맥락에서 `10-projects/<slug>/...`
3. **사용자에게 확인** — 후보가 2개 이상이면 `AskUserQuestion`으로 선택

slug 확정 못 하면 조용히 종료.

활성 프로젝트 목록 캐시:
```bash
ls -1 ./10-projects/ | grep -v '^_' > /dev/null  # 폴더 후보 확인
```

---

## Step 2: 자동 감지 점수 (S1~S5)

명시 호출(S5)이면 즉시 Step 3로. 그 외에는 다음을 평가하고 **2개 이상**이 참일 때만 "PROGRESS 업데이트할까요?"를 제안.

| 신호 | 판정 방법 | 임계값 |
|---|---|---|
| **S1** 프로젝트 폴더 다수 수정 | `git status --short -- ./10-projects/<slug>` | 3개 이상 변경 |
| **S1b** 외부 워크벤치 수정 | `./10-projects/<slug>/README.md` frontmatter `external_sources` 경로 중 어떤 것이 사용자 메시지에 언급되거나 그 경로의 파일이 입력으로 들어옴 | 1회로 S1과 동급 |
| **S2** 데일리 노트 반복 언급 | 오늘 daily에서 `<slug>` Grep | 2회 이상 |
| **S3** 사용자 원문 붙여넣음 | 메시지 길이 ≥300자 + 시그니처 정규식 매칭(아래) | 1회로 충분 |
| **S4** 마지막 갱신 후 N일 | PROGRESS.md frontmatter `last_updated` | 7일+ & 그 사이 git 변경 ≥1 |
| **S5** 명시 호출 | 트리거 키워드 | 1회로 즉시 실행 |

**S3 시그니처 정규식** (대소문자 무시, 줄 단위):
- 카톡: `\[(오전|오후) ?\d{1,2}:\d{2}\]` 또는 `^[\p{L}\w]+ ?\[(오전|오후) ?\d{1,2}:\d{2}\]`
- 메일: `^(보낸사람|From|받는사람|To|보낸 날짜|Date|제목|Subject)\s*[:：]`
- 통화/회의 녹취: `^(통화|회의|미팅|Call|Meeting)\s*[:：]` 또는 `^\d{1,2}:\d{2}:\d{2}\s+`

**세션당 같은 프로젝트 자동 제안 1회 제한**:
```
./.cache/progress/session-<YYYY-MM-DD>.json
  { "proposed": ["<slug1>", "<slug2>"], "executed": ["<slug1>"] }
```
`proposed`에 이미 있으면 조용히 스킵(명시 호출은 영향 안 받음).

---

## Step 3: PROGRESS.md 존재 여부

위치: `./10-projects/<slug>/PROGRESS.md`

- **없음** → 템플릿(`./00-system/01-templates/progress-template.md`)을 복사해 초안 생성. 필수 frontmatter 채움:
  - `project: <slug>`
  - `started: <오늘>` (감지 가능하면 가장 오래된 raw 또는 git log 첫 커밋 날짜)
  - `last_updated: <오늘>`
  - 그 외는 비워두고 사용자 검토 요청
- **있음** → Read 후 변경 후보 식별 (Step 5에서 처리)

---

## Step 4: 원자료 처리 (S3 발동 시)

### 4.1 타입 자동 분류

붙여넣은 본문에서 시그니처로 type 추정 (Step 2의 정규식 재사용):

| 신호 | type |
|---|---|
| `[오후 X:XX]` 또는 카톡 닉네임 패턴 | `kakao` |
| `보낸사람:` / `From:` | `email` |
| `통화:` / `Call:` / 타임스탬프 `00:01:23` | `call` |
| `회의:` / `Meeting:` / 참석자 명단 | `meeting` |
| 그 외 | `note` |

### 4.2 raw 파일 작성

위치: `./10-projects/<slug>/raw/`

파일명: `<type>-<YYYY-MM-DD>[-<짧은제목>].md`
- 제목 추출: 메일이면 `제목:` 라인, 카톡이면 첫 의미 있는 문장 앞 20자, 통화/회의면 사용자에게 물어봄
- 한글 가능, 공백은 하이픈으로

frontmatter (최소):
```yaml
---
type: kakao | email | call | meeting | note
date: YYYY-MM-DD
project: <slug>
participants: []
source:        # 선택, URL/원본 위치
---
```

본문은 붙여넣은 원문을 그대로 보존. 정리/요약 금지 (검색 가능성을 위해 원문 유지).

raw/ 디렉토리가 없으면 `mkdir -p`로 생성.

### 4.3 외부 워크벤치 / 보조 위치는 옮기지 않음

`./10-projects/<slug>/README.md` frontmatter `external_sources:` 가 있으면, 그 경로의 파일은 **raw/로 복사하지 않음**. 외부 SSOT/워크벤치 원본은 제자리 유지가 원칙(archive-index 규약과 동일). 대신:

- PROGRESS.md `## 원자료 인덱스` 섹션 아래에 `### 외부 참조` 서브섹션을 두고 각 external_sources 항목을 한 줄씩 기록:
  ```
  - <role>: <path> — 최근 갱신 YYYY-MM-DD (find -mtime -7 최대 3개 파일명)
  ```
- 사용자 메시지에 외부 경로의 특정 파일이 언급되면 이번 갱신의 출처로 인식해 §5.1의 `[source: <role>]` 태그를 줄 끝에 부착.

---

## Step 5: 변경사항 합성 (PROGRESS.md 갱신)

### 5.1 섹션별 갱신 규칙

| 섹션 | 갱신 방식 |
|---|---|
| **현재 상태** | 1줄 + 5줄 이내. 가장 최근의 단일 진실. 매번 사용자 확인 후 교체 |
| **이번 주 진행** (rolling 7일) | 오늘에서 7일 이전 항목은 `타임라인`으로 자동 이동. 새 항목 append. **출처 태그**: 워크벤치(`external_sources` role: workbench) 유래는 `[source: 워크벤치]`, raw/ 유래는 `[source: raw]`, 그 외 외부 경로는 `[source: <role>]` 형식으로 줄 끝에 표시 |
| **타임라인** | 굵직한 마일스톤만. rolling 7일에서 흘러나온 항목 자동 들어옴. 사용자에게 "어느 줄을 마일스톤으로 승격?" 확인. 출처 태그는 그대로 유지 |
| **원자료 인덱스** | `ls raw/*.md` 정렬 결과로 **전체 교체** (디렉토리가 truth). 워크벤치 등 외부 경로 파일은 raw/로 **옮기지 않음** — 별도 하위 섹션 `### 외부 참조` 에 경로·role·최근 갱신일만 나열 |
| **의사결정 로그** | 사용자가 명시한 결정만 추가. 형식 `- YYYY-MM-DD <내용> (근거: <짧게>)` |
| **Open Items / 막힌 점** | Diff 형식 제안 — 추가/완료 |
| **Next Actions** | 3개 이내 유지. 4개째 들어오면 사용자에게 "어떤 것을 빼나?" |

### 5.2 frontmatter 갱신

- `last_updated: <오늘>`
- `status`는 사용자가 명시할 때만 변경

### 5.3 충돌 방지

- `git status`로 PROGRESS.md가 이미 수정 중이면 사용자에게 알리고 머지 확인 후 진행

---

## Step 6: 데일리 노트와 양방향 연결

### 6.1 daily → PROGRESS (상대 경로 텍스트)

오늘 daily 노트(`./40-personal/41-daily/YYYY-MM/YYYY-MM-DD.md`)의 `## 완료한 일` 섹션에 한 줄 append:

```
- <slug> progress 갱신: <한 줄 요약> — ./10-projects/<slug>/PROGRESS.md
```

**중복 방지**: 같은 날 동일 경로 줄이 이미 있으면 새로 append하지 말고 기존 줄을 갱신 (요약을 새 요약으로 교체).

daily 노트가 오늘 없으면 생성하지 않음 — 사용자가 `daily-note` 스킬로 먼저 만들도록 안내.

### 6.2 PROGRESS → daily (WikiLink)

PROGRESS.md 하단의 `related daily notes:` 리스트에 오늘 날짜 WikiLink append:

```yaml
related daily notes:
  - [[2026-05-17]]
  - [[2026-05-18]]
```

중복 금지 — 같은 날짜가 이미 있으면 추가하지 않음.

---

## Step 7: 위키 흡수 후보 판단 (제안만)

raw/에 새 파일이 추가됐거나 의사결정 로그에 새 항목이 생긴 경우만 평가. 다음 중 **2개 이상** 만족 → wiki-ingest 제안:

| 신호 | 판정 |
|---|---|
| **W1** 재사용 가능성 | 본문에 "원칙/기준/체계/프레임워크/표준/패턴" 단어 또는 index.md에 동일 토픽 존재 |
| **W2** 일반화 가능성 | 본문에서 고유명사(대문자 시작 또는 회사명/사람명) 비율이 30% 미만 추정 |
| **W3** 패턴 반복 | 같은 키워드가 다른 프로젝트 PROGRESS.md/raw에서 3회+ 등장 (`Grep -r` 사용) |
| **W4** 사용자 명시 | 본문이나 대화에 "기록해둬", "다른 프로젝트에도", "체계화", "위키" 류 표현 |

제안 형식:
```
위키 흡수 후보 (제안만, 자동 실행 X):
- 토픽 후보: <한 줄>
- 근거: W<n>, W<m>
- 실행? [Y] wiki-ingest 호출 / [N] 무시
```

Y면 wiki-ingest 스킬 트리거 키워드("위키에 반영")로 자연스럽게 이어 호출.

---

## Step 8: 결과 리포트

```markdown
# Progress 갱신 완료 (<slug>)

## 변경
- PROGRESS.md: <갱신된 섹션 목록>
- raw 추가: <N건> (파일명 목록)

## 연동
- 데일리 노트: ./40-personal/41-daily/YYYY-MM/YYYY-MM-DD.md (한 줄 추가/갱신)
- 위키 흡수 후보: <있으면 한 줄, 없으면 "없음">

## 캐시
- ./.cache/progress/session-YYYY-MM-DD.json 갱신
```

---

## 첫 실행(프로젝트에 PROGRESS.md가 처음 생길 때)

기존 프로젝트에 이미 `00-session-log-*.md`, `CLAUDE.md`, `README.md`가 있을 수 있음. 처음 한 번은 사용자에게 묻고 다음 중 선택:

1. **세션 로그 분해**: `00-session-log-*.md`의 항목을 타임라인/의사결정 로그로 옮김
2. **CLAUDE.md 역할 분리**: CLAUDE.md = 인덱스/규약(읽기 순서), PROGRESS.md = 시간축/상태 본문. `Last updated`는 양쪽 모두 갱신
3. **빈 슬레이트**: 템플릿 그대로 시작

선택 후 초안 작성 → 사용자 검토.

---

## 에러 처리

| 상황 | 대응 |
|---|---|
| 워크스페이스 루트 아님 | `test -f ./CLAUDE.md && test -d ./10-projects` 실패 시 안내 후 중단 |
| 프로젝트 slug 미확정 | `AskUserQuestion`으로 후보 제시. 사용자가 취소하면 조용히 종료 |
| daily 노트 없음 | 한 줄 추가 스킵. 리포트에 명시 |
| 템플릿 파일 누락 | inline 기본 템플릿으로 폴백 (아래 §부록 참조) |
| 자동 감지 점수 부족 | 조용히 종료 (S5 명시 호출 시에는 무시) |

---

## 부록: inline 기본 템플릿 (폴백용)

템플릿 파일이 없을 때 사용:

```markdown
---
project: <slug>
status: active
started: YYYY-MM-DD
last_updated: YYYY-MM-DD
related_projects: []
stakeholders: []
tags: [progress]
---

# <slug> — Progress

## 현재 상태

## 이번 주 진행 (rolling 7일)

## 타임라인 (역순, 굵직한 마일스톤)

## 원자료 인덱스 (raw/ 자동 반영)

## 의사결정 로그

## Open Items / 막힌 점

## Next Actions (3개 이내)

---
related daily notes:
last_enriched_by: progress skill
```

---

## 핵심 원칙

- **raw 디렉토리가 truth**: 원자료 인덱스는 `ls raw/*.md`로 항상 재생성. 손으로 정리하지 않음.
- **원문 보존**: raw 파일에는 붙여넣은 원문 그대로. 요약은 PROGRESS.md에서.
- **양방향 링크 일관성**: daily ↔ PROGRESS 양쪽 모두 갱신. 한쪽만 갱신하면 cross-ref 부패.
- **자동 제안 ≠ 자동 실행**: 사용자 승인 없이 PROGRESS.md를 고치지 않음.
- **세션당 1회 제안**: 노이즈 방지. 명시 호출은 예외.
