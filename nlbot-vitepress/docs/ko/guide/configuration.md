---
title: 구성
description: 자세한 시스템 구성 가이드
layout: doc
sidebar: true
aside: true
outline: [2, 3]
editLink: true
lastUpdated: true
head:
  - - meta
    - name: keywords
      content: config, env, settings, parameters
---

# 구성 가이드

TelegramPress의 구성은 주로 두 부분으로 구성됩니다: 환경 변수(`.env`)와 봇 애플리케이션 구성(`al.py` / `config.txt`).

## 환경 변수 (.env)

`.env` 파일은 데이터베이스 연결 및 포트 매핑과 같은 Docker 컨테이너의 기본 설정을 제어합니다.

```bash
# 데이터베이스 구성
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=tgnl
MYSQL_USER=tgnl_user
MYSQL_PASSWORD=your_db_password

# 웹 서비스 포트
PORT=35474

# 기타 시스템 구성...
```

::: warning 보안 경고
무차별 대입 공격을 방지하려면 기본 데이터베이스 비밀번호를 변경하십시오.
:::

## 봇 구성

봇의 핵심 로직 구성은 일반적으로 `nl-2333/al.py`의 상단 또는 동일한 디렉토리의 구성 파일에 있습니다.

### 주요 매개변수

| 매개변수 | 설명 | 예 |
| :--- | :--- | :--- |
| `api_key` | 에너지 풀 API 키 | `your_api_key` |
| `privateKey` | 지급 지갑 개인 키 | `xxxxxxxx` (비밀 유지) |
| `control_address` | 수신 지갑 주소 | `TRX_Address...` |
| `username` | API 사용자 이름 | `HFTGID` |
| `CUSTOMER_SERVICE_ID` | 고객 서비스 TG 링크/ID | `https://t.me/service` |

### 가격 구성

다양한 기간의 에너지 임대 단가를 설정할 수 있습니다:

- `hour_price`: 1시간 단가
- `day_price`: 1일 단가
- `three_day_price`: 3일 단가
- `yucun_price`: 선입금 단가

## 관리자 패널 구성

웹 관리자 패널에 로그인한 후 동적 구성을 수행할 수도 있습니다:

1. **봇 관리**: 토큰, 관리자 ID 설정.
2. **에너지 풀 구성**: 연결된 에너지 풀 노드를 추가하고 관리합니다.
3. **제품 관리**: 에너지 임대 패키지를 나열하거나 제거합니다.

::: tip 참고
`.env` 또는 코드 수준 구성을 수정한 후에는 변경 사항을 적용하려면 일반적으로 컨테이너를 다시 시작해야 합니다:
`docker compose restart`
:::