## -- 테이블 생성 SQL
-- 1. 브랜드 테이블 (Brand)
CREATE database cardb;

CREATE TABLE Brand (
    brand_id INT NOT NULL,
    brand_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (brand_id)
);

-- 2. 모델 테이블 (Car_Model)
CREATE TABLE Car_Model (
    model_id INT NOT NULL,
    brand_id INT NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (model_id),
    FOREIGN KEY (brand_id) REFERENCES Brand(brand_id)
);

-- 3. 월별등록데이터 테이블 (Monthly_Registration)
CREATE TABLE Monthly_Registration (
    reg_id INT NOT NULL,
    model_id INT NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    monthly_reg_count INT NOT NULL,
    PRIMARY KEY (reg_id),
    FOREIGN KEY (model_id) REFERENCES Car_Model(model_id)
);

-- 4. 연령대별 통계 테이블 (Age_Registration)
-- ERD 예시 데이터 상 brand_id나 model_id에 NULL이 들어올 수 있으므로 NULL 허용으로 설정합니다.
CREATE TABLE Age_Registration (
    age_reg_id INT NOT NULL AUTO_INCREMENT, -- 파이썬이 일일이 번호 계산 안 해도 되게 자동 증가 추가
    brand_id INT NULL,                      -- 브랜드 통계일 땐 모델이 NULL이 되므로 NULL 허용 유지
    model_id INT NULL,                      -- 모델 통계일 땐 브랜드가 NULL이 될 수 있으므로 NULL 허용 유지
    age_group VARCHAR(20) NOT NULL,         -- '20대 이하' 글자가 안 터지게 20자로 안전하게 확장
    gubun VARCHAR(20) NOT NULL,             -- 데이터의 '모델' / '브랜드' 글자를 저장할 칸 필수 추가!
    ranking INT NOT NULL,                   -- 순위는 필수 값이므로 엄격하게 NOT NULL 유지
    age_reg_count INT NOT NULL,             -- 등록대수도 필수 값이므로 엄격하게 NOT NULL 유지
    PRIMARY KEY (age_reg_id),
    FOREIGN KEY (brand_id) REFERENCES Brand(brand_id),
    FOREIGN KEY (model_id) REFERENCES Car_Model(model_id)
);

-- 5. 성별 통계 테이블 (Gender_Registration) - 최종 완성본
CREATE TABLE Gender_Registration (
    gender_reg_id INT NOT NULL,             -- 기존 설계대로 INT 유지 (파이썬에서 직접 번호를 매겨서 넣는 구조)
    brand_id INT NULL,                      -- 브랜드 전체 통계일 때는 모델이 없으므로 NULL 허용 유지
    model_id INT NULL,                      -- 특정 모델 통계일 때는 브랜드가 NULL이 될 수 있으므로 NULL 허용 유지
    gender VARCHAR(20) NOT NULL,            -- '남성', '여성' 데이터가 안전하게 들어가도록 확장
    gubun VARCHAR(20) NOT NULL,             -- 올려주신 데이터의 '모델' / '브랜드' 타입을 저장할 컬럼 필수 추가!
    ranking INT NOT NULL,                   -- 순위는 필수 값이므로 원래 설계대로 NOT NULL 엄격하게 유지
    gender_reg_count INT NOT NULL,          -- 등록대수도 필수 값이므로 원래 설계대로 NOT NULL 엄격하게 유지
    PRIMARY KEY (gender_reg_id),
    FOREIGN KEY (brand_id) REFERENCES Brand(brand_id),
    FOREIGN KEY (model_id) REFERENCES Car_Model(model_id)
);

SELECT a.age_group,
       b.brand_name,
       a.ranking,
       a.age_reg_count
FROM age_registration a
JOIN brand b
ON a.brand_id = b.brand_id;