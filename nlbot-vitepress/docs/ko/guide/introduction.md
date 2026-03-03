---
title: 소개
description: TelegramPress (TGNL Admin) 프로젝트에 대한 자세한 소개
layout: doc
sidebar: true
aside: true
outline: [2, 3]
editLink: true
lastUpdated: true
head:
  - - meta
    - name: keywords
      content: telegram, bot, tron, energy, leasing, admin
---

# 소개

**TelegramPress (TGNL Admin)**는 텔레그램 봇과 웹 관리자 패널을 기반으로 하는 트론(TRX) 에너지 임대 및 자동 전송 시스템입니다. 에너지 풀 관리, 자동 모니터링 및 사용자 셀프 서비스 구매를 통합하여 트론 생태계 사용자에게 편리한 에너지 획득 서비스를 제공하는 것을 목표로 합니다.

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg> 미리보기

<div class="screenshot-grid">
  <div class="screenshot-card">
    <img src="/images/preview-1.png" alt="대시보드" class="screenshot-img" />
    <div class="screenshot-caption">대시보드 - 실시간 비즈니스 모니터링</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-2.png" alt="봇 관리" class="screenshot-img" />
    <div class="screenshot-caption">봇 관리 - 시각적 구성</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-3.png" alt="사용자 정의 키보드" class="screenshot-img" />
    <div class="screenshot-caption">사용자 정의 키보드 - 유연한 상호 작용</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-4.png" alt="시스템 설정" class="screenshot-img" />
    <div class="screenshot-caption">시스템 설정 - 전역 매개변수</div>
  </div>
</div>

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg> 핵심 기능

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg> 스마트 봇
- **자동 거래**: 24/7 사용자 주문에 대한 자동 응답, 즉각적인 에너지 전송.
- **사용자 정의 응답**: 사용자 정의 키워드 응답, 환영 메시지 및 운영 가이드 지원.
- **다단계 배포**: 사용자 성장을 촉진하기 위한 내장 초대 리베이트 메커니즘.

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg> 강력한 관리자 패널
- **시각적 대시보드**: 주문량, 매출액 및 신규 사용자와 같은 주요 지표의 실시간 표시.
- **다중 풀 스케줄링**: 안정적인 공급을 보장하기 위해 여러 에너지 풀 API 추가, 스마트 로드 밸런싱 지원.
- **사용자 프로파일링**: 상세한 사용자 행동 기록, 차단, 잔액 조정 등 지원.

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg> 보안 및 안정성
- **로컬 개인 키 저장소**: 지불 개인 키는 암호화되어 로컬 서버에만 저장되어 자금 보안을 보장합니다.
- **Docker 컨테이너화**: 서비스 격리, 간단한 배포 및 강력한 확장성.
- **자동 경고**: 시스템 이상 또는 에너지 부족 시 관리자에게 자동으로 알림.

## 아키텍처 개요

이 프로젝트는 다음과 같은 주요 구성 요소로 구성됩니다:

- **봇 서비스 (Python)**: 텔레그램 메시지, 사용자 상호 작용, 주문 처리 및 온체인 상호 작용을 처리합니다.
- **웹 서비스 (Nuxt/Node.js)**: 관리자 API 및 프론트엔드 페이지를 제공합니다.
- **데이터베이스 (MySQL/Redis)**: 사용자 데이터, 주문 기록 및 캐시 대기열을 저장합니다.
- **Nginx**: HTTP 요청을 처리하는 역방향 프록시 서버 역할을 합니다.

## 사용 사례

- **에너지 임대 제공업체**: 자체 에너지 임대 플랫폼을 구축하고 TG 봇을 통해 에너지를 자동으로 판매합니다.
- **트론 개발자**: 에너지 임대 기능을 자체 애플리케이션에 통합합니다.
- **커뮤니티 관리자**: 커뮤니티 회원에게 저렴한 에너지 임대 혜택을 제공합니다.

::: tip 참고
이 프로젝트의 오픈 소스 버전은 학습 및 연구 목적으로만 사용됩니다. 상업적 사용을 위해 관련 오픈 소스 라이선스를 준수하십시오.
:::