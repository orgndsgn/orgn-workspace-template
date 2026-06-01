# .claude/rules/ - Source of Truth

> **Source**: [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)
> **Updated**: 2026-05-16 (v2.1.143) - PowerShell 기본화, `sandbox.bwrapPath`/`socatPath`, `parentSettingsBehavior`, `autoMode.hard_deny`, `--dangerously-skip-permissions` 보호 경로 확대, drive-root allow rule 수정
> **Purpose**: .claude/rules/ 시스템 유일한 참조 문서

---

## 1. 개요

`.claude/rules/` 디렉토리는 CLAUDE.md를 여러 파일로 모듈화하여 관리. 모든 `.md` 파일이 자동 로드됨. 서브디렉토리도 재귀 탐색.

---

## 2. 기본 구조

```
your-project/
├── .claude/
│   ├── CLAUDE.md
│   └── rules/
│       ├── code-style.md
│       ├── testing.md
│       ├── security.md
│       ├── frontend/
│       │   └── react.md
│       └── backend/
│           └── api.md
```

---

## 3. 저장 위치 및 우선순위

| 위치 | 경로 | 적용 범위 |
|------|------|----------|
| 프로젝트 | `./.claude/rules/*.md` | 해당 프로젝트 |
| 사용자 | `~/.claude/rules/*.md` | 모든 프로젝트 |

**우선순위** (높음 -> 낮음):
1. Enterprise policy
2. 프로젝트 CLAUDE.md
3. 프로젝트 rules
4. 사용자 CLAUDE.md
5. 사용자 rules
6. CLAUDE.local.md

`paths` 필드가 없는 규칙은 모든 파일에 무조건 적용.

---

## 4. 조건부 규칙 (Path-Specific Rules)

YAML frontmatter로 특정 파일에만 규칙 적용 가능.

### 작동하는 형식

```markdown
---
globs: **/*.ts, src/**/*.tsx
---

# API 개발 규칙
- 모든 API 엔드포인트에 입력 검증 필수
```

### paths 필드 개선 (v2.1.84)

**(v2.1.84)** Rules와 Skills의 `paths:` frontmatter가 **YAML 리스트 형식**을 정식 지원:

```yaml
# v2.1.84부터 작동 - YAML 리스트
paths:
  - "src/**/*.ts"
  - "lib/**/*.tsx"

# 기존 방식도 계속 작동
globs: **/*.ts, src/**/*.tsx
```

**이전 버그 참고** (Issue #17204): v2.1.83 이전에는 YAML 배열 형식이 작동하지 않았음. v2.1.84에서 수정됨.

**현재 권장**: `paths:` YAML 리스트 또는 `globs:` CSV 형식 모두 사용 가능.

### 알려진 제한사항

1. **user-level paths 미작동**: `~/.claude/rules/`에서 `paths:` / `globs:` 조건부 로딩이 완전히 비작동 (Issue #21858, 미해결)
2. **세션 내 해제 안 됨**: 한 번 로드된 조건부 규칙은 다른 디렉토리로 이동해도 세션 내에서 계속 활성 (Issue #16299, 미해결)
3. **Git worktree 무시**: Worktree 내에서 paths/globs 필터링이 무시됨 (Issue #23569)
4. **(v2.1.69 수정)** print 모드(`claude -p`)에서 조건부 rules와 중첩 CLAUDE.md가 로드되지 않던 버그 수정됨

### Glob 패턴

| 패턴 | 매칭 대상 |
|------|-----------|
| `**/*.ts` | 모든 디렉토리의 TypeScript 파일 |
| `src/**/*` | src/ 하위 모든 파일 |
| `*.md` | 프로젝트 루트의 마크다운 파일 |
| `**/*.{ts,tsx}` | ts와 tsx 파일 모두 |
| `{src,lib}/**/*.ts` | src와 lib 디렉토리 |

---

## 5. --add-dir 디렉토리 rules 로딩 (v2.1.20)

추가 디렉토리의 rules도 로드 가능:

```bash
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ../shared-config
```

공유 규칙 저장소를 여러 프로젝트에서 참조할 때 유용.

---

## 6. @import 활용

rules 파일에서 외부 문서 참조 가능:

```markdown
# Subagent 작성 규칙

@/path/to/official-docs/subagents-guide.md

## 추가 규칙
- 프로젝트 특화 규칙...
```

Recursive import 최대 깊이: 5 hops.

---

## 7. Symlink 활용

여러 프로젝트에서 공통 규칙 공유:

```bash
# 공유 rules 디렉토리 심링크
ln -s ~/shared-claude-rules .claude/rules/shared

# 개별 규칙 파일 심링크
ln -s ~/company-standards/security.md .claude/rules/security.md
```

순환 심링크는 자동 감지되어 안전하게 처리.

**(v2.1.89)** `Edit(//path/**)` 및 `Read(//path/**)` allow 규칙이 이제 심링크의 **해결된 대상 경로**(resolved symlink target)를 확인. 이전에는 요청 경로만 확인했으나, 이제 실제 파일 위치 기준으로 권한 매칭.

### Bash Permission 강화 (v2.1.97~2.1.101)

- **(v2.1.98)** 백슬래시 이스케이프된 플래그(`\-flag`)로 Bash 도구 권한 우회 방지
- **(v2.1.98)** 복합 Bash 명령어(`cmd1 && cmd2`)가 강제 권한 프롬프트를 우회하던 버그 수정
- **(v2.1.98)** 읽기 전용 명령어에 env-var 접두사가 있으면 안전한 것으로 알려진 경우에만 프롬프트 생략
- **(v2.1.98)** `/dev/tcp/...` 또는 `/dev/udp/...`로의 리다이렉트 시 프롬프트 표시
- **(v2.1.101)** `permissions.deny` 규칙이 PreToolUse 훅의 `permissionDecision: "ask"` 결정을 올바르게 오버라이드
- **(v2.1.120)** `Bash(mkdir *)`, `Bash(touch *)` 등 in-project 경로 allow rule이 정상 honor되도록 수정
- **(v2.1.139)** `autoAllowBashIfSandboxed`가 `$VAR`·`$(cmd)` 등 **shell expansion 포함 명령**도 auto-approve

### PowerShell Tool (v2.1.126~143, Windows)

PowerShell 7가 Windows에서 점차 기본 셸 도구로 전환:

- **(v2.1.119)** PowerShell 명령이 permission mode에서 auto-approve 대상 (Bash와 동일)
- **(v2.1.126)** Windows: PowerShell 7이 MS Store/MSI without PATH/.NET global tool 설치 모두 자동 탐지. PowerShell 활성 시 PowerShell이 primary shell이 되고 Bash는 fallback
- **(v2.1.143)** PowerShell tool이 `-ExecutionPolicy Bypass`를 기본 전달. opt-out: `CLAUDE_CODE_POWERSHELL_RESPECT_EXECUTION_POLICY=1`
- **(v2.1.143)** Bedrock/Vertex/Foundry Windows 사용자에게 PowerShell tool 기본 활성화. opt-out: `CLAUDE_CODE_USE_POWERSHELL_TOOL=0`

### Sandbox 설정 (v2.1.133, Linux/WSL)

```jsonc
// managed-settings.json
{
  "sandbox": {
    "bwrapPath": "/opt/bin/bwrap",     // bubblewrap 바이너리 위치
    "socatPath": "/opt/bin/socat"      // socat 바이너리 위치
  }
}
```

비표준 경로에 bubblewrap/socat이 설치된 호스트에서 sandbox가 fallback 없이 정상 시작하도록 명시 가능.

### 관리 설정 동작 (v2.1.133, Admin)

```jsonc
// managed-settings.json
{
  "parentSettingsBehavior": "merge"   // 기본 'first-wins'
}
```

`merge`로 설정하면 SDK `managedSettings` (parent tier)가 정책 merge에 참여 — 호스트가 일부 정책만 덮어쓰는 hybrid 운영 시 유용.

### Auto Mode `hard_deny` (v2.1.136)

```jsonc
{
  "autoMode": {
    "hard_deny": [
      "Bash(rm -rf /)",
      "Write(/etc/**)"
    ]
  }
}
```

기존 `soft_deny`는 사용자 의도·allow 예외에 따라 통과 가능. `hard_deny`는 **사용자 의도와 무관하게 무조건 차단**. classifier가 LLM 판단을 거치지 않고 즉시 거부.

### `--dangerously-skip-permissions` 보호 경로 변화

bypass 모드에서도 catastrophic removal command는 여전히 prompt하지만, 디렉토리 쓰기 보호는 점진적으로 완화됨:

- **(v2.1.121)** `.claude/skills/`, `.claude/agents/`, `.claude/commands/` 쓰기 prompt 생략
- **(v2.1.126/128)** `.claude/`, `.git/`, `.vscode/`, shell config 파일 등 이전에 보호되던 모든 경로로 확대

신뢰하는 자동화 워크플로우에서 거의 모든 쓰기가 무인 진행 가능. 안전한 환경 외에서는 사용 금지.

### Allow Rule 매칭 수정

- **(v2.1.133)** `Edit`/`Write` allow rule이 드라이브 루트(`C:\`)나 POSIX `/`로 스코프되면 잘못 매칭되어 항상 prompt하던 버그 수정
- **(v2.1.136)** plan 모드에서 매칭되는 `Edit(...)` allow rule이 있을 때 파일 쓰기를 차단하지 않던 버그 수정 — plan 모드가 의도대로 차단 유지

### Managed Sandbox 정책 수정 (v2.1.126)

**Security:** `allowManagedDomainsOnly`/`allowManagedReadPathsOnly`가 상위 priority managed-settings 소스에 `sandbox` 블록이 없을 때 무시되던 보안 버그 수정. 다중 tier 정책에서 `sandbox` 누락 tier가 lower tier의 제약을 무력화하지 않도록 정정.

---

## 8. Best Practice

### DO

- 주제별 분리: 각 파일은 하나의 주제만 (testing.md, api-design.md)
- 명확한 파일명: 파일명만으로 내용 파악 가능
- 조건부 규칙은 `globs:` CSV 형식 사용
- 정기적 검토: 프로젝트 변화에 맞춰 갱신

### DON'T

- 모든 규칙을 조건부로 만들기
- 너무 세분화된 파일 구조
- 중복되는 규칙
- user-level rules에서 조건부 규칙 의존 (현재 미작동)

---

## 9. 일반적인 규칙 구성

| 파일 | 용도 |
|------|------|
| `code-style.md` | 코드 스타일, 포맷팅 |
| `testing.md` | 테스트 작성 컨벤션 |
| `security.md` | 보안 요구사항 |
| `git.md` | Git 워크플로우 |
| `api-design.md` | API 설계 원칙 |

---

## Sources

- [Manage Claude's memory](https://code.claude.com/docs/en/memory)
- [Issue #17204 - globs vs paths](https://github.com/anthropics/claude-code/issues/17204)
- [Issue #16299 - paths scope bug](https://github.com/anthropics/claude-code/issues/16299)
- [Issue #21858 - user-level paths](https://github.com/anthropics/claude-code/issues/21858)

## Related

- [[claude-md-guide]] - CLAUDE.md 가이드
- [[skills-guide]] - Skills 시스템 가이드

---

## Update History

- **2026-05-16**: v2.1.120~2.1.143 변경사항 반영
  - `Bash(mkdir *)`/`Bash(touch *)` 등 in-project 경로 allow rule honor 수정 (v2.1.120)
  - `--dangerously-skip-permissions`가 `.claude/skills/`, `.claude/agents/`, `.claude/commands/` 쓰기 prompt 생략 (v2.1.121)
  - **Security:** `allowManagedDomainsOnly`/`allowManagedReadPathsOnly`가 상위 tier managed-settings에 `sandbox` 누락 시 무시되던 버그 수정 (v2.1.126)
  - PowerShell tool: MS Store/MSI without PATH/.NET global tool 자동 탐지, PowerShell이 primary shell (v2.1.126, Windows)
  - `--dangerously-skip-permissions` 보호 경로 확대: `.claude/`, `.git/`, `.vscode/`, shell config (v2.1.126/128)
  - `sandbox.bwrapPath`/`sandbox.socatPath` 관리 설정 (v2.1.133)
  - `parentSettingsBehavior` admin 키 (`first-wins`/`merge`) (v2.1.133)
  - `Edit/Write` allow rule이 드라이브 루트(`C:\`)/`/`로 스코프 시 항상 prompt하던 버그 수정 (v2.1.133)
  - `autoMode.hard_deny` — 사용자 의도와 무관한 무조건 차단 규칙 (v2.1.136)
  - plan 모드가 매칭 `Edit(...)` allow rule 있을 때 파일 쓰기 차단하지 않던 버그 수정 (v2.1.136)
  - `autoAllowBashIfSandboxed`가 shell expansion 포함 명령도 auto-approve (v2.1.139)
  - `Skill(name *)` 와일드카드 prefix-match 정상화 (v2.1.139 fix)
  - PowerShell tool이 `-ExecutionPolicy Bypass` 기본 전달 (v2.1.143)
  - Bedrock/Vertex/Foundry Windows 사용자에게 PowerShell tool 기본 활성화 (v2.1.143)

- **2026-04-19**: v2.1.110~2.1.114 변경사항 반영
  - **Bash 권한 관대화 (v2.1.111)**: Read-only Bash 명령에 glob 패턴 사용(`ls *.ts`)과 `cd <project-dir> && ...` 형태의 명령이 더 이상 권한 프롬프트를 띄우지 않음
  - **`cd <current-directory> && git ...` 권한 프롬프트 제거 (v2.1.114)**: `cd`가 no-op일 경우 git 명령 실행 시 프롬프트 없음
  - **macOS 위험 경로 인식 강화 (v2.1.114)**: `/private/{etc,var,tmp,home}` 경로가 `Bash(rm:*)` allow rule 하에서 dangerous removal target으로 처리
  - **deny rule wrapper 매칭 (v2.1.114)**: Bash deny rule이 `env`/`sudo`/`watch`/`ionice`/`setsid` 등 exec wrapper로 감싼 명령도 매칭
  - **`Bash(find:*)` allow rule 강화 (v2.1.114)**: `find -exec`/`find -delete`는 더 이상 자동 승인 안 됨 — 명시적 권한 필요
  - **`sandbox.network.deniedDomains` 설정 추가 (v2.1.113)**: 더 넓은 `allowedDomains` wildcard로 허용된 상태에서도 특정 도메인을 명시적으로 차단
  - **`Bash(dangerouslyDisableSandbox)` 보안 수정 (v2.1.114)**: 권한 프롬프트 없이 sandbox 외부에서 명령을 실행하던 보안 버그 수정
  - **Bash UI-spoofing 방지 (v2.1.114)**: 첫 줄이 주석인 multi-line 명령이 트랜스크립트에 전체 명령을 표시 (이전: 첫 줄만 표시되어 실제 명령 가려질 수 있었음)
- **2026-04-13**: v2.1.93~2.1.101 변경사항 반영
  - Bash 권한 강화: 백슬래시 이스케이프, 복합 명령어 우회, /dev/tcp 리다이렉트 등 (v2.1.97~2.1.98)
  - `permissions.deny`가 PreToolUse 훅의 `"ask"` 결정을 오버라이드 (v2.1.101)
  - Cedar 정책 파일 구문 강조 지원 (v2.1.97, `.cedar`, `.cedarpolicy`)
  - `sandbox.failIfUnavailable` 설정 추가 (v2.1.83 문서화, v2.1.98 PID 네임스페이스 격리 추가)
- **2026-04-04**: v2.1.90~2.1.92 변경사항 반영
  - `forceRemoteSettingsRefresh` 정책 추가 (v2.1.92) - managed settings fail-closed 동작
  - `.husky` 디렉토리 보호 (acceptEdits 모드) 추가 (v2.1.90)
  - auto mode가 사용자 명시 경계("don't push" 등)를 무시하던 버그 수정 (v2.1.90)
  - PowerShell 도구 권한 검사 강화: trailing `&` 우회, `-ErrorAction Break` 디버거 행 등 수정 (v2.1.90)
  - `Get-DnsClientCache`, `ipconfig /displaydns` auto-allow 제거 (v2.1.90, DNS 캐시 프라이버시)
- **2026-04-01**: v2.1.89 변경사항 반영
  - Symlink allow 규칙이 resolved target 경로 기준으로 매칭 (v2.1.89)
- **2026-03-31**: v2.1.79~2.1.88 변경사항 반영
  - `paths:` frontmatter YAML 리스트 정식 지원 (v2.1.84)
  - hooks `if` 조건 필드 compound commands 수정 (v2.1.88)
- **2026-03-18**: v2.1.51~2.1.78 변경사항 반영
  - print 모드 조건부 rules 로딩 수정 (v2.1.69)
  - `InstructionsLoaded` 훅 이벤트 참조 추가 (v2.1.69)
- **2026-02-22**: 전면 갱신 (source of truth 목적)
  - paths vs globs 버그 경고 추가 (Issue #17204)
  - user-level 조건부 규칙 미작동 명시 (Issue #21858)
  - Git worktree 제한사항 추가 (Issue #23569)
  - --add-dir rules 로딩 (v2.1.20)
  - Auto Memory 교차 참조 제거 (claude-md-guide에서 다룸)
- **2026-01-19**: 초기 작성
