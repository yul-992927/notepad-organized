# Network Automation Lab

> 공개용 사본입니다. 장비 관리 주소와 EIGRP 대역은 문서용 예시 주소로 바꾸었고, 실행 로그와 자격 증명은 포함하지 않았습니다. 실제 장비에 적용하려면 본인의 허가된 환경 값으로 인벤토리와 프로필을 직접 검증·교체하세요.

C&C PC의 Jupyter Notebook에서 각 라우터의 관리 IP로 직접 SSH 접속해 설정을 자동화하는 학원 실습용 프로젝트입니다. R12는 SSH 프록시가 아니라 C&C 관리망의 라우팅 게이트웨이로 사용합니다.

## 현재 구현 범위

- R1~R13 인벤토리와 기술별 그룹
- EIGRP AS 100/200 대상 선택
- EIGRP 프로세스 생성, Network 추가, Passive Interface, 상태 조회 명령 생성
- 명령 미리 보기와 Dry Run
- `APPLY` 확인 후 Netmiko로 실제 실행
- 장비별 성공/실패 결과와 JSON 로그 저장
- Jupyter Notebook 실행 예제
- 전체 흐름을 담당하는 `NetworkAutomationApp` 중심의 class 구조
- 자동 입력 모드와 수동 명령 입력 모드
- 라우터와 기술만 선택하는 장비별 자동 명령 프로필

## Class 구조

- `NetworkAutomationApp`: Notebook과 CLI가 사용하는 전체 실행 흐름
- `InventoryRepository`: 장비와 그룹 인벤토리 조회
- `EigrpFeature`: EIGRP 입력 검증과 명령 생성
- `DeviceExecutionService`: 장비별 Dry Run 및 실제 명령 실행
- `RouterConnection`: Netmiko SSH 세션 관리
- `CredentialProvider`: 환경변수 기반 인증정보 제공
- `ExecutionLogger`: 실행 결과 JSON 기록
- `TechnologyProfileRepository`: 장비별 기술 프로필 조회
- `GuidedCommandFeature`: 장비·기술 선택을 전체 명령 묶음으로 변환
- `GuidedSelectionConsole`: 라우터와 기술을 번호로 선택하는 화면

## 파일 배치 구조

```text
network-automation-lab/
├── main.py                         # 전체 class를 조립하는 애플리케이션 진입점
├── console.py                      # 세 가지 실행 방식 통합 메뉴
├── guided_console.py               # 라우터/기술 번호 선택 화면
├── services.py                     # 실행·인증·로그 class
├── inventory_loader.py             # 장비/그룹 조회 class
├── profile_repository.py           # 기술 프로필 조회 class
├── connections/
│   ├── __init__.py
│   └── router_connection.py        # Netmiko SSH 연결 class
├── features/
│   ├── __init__.py
│   ├── guided_command.py           # 선택 결과 → 전체 명령 변환
│   ├── eigrp.py                    # EIGRP 값 입력형 명령 생성
│   └── custom_command.py           # IOS 명령 직접 입력
├── inventory/
│   ├── devices.yaml                # 장비 관리 IP와 그룹
│   ├── groups.yaml                 # 기술별 장비 그룹
│   └── technology_profiles.yaml    # 장비별 자동 명령 및 미확정 값
├── notebooks/
│   └── network_automation.ipynb    # Jupyter 실행 화면
├── tests/                          # class 단위 자동 테스트
├── logs/                           # Dry Run/실행 결과 JSON
├── requirements.txt
└── README.md
```

`main.py`가 모든 class를 생성하고 연결하므로 파일을 임의의 다른 폴더로 옮기면 import가 깨질 수 있습니다. 위 구조를 그대로 유지해야 합니다.

## 설치

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`.env.example`의 변수 이름을 참고해 현재 셸에 접속 정보를 설정합니다. 비밀번호는 YAML이나 Notebook에 저장하지 않습니다.

```powershell
$env:NETWORK_USERNAME = "admin"
$env:NETWORK_PASSWORD = "<your-password>"
$env:NETWORK_SECRET = "<your-enable-secret>"
```

## 먼저 확정할 값

1. 각 장비 Loopback 또는 관리 인터페이스의 실제 호스트 IP
2. R13의 관리 IP
3. C&C PC에서 각 관리 IP까지의 라우팅 및 SSH(22/tcp) 도달성
4. Cisco IOS 버전과 EIGRP Classic Mode 사용 여부
5. 실제 인터페이스 이름

현재 `devices.yaml`의 R1~R12는 공개용 문서 주소(`192.0.2.0/24`)를 사용하며, R13은 비워 두었습니다. `technology_profiles.yaml`의 `198.18.0.0/15` 대역도 공개용 예시입니다. 실제 적용 전 모든 주소와 명령을 검증·교체하세요.

## Dry Run

```powershell
python main.py
```

대화형 메뉴는 다음 명령으로 실행합니다.

```powershell
python console.py
```

라우터와 기술만 선택하는 전용 화면은 다음과 같이 실행합니다.

```powershell
python guided_console.py
```

프로필 상태가 `ready`인 기술만 실행할 수 있습니다. `pending` 기술은 GNS3 인터페이스명, Next-hop IP, DLCI 또는 ACL 정책이 확정된 뒤 `inventory/technology_profiles.yaml`의 명령 목록을 완성해야 합니다.

### 자동 입력 모드

기술별 Feature class가 사용자 입력을 검증하고 Cisco IOS 명령을 생성합니다. 현재 EIGRP 기본 기능이 구현되어 있습니다.

### 수동 입력 모드

Notebook의 `run_manual_group()` 또는 `run_manual_devices()`로 여러 줄 명령을 직접 입력할 수 있습니다.

- `config`: 설정 모드 명령
- `exec`: privileged EXEC 명령
- `show`: 조회 명령

두 모드 모두 기본값은 Dry Run이며 실제 실행에는 `APPLY` 확인과 환경변수 인증정보가 필요합니다. `reload`, `write erase`와 같은 초기화 명령은 초기 버전에서 차단합니다.

실제 실행 전에는 C&C PC에서 대상 관리 IP로 ping/SSH가 되는지 먼저 확인하십시오.

## 안전 및 공개 범위

이 프로젝트는 본인 소유 또는 명시적으로 허가된 실습 장비에서만 사용하세요. 기본 실행은 Dry Run이지만, `APPLY`를 입력하면 실제 네트워크 설정이 바뀔 수 있습니다. 프로필이 `ready`로 표시되어도 공개용 예시가 실제 토폴로지에 맞다는 뜻은 아닙니다. 무단 사용과 오용으로 인한 책임은 해당 행위자에게 있습니다. [저장소 안전 안내](../../docs/LEGAL_AND_SAFETY.md)를 확인하세요.

원본의 실행 로그, 캐시, 노트북 출력과 실제 인벤토리 주소는 공개하지 않았습니다.
