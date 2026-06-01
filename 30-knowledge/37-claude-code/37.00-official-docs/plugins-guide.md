# Claude Code Plugins - Source of Truth

> **Source**: claude-plugins-official marketplace (plugin-dev, plugins-reference), 실제 설치/운용 경험
> **Updated**: 2026-05-16 (v2.1.143) - **plugin dependency enforcement**, marketplace projected context cost, `claude plugin details`/`prune`, root-level SKILL.md auto-surface, `--plugin-url`/`--plugin-dir` .zip, `experimental` 키, `CLAUDE_CODE_PLUGIN_PREFER_HTTPS`
> **Purpose**: Plugin 개발/설치/관리 시 유일한 참조 문서. 이 파일이 source of truth.

---

## 1. Plugin 개요

**Plugin**은 Skills, Commands, Agents, Hooks, MCP Servers를 하나의 배포 가능한 패키지로 묶은 단위. 개인이 만든 자동화를 팀/조직에 배포하거나, 마켓플레이스에서 다른 사람이 만든 Plugin을 설치하여 사용할 수 있다.

### 핵심 특성

- `.claude-plugin/plugin.json` manifest 파일이 Plugin의 정체성을 정의
- 설치 한 줄로 Skills + Commands + Agents + Hooks + MCP를 일괄 적용
- 네임스페이스로 다른 Plugin/개인 스킬과 충돌 방지
- user / project / local 3가지 설치 스코프 지원
- Anthropic 공식 마켓플레이스 + 커뮤니티 마켓플레이스 지원

### Skills/Commands와의 관계

```
개인 Skill:   ~/.claude/skills/my-skill/SKILL.md        -> /my-skill
프로젝트 Skill: .claude/skills/my-skill/SKILL.md          -> /my-skill
Plugin Skill:  <plugin>/skills/my-skill/SKILL.md          -> /plugin-name:my-skill
```

Plugin은 기존 Skills/Commands의 상위 배포 레이어. 개별 파일들은 동일한 문법을 따르고, Plugin이 이를 패키징하여 네임스페이스와 배포 기능을 추가한다.

---

## 2. 디렉토리 구조

### 최소 구조 (Plugin으로 인식되기 위한 최소 요건)

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json        # 필수: manifest
└── (아무 컴포넌트 1개 이상)
```

### 표준 구조

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json        # 필수: manifest
├── commands/              # 슬래시 커맨드 (자동 발견)
│   ├── analyze.md         # -> /plugin-name:analyze
│   └── report/            # 하위 디렉토리 = 네임스페이스
│       └── weekly.md      # -> /plugin-name:weekly (plugin:plugin-name:report)
├── skills/                # 도메인 지식 (자동 로드)
│   └── my-domain/
│       ├── SKILL.md
│       ├── references/
│       └── examples/
├── agents/                # 자율 실행 에이전트
│   └── validator.md
├── hooks/                 # 이벤트 기반 자동화
│   └── hooks.json
├── servers/               # MCP 서버
│   └── .mcp.json
├── lib/                   # 공유 라이브러리/스크립트
│   └── utils.js
└── README.md
```

### 자동 발견 규칙

| 컴포넌트 | 위치 | 발견 시점 |
|----------|------|----------|
| Commands | `commands/*.md` | Plugin 로드 시 자동 등록 |
| Skills | `skills/*/SKILL.md` | Plugin 로드 시 자동 로드 |
| Agents | `agents/*.md` | Plugin 로드 시 자동 등록 |
| Hooks | `hooks/hooks.json` | Plugin 로드 시 자동 적용 |
| MCP | `servers/.mcp.json` | Plugin 로드 시 자동 연결 |

수동 등록 불필요. 정해진 디렉토리에 파일을 배치하면 Claude Code가 자동 인식한다.

---

## 3. plugin.json Manifest

### 필수 필드

```json
{
  "name": "my-plugin",
  "version": "0.1.0",
  "description": "Plugin이 하는 일을 한 줄로 설명"
}
```

### 전체 필드

```json
{
  "name": "iloom-ax",
  "version": "1.0.0",
  "description": "일룸 AX 컨설팅 업무 자동화",
  "author": {
    "name": "일룸 DX팀",
    "email": "dx@iloom.com"
  },
  "homepage": "https://github.com/iloom/ax-plugin",
  "repository": "https://github.com/iloom/ax-plugin",
  "license": "MIT",
  "keywords": ["iloom", "ax", "automation"]
}
```

### 필드 설명

| 필드 | 필수 | 설명 |
|------|------|------|
| name | O | Plugin 이름 (kebab-case, 영문) |
| version | O | 시맨틱 버전 (major.minor.patch) |
| description | O | 한 줄 설명 |
| author | X | 작성자 정보 (name, email) |
| homepage | X | Plugin 홈페이지 URL |
| repository | X | Git 저장소 URL |
| license | X | 라이선스 종류 |
| keywords | X | 검색용 키워드 배열 |

---

## 4. 네임스페이스

Plugin 설치 후 모든 커맨드에 Plugin 이름이 prefix로 붙는다.

```
개인 스킬:        /analyze-review
Plugin 설치 후:   /iloom-ax:analyze-review
```

### 하위 디렉토리 네임스페이스

```
commands/
├── deploy/
│   ├── staging.md      # /staging (plugin:my-plugin:deploy)
│   └── prod.md         # /prod (plugin:my-plugin:deploy)
└── review/
    └── security.md     # /security (plugin:my-plugin:review)
```

`/help` 출력에서 `(plugin:plugin-name)` 또는 `(plugin:plugin-name:namespace)` 라벨로 표시된다.

### 충돌 방지

- 서로 다른 Plugin에 같은 이름의 커맨드가 있어도 네임스페이스로 구분
- 개인 스킬과 Plugin 스킬이 같은 이름이면, 개인 스킬은 `/name`, Plugin 스킬은 `/plugin-name:name`으로 분리

---

## 5. 설치 스코프

| 스코프 | 명령어 | 영향 범위 | 사용 시점 |
|--------|--------|----------|----------|
| user | `/plugin install --scope user` | 내 모든 프로젝트 | 개인용 유틸리티 |
| project | `/plugin install --scope project` | 이 프로젝트의 모든 사용자 | 팀 표준 도구 |
| local | `/plugin install --scope local` | 내 로컬, 이 프로젝트만 | 테스트/실험 |

- **project 스코프**: `.claude/plugins/` 디렉토리에 설치. git으로 공유되므로 팀원 전원이 자동 적용
- **user 스코프**: `~/.claude/plugins/` 디렉토리에 설치. 개인 환경에만 적용
- **local 스코프**: 로컬에만, git에 포함되지 않음

---

## 6. Plugin 관리 명령어

### 설치/제거/리로드

```bash
# 마켓플레이스에서 설치
/plugin install <plugin-name>

# 특정 마켓플레이스 소스 등록
/plugin marketplace add <marketplace-url-or-org/repo>

# 마켓플레이스에서 설치 (소스 지정)
/plugin install <plugin-name>@marketplace

# 제거
/plugin uninstall <plugin-name>
```

### 조회

```bash
# 설치된 Plugin 목록
/plugin list

# Plugin 상세 정보
/plugin info <plugin-name>
```

### 활성화/비활성화

```bash
# 임시 비활성화 (제거하지 않고 끔)
/plugin disable <plugin-name>

# 다시 활성화
/plugin enable <plugin-name>
```

### 업데이트

```bash
# 최신 버전으로 업데이트
/plugin update <plugin-name>

# 세션 재시작 없이 변경사항 적용 (v2.1.69)
/reload-plugins
```

**동작 노트 (v2.1.119)**: 다른 플러그인의 의존성 version constraint로 pinned된 플러그인은 constraint를 만족하는 최고 git tag로 자동 업데이트된다. 제약 때문에 auto-update가 스킵되면 `/doctor`와 `/plugin` Errors 탭에 표시된다 (v2.1.118).

### Plugin Dependency Enforcement (v2.1.143, 동작 변경)

플러그인 의존성이 enable/disable에 강제됨:

```bash
# A 플러그인이 B 플러그인에 의존하는 경우
/plugin disable B
# → 거부됨: A still depends on B
# → disable-chain hint 출력 (copy-paste 가능): "claude plugin disable A B"

/plugin enable A
# → B (transitive dependency)가 자동으로 force-enable됨
```

기존 동작: B를 그냥 disable하면 A가 silent로 깨졌음. 이제 명시적으로 chain disable을 요구.

### Plugin Prune (v2.1.121)

```bash
# 다른 플러그인이 의존하지 않는 orphan auto-installed 플러그인 제거
claude plugin prune

# 제거 시 cascading prune
/plugin uninstall <name> --prune
```

수동 설치 플러그인은 prune 대상이 아니므로, dependency-only auto-install된 항목만 정리됨.

### Plugin Details (v2.1.139)

```bash
claude plugin details <name>
```

플러그인의 component inventory(commands/skills/agents/hooks/MCP), projected per-session token cost, hook event names, MCP server names 표시. **(v2.1.142)** LSP 서버도 포함.

### 마켓플레이스 Browse: Projected Context Cost (v2.1.143)

`/plugin` 마켓플레이스 browse pane에 plugin별 per-turn / per-invocation 토큰 추정치가 표시됨. 설치 전에 컨텍스트 점유 비용을 가늠하여 선택 가능.

### 플러그인 릴리스 태깅 (v2.1.118 신규)

플러그인 개발자가 릴리스 git tag를 생성할 때 사용. 버전 유효성 검증 포함:

```bash
# 플러그인 루트에서 실행 — plugin.json의 version을 읽어 git tag 생성
claude plugin tag
```

`plugin.json`의 `version` 필드(semver)와 git tag를 동기화하여, 다른 플러그인이 version constraint로 이 플러그인을 참조할 때 올바른 태그가 해석되도록 한다.

---

## 7. `${CLAUDE_PLUGIN_ROOT}` 환경 변수

Plugin 내부에서 파일 경로를 참조할 때 사용하는 특수 환경 변수. Plugin이 어디에 설치되든 올바른 경로로 확장된다.

### 사용법

```markdown
---
description: Plugin 스크립트 실행
allowed-tools: Bash(node:*)
---

분석 실행: !`node ${CLAUDE_PLUGIN_ROOT}/scripts/analyze.js`

템플릿 참조: @${CLAUDE_PLUGIN_ROOT}/templates/report.md

설정 로드: @${CLAUDE_PLUGIN_ROOT}/config/settings.json
```

### 확장 결과

```
${CLAUDE_PLUGIN_ROOT}/scripts/analyze.js
-> /home/user/.claude/plugins/my-plugin/scripts/analyze.js
```

### 필수 사용 규칙

```markdown
# 올바른 사용 (항상 CLAUDE_PLUGIN_ROOT 사용)
@${CLAUDE_PLUGIN_ROOT}/templates/foo.md

# 잘못된 사용 (상대 경로는 현재 디렉토리 기준이 됨)
@./templates/foo.md
```

Plugin 내부 파일을 참조할 때는 반드시 `${CLAUDE_PLUGIN_ROOT}`를 사용해야 한다. 상대 경로는 사용자의 현재 작업 디렉토리 기준으로 해석되어 오동작한다.

### `${CLAUDE_PLUGIN_DATA}` (v2.1.78)

Plugin 업데이트 후에도 유지되는 영구 상태 저장 경로:

```markdown
설정 저장: @${CLAUDE_PLUGIN_DATA}/user-config.json
```

- `/plugin uninstall` 시 삭제 여부 확인 프롬프트 표시
- Plugin 업데이트 시 데이터 보존

### Plugin-shipped Agent 확장 frontmatter (v2.1.78)

Plugin의 `agents/` 디렉토리에 포함된 에이전트에 추가 frontmatter 지원:

```yaml
---
name: my-agent
effort: medium
maxTurns: 50
disallowedTools: Bash, Write
---
```

### Plugin 사용자 설정 (v2.1.83)

Plugin manifest에 `userConfig` 옵션 지원. Plugin 활성화 시 사용자에게 설정 입력 요청:

```json
{
  "userConfig": {
    "api_key": {
      "description": "API key for the service",
      "sensitive": true
    }
  }
}
```

- `sensitive: true`: macOS keychain 또는 보호된 credentials 파일에 저장
- Plugin 활성화 시 설정 입력 프롬프트 표시

### `source: 'settings'` Plugin (v2.1.80)

settings.json에 Plugin 항목을 인라인으로 선언 가능:

```json
{
  "plugins": {
    "my-plugin": {
      "source": "settings",
      "path": "/path/to/plugin"
    }
  }
}
```

### `CLAUDE_CODE_PLUGIN_SEED_DIR` 다중 경로 (v2.1.79)

플랫폼 경로 구분자(Unix `:`, Windows `;`)로 여러 seed 디렉토리 지정 가능:

```bash
export CLAUDE_CODE_PLUGIN_SEED_DIR="/path/one:/path/two"
```

---

## 8. 공식 마켓플레이스 Plugin 목록

### Development & Code Quality

| Plugin | 용도 | 주요 기능 |
|--------|------|----------|
| plugin-dev | Plugin 개발 | Skills/Commands/Agents/Hooks 생성 가이드 |
| code-review | 코드 리뷰 | 멀티 에이전트 리뷰 + 신뢰도 점수 |
| code-simplifier | 코드 리팩토링 | 기능 유지하며 코드 단순화 |
| feature-dev | 기능 개발 | E2E 기능 개발 워크플로우 |

### Git & Workflow

| Plugin | 용도 | 주요 기능 |
|--------|------|----------|
| commit-commands | Git 워크플로우 | /commit, /commit-push-pr |
| hookify | 자동화 규칙 | 대화 패턴에서 Hook 자동 생성 |

### Frontend & Design

| Plugin | 용도 | 주요 기능 |
|--------|------|----------|
| frontend-design | UI 개발 | 프로덕션급 UI, 제네릭 디자인 방지 |
| playground | 시각화 | 데이터 탐색, 디자인 플레이그라운드 |

### Learning & Guidance

| Plugin | 용도 | 주요 기능 |
|--------|------|----------|
| explanatory-output-style | 학습 | 코드 선택 이유를 교육적으로 설명 |
| learning-output-style | 인터랙티브 학습 | 의사결정 지점에서 사용자 참여 유도 |
| security-guidance | 보안 | 코드 편집 시 보안 이슈 경고 |

### Language Servers (LSP)

| Plugin | 언어 |
|--------|------|
| typescript-lsp | TypeScript/JavaScript |
| pyright-lsp | Python |
| gopls-lsp | Go |
| rust-analyzer-lsp | Rust |
| clangd-lsp | C/C++ |
| jdtls-lsp | Java |
| kotlin-lsp | Kotlin |
| swift-lsp | Swift |
| csharp-lsp | C# |
| php-lsp | PHP |
| lua-lsp | Lua |

### External Plugins (외부 서비스 연동)

| Plugin | 서비스 |
|--------|--------|
| supabase | Supabase DB/Auth |
| slack | Slack 메시지 |
| github | GitHub API |
| firebase | Firebase |
| stripe | Stripe 결제 |
| greptile | 코드베이스 검색 |

---

## 9. Plugin 만들기: Claude Code에게 요청

Plugin을 직접 손으로 만들 필요 없다. Claude Code에게 자연어로 요청하면 된다.

### 기본 요청

```
"내가 만든 VOC 분석 스킬이랑 리포트 커맨드를 iloom-ax라는 Plugin으로 만들어줘"
```

Claude Code가 처리하는 작업:
1. 디렉토리 구조 생성
2. plugin.json manifest 작성
3. 기존 스킬/커맨드 파일 복사 및 배치
4. README.md 생성

### plugin-dev Plugin 활용

공식 마켓플레이스의 `plugin-dev` Plugin을 설치하면 `/create-plugin` 커맨드를 사용할 수 있다.

```bash
/plugin install plugin-dev
/create-plugin "일룸 AX 업무 자동화 플러그인"
```

8단계 가이드 워크플로우로 진행:

| 단계 | 내용 |
|------|------|
| Phase 1 | Discovery: 요구사항 파악 |
| Phase 2 | Component Planning: 컴포넌트 구성 결정 |
| Phase 3 | Detailed Design: 상세 설계 + 질문 |
| Phase 4 | Structure Creation: 디렉토리 + manifest 생성 |
| Phase 5 | Implementation: 각 컴포넌트 구현 |
| Phase 6 | Validation: 품질 검증 |
| Phase 7 | Testing: 테스트 + 검증 |
| Phase 8 | Documentation: 문서화 + 배포 준비 |

### 조직 정책 관리

**(v2.1.83)** `managed-settings.d/` drop-in 디렉토리 지원. `managed-settings.json`과 함께 별도 팀이 독립적 정책 조각을 배포 가능 (알파벳 순 병합).

**(v2.1.84)** `allowedChannelPlugins` managed setting으로 팀/기업 관리자가 channel plugin allowlist 정의.

**(v2.1.85)** 조직 정책(`managed-settings.json`)으로 차단된 Plugin은 설치/활성화 불가, 마켓플레이스에서 숨김.

### Plugin bin/ 실행 파일 (v2.1.91)

Plugin이 `bin/` 디렉토리에 실행 파일을 포함할 수 있으며, Bash 도구에서 bare command로 직접 호출 가능:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── bin/
│   └── my-tool          # Bash에서 `my-tool` 로 직접 실행 가능
└── skills/
```

### Plugin Skills 이름 기반 호출 (v2.1.94)

Plugin manifest에서 `"skills": ["./"]`로 선언된 스킬이 frontmatter의 `name` 필드를 기반으로 호출됨. 디렉토리명이 아닌 명시적 이름으로 정확한 매칭.

### Plugin Hooks 개선 (v2.1.94~2.1.101)

- **(v2.1.94)** Plugin skill hooks가 YAML frontmatter에서 정의해도 무시되던 버그 수정
- **(v2.1.94)** `CLAUDE_PLUGIN_ROOT` 없이 plugin hooks가 "No such file or directory" 에러 발생하던 버그 수정
- **(v2.1.94)** `${CLAUDE_PLUGIN_ROOT}`가 local-marketplace plugin에서 잘못된 디렉토리로 확장되던 버그 수정
- **(v2.1.101)** `allowManagedHooksOnly` 설정에서도 plugin hooks가 정상 실행되도록 개선
- **(v2.1.101)** `/plugin` 및 `claude plugin update`에 마켓플레이스 새로고침 경고 추가

### 백그라운드 모니터 (v2.1.105)

Plugin manifest에 최상위 `monitors` 키 지원. 세션 시작 또는 스킬 호출 시 자동으로 arm 되는 백그라운드 모니터를 정의할 수 있음.

### PreCompact Hook 차단 (v2.1.105)

Plugin hooks의 `PreCompact` 이벤트에서 exit code 2 또는 `{"decision":"block"}` 반환으로 컨텍스트 압축 자체를 차단 가능.

### Package.json 의존성 자동 설치 (v2.1.105)

`package.json`과 lockfile을 포함한 마켓플레이스 플러그인 설치/업데이트 시 의존성이 자동 설치됨 (이전 버전 버그 수정).

### Policy-managed Plugin 자동 업데이트 (v2.1.108)

Policy로 관리되는 플러그인이 처음 설치된 프로젝트가 아닌 다른 프로젝트에서 실행되어도 자동 업데이트 되도록 수정.

### MCP Tool Result Size Override (v2.1.91)

MCP 도구 결과에 `_meta["anthropic/maxResultSizeChars"]` 어노테이션으로 최대 500K까지 결과 크기를 늘릴 수 있음. DB 스키마 등 대형 결과가 잘리지 않고 전달됨.

### 오프라인 마켓플레이스 캐시 보존 (v2.1.90)

`CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE` 환경변수: `git pull` 실패 시 기존 마켓플레이스 캐시를 유지. 오프라인 환경에서 유용.

### 유효성 검사 (v2.1.77)

```bash
claude plugin validate
```

Skill, Agent, Command frontmatter와 `hooks/hooks.json`을 검사하여 YAML 파싱 오류 및 스키마 위반을 감지.

**(v2.1.120)** `marketplace.json` 최상위에 `$schema`, `version`, `description` 키를 허용. `plugin.json` 최상위에도 `$schema` 키 허용. JSON Schema 기반 IDE 자동완성/검증 가능.

**(v2.1.129)** `themes`와 `monitors`는 plugin.json `"experimental": { ... }` 블록 내로 이동 권장:

```jsonc
{
  "name": "my-plugin",
  "version": "1.0.0",
  "experimental": {
    "themes": ["themes/"],
    "monitors": ["monitors/"]
  }
}
```

최상위 선언도 계속 작동하지만 `claude plugin validate`에서 warning 발생.

**(v2.1.140)** Plugin이 default component 폴더(예: `commands/`)를 가지고 있는데 `plugin.json`에 같은 키를 명시하면 default가 silent로 ignore 되던 동작에 명시적 warning 추가. `/doctor`, `claude plugin list`, `/plugin`에서 모두 표시.

### Plugin Root SKILL.md (v2.1.142)

`skills/` 서브디렉토리 없이 플러그인 루트에 `SKILL.md`만 두면 자동으로 단일 스킬로 인식됨:

```
my-plugin/
├── .claude-plugin/plugin.json
└── SKILL.md              # 자동 surfacing
```

또는 명시적으로 `"skills": ["./"]` 선언 가능 (v2.1.142에서 "path escapes plugin directory" 거짓 오류 수정). 단일 스킬 플러그인 작성이 더 간단해짐.

### `--plugin-dir` / `--plugin-url` 확장

- **(v2.1.128)** `--plugin-dir`이 디렉토리뿐 아니라 `.zip` 플러그인 아카이브도 수용
- **(v2.1.129)** `--plugin-url <url>` 신규 플래그: 원격 URL에서 `.zip` 아카이브를 받아 현재 세션에 일시 적용. 마켓플레이스 등록 없이 테스트용으로 활용

### GitHub HTTPS Clone (v2.1.141)

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

GitHub 플러그인 소스를 SSH 대신 HTTPS로 clone — GitHub SSH key 미설정 환경(CI, sandbox)에서 유용.

### 마켓플레이스 Auto-refresh (v2.1.141)

`claude plugin install <name>@<marketplace>`가 not-found 보고 전에 자동으로 마켓플레이스를 새로고침 후 재시도 — stale 캐시로 인한 "최신 플러그인 미발견" 문제 해소.

### 테스트

```bash
# 로컬에서 Plugin 테스트
cc --plugin-dir /path/to/my-plugin

# 또는 프로젝트의 .claude-plugin/ 디렉토리에 복사하여 테스트
```

---

## 10. 팀 배포 흐름

### 만드는 사람 (1회)

```
1. Claude Code에게 Plugin 생성 요청
2. 결과 확인 (폴더 구조, plugin.json)
3. GitHub 저장소에 push
```

### 사용하는 사람 (팀원)

```bash
# 1) 마켓플레이스 소스 등록
/plugin marketplace add org/repo

# 2) Plugin 설치
/plugin install plugin-name@marketplace
```

### 업데이트 배포

```
만드는 사람: 변경 후 GitHub push + version 올리기
사용하는 사람: /plugin update plugin-name
```

---

## 11. 코드베이스 -> Plugin 추천 매핑

| 상황 | 추천 Plugin |
|------|-------------|
| Plugin 개발하려는 경우 | plugin-dev |
| PR 기반 워크플로우 | commit-commands |
| 코드 리뷰 자동화 | code-review |
| React/Vue/Angular 프론트엔드 | frontend-design |
| 자동화 규칙 만들기 | hookify |
| TypeScript 프로젝트 | typescript-lsp |
| Python 프로젝트 | pyright-lsp |
| 보안 민감 코드 | security-guidance |
| 학습/온보딩 | explanatory-output-style |

---

## Related

- [[skills-guide]] - Skills 시스템 (Plugin의 하위 컴포넌트)
- [[subagents-guide]] - Subagent 가이드 (Plugin의 agents/ 컴포넌트)
- [[rules-guide]] - Rules 가이드 (Plugin의 hooks와 관련)
- [[claude-md-guide]] - CLAUDE.md 가이드

---

## Update History

- **2026-05-16**: v2.1.120~2.1.143 변경사항 반영
  - `claude plugin validate`가 `marketplace.json` 최상위 `$schema`/`version`/`description`, `plugin.json` 최상위 `$schema` 허용 (v2.1.120)
  - `claude plugin prune` — orphan auto-installed dependency 제거, `uninstall --prune`로 cascading (v2.1.121)
  - `--plugin-dir`이 `.zip` 아카이브 수용 (v2.1.128)
  - `--plugin-url <url>` — 원격 .zip 일회성 적용 (v2.1.129)
  - Plugin manifest의 `themes`/`monitors`가 `experimental` 블록 내 권장; 최상위 선언은 `validate` warning (v2.1.129)
  - `CLAUDE_CODE_PLUGIN_PREFER_HTTPS` — GitHub 플러그인 HTTPS clone (v2.1.141)
  - `claude plugin install @marketplace`가 not-found 전에 자동 새로고침/재시도 (v2.1.141)
  - Plugin이 default component 폴더 ignore 시 명시 warning (v2.1.140) — `/doctor`, `claude plugin list`, `/plugin` 표시
  - `claude plugin details <name>` — component inventory + projected token cost (v2.1.139)
  - `/context`가 plugin-sourced skill의 providing plugin 이름 표시 (v2.1.139)
  - 플러그인 루트의 `SKILL.md`가 단일 스킬로 자동 surfacing (v2.1.142)
  - `skills: ["./"]` 사용 시 "path escapes plugin directory" 거짓 오류 수정 (v2.1.142)
  - `/plugin` 상세 pane이 plugin이 제공하는 LSP 서버 표시 (v2.1.142)
  - **Plugin dependency enforcement** (v2.1.143): `disable` 거부 + chain hint, `enable` transitive force-enable
  - `/plugin` 마켓플레이스 browse에 projected context cost 표시 (v2.1.143)
  - `claude plugin install`이 marketplace `ref`가 사라지고 `sha`가 pinned된 경우 실패하던 버그 수정 (v2.1.141)
  - Plugin uninstall/enable-disable이 slug case-insensitive 매칭 (v2.1.136)
  - Plugin advisories가 `plugin.json` shadow된 default 폴더 키를 모두 명시 (v2.1.142)

- **2026-04-19**: v2.1.110~2.1.114 변경사항 반영
  - **Plugin 의존성 에러 핸들링 개선 (v2.1.111)**: conflicting/invalid/overly complex version requirement를 구분해서 보고. `plugin update` 후 stale resolved version 수정. `plugin install`이 중단된 이전 설치에서 복구
  - **`plugin install` 의존성 충돌 보고 (v2.1.114)**: 이미 설치된 플러그인과 dependency 버전이 충돌할 때 install이 잘못 성공하던 버그 수정 — 이제 `range-conflict`로 보고
  - **Headless `--output-format stream-json` plugin_errors (v2.1.111)**: init 이벤트에 `plugin_errors` 포함 (의존성 미충족으로 demoted된 플러그인)
  - `/plugin` Installed 탭 개선 (v2.1.110): 주의 필요한 항목과 favorites가 상단에 표시, disabled 항목은 fold 뒤로, `f` 키로 favorite 토글
  - `/doctor`가 동일 MCP 서버가 여러 config scope에 다른 endpoint로 정의된 경우 경고 (v2.1.110)
- **2026-04-15**: v2.1.105~2.1.109 변경사항 반영
  - 최상위 `monitors` manifest 키 지원 - 세션 시작/스킬 호출 시 자동 arm 되는 백그라운드 모니터 (v2.1.105)
  - PreCompact hook 차단 지원 - exit code 2 또는 `{"decision":"block"}` 반환 (v2.1.105)
  - `package.json` + lockfile 플러그인 설치/업데이트 시 의존성 자동 설치 (v2.1.105)
  - 마켓플레이스 auto-update가 파일 열린 상태에서 공식 마켓플레이스를 깨뜨리던 버그 수정 (v2.1.105)
  - Policy-managed 플러그인이 다른 프로젝트에서 실행 시 auto-update 안 되던 버그 수정 (v2.1.108)
- **2026-04-13**: v2.1.93~2.1.101 변경사항 반영
  - Plugin skills `"skills": ["./"]` 선언 시 frontmatter `name` 기반 호출 (v2.1.94)
  - `keep-coding-instructions` frontmatter 필드 (v2.1.94) - output style plugin용
  - Plugin skill hooks YAML frontmatter 무시 수정 (v2.1.94)
  - `${CLAUDE_PLUGIN_ROOT}` local-marketplace 경로 수정 (v2.1.94)
  - `allowManagedHooksOnly`에서 plugin hooks 실행 허용 (v2.1.101)
  - `/plugin update` 마켓플레이스 새로고침 경고 추가 (v2.1.101)
  - `/reload-plugins`가 스킬 변경 즉시 반영 (v2.1.98)
  - 다수 plugin 슬래시 커맨드 해석, `ENAMETOOLONG`, 버전 캐시 수정 (v2.1.101)
- **2026-04-04**: v2.1.90~2.1.92 변경사항 반영
  - Plugin `bin/` 디렉토리 실행 파일 지원 (v2.1.91)
  - MCP tool result size override `_meta["anthropic/maxResultSizeChars"]` 최대 500K (v2.1.91)
  - `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE` 오프라인 캐시 보존 (v2.1.90)
  - Plugin MCP 서버 세션 시작 시 "connecting" 상태 멈춤 수정 (v2.1.92)
  - `disableSkillShellExecution` 설정으로 Plugin 커맨드 셸 실행 비활성화 (v2.1.91)
  - `forceRemoteSettingsRefresh` 정책 (v2.1.92) - fail-closed managed settings
- **2026-03-31**: v2.1.79~2.1.88 변경사항 반영
  - Plugin `userConfig` 옵션 + `sensitive` 키체인 저장 (v2.1.83)
  - `source: 'settings'` 인라인 Plugin 선언 (v2.1.80)
  - `managed-settings.d/` drop-in 디렉토리 (v2.1.83)
  - `allowedChannelPlugins` managed setting (v2.1.84)
  - 조직 정책 차단 Plugin 숨김 (v2.1.85)
  - `CLAUDE_CODE_PLUGIN_SEED_DIR` 다중 경로 (v2.1.79)
- **2026-03-18**: v2.1.69~2.1.78 변경사항 반영
  - `${CLAUDE_PLUGIN_DATA}` 영구 상태 변수 (v2.1.78)
  - Plugin-shipped agent `effort`, `maxTurns`, `disallowedTools` frontmatter (v2.1.78)
  - `claude plugin validate` 명령 (v2.1.77)
  - `/reload-plugins` 명령 (v2.1.69)
  - `pluginTrustMessage` managed settings (v2.1.69)
  - `git-subdir` 소스 타입 (v2.1.69)
- **2026-03-10**: 초기 작성

**Last Updated**: 2026-05-16
