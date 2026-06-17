## -- 테이블 생성 SQL
-- 1. 브랜드 테이블 (Brand)
CREATE TABLE Brand (
    brand_id INT NOT NULL,
    brand_name VARCHAR(10) NOT NULL,
    PRIMARY KEY (brand_id)
);

-- 2. 모델 테이블 (Car_Model)
CREATE TABLE Car_Model (
    model_id INT NOT NULL,
    brand_id INT NOT NULL,
    model_name VARCHAR(10) NOT NULL,
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
    age_reg_id INT NOT NULL,
    brand_id INT NULL,
    model_id INT NULL,
    age_group VARCHAR(10) NOT NULL,
    ranking INT NOT NULL,
    age_reg_count INT NOT NULL,
    PRIMARY KEY (age_reg_id),
    FOREIGN KEY (brand_id) REFERENCES Brand(brand_id),
    FOREIGN KEY (model_id) REFERENCES Car_Model(model_id)
);

-- 5. 성별통계 테이블 (Gender_Registration)
-- 마찬가지로 brand_id나 model_id에 NULL이 들어올 수 있도록 설정합니다.
CREATE TABLE Gender_Registration (
    gender_reg_id INT NOT NULL,
    brand_id INT NULL,
    model_id INT NULL,
    gender VARCHAR(10) NOT NULL,
    ranking INT NOT NULL,
    gender_reg_count INT NOT NULL,
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