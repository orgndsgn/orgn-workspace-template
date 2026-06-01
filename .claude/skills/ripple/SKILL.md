---
name: ripple
description: |
  변경의 파급을 한 번에 처리. 한 파일을 고치면 영향 받는 다른 문서/스킬/위키/SSOT 인덱스를 찾아 일괄 갱신 제안.
  네 가지 변경 유형(스킬·에이전트 / 프로젝트 / 위키 / 회사SSOT 인덱스)을 자동 분기.
  영향도 리포트 → 사용자 승인 → 일괄 Edit. 필요 시 progress·wiki-ingest로 흐름을 잇는다.
  "ripple", "연쇄 반영", "영향도 확인", "관련 문서 같이 업데이트", "cross-ref 정리"를 언급하거나
  세션 종료 신호("정리해줘"/"마무리") 또는 마지막 ripple 이후 새 변경 ≥5건이면 자동 실행.
allowed-tools:
  - Read
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# Ripple

한 파일을 고쳤을 때 그 변화가 닿아야 할 다른 문서들을 자동으로 찾아내고 일괄 갱신을 제안한다.

> 짝꿍 스킬:
> - 프로젝트 파일 변경(T2)이면 끝에 [`progress`](../progress/SKILL.md) 후속 호출.
> - 위키 토픽 변경(T3)이면 [`wiki-ingest`](../wiki-ingest/SKILL.md) §3D~F를 부분 재실행.

## 경로 규약

```
WORKSPACE_ROOT = .                                    (워크스페이스 최상위, 모든 경로 ./ 상대)
SKILLS_DIR     = ./.claude/skills
AGENTS_DIR     = ./.claude/agents
PROJECTS_DIR   = ./10-projects
WIKI_DIR       = ./30-knowledge/00-wiki
DOC_GUIDE_DIR  = ./30-knowledge/37-claude-code
SSOT_INDEX_DIR = ./20-operations/<your-ssot-folder>   (선택 — 외부 SSOT를 archive-index로 인덱싱한 경우)
SSOT_EXTERNAL  = ~/Desktop/<your-external-folder>     (선택 — SSOT 원본 폴더)
CACHE_DIR      = ./.cache/ripple
```

`.cache/`는 `.gitignore`에 등록됨.

T4(SSOT 인덱스) 기능을 쓰지 않는다면 `SSOT_INDEX_DIR`/`SSOT_EXTERNAL`은 무시. T1~T3만 동작한다.

---

## 진입 시 흐름 (요약)

```
1. 변경 수집     — git status/diff
2. 유형 분류     — T1~T4 (한 파일이 복수 유형 가능)
3. 영향 탐색     — 유형별 glob+grep+양방향 링크
4. 리포트 생성   — 변경 요약 + 영향 파일 + 미리보기 + A/S/N
5. 일괄 Edit     — 승인 항목만
6. 후속 호출     — T2면 progress, T3면 wiki-ingest §3D~F
7. 캐시 갱신     — 처리된 diff 기록
```

---

## Step 1: 변경 수집

```bash
git -C . status --short
git -C . diff --name-only HEAD
git -C . diff --name-only --cached
```

- 세 결과의 합집합이 후보. 삭제된 파일도 포함(`D ` 상태).
- 캐시 `./.cache/ripple/session-<YYYY-MM-DD>.json`을 읽어 이미 처리한 diff는 제외:
  ```json
  { "last_run_at": "...", "processed_diffs": ["<sha or path:hash>"] }
  ```

명시 호출이면 캐시 무시하고 전체 스캔.

**자동 트리거 조건** (명시 호출 외):
- 사용자 메시지에 "정리해줘", "마무리", "ripple", "연쇄 반영" 등이 포함되거나
- 마지막 ripple 이후 새 변경이 5건 이상.

조건 미충족이면 조용히 종료.

---

## Step 2: 유형 분류 (T1~T4)

각 파일을 경로 패턴으로 분류. 한 파일이 여러 유형에 해당할 수 있음 — 모두 처리.

| 패턴 | 유형 |
|---|---|
| `./.claude/skills/<x>/SKILL.md`, `./.claude/skills/<x>/**` | **T1** 스킬 |
| `./.claude/agents/<x>.md` | **T1** 에이전트 |
| `./10-projects/<slug>/**` (PROGRESS.md, raw/ 제외) | **T2** 프로젝트 |
| `./30-knowledge/00-wiki/*.md` (SCHEMA.md, index.md, log.md 제외) | **T3** 위키 토픽 |
| `./30-knowledge/00-wiki/index.md` | **T3** 위키 인덱스 (특수 처리) |
| `./20-operations/<ssot-folder>/**` | **T4** SSOT 인덱스 (선택 기능) |
| 그 외 | 분류 안 됨 — 리포트에 "기타"로 표시 |

---

## Step 3: 유형별 영향 탐색

### T1 — 스킬·에이전트 수정

변경된 파일에서 추출:
- 스킬명: 디렉토리명 또는 frontmatter `name`
- 변경 핵심: frontmatter `description` 또는 본문에서 트리거 키워드 줄

영향 탐색:
1. **CLAUDE.md / README.md** — Grep으로 스킬명 검색
   ```bash
   grep -rn "<스킬명>" ./CLAUDE.md ./README.md 2>/dev/null
   ```
2. **다른 SKILL.md / agents 파일** — cross-ref
   ```bash
   grep -rn "<스킬명>" ./.claude/skills/ ./.claude/agents/
   ```
3. **가이드 문서** — `./30-knowledge/37-claude-code/` 내 모든 .md
   ```bash
   grep -rn "<스킬명>" ./30-knowledge/37-claude-code/
   ```

제안 변경:
- 트리거 키워드가 추가/제거됐으면 인용된 곳들의 키워드 목록을 비교 → diff 제안
- 스킬명 자체가 바뀌었으면 인용 위치 일괄 교체 제안
- 단순 본문 보강이면 cross-ref는 변경 불필요 — 리포트에만 표시

### T2 — 프로젝트 파일 수정

변경된 파일에서 추출:
- 프로젝트 slug: `./10-projects/<slug>/...`의 `<slug>`
- 한 줄 요약: diff에서 추출하거나 사용자에게 묻기

영향 탐색:
1. **PROGRESS.md** — 같은 프로젝트의 `./10-projects/<slug>/PROGRESS.md` 존재 여부 확인
2. **오늘 데일리 노트** — `./40-personal/41-daily/<오늘월>/<오늘>.md`의 `## 완료한 일` 섹션
3. **프로젝트 CLAUDE.md** — 있으면 `현재 상태` / `Last updated` 행
4. **형제 프로젝트** — PROGRESS.md frontmatter `related_projects:` 에 등재된 프로젝트들
5. **외부 워크벤치 / 보조 위치** — 같은 프로젝트의 `README.md` frontmatter `external_sources:` 가 있으면 그 경로들도 영향 후보:
   - 사용자 메시지에서 `~/Documents/Claude/Projects/<...>/`, `~/Documents/Zoom/<...>`, `~/iCloud Drive/Obsidian/<...>` 등 절대경로가 언급되거나 git 외부에서 수정된 파일이 입력으로 들어오면 → 프로젝트 README의 external_sources 배열과 매칭해 해당 slug를 T2 후보로 끌어올림
   - 매칭된 slug의 portfolio 인덱스(`./20-operations/<ssot-folder>/portfolio/*.md`) frontmatter `source_files[].path` 에 같은 경로가 있으면 그 portfolio 인덱스도 영향 후보(T4)로 함께 등록

제안 변경:
- a) `progress` 스킬 호출로 PROGRESS.md 갱신 (자동 진행 X — 승인 후)
- b) 데일리 노트 `## 완료한 일`에 한 줄 추가
  ```
  - <slug> <한 줄 요약> — ./10-projects/<slug>/<변경 파일>
  ```
  같은 줄 이미 있으면 갱신.
- c) 프로젝트 CLAUDE.md의 `Last updated` 갱신 (있을 때만)
- d) `related_projects`에 등재된 형제 PROGRESS.md의 cross-ref가 깨졌는지 점검 (자동 수정 X, 리포트에만)

### T3 — 위키 토픽 수정

변경된 페이지에서 추출:
- 토픽명: 파일명(케밥) → 표시명
- Related 링크: 본문 `> **관련**:` 줄 + `## Related` 섹션
- 변경 핵심: H1/핵심 섹션 변화 여부

영향 탐색:
1. **Related 양방향 점검**
   - 수정 페이지의 Related에 있는 토픽 A → A의 Related에 자기 자신이 있는가?
   - 없으면 양방향 보강 제안
2. **Infobox ↔ Related 동기화**
   - `> **관련**:` 줄과 `## Related` 섹션의 토픽 리스트가 일치하는가?
   - 불일치면 합집합으로 동기화 제안 (Infobox는 최대 6개)
3. **index.md 갱신**
   - 한 줄 설명·sources 수·`Last enriched` 날짜
4. **log.md append**
   ```
   ## [YYYY-MM-DD] enrich | [토픽명]
   - cross-refs: [[A]] ↔ [[B]] (보강 시)
   ```

제안 후 사용자 승인되면 wiki-ingest §3D~F(교차 참조 / Footer / log) 부분 재실행. wiki-ingest 스킬을 "위키에 반영" 트리거로 자연스럽게 이어 호출하되, Step 1~3(소스 분석/통합)은 스킵.

### T4 — 외부 SSOT 인덱스 변경 (선택)

`archive-index` 스킬로 외부 폴더를 워크스페이스에 인덱싱한 경우에만 동작.

변경된 인덱스 파일에서 추출:
- 가리키는 외부 경로:
  - frontmatter `source_files[].path` 배열 (표준, 다중 위치) — 각 항목의 `role` 확인 (`ssot` / `workbench` / `recording` / `notes` / `social` / `cloud`)
  - 또는 frontmatter `source_file:` 단일 키 (deprecated, 호환)
  - 또는 본문의 외부 절대경로 (예: `~/Desktop/<폴더>/...`)

영향 탐색:
1. **모든 source path 존재 여부** — source_files의 각 path를 순회
   ```bash
   test -e "<외부 경로>" && echo OK || echo MISSING
   ```
2. **role별 최근 수정 비교**
   ```bash
   find "<외부 폴더>" -mtime -90 -type f 2>/dev/null | head -20
   ```
   - `ssot` 경로: 90일 미반영이면 미스매치
   - `workbench` 경로: 30일 미반영이면 미스매치 (작업본체는 변경 주기 더 빠름)
   - `recording` / `social`: 미스매치 판정 제외 (정적 자산)
3. **`Last updated` 갱신**
   - 인덱스 자체의 `Last updated:` 줄

제안:
- 외부 경로 MISSING → 리포트에 별도 강조 (role 함께 표시)
- 미스매치 폴더 → 리포트에 role 태그와 함께 나열 (자동 수정 X — 사용자가 직접 확인)
- `Last updated`만 자동 갱신 제안

자동 수정 금지 원칙: T4는 외부 SSOT가 truth. 워크스페이스 인덱스가 임의로 외부를 따라잡지 않음.

---

## Step 4: 영향도 리포트

```markdown
# Ripple 영향도 리포트 (YYYY-MM-DD HH:MM)

## 변경 요약
- <T?> <파일> — <한 줄>
- <T?> <파일> — <한 줄>

## 영향 받는 파일 (N건)

### T1 (스킬·에이전트)
1. ./CLAUDE.md — "Skills 사용" 섹션 wiki-ingest 예시 (L142)
2. ./30-knowledge/37-claude-code/.../skills-guide.md — 트리거 키워드 인용 (L37)

### T2 (프로젝트)
1. ./10-projects/<slug>/PROGRESS.md — progress 스킬 후속 제안
2. ./40-personal/41-daily/YYYY-MM/YYYY-MM-DD.md — "완료한 일" 한 줄 추가

### T3 (위키)
1. ./30-knowledge/00-wiki/<other-topic>.md — Related 양방향 보강
2. ./30-knowledge/00-wiki/index.md — sources/Last enriched
3. ./30-knowledge/00-wiki/log.md — enrich append

### T4 (SSOT) — 자동 수정 안 함, 정합성 리포트만
- ./20-operations/<ssot-folder>/portfolio/<프로젝트-인덱스>.md
  - 외부: ~/Desktop/<외부 SSOT 경로> (OK)
  - 외부 최근 수정 발견(45일 전) — 인덱스 미반영 가능성

## 각 파일별 제안 변경 (미리보기)

### ./CLAUDE.md
- L142: 기존 → 새 키워드 추가

### ./30-knowledge/00-wiki/<other-topic>.md
- `## Related` 끝에 `[[<수정한-토픽>]]` 추가

## 후속 제안
- T2 있음 → progress 스킬 실행 (<slug>)
- T3 있음 → wiki-ingest §3D~F 부분 재실행

## 승인
[A] 모두 적용  /  [S] 개별 선택  /  [N] 취소
```

`AskUserQuestion`으로 A/S/N 받기. S면 영향 파일 리스트를 순회하며 각각 yes/no.

---

## Step 5: 일괄 Edit

승인된 항목만 Edit 도구로 처리. 각 파일별로:
- 정확한 `old_string` → `new_string` 매칭이 가능해야 함. 불가능하면 그 파일은 스킵하고 리포트에 표시.
- 한 파일에 여러 변경이 있으면 가장 명확한 것부터.
- 변경 후 즉시 다음 파일.

대량 변경(10파일+) 시 사용자에게 진행 상태 한 번 더 확인.

---

## Step 6: 후속 호출

| 조건 | 후속 |
|---|---|
| T2가 처리됐고 progress 미실행 | "progress 스킬을 이어 실행할까요? (<slug>)" 묻기 |
| T3가 처리됐고 위키 변경 일관성 보강이 필요 | wiki-ingest "위키에 반영" 트리거로 §3D~F 재실행 (Step 1~3 스킵) |
| T1만 처리됐고 cross-ref가 정리됨 | 후속 없음 |
| T4 미스매치 발견 | "외부 SSOT 확인하시겠어요?" 안내만 (자동 호출 X) |

---

## Step 7: 캐시 갱신 및 리포트

`./.cache/ripple/session-<YYYY-MM-DD>.json`:
```json
{
  "last_run_at": "2026-05-17T15:42:00",
  "processed_diffs": ["<파일경로>:<sha-short>", "..."]
}
```

결과 보고:
```
Ripple 완료:
- 처리: T1 N건 / T2 M건 / T3 K건 / T4 L건
- 적용된 파일: <목록>
- 스킵된 파일: <매칭 실패 등, 있으면 표시>
- 후속: progress(<slug>) 실행 예약 / wiki-ingest §3D~F 호출 / 없음
```

---

## 자동 vs 명시

| 경로 | 동작 |
|---|---|
| 사용자가 "ripple", "연쇄 반영", "관련 문서 같이 업데이트" 발화 | 즉시 전체 스캔 |
| 사용자가 "정리해줘", "마무리" 발화 + 변경 ≥1 | 자동 트리거 |
| 마지막 ripple 이후 새 변경 ≥5 | 자동 트리거 |
| 그 외 | 조용히 대기 |

자동 트리거여도 *영향 적용은 항상 사용자 승인 후*. Step 4 리포트에서 [A/S/N] 입력 없이 변경 금지.

---

## 에러 처리

| 상황 | 대응 |
|---|---|
| 워크스페이스 루트 아님 | `test -f ./CLAUDE.md && test -d ./.claude` 실패 → 안내 후 중단 |
| `git` 사용 불가 | git 없는 환경이면 `find ... -newer` 폴백 (정확도 떨어짐, 리포트에 명시) |
| Edit 매칭 실패 | 해당 파일 스킵, 리포트에 표시. 사용자 직접 수정 권장 |
| 외부 경로 접근 실패 (T4) | 리포트에 MISSING으로 명시, 자동 무시 X |
| 영향 후보가 0개 | "Ripple 영향 없음" 리포트만 출력 후 종료 |

---

## 핵심 원칙

- **변경의 파급은 항상 양방향**: A를 고치면 B에 미치는 영향이 있고, B를 고쳐도 A의 cross-ref가 깨질 수 있음. 매번 양방향 점검.
- **자동 적용 금지**: 영향도 리포트 → 승인 → 적용. 자동으로 건드리지 않음.
- **외부 SSOT는 truth**: T4는 정합성 리포트만. 워크스페이스가 외부를 수정 시도하지 않음.
- **세션당 1회 통합 실행**: 캐시로 중복 방지. 같은 변경을 두 번 처리하지 않음.
- **짝꿍 스킬 신뢰**: T2 → progress, T3 → wiki-ingest. 모든 일을 ripple이 다 하지 않음.
