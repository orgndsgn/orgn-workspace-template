---
name: archive-index
description: |
  외부 SSOT 폴더(예: ~/Desktop/ORGN/)를 워크스페이스에 **인덱스 .md만**으로 마이그레이션. 사본·심볼릭 링크 없음.
  Tier 체계(S/A/B/C)로 중요도 차등 + 진행하지 않은 시도까지 카탈로그로 보존.
  "외부 자료 정리", "아카이브 인덱싱", "SSOT 인덱싱", "프로젝트 폴더 마이그레이션", "archive-index", "Tier 카탈로그", "회사 자료 정리" 등을 언급하면 자동 실행.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - AskUserQuestion
  - Agent
---

# Archive Index

외부 SSOT 폴더를 **워크스페이스에 인덱스만** 두는 방식으로 마이그레이션.

## 핵심 원칙 (먼저 이 그림 합의)

```
외부 폴더 (SSOT, 그대로)        워크스페이스 (인덱스만)
~/Desktop/<회사명>/              20-operations/25-about-<조직>/
  ├── 1.회사소개서/                ├── profile/      # frontmatter + 요약 + source_file 경로
  ├── 2.Project/                   ├── portfolio/    # 사본 X, 심볼릭 링크 X
  ├── 3.Branding/        ←─────    └── _catalog.md   # 전체 폴더 메타데이터
  └── ...
```

**왜 인덱스만**:
- 외부 = 사용자 평소 Finder 동선 그대로 보호
- 워크스페이스 = Claude 자연어 검색·위키 통합 가능
- 사본·링크 = 동기화 부담만 큼

**왜 Tier**:
- 모든 폴더에 풀세트 인덱스 만들면 시간만 듦, 중요도 차이 안 보임
- 진행 안 한 시도(드롭·제안)도 자산 — "어떤 시도를 했는가" 기록 가치

## Tier 체계

| Tier | 의미 | 처리 |
|------|------|------|
| **S** | 대표 정체성 사례 (회사소개서·세일즈 인용) | **풀세트 인덱스 .md** (5~9KB) |
| **A** | 실제 진행 일반 사업 (수주·완료·진행 중) | 풀세트 또는 가벼운 인덱스 (2~5KB) |
| **B** | 진행 안 한 시도 (드롭·제안·공모탈락·기획까지만) | **카탈로그 한 줄만** |
| **C** | 기타 (기획자료·단독 파일) | 카탈로그 한 줄 또는 부록 |

## Phase 흐름

### Phase 1: 외부 폴더 분석 (Explore agent 활용)

**Explore subagent에게 위임**해 외부 폴더 패턴 추출:
- 전체 구조 (depth·카테고리·중첩)
- 파일 종류 분포
- 명명 패턴 (날짜 prefix? 클라이언트 prefix? 한글/영어?)
- 갱신 패턴 (최근 활발 vs 정적)
- 의미 단위 클러스터 (어떤 폴더가 어떤 주제)
- **사용자의 분류 멘탈 모델** (관찰 기반 가설)

산출: 검토 보고서 (구체적 인용 5~10개 포함)

### Phase 2: CLAUDE.md 보강

Phase 1에서 발견된 **사용자의 정리 패턴·멘탈 모델**을 CLAUDE.md에 반영:

```markdown
## [영역] 자료 SSOT

**위치**: ~/Desktop/.../  ← 단일 출처(SSOT)
**주변 보조 위치** (참고): ...

## 자료 분류 멘탈 모델

**축 체계** (관찰 기반):
- 주축: ...
- 보조축: ...

**의도된 설계 (Claude는 손대지 않음)**:
- [예: "X 폴더는 동선상 의도적 혼합"]
- [예: "Y 빈약 폴더 = 드롭된 프로젝트, 보강 X"]

**Claude 활용 시 규칙**:
- 자료 호출 → 외부 SSOT 먼저 검색
- 새 자료 추가 시 위 멘탈 모델 그대로 따름
- 워크스페이스 = 인덱스 .md만 (사본 X, 링크 X)
```

### Phase 3: 미세 보정 (선택, 보통 건너뜀)

기존 외부 체계가 견고하면 **재정돈 거의 불필요**. 명명 통일·중복 정리 같은 가벼운 작업만.

⚠ 위험: 외부 파일 리네임은 신중. dry-run 후 사용자 확인.

### Phase 4: 워크스페이스 인덱싱 (핵심 작업)

#### 4.1 `_catalog.md` 작성 (가장 먼저)

전체 폴더 메타데이터를 한 표에 정리. **Tier 분류·status·매출·메모** 명시.

```markdown
---
title: [영역] 프로젝트 카탈로그
source_type: catalog
source_folder: ~/Desktop/.../
purpose: 전체 폴더 메타데이터 한눈에 — Tier 체계로 중요도·진행상태 차등
---

# [영역] 프로젝트 카탈로그

## 📊 한 줄 통계
| Tier | 개수 | 폴더 번호 |
| S    | N    | ...      |
| A    | N    | ...      |
| B    | N    | ...      |

## 🌟 Tier S — 핵심 정체성 사례 (풀세트)
| # | 프로젝트 | 클라이언트 | status | 매출 | 핵심 | 인덱스 |

## ✅ Tier A — 실제 진행
| # | 프로젝트 | 클라이언트 | 사업유형 | status | 매출 | 메모 | 인덱스 |

## ⏸ Tier B — 진행하지 않은 시도 (메타데이터 보존)
| # | 프로젝트 | 클라이언트 | 사업유형 | status | 메모 |

## 🗂 Tier C — 기타

## 📚 대표 자료 사례 매핑 (회사소개서 등)
| 사례 | 해당 프로젝트 | 인덱스 |

## 🔄 Tier 재분류 트리거
- B → A: 제안이 수주 성공 시 + 풀세트 인덱스 후보
- A → S: 회사소개서·세일즈에 인용되기 시작 시
```

#### 4.2 Tier S 풀세트 인덱스 .md 작성

사용자와 함께 **Tier S 후보 식별** (대표 자료에 이미 인용되는 사례). 각각 풀세트 인덱스.

**Frontmatter 표준** (프로젝트 인덱스):
```yaml
---
title: "[클라이언트] 프로젝트명 — 한줄 요약"
entity: [organization]
source_type: project_folder  # 또는 pdf, catalog 등
source_files:                # 배열 표준 (워크벤치/녹화 등 동시 참조 시 필수)
  - path: ~/Desktop/.../     # 절대 경로
    role: ssot               # 아래 role 어휘 참조
    kind: project_folder
source_file: ~/Desktop/.../  # 단일 경로 (deprecated, 호환 유지용. 신규 인덱스는 source_files 권장)
captured_date: YYYY-MM-DD
status: active | completed | dropped | proposed
about: [organization]
client: [클라이언트명]
sub_clients: [협업 기관들]  # 다자 협업 시
project: [공식 사업명]
contract_amount: 85700000  # 매출 발생 시
contract_period: YYYY-MM ~ YYYY-MM
deal_type: 수주 | 공모 | 제안 | 대행 | 협력사업
tags: [...]
related_projects:  # 자매·선행·후속
  - X. [...]
---
```

**`role` 어휘 (고정 6개)**:

| role | 의미 | 전형 위치 |
|------|------|----------|
| `ssot` | 회사 메인 SSOT (단일 출처) | `~/Desktop/ORGN/...` |
| `workbench` | 실작업 본체 (Claude/디자인 툴이 직접 쓰는 작업물) | `~/Documents/Claude/Projects/...` |
| `recording` | 회의·강의 녹화·자막 | `~/Documents/Zoom/...` |
| `notes` | 사고·영업·전략 노트 | `~/iCloud Drive/Obsidian/...` |
| `social` | SNS 백업·콘텐츠 | `~/Downloads/instagram-*` 등 |
| `cloud` | 외부 클라우드 자산 (Gmail/Drive/Calendar/Sheets) | gws CLI URL 또는 식별자 |

- 한 인덱스가 여러 위치를 가리킬 때 `source_files`에 모두 등재. role 어휘는 6개로 고정 — 늘리려면 이 SKILL.md 갱신.
- 워크벤치가 존재하는 프로젝트는 `source_files` 사용 **필수**(ripple·progress가 변경 파급을 함께 보기 위함).
- 단일 위치만 있으면 `source_file` 단일 키도 허용 (기존 호환).

**예시 — 어떤 프로젝트** (SSOT + 워크벤치 동시):
```yaml
source_files:
  - path: ~/Desktop/<회사명>/<클라이언트>/<프로젝트>/
    role: ssot
    kind: project_folder
  - path: ~/Documents/Claude/Projects/<프로젝트>/
    role: workbench
    kind: project_folder
```

**본문 구조 표준**:
1. **인용구** (1~3줄) — 한 줄 요약 + 대표 자료(회사소개서 등)와의 연결
2. **프로젝트 개요 표** — 사업명·목적·대상·기간·금액·이해관계자
3. **산출물 명세** — 계약서 기반 최종 납품 대상
4. **사업 구성 트랙** — 영역별 분해
5. **마일스톤 시간순 표** — 견적부터 최근까지
6. **폴더 카탈로그** — 하위 폴더별 자료 종류·최근 갱신
7. **대표 자료(회사소개서)와의 연결**
8. **외부에서 같이 봐야 할 위치** — 자매 프로젝트·녹화·타 위치
9. **활용 시나리오** — 분기 보고·유사 제안·계약 레퍼런스 등

**핵심 자료 PDF 추출** (2~3개):
- 견적서·계약서 (계약 정보)
- 사업계획서·제안서 (사업 본질)
- 임팩트리포트·결과보고서 (산출물)
- `pymupdf4llm`으로 텍스트 추출 후 본문에 압축 반영

**파일명 명명**:
- 번호 prefix + 클라이언트 + 핵심키워드: `17-<클라이언트>-<프로젝트>.md`
- 케밥+한글

#### 4.3 Tier A 가벼운 인덱스 (선택)

매출 발생했거나 진행 중이지만 정체성 핵심은 아닌 사업. 풀세트 일부 생략 또는 카탈로그 한 줄만.

#### 4.4 Tier B는 카탈로그만

별도 인덱스 만들지 않음. `_catalog.md`의 표에 한 줄로 메타데이터 보존:
- 어떤 클라이언트와 어떤 사업 시도했는지
- status: dropped / proposed
- 메모: "기획까지만", "공모 탈락" 등

#### 4.5 검증

```bash
# 모든 source_file / source_files[].path 경로 실재 확인
python -c "import re, os, glob, yaml
for md in glob.glob('25-about-.../**/*.md', recursive=True):
    with open(md) as f: c = f.read()
    fm = re.search(r'^---\n(.*?)\n---', c, re.DOTALL)
    if not fm: continue
    meta = yaml.safe_load(fm.group(1)) or {}
    paths = []
    if 'source_file' in meta: paths.append(meta['source_file'])
    if 'source_files' in meta:
        paths += [s.get('path') for s in (meta['source_files'] or []) if s]
    for p in paths:
        if not p: continue
        p = os.path.expanduser(str(p))
        print(('✅' if os.path.exists(p) else '❌'), md, '→', p)"

# 자연어 검색 시나리오
grep -l "키워드" 25-about-.../**/*.md

# 양방향 cross-ref 확인
grep -c "프로젝트A" 프로젝트B.md
grep -c "프로젝트B" 프로젝트A.md
```

### Phase 5: 위키 통합 (선택)

`30-knowledge/00-wiki/[영역].md`에 핵심 정리. synthesis 페이지가 필요한 토픽(사업 모델 패턴 등) 별도 작성.

## 운영 규칙

### 점진적 진행 (한 번에 다 하지 않음)
- 가장 작고 정적인 카테고리부터 시작 (profile, 회사소개서)
- 검증 후 → 동적 영역 (진행 중 프로젝트)
- 한 폴더당 15~30분 (PDF 추출 + 인덱스 작성 + 검증)

### Tier S 풀세트 vs Tier A 가벼움
**Tier S 기준**: 사용자가 대표 자료(회사소개서·포트폴리오)에 인용하는 사례.
**Tier A 기준**: 매출/진행은 있지만 정체성 핵심은 아님.
**Tier B 기준**: 매출 없고 진행도 안 됨 (기획·제안·공모탈락).

### "진행 안 한 시도"의 가치
- 어떤 클라이언트와 시도했는지 = 영업 관계 자산
- 왜 진행 안 됐는지 = 학습
- 후속 영업 시 참고 가능

### Cross-ref 양방향
- 17번이 4번 참조하면 → 4번도 17번 참조
- 자매·후속·선행 관계 명시
- `related_projects:` frontmatter + 본문 "외부에서 같이 봐야 할 위치"

### 사례 매핑은 명시적으로
- 대표 자료(회사소개서)에 인용된 사례 = 해당 프로젝트 폴더 = 인덱스 .md
- 매핑 표 `_catalog.md`에 두기
- "사례 1은 어느 폴더?" 답변 즉시

## 흔한 함정

- **모든 폴더에 풀세트 만들기** → 시간만 듦, 중요도 안 보임. Tier 분류 필수
- **진행 안 한 것 건너뛰기** → 영업 관계 자산 손실. 카탈로그에 메타데이터만이라도
- **사본/링크 두기** → 동기화 부담. 인덱스만이면 충분 (source_file 경로로 외부 직접 접근)
- **외부 폴더 재정돈 의욕** → 이미 사용자가 정돈해놓은 체계는 보통 의도된 것. CLAUDE.md에 패턴 기록만, 손대지 않음
- **PDF 전부 읽기** → 핵심 2~3개만 (견적·계약·결과보고서). 나머지는 폴더 카탈로그로

## 결과 보고 양식

```
Archive Index — [영역]:
- _catalog.md: N개 폴더 (S: N / A: N / B: N / C: N)
- 풀세트 인덱스: N개 (Tier S 중심)
- 검증: source_file 경로 N개 모두 실재 ✅
- Cross-ref: A개 양방향 연결
- 다음 후보: ...
```
