# 🚗 자동차 등록 통계 분석 대시보드

## 📌 프로젝트 소개

NICE 블루마크와 다나와 자동차 판매 데이터를 활용하여 자동차 등록 현황 및 판매 추이를 분석하고 시각화하는 프로젝트입니다.

사용자는 연도별, 월별, 브랜드별, 차종별, 성별 데이터를 조회할 수 있으며 FAQ를 통해 주요 통계 정보를 쉽게 확인할 수 있습니다.

---

## 🎯 프로젝트 목표

* 자동차 등록 통계 데이터 수집 및 분석
* 브랜드별 및 차종별 시장 현황 파악
* 성별 선호 차량 분석
* 데이터 시각화를 통한 인사이트 제공
* Streamlit 기반 대시보드 구축

---

## 🛠 사용 기술

### Language

* Python

### Database

* MySQL

### Data Processing

* Pandas
* NumPy

### Crawling

* Requests
* BeautifulSoup
* Selenium

### Visualization

* Plotly
* Matplotlib

### Web Application

* Streamlit

### Collaboration

* Git
* GitHub

---

## 📂 데이터 출처

### NICE 블루마크

* 자동차 등록 통계
* 성별 등록 현황
* 차종별 등록 현황
* 연도별 등록 현황

### 다나와 자동차

* 브랜드별 판매 실적
* 모델별 판매 실적
* 월별 판매 실적

---

## 📊 주요 기능

### 1. 연도별 분석

* 연도별 등록 대수 조회
* 연도별 증감 추이 분석

### 2. 월별 분석

* 월별 등록 현황 조회
* 월별 판매량 비교

### 3. 브랜드별 분석

* 브랜드 점유율 분석
* TOP 브랜드 조회

### 4. 차종별 분석

* SUV
* 세단
* 경차
* 승합차

차종별 등록 현황 분석

### 5. 성별 분석

* 남성 등록 현황
* 여성 등록 현황
* 성별 선호 브랜드 비교

### 6. FAQ

* 가장 많이 등록된 브랜드는?
* 가장 인기 있는 차종은?
* 성별 선호 차종은?
* 등록 대수가 가장 많은 연도는?

---

## 🗂 프로젝트 구조

```text
car-dashboard-project

├── data
│   ├── raw
│   │   ├── nice_data.csv
│   │   └── danawa_data.csv
│   │
│   └── processed
│       └── clean_data.csv
│
├── sql
│   ├── create_table.sql
│   └── insert_data.sql
│
├── streamlit
│   ├── app.py
│   └── pages
│       ├── year.py
│       ├── month.py
│       ├── brand.py
│       ├── cartype.py
│       ├── gender.py
│       └── faq.py
│
├── crawler
│   ├── nice_crawler.py
│   └── danawa_crawler.py
│
├── preprocessing
│   └── preprocessing.py
│
├── docs
│   ├── ERD.png
│   └── PPT
│
└── README.md
```

---

## 🗄 데이터베이스 설계

### Brand

| 컬럼명        | 타입      |
| ---------- | ------- |
| brand_id   | INT     |
| brand_name | VARCHAR |

### Car_Type

| 컬럼명       | 타입      |
| --------- | ------- |
| type_id   | INT     |
| type_name | VARCHAR |

### Registration

| 컬럼명      | 타입      |
| -------- | ------- |
| reg_id   | INT     |
| year     | INT     |
| month    | INT     |
| brand_id | INT     |
| type_id  | INT     |
| gender   | VARCHAR |
| count    | INT     |

---

## 👥 역할 분담

> 데이터 수집은 팀원 전원이 공동으로 수행하였습니다.

| 팀원 | 담당 역할                      | 주요 업무                                                    | 산출물                         |
| -- | -------------------------- | -------------------------------------------------------- | --------------------------- |
| A  | 데이터 수집 / 전처리               | NICE 블루마크·다나와 데이터 수집, 데이터 검증, 전처리 지원                     | 원본 데이터, 전처리 코드              |
| B  | 데이터 수집 / DB 설계             | 데이터 수집, 테이블 구조 설계, 데이터베이스 구축 지원                          | ERD 초안, SQL                 |
| C  | 데이터 수집 / 전처리 / Streamlit   | 데이터 정제 및 병합, 연도별·월별 페이지 개발                               | clean_data.csv, 연도별·월별 페이지  |
| D  | 데이터 수집 / DB 설계 / Streamlit | ERD 작성, MySQL 구축, 브랜드별·차종별 페이지 개발                        | ERD, SQL, 브랜드별·차종별 페이지      |
| E  | 데이터 수집 / Streamlit / PM    | 메인 페이지, 성별 페이지, FAQ 페이지 개발, GitHub 관리, README 및 발표 자료 작성 | app.py, FAQ, README.md, PPT |

### 📌 파트별 담당자

| 파트            | 담당자           |
| ------------- | ------------- |
| 데이터 수집 (크롤링)  | A, B, C, D, E |
| 데이터 전처리       | A, C          |
| DB 설계 및 MySQL | B, D          |
| Streamlit 개발  | C, D, E       |
| GitHub 관리     | E             |
| README 작성     | E             |
| 발표 자료 제작      | E             |

### 🤝 협업 방식

* 모든 팀원이 데이터 수집 및 크롤링에 참여
* 전처리 담당자가 분석용 데이터셋 생성
* DB 설계 담당자가 MySQL 구축 및 데이터 적재
* Streamlit 담당자가 분석 페이지 구현
* PM 담당자가 프로젝트 통합, 문서화 및 발표 준비 수행

---

## 📅 프로젝트 일정

# Day 1

### 🌅 오전

| 작업 내용                           | 담당자 |
| ------------------------------- | --- |
| 프로젝트 주제 선정 및 역할 분담              | 전체  |
| GitHub Repository 생성 및 개발 환경 설정 | 전체  |
| NICE 블루마크 및 다나와 사이트 구조 분석       | 전체  |

### 🌇 오후

| 작업 내용                 | 담당자  |
| --------------------- | ---- |
| 데이터 수집(크롤링) 및 CSV 저장  | 전체   |
| 데이터 검증 및 전처리          | A, C |
| 데이터베이스 구조 설계 및 ERD 작성 | B, D |
| 진행 상황 공유 및 이슈 정리      | 전체   |

---

# Day 2

### 🌅 오전

| 작업 내용             | 담당자     |
| ----------------- | ------- |
| MySQL 구축 및 데이터 적재 | B, D    |
| Streamlit 화면 개발   | C, D, E |
| 그래프 및 시각화 구현      | C, D, E |

### 🌇 오후

| 작업 내용                | 담당자 |
| -------------------- | --- |
| FAQ 작성 및 분석 내용 정리    | E   |
| 기능 통합 및 테스트          | 전체  |
| 오류 수정 및 최종 점검        | 전체  |
| README 작성 및 발표 자료 제작 | E   |
| 최종 발표 준비 및 리허설       | 전체  |

---

## 📌 개발 진행 순서

```text
주제 선정 및 역할 분담
        ↓
데이터 수집
        ↓
데이터 전처리
        ↓
DB 설계 및 데이터 적재
        ↓
Streamlit 개발
        ↓
시각화 구현
        ↓
통합 테스트
        ↓
발표 준비
```

---

## 🚀 실행 방법

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. Streamlit 실행

```bash
streamlit run app.py
```

---

## 📈 기대 효과

* 자동차 시장 현황 파악
* 데이터 수집 및 전처리 경험
* MySQL 데이터베이스 설계 경험
* Streamlit 기반 대시보드 개발 경험
* 협업 및 GitHub 활용 능력 향상

```
```
