# context-curation 설치·운영 가이드

이 문서는 **설치·운영 담당자용**입니다. Agent가 실행 중 따라야 할 감사, 수확, 승격,
제안·적용 절차의 기준 문서는 `SKILL.md`입니다.

## 1. 설치 위치

이 환경에서는 프로젝트 스킬을 항상 루트의 **복수형** `.opencode/skills/` 아래에 둡니다.
전역 설치 경로도 OpenCode 1.x의 복수형 `~/.config/opencode/skills/`를 사용합니다.

**프로젝트 전용:**
```
<프로젝트>/.opencode/skills/context-curation/
```

**모든 프로젝트에서 공용 (권장):**
```
~/.config/opencode/skills/context-curation/
```

이 스킬은 프로젝트마다 다시 만들 이유가 없으므로 전역 설치가 낫습니다.
압축을 풀어 폴더째로 복사하면 끝입니다.

```bash
unzip context-curation.zip -d ~/.config/opencode/skills/
opencode
```

설치 확인은 새 세션에서 `/skills` 또는 에이전트에게 "context-curation 스킬 있어?"로 하면 됩니다.

### 슬래시 커맨드도 같이 설치 (GLM 5.2 환경에서는 권장)

`command/tune-docs.md`를 커맨드 디렉토리에 복사하면 `/tune-docs`로 명시 호출할 수 있습니다.

```bash
cp ~/.config/opencode/skills/context-curation/command/tune-docs.md \
   ~/.config/opencode/commands/tune-docs.md
```

스킬 자동 트리거는 모델이 description을 보고 "이 스킬을 읽어야겠다"고 판단해야 작동합니다.
Claude 계열은 이게 꽤 안정적인데, 오픈웨이트 모델은 편차가 큽니다. 명시 커맨드가 있으면
자동 트리거가 안 될 때의 대비책이 되고, 자동 트리거가 잘 되면 그냥 안 쓰면 됩니다.

## 2. 기존 셋업에 연결하기

다음 프로젝트 구조를 기준으로 연동합니다.

```
<프로젝트>/
├── AGENTS.md                         ← session-context-init 이 생성
├── PLAN.md                           ← session-context-init 이 생성
├── .opencode/skills/
│   ├── session-context-init/         ← 공유 원본에서 복사한 프로젝트 고정본
│   └── session-handoff/              ← 공유 원본에서 복사한 프로젝트 고정본
└── docs/handoff/
    ├── handoff-spec.md               ← context-curation 이 승인 후 관리
    ├── handoff.md                    ← session-handoff 가 매 세션 갱신
    ├── session-log.md                ← session-handoff 가 append
    ├── decisions.md                  ← session-handoff 가 on-event append
    └── .curation-state.json          ← context-curation 이 관리
```

`context-curation`은 전역 설치를 유지하되, `session-context-init`과 `session-handoff`는 공유
원본을 프로젝트의 `.opencode/skills/`로 복사해 고정해서 사용합니다. 두 로컬 스킬의 upstream
버전이나 복사 날짜를 기록해 두세요.

`integration/` 폴더에는 두 session 스킬용 contract instruction block, AGENTS.md 조각과 설명
문서가 있습니다. 여기서 contract block은 Markdown 지시문이며 OpenCode runtime hook이 아닙니다.

1. **`session-context-init-contract-block.md`** — 로컬 init 스킬이 실행 전에
   `docs/handoff/handoff-spec.md`를 요구하고, 루트 `AGENTS.md`·`PLAN.md`와 handoff 하위 파일을
   올바른 위치에 만들게 하는 정본 contract block입니다.
2. **`session-handoff-contract-block.md`** — 로컬 handoff 스킬이 같은 spec을 읽고 쓰기 경로·
   주기·필드를 따르게 하는 정본 contract block입니다.
3. **`agents-md-snippet.md`** — 생성된 AGENTS.md의 포인터 표에 한 줄을 추가합니다.
   자동 트리거가 불안정해도 5세션 주기와 문서 이상 징후를 인식하게 합니다.
4. **`README-integration.md`** — pre-init부터 주기적 tuning까지 전체 관계를
   설명합니다. 설치 대상은 아닙니다.

### 첫 프로젝트 실행 순서

1. 프로젝트 초기 구상과 대략적인 계획을 세웁니다.
2. 두 session 스킬을 프로젝트의 `.opencode/skills/`로 복사합니다.
3. `context-curation`을 pre-init mode로 실행합니다. Contract-block 검사 결과 누락·구버전이면
   제안서의 blocking 항목으로 나타납니다.
4. 승인 후 contract block과 `docs/handoff/handoff-spec.md`, 상태 파일을 적용합니다.
5. 그다음 `session-context-init`을 실행합니다.

Init보다 먼저 실행하는 감사 명령은 `--pre-init`을 사용합니다. 이 모드에서는 아직 없는
AGENTS.md, PLAN.md와 session log를 오류로 보고하지 않습니다.

```bash
python ~/.config/opencode/skills/context-curation/scripts/docs_inventory.py --root . --pre-init
```

두 session contract block만 별도로 점검할 수도 있습니다. 기본 동작은 읽기 전용입니다.

```bash
python ~/.config/opencode/skills/context-curation/scripts/session_contract_blocks.py --root .
```

제안서의 contract block 항목을 승인한 뒤에만 적용 옵션을 사용합니다.

```bash
python ~/.config/opencode/skills/context-curation/scripts/session_contract_blocks.py --root . --apply
```

이 스크립트는 `.opencode/skills/session-context-init/SKILL.md`와
`.opencode/skills/session-handoff/SKILL.md`만 수정합니다. 전역 스킬은 수정하지 않으며, 같은
마커 블록이 이미 있으면 다시 삽입하지 않습니다. 이전 버전의 `hook` 마커는 승인 적용 시 새
contract-block 마커로 이관합니다. `skill-missing`이나 malformed/duplicate marker 상태는 자동으로
우회하지 않으므로 해당 프로젝트 사본을 먼저 바로잡습니다.

placeholder 상태 파일을 미리 복사하거나 날짜를 손으로 채우지 마세요. init 후 상태 파일이 없거나
읽을 수 없으면 감사기는 전체 로그의 태그를 추출한 뒤 최근 5개 세션 항목을 bootstrap 범위로
안내합니다.

### 공유 파일 정책

큐레이션은 **프로젝트 디렉토리 밖에 아무것도 쓰지 않습니다.**

| 변경 성격 | 대상 | 적용 주체 |
|---|---|---|
| 이 프로젝트 전용 (문서 집합, 주기, 필드) | `docs/handoff/handoff-spec.md` | 큐레이션 (승인 후) |
| 일반화 가능 (모든 프로젝트가 원할 개선) | 제안서 섹션 G에 메모만 | 공유 스킬 관리자 |

프로젝트 로컬 스킬은 해당 저장소에서 검토·버전 관리할 수 있습니다. 그래도 경로와 필드 같은
선언적 설정은 SKILL.md 두 곳에 복사하지 말고 spec 한 곳에 둡니다. 절차 자체를 바꿔야 할 때만
로컬 SKILL.md를 수정합니다.

섹션 G는 **실행 항목이 아니라 운영자 검토용 메모**입니다. 공유 스킬 관리자가 다른 프로젝트에
미칠 영향을 확인한 뒤 별도로 적용합니다.

## 3. 사용법

명시적으로 부르는 경우:

```
AGENTS.md가 너무 커진 것 같아. context-curation 스킬로 문서 레이어 정리해줘.
```

또는 그냥 상황만 말해도 트리거되도록 description을 써 두었습니다:

```
에이전트가 자꾸 같은 걸 까먹어. 문서 구조 좀 손봐줘.
M2 마일스톤 끝났으니 문서 정리하자.
```

에이전트는 감사 → 수확 → 분류 → 제안 순으로 진행하고
`docs/_tuning-proposal.md`를 쓴 뒤 **멈춥니다.** 승인 전에는 아무것도 안 고칩니다.
제안서를 읽고 항목별로 승인/거부하면 그때 적용합니다.

## 4. 감사 스크립트 단독 실행

스킬 없이 현황만 보고 싶을 때:

```bash
python ~/.config/opencode/skills/context-curation/scripts/docs_inventory.py --root .
# project-local installation:
# python .opencode/skills/context-curation/scripts/docs_inventory.py --root .
```

표준 라이브러리만 쓰고 네트워크 접근이 없어서 사내망에서 그대로 돕니다.
Python 3.8 이상이면 됩니다. 환경에서 실행 파일 이름이 `python3`이면 그 이름을 사용하세요.

주요 옵션:

| 옵션 | 기본값 | 의미 |
|---|---|---|
| `--l0-budget` | 2000 | AGENTS.md 토큰 상한 |
| `--l1-budget` | 1500 | 루트 PLAN.md / docs/handoff/handoff.md 상한 |
| `--stale-days` | 90 | 이보다 오래된 문서를 의심 대상으로 표시 |
| `--dup-threshold` | 0.45 | 문단 중복 판정 유사도 (0~1) |
| `--context-window` | 200000 | 수확 범위를 계산할 컨텍스트 크기 |
| `--bootstrap-sessions` | 5 | 상태 파일이 없을 때 본문을 읽을 최근 세션 수 |
| `--pre-init` | 꺼짐 | init 전 누락 startup/session 파일을 정상으로 처리 |
| `--json` | | 사람 대신 에이전트가 읽을 형식 |

토큰 수치는 문자 수 기반 **추정치**입니다(한글은 1.5자/토큰, ASCII는 4자/토큰 가정).
±20% 정도로 보시면 되고, 절대값보다 추세를 보는 용도입니다.
사내 모델의 실제 토크나이저와는 다르므로, 정확한 값이 필요하면
`estimate_tokens()` 함수만 사내 토크나이저로 바꿔 끼우면 됩니다.

## 5. 운영 설정

### L0 예산

기본값은 2,000 토큰입니다. 이 값은 비용 한도가 아니라 AGENTS.md를 라우팅 표로 유지하기 위한
형태 제약이므로, 컨텍스트가 크다는 이유만으로 올리지 마세요. 조정이 꼭 필요하면 다음 세 곳을
같이 변경합니다.

1. `SKILL.md`의 레이어 표
2. `references/agents-md-contract.md`의 Budget enforcement
3. 감사기 실행의 `--l0-budget` 또는 스크립트 기본값

### 사내 모델

- 외부 API나 추가 Python 패키지는 필요하지 않습니다. Python 3.8+만 준비하세요.
- 자동 스킬 트리거가 불안정하면 `/tune-docs` 명령을 사용하세요.
- 처음 두세 번은 제안서가 생성된 뒤 실제 문서가 승인 전에 바뀌지 않았는지 확인하세요.
- 짧은 컨텍스트 모델보다 감사 결과와 세션 기록을 함께 처리할 수 있는 모델을 사용하세요.

## 6. 문제 해결

| 증상 | 확인할 것 |
|---|---|
| `/tune-docs`가 없음 | `command/tune-docs.md`를 `~/.config/opencode/commands/`에 복사했는지 확인 |
| 자동 호출이 안 됨 | AGENTS.md에 `integration/agents-md-snippet.md`를 추가했는지 확인 |
| init이 예전 경로에 파일을 만듦 | contract-block 검사기로 `.opencode/skills/session-context-init/SKILL.md` 상태 확인 |
| handoff spec이 무시됨 | contract-block 검사기로 `.opencode/skills/session-handoff/SKILL.md` 상태 확인 |
| 검사 결과가 `skill-missing` | 두 프로젝트 스킬이 정확히 `.opencode/skills/` 아래에 있는지 확인 |
| 검사 결과가 malformed/duplicate markers | 불완전하거나 중복된 마커를 수동 복구한 뒤 다시 점검 |
| 감사기가 실행되지 않음 | Python 3.8+와 설치 위치에 맞는 스크립트 경로 확인 |
| 상태 파일이 없음 | 정상적인 pre-init일 수 있음; 직접 만들지 말고 첫 승인 실행에서 생성 |
| 승인 전에 문서가 변경됨 | 적용하지 말고 제안서만 남긴 뒤 `SKILL.md`의 Step 5 준수 여부 확인 |
| 섹션 G가 자동 적용됨 | 되돌린 뒤 공유 스킬 관리자가 영향 범위를 별도로 검토 |

`references/`를 읽지 않는 것 자체는 오류가 아닙니다. 정상 경로는 `SKILL.md`만으로 완결되고,
참조 문서는 경계 사례나 상세 포맷이 필요할 때만 읽습니다.
