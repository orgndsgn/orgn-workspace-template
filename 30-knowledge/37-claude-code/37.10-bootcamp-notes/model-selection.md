# Model Selection: Opus vs Sonnet

> Claude Code에서 어떤 모델을 쓸지의 의사결정 트리.
> 가격·모델 라인업은 자주 바뀌므로 이 페이지는 위키 승격 보류. 매뉴얼에 머무름.

## 빠른 결론

```
요금제가 $20짜리?
  ├─ YES → Sonnet 권장 (Opus 사용량 빠르게 소진)
  └─ NO  → Opus 기본, 빠른 출력 필요 시 /fast (Opus 4.7 Fast Mode)
```

## 명령어

```
/model
```
→ 사용 가능한 모델 목록 (Sonnet, Opus 등) 표시 후 선택.

## 모델별 특성

### Opus
- **품질**: 깊은 추론, 복잡한 작업
- **사용처**: Decompose, 큰 매니페스트 작성, 복합 분석, 디자인 시스템 설계
- **단점**: 토큰 소진 빠름
- **Fast Mode (Opus 4.7)**: `/fast` 토글로 출력 속도 향상. **모델 다운그레이드 아님**.

### Sonnet
- **품질**: 일반 작업에 충분, 가끔 오류 반복할 수 있음
- **사용처**: 반복 작업, 간단한 정리, 글 다듬기
- **장점**: 토큰 효율
- **단점**: "어느 순간 오류를 반복하기도 함" (옵시디언 실습.md 줄 388)

## 의사결정 가이드

| 상황 | 권장 모델 |
|---|---|
| 새 미션 분해(Decompose) | Opus |
| 매니페스트 실행(Execute) — 단순 조사 | Sonnet (워커별 분리) |
| 디자인 시스템·PRD 작성 | Opus |
| 회의록 정리, 간단 요약 | Sonnet |
| 코딩 (Vibe Coding) | Opus 또는 Opus Fast |
| 같은 작업 다수 병렬 | Sonnet 워커 + Opus 메인 |

## 요금제별 운영 팁

### $20 (Pro)
- Sonnet 위주
- Auto Mode 없음 (옵시디언 실습.md 줄 37)
- Opus는 결정적 순간에만

### $100+ (Team/Max 등)
- Opus 기본
- Fast Mode로 속도 보완
- 병렬 워커 적극 사용

### 사용량 확인
```
/usage
```
- 남은 사용량 표시
- 5시간 마다 리셋 (시간대 인지하면 더 많은 양 사용 가능, 예: 새벽 7시 첫 메시지)

## 흔한 함정

- **항상 Opus만 쓰기**: 한도 빨리 소진. 워커는 Sonnet으로 분리.
- **Fast Mode = 저품질로 오해**: 다운그레이드 아님, 동일 모델의 빠른 출력.
- **모델만 바꾸고 컨텍스트 안 정리**: 모델보다 [`context-management.md`](context-management.md)가 우선.

## 소스 인용

- 옵시디언 `실습.md`: Model 섹션 (줄 385-389)
- 옵시디언 `실습.md`: 오토모드와 요금제 (줄 36-37)
- 옵시디언 `260517 AX Bootcamp.md`: /usage 섹션 (줄 131-134), Fast mode (줄 83-84)

## Related

- [[context-management]] — 모델보다 컨텍스트 관리가 우선
- [[workflow-decompose-execute]] — Decompose는 Opus, 워커는 Sonnet 분리 패턴
