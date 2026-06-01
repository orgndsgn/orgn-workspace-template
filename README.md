# ORGN Workspace

> Claude Code + Johnny Decimal 기반의 1인·소규모 조직용 PKM 워크스페이스 템플릿.
> 개인 노트·프로젝트 진행·지식 위키를 한 곳에서, AI와 같이 운영합니다.

---

## 이 워크스페이스는 뭔가요?

`Claude Code`와 `Johnny Decimal` 시스템을 결합한 **실전 PKM 워크스페이스 템플릿**입니다.

- **Claude Code 기반** — 자연어로 일을 시키면 폴더·파일을 직접 만들고 갱신합니다.
- **Skills 기반** — `/slash-command`가 아니라, 키워드를 말하면 알맞은 스킬이 자동으로 트리거됩니다 ("오늘 daily note 만들어줘", "이거 할 일에 추가해줘").
- **Wiki 복리 시스템** — `30-knowledge/00-wiki/`는 지식이 통합·갱신되며 쌓이는 위키입니다 (Karpathy "LLM Wiki" 아이디어).
- **클론 → 프로필 → 운영** — clone 받아서 `CLAUDE.md`의 프로필 4문항만 채우면 바로 시작할 수 있습니다.

## Quick Start

### 1. Clone

```bash
git clone https://github.com/<your-account>/orgn-workspace.git
cd orgn-workspace
```

> 본인 계정으로 fork하거나, 원본 그대로 받아서 새 repo로 push해도 됩니다.

### 2. Claude Code에서 열기

VS Code 또는 터미널에서 Claude Code를 실행합니다.

```bash
cd orgn-workspace
claude
```

### 3. 프로필 채우기

`CLAUDE.md`를 열어 **내 프로필** 섹션의 4문항(이름·역할·관심사·용도)을 본인 정보로 채워주세요. 이 파일은 Claude가 매 세션 시작 시 자동으로 읽어, 협업의 첫 맥락이 됩니다.

### 4. (선택) Python 환경

데이터 변환 스킬(`pdf-to-md`, `hwpxskill`, `web-crawler-ocr`)을 쓰려면 가상환경을 만듭니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

각 스킬 폴더의 `requirements.txt`를 보고 필요한 패키지만 설치하세요.

### 5. 첫 Daily Note

Claude에게:

```
오늘 daily note 만들어줘
```

`daily-note` 스킬이 `40-personal/41-daily/YYYY-MM/YYYY-MM-DD.md`를 만들어 줍니다.

## 일상 루틴 예시

| 발화 | 트리거되는 스킬 |
|---|---|
| "오늘 daily note 만들어줘" | `daily-note` |
| "할 일 추가해줘: 이메일 답장" | `todo` |
| "이 아이디어 기록해줘" | `idea` |
| "이 프로젝트 progress 갱신해줘" | `progress` |
| "이 내용 위키에 통합해줘" | `wiki-ingest` |
| "이 PDF 마크다운으로 바꿔줘" | `pdf-to-md` |
| "이 마크다운 핸드아웃 PDF로" | `md-to-pdf` |
| "같이 생각해보자" | `thinking-partner` |
| "이거 같이 읽자" | `sensemaking` |

전체 스킬 목록은 [.claude/skills/README.md](.claude/skills/README.md) 참조.

## 폴더 구조

Johnny Decimal 시스템 기반.

```
orgn-workspace/
├── .claude/
│   ├── agents/        # 전용 서브에이전트 (research / analysis / content / development / zettelkasten)
│   └── skills/        # 프로젝트 스킬 (키워드 자동 트리거)
├── 00-inbox/          # 빠른 캡처 공간 (20개 미만 유지, 주간 처리)
├── 00-system/         # 시스템 설정, 템플릿, 가이드
│   ├── 01-templates/  # daily, weekly, project, progress
│   └── 03-guides/     # Git, Notion, 한글(HWPX), Claude Code 실습 가이드
├── 10-projects/       # 활성 프로젝트 (시한부)
├── 20-operations/     # 지속적 운영 업무
├── 30-knowledge/
│   ├── 00-wiki/       # 지식 위키 (복리 축적)
│   └── 37-claude-code/ # Claude Code 자체 사용법 노하우
├── 40-personal/
│   ├── 41-daily/      # Daily Notes (월별)
│   ├── 42-weekly/     # Weekly Reviews
│   ├── 43-ideas/      # 아이디어
│   ├── 44-reflections/ # 회고·학습
│   └── 46-todos/      # active-todos.md
├── 50-resources/      # 참고 자료, 첨부, 외부 데이터
└── 90-archive/        # 완료·중단 항목
```

운영 원칙: **[30-knowledge/00-wiki/워크스페이스-구조-원칙.md](30-knowledge/00-wiki/워크스페이스-구조-원칙.md)** — "폴더는 얕게, 명명·링크·인덱스를 풍부하게".

## Skills vs Slash Commands

| Slash Command (구) | Skill (신) |
|---|---|
| `/daily-note` 수동 입력 | "오늘 노트 만들어줘" 자연어 호출 |
| 이름을 외워야 함 | 키워드로 자동 트리거 |
| 빠르지만 경직됨 | 유연하고 대화적 |

## Wiki System

`30-knowledge/00-wiki/`는 **지식이 복리로 축적되는 위키**입니다.

- 주제에 대해 물으면 Claude가 여기부터 확인
- 새 소스(회의록, 영상, 기사)를 여기에 통합 (`wiki-ingest` 스킬)
- 주기적 헬스체크 (`wiki-lint` 스킬)

운영 규칙·페이지 형식은 [30-knowledge/00-wiki/SCHEMA.md](30-knowledge/00-wiki/SCHEMA.md) 참조.

## 외부 도구 연동 (선택)

- **Google Workspace** (`gws` CLI) — Gmail·Drive·Calendar·Docs·Sheets 연동
- **Notion** — `notion-handler` 스킬 (DB·페이지 관리)
- **MCP 서버** — `.mcp.json`에 정의된 서버들이 Claude Code 시작 시 자동 연결

설치 가이드: [00-system/03-guides/](00-system/03-guides/)

## Philosophy

1. **AI가 사고를 증폭**한다 — 작성만이 아니라 사고 자체.
2. **파일 시스템 = AI의 기억**.
3. **구조는 창의를 막지 않고, 가능하게** 한다.
4. **완벽보다 반복**.
5. **지식은 복리로 쌓인다** (위키를 통해).

## Credits

- [Claudesidian](https://github.com/heyitsnoah/claudesidian) by Noah Brier — PKM 아이디어 원형
- [Karpathy on LLM Wiki](https://x.com/karpathy) — 위키 복리 구조의 영감
- 원본 배포판 "do-better-workspace" by hovoo (이림) — 본 템플릿의 직계 조상

## License

MIT — 자유롭게 사용하고 수정하세요.

---

**ORGN Workspace** by ORGN
