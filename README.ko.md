# context-curation

[English](README.md) | 한국어

멀티 세션 AI 코딩 에이전트 작업에서 **지속 컨텍스트 레이어를 관리**하는 opencode 스킬.

`session-handoff`가 세션 경계를 넘겨준다면, 이 스킬은 *무엇이 세션 상태를 그만두고 프로젝트
상태가 되어야 하는지* 를 판단하고, 그 프로젝트 상태가 계속 작고 도달 가능하며 서로 모순되지
않게 유지합니다.

## 문제

프로젝트가 길어지면 AGENTS.md는 커지고, 문서는 낡고 중복되고, 아무도 가리키지 않는 문서가
생깁니다. 도달 불가능한 문서는 없는 문서보다 나쁩니다 — 잘못된 확신을 만들기 때문입니다.

초기 설정 시점에는 그 프로젝트가 어떤 문서를 필요로 할지 알 수 없습니다. 그건 프로젝트가
진행되면서 드러납니다. 그 사이를 메우는 게 이 스킬입니다.

## 레이어 모델

읽는 **빈도**로 분류합니다. 중요도가 아니라.

| 레이어 | 문서 | 읽는 시점 | 예산 |
|---|---|---|---|
| L0 | `AGENTS.md` | 매 세션 무조건 | 2,000 토큰 하드캡 |
| L1 | 루트 `PLAN.md`, `docs/handoff/handoff.md` | 세션 시작 시 | 각 ~1,500 |
| L2 | `decisions` · `architecture` · `domain` · `rules` · `reference` | 조건부 | 무제한, 포인터 필수 |
| L3 | `docs/handoff/session-log.md`, `docs/archive/` | 통째로 안 읽음, grep만 | append-only |

L0 상한은 지출 한도가 아니라 **형태 강제 장치**입니다. 반드시 지켜야 할 불변 규칙 일곱 줄이
단지 사실일 뿐인 문단들과 같은 지면에서 경쟁하면, 규칙이 규칙으로 읽히기를 그칩니다.

## 작동 방식

1. 첫 context init 전에 프로젝트 초기 구상과 대략적인 계획으로 최소 메모리 계약을 설계합니다.
2. init 후 문서 예산, 포인터, 도달성, 중복, freshness와 세션 로그 규모를 감사합니다.
3. 전체 로그의 태그를 검색하고 필요한 세션 본문만 읽습니다. 상태 파일이 아직 없으면 최근
   5개 세션 항목을 bootstrap 범위로 사용합니다.
4. 반복성·손실 비용·안정성·비유도성으로 영구 승격 후보를 판정합니다.
5. `AGENTS.md`의 읽기 경로와 `docs/handoff/handoff-spec.md`의 쓰기 경로를 함께 조정하는 제안서를
   작성하고 멈춥니다.
6. 사용자가 항목별로 승인한 뒤에만 적용하고, 감사기를 다시 실행해 검증합니다.

한 번 거부된 후보도 영구 제외하지 않습니다. 이후 세션에서 다시 나타나거나 증거가 바뀌면
재평가합니다.

## 설치

```bash
# 전역 설치 (권장)
cp -r context-curation ~/.config/opencode/skills/
cp context-curation/command/tune-docs.md ~/.config/opencode/commands/

# 프로젝트 로컬 설치가 필요하면:
# cp -r context-curation <project>/.opencode/skills/
```

`context-curation`은 전역으로 두되 `session-context-init`과 `session-handoff`는 프로젝트의
`.opencode/skills/`로 복사합니다. 초기 계획이 선 뒤 `session-context-init`보다 먼저 curation
pre-init mode를 실행합니다. 스킬은 고정된 두 로컬 경로에서 contract instruction block 누락을
감지해 설치를 제안하며, 첫 승인 실행이 해당 블록과 `docs/handoff/handoff-spec.md`,
`docs/handoff/.curation-state.json`을 적용합니다.

Contract block은 Markdown 지시문이며 deterministic runtime hook이 아닙니다. 이 스킬은 OpenCode
runtime hook을 설치하지 않습니다.

전체 설치 및 연동 절차는 [`context-curation/INSTALL.md`](context-curation/INSTALL.md),
실행 계약은 [`context-curation/SKILL.md`](context-curation/SKILL.md)를 참고하세요.

## 사용법

### 첫 프로젝트 설정

1. 프로젝트 초기 구상과 대략적인 계획을 세웁니다.
2. 프로젝트 로컬 `session-context-init`, `session-handoff` 사본을 `.opencode/skills/` 아래에
   설치합니다.
3. context init을 실행하기 전에 curation을 명시적으로 호출합니다.

   ```text
   /tune-docs pre-init
   ```

   또는 `context-curation을 pre-init mode로 실행해서 이 프로젝트의 메모리 계약을 설계해줘.`라고
   요청합니다.
4. `docs/_tuning-proposal.md`를 읽습니다. 누락되거나 오래된 session contract block은 blocking
   항목으로 나타납니다. 항목 ID별로 승인하거나 거부하며, 승인 전에는 지속 프로젝트 파일을
   변경하지 않습니다.
5. 승인 항목이 적용된 다음 `session-context-init`을 실행합니다. 루트 `AGENTS.md`, 루트
   `PLAN.md`와 `docs/handoff/` 아래의 계약된 파일이 생성됩니다.

### 주기적 튜닝

`/tune-docs`를 실행하거나 자연어로 요청합니다.

```text
에이전트가 같은 제약을 계속 잊어. 프로젝트 문서를 튜닝해줘.
마일스톤을 종료했어. 다음 세션 전에 context-curation을 실행해줘.
```

스킬은 감사와 증거 수확을 수행하고 `docs/_tuning-proposal.md`를 작성한 뒤 멈춥니다. 제안서를
항목별로 검토하며 승인된 항목만 적용됩니다. 대표적인 실행 시점은 마지막 튜닝 이후 5세션 이상,
마일스톤 종료, 문서 drift, 비대해진 AGENTS.md 또는 반복되는 에이전트 실수입니다.

감사 명령만 필요하면 [감사 스크립트](#감사-스크립트)를, 상세 설치·운영 설정·문제 해결은
[`context-curation/INSTALL.md`](context-curation/INSTALL.md)를 참고하세요.

## 구성

```
context-curation/
├── SKILL.md                       # 레이어 모델, 7단계 실행 절차, 가드레일
├── INSTALL.md                     # 설치 및 기존 스킬 연동
├── command/tune-docs.md           # 명시 호출용 슬래시 커맨드
├── scripts/docs_inventory.py      # 구조 감사 (표준 라이브러리만, 네트워크 없음)
├── scripts/session_contract_blocks.py  # 프로젝트 로컬 contract block 점검/승인 적용
├── references/
│   ├── promotion-test.md          # 승격 4기준과 예시
│   ├── routing-table.md           # 목적지 결정과 문서 포맷
│   ├── audit-checks.md            # 감사 항목별 대처
│   ├── agents-md-contract.md      # L0에 들어갈 것 / 안 될 것
│   └── profiles/
│       └── physics-modeling.md    # 물리 모델링·데이터 피팅 프로젝트용 프로파일
├── templates/                     # 새 문서 생성용 템플릿
└── integration/                   # 프로젝트 로컬 init/handoff 연동 블록

tests/
├── test_docs_inventory.py         # 표준 라이브러리 회귀 테스트
├── test_session_contract_blocks.py  # contract block 회귀 테스트
└── fixtures/bootstrap-project/    # 익명 forward-test 프로젝트
```

## 핵심 설계

**제안 후 정지.** Step 5에서 `docs/_tuning-proposal.md`를 쓰고 멈춥니다. 승인 전에는 아무것도
고치지 않습니다. 문서 재구성은 사후 검토가 어렵습니다.

**실행 session 스킬은 프로젝트 로컬.** 공유 스킬은 upstream 템플릿으로 두고 프로젝트마다
고정한 사본을 사용합니다. 로컬이어도 선언적 handoff spec을 유지해 init과 handoff의 계약이
갈라지지 않게 합니다.

**지속 문서 삭제 없음.** `docs/archive/`로 이동하고 무엇이 대체했는지 남깁니다.
검토용 임시 파일인 `docs/_tuning-proposal.md`만 승인된 적용이 끝난 뒤 제거합니다.

**단일 출처.** 하나의 사실은 한 곳에만 서술하고 나머지는 포인터. AGENTS.md에 내용을 복사하는
순간 drift가 시작됩니다.

**작은 변화 단위.** 한 번에 새 durable L2 지식 문서는 최대 2개만 만듭니다. 검토용 제안서,
curation 상태와 handoff control spec은 이 제한에 포함하지 않습니다.

**2-패스 실행.** Pass A(감사·수확·제안) → 검토 → Pass B(적용·검증). 분할 지점이 승인 경계와
같아서 추가 비용이 없고, 품질이 결정되는 후반 단계에 컨텍스트 여유를 남깁니다.

## 감사 스크립트

스킬 없이 현황만 보고 싶을 때:

```bash
# 저장소에서 직접
python context-curation/scripts/docs_inventory.py --root /path/to/project

# session-context-init 실행 전
# python context-curation/scripts/docs_inventory.py --root /path/to/project --pre-init

# 고정된 프로젝트 로컬 session skill contract block 점검 (기본은 읽기 전용)
# python context-curation/scripts/session_contract_blocks.py --root /path/to/project

# 전역 설치본
# python ~/.config/opencode/skills/context-curation/scripts/docs_inventory.py --root /path/to/project
```

감사기는 다음을 보고합니다.

- L0/L1 토큰 예산과 필수 시작 문서 누락
- AGENTS.md에서 도달할 수 없는 문서와 reachable 문서의 깨진 포인터
- 마지막 Git 커밋 또는 파일 mtime과 `<!-- verified: YYYY-MM-DD -->`를 함께 사용한 freshness
- 문단 중복, 세션 로그 규모와 미수확 세션
- 상태 파일이 없는 첫 실행의 최근 세션 bootstrap 범위

README는 조건부 문서인 L2로 취급하며, 파일명이 README라는 이유로 always-read 비용에 넣지
않습니다. 스크립트는 표준 라이브러리만 사용하고 네트워크에 접근하지 않습니다. Python 3.8+.

## 검증

감사기의 레이어 판정, 도달성, 검증 날짜, 첫 실행 수확 범위, Git 날짜와 작업 중 변경 처리를
익명 합성 프로젝트로 회귀 테스트합니다.

```bash
python -m unittest discover -s tests -v
```

현재 pre-init 생명주기, handoff 하위 경로, bootstrap 범위, 도달성, freshness, curation state
탐색, 복수형 프로젝트 스킬 경로, 승인된 contract block 삽입, 구형 마커 이관과 멱등성을
포함한 회귀 테스트 16개가 통과합니다.

## 라이선스

미정.
