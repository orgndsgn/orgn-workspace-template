# 37.00 Official Docs

> Claude Code 공식 문서 기반 Source of Truth 가이드.
> Skills/Subagents/Plugins/CLAUDE.md/Rules를 만들 때 **유일한 참조**로 사용한다.

## 목적

- Claude Code로 워크스페이스를 확장할 때(커스텀 스킬·서브에이전트·플러그인 작성, CLAUDE.md 튜닝 등) 공식 문서의 핵심만 발췌·번역해 둔 요약본
- 세부가 바뀌는 주제(Hooks 필드, YAML frontmatter, 권한 모드 등)는 여기서 먼저 확인
- 원문이 필요한 순간에는 각 문서 상단의 **Source** 링크를 따라갈 것

## 문서 목록

| 파일 | 내용 |
|------|------|
| [skills-guide.md](skills-guide.md) | Skills: SKILL.md 구조, 자동 트리거, 번들 스크립트 |
| [subagents-guide.md](subagents-guide.md) | Subagents: frontmatter, 권한, Hooks, MCP 연동 |
| [claude-md-guide.md](claude-md-guide.md) | CLAUDE.md 계층, Auto Memory, settings.json과의 관계 |
| [plugins-guide.md](plugins-guide.md) | Plugins: manifest, 설치 스코프, 네임스페이스, 배포 |
| [rules-guide.md](rules-guide.md) | `.claude/rules/` 디렉토리 모듈화 규칙 |

> Slash Commands 문서는 의도적으로 제외. 현재 공식 권장은 **Skills로 통합**.

## 공식 레퍼런스 링크

- 문서 루트: https://code.claude.com/docs/en/
- Memory & CLAUDE.md: https://code.claude.com/docs/en/memory
- Skills: https://code.claude.com/docs/en/skills
- Sub-agents: https://code.claude.com/docs/en/sub-agents
- Interactive Mode: https://code.claude.com/docs/en/interactive-mode
- CHANGELOG (진짜 최신): https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md

## 사용 흐름

1. **만들기 전에 읽기** — 새 스킬·서브에이전트·플러그인을 구상할 때 해당 문서를 먼저 훑는다
2. **frontmatter 복사 금지** — 구 버전 파일에서 복붙하지 말고 여기 최신 필드 목록을 근거로 작성
3. **헷갈리면 Source 원문** — 번역·요약 과정에서 미묘한 뉘앙스가 빠질 수 있으니 최종 의사결정 전 공식 문서 직접 확인
4. **CHANGELOG 체크** — Claude Code 버전이 올라가면 이 폴더의 `Updated` 라인과 CHANGELOG 사이 간격을 본다

## 문서 갱신 규칙

- 각 파일 상단의 `> **Updated**: YYYY-MM-DD (vX.Y.Z)` 라인을 진실의 원점으로 본다
- Claude Code 버전이 올라갔는데 문서 `Updated`가 오래됐으면 → CHANGELOG 훑고 영향 있는 섹션만 부분 갱신
- 원문이 크게 재구성되면 해당 파일 전체 재작성 후 `Updated` 갱신

## 자동 갱신: `doc-updater` 스킬

이 폴더의 5개 가이드는 **`doc-updater` 스킬**(`.claude/skills/doc-updater/`)로 유지관리한다.

- 트리거: "문서 업데이트", "CHANGELOG 확인", "doc update", "공식문서 업데이트"
- 동작: GitHub CHANGELOG를 읽고 → `docs_synced_version` 대비 새 변경사항을 카테고리별 분류 → 영향받는 문서만 부분 업데이트 → Breaking Change는 별도 리포트
- 캐시: `./.cache/doc-updater/` (gitignore 됨)

즉, Claude Code 버전이 올라갔다 싶으면 "문서 업데이트" 한 줄이면 이 폴더 전체가 최신으로 당겨진다.

---

**Last Updated**: 2026-04-24 (Claude Code v2.1.119 기준)
