# ORGN Workspace 가이드

> Claude Code + Johnny Decimal 기반 PKM 워크스페이스.
> 이 파일은 Claude Code가 매 세션 시작 시 자동으로 읽는 프로젝트 지침입니다.

## 폴더 구조 (Johnny Decimal)

```
00-inbox/      # 임시 캡처 (20개 미만 유지, 주간 처리)
00-system/     # 시스템 설정, 템플릿, 가이드
10-projects/   # 활성 프로젝트 (시한부)
20-operations/ # 지속적 운영 (종료일 없음)
30-knowledge/  # 지식 (00-wiki + 도메인 아카이브)
40-personal/   # 개인 노트 (daily, weekly, ideas, reflections, todos)
50-resources/  # 외부 자료, 첨부파일
90-archive/    # 완료/중단 항목
```

### 주요 하위 폴더

| 번호 | 폴더 | 용도 |
|------|------|------|
| **00-wiki** | 30-knowledge/ | 지식 위키 (복리 축적). 작업 시 `index.md` 먼저 확인 |
| 41-daily | 40-personal/ | Daily Notes (월별: 41-daily/YYYY-MM/) |
| 42-weekly | 40-personal/ | Weekly Review |
| 43-ideas | 40-personal/ | 아이디어 캡처 |
| 44-reflections | 40-personal/ | 회고 및 학습 |
| 46-todos | 40-personal/ | active-todos.md |
| 37-claude-code | 30-knowledge/ | Claude Code 관련 지식 |

위키 운영 규칙(3계층·3오퍼레이션·페이지 형식·복리 메커니즘)은 위키 작업 시 `30-knowledge/00-wiki/SCHEMA.md`를 직접 Read.

## 파일 명명 규칙

| 유형 | 형식 | 예시 |
|------|------|------|
| Daily Note | `YYYY-MM-DD.md` | 2026-04-24.md |
| 주제 노트 | `주제명.md` | thinking-partner.md |
| JD 폴더 | `XX-name` 또는 `XX.YY-name` | 37-claude-code, 37.01-learning |
| 중복 파일명 | JD prefix 필수 | 18-progress-tracker.md |

## Inbox · 첨부파일

- **Inbox (00-inbox)**: 임시 캡처, 20개 미만 유지, 주간 처리 (Capture → Process → Organize)
- **첨부 (50-resources/attachments/)**: 모든 비텍스트 파일, 명명 `[관련노트]_[설명].[ext]`

## Skills · Agents

`.claude/skills/`에 프로젝트 전용 스킬, `.claude/agents/`에 서브에이전트. 스킬은 키워드 기반 **자동 트리거** (수동 슬래시 커맨드 아님).

---

## 내 프로필

> **TODO**: 아래 4개 필드를 본인 정보로 채워주세요. 채워진 내용은 매 세션 시작 시 Claude가 자동으로 읽어 협업의 첫 맥락이 됩니다.

**이름**: <YOUR_NAME>
**역할**: <YOUR_ROLE — 직책·하는 일·전문 영역을 1~3문장으로>
**관심사**: <YOUR_FOCUS — 이 워크스페이스로 다루고 싶은 주제·문제·시스템>
**이 워크스페이스 용도**: <YOUR_PURPOSE — 어떤 축으로 정보를 누적할 것인가>

**연동 도구**: <선택 — 예: Google Workspace (`gws` CLI), Notion, Linear 등 외부 연동 시 여기 명시>

---

## 회사·프로젝트 진입점 (선택)

> 특정 조직/프로젝트의 컨텍스트로 작업할 때, 먼저 읽어야 할 위키·문서를 여기에 모은다. 처음에는 비워두고 위키가 쌓이면 채우세요.

- **조직 정체성**: <예: [[조직-소개]]>
- **브랜딩·라이팅 가이드**: <예: [[brand-os]]>
- **자료 분류·SSOT**: <예: [[자료-분류]]>

---

**Last Updated**: 워크스페이스 초기화 시점
