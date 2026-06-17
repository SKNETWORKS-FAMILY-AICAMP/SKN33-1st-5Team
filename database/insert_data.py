import pandas as pd
import os
from database.db_connection import get_connection


def insert_all_project_data():
    conn = get_connection()
    if not conn:
        print("❌ DB 연결에 실패하여 작업을 중단합니다.")
        return

    cursor = conn.cursor()

    try:
        # 경로 정의
        base_path = '../data/processed/'
        brand_path = os.path.join(base_path, 'danawa_brand_clean.csv')
        model_path = os.path.join(base_path, 'danawa_model_clean.csv')
        age_path = os.path.join(base_path, 'nice_age_clean.csv')
        gender_path = os.path.join(base_path, 'nice_gender_clean.csv')

        # --------------------------------------------------------
        # 1. Brand 적재
        # --------------------------------------------------------
        print("▶ 1. Brand 테이블 적재 중...")
        brand_df = pd.read_csv(brand_path)
        unique_brands = brand_df['브랜드'].unique()

        brand_map = {}
        for idx, b_name in enumerate(unique_brands, start=1):
            sql = "INSERT IGNORE INTO Brand (brand_id, brand_name) VALUES (%s, %s)"
            cursor.execute(sql, (idx, b_name))
            brand_map[b_name] = idx

        print(f"   - Brand 완료 ({len(unique_brands)}개)")


        # --------------------------------------------------------
        # 2. Car_Model 적재
        # --------------------------------------------------------
        print("▶ 2. Car_Model 테이블 적재 중...")
        model_df = pd.read_csv(model_path)
        unique_models = model_df[['모델', '브랜드']].drop_duplicates()

        model_map = {}
        for idx, row in enumerate(unique_models.itertuples(), start=1):
            m_name = row.모델
            b_name = row.브랜드
            b_id = brand_map.get(b_name)

            if b_id:
                sql = "INSERT IGNORE INTO Car_Model (model_id, brand_id, model_name) VALUES (%s, %s, %s)"
                cursor.execute(sql, (idx, b_id, m_name))
                model_map[m_name] = idx

        print(f"   - Car_Model 완료 ({len(unique_models)}개)")

        # 빈값(NaN, NULL) 처리 함수
        def clean_val(val):
            if pd.isna(val) or val == 'NULL' or val == '':
                return None
            return val

        # --------------------------------------------------------
        # 3. 연령대별 통계 적재
        # --------------------------------------------------------
        print("▶ 3. Age_Registration 테이블 적재 중...")
        age_df = pd.read_csv(age_path)


        if len(age_df) > 0 and (age_df.iloc[0]['카테고리'] == '연령대' or age_df.iloc[0]['카테고리'] == '카테고리'):
            age_df = age_df.drop(age_df.index[0]).reset_index(drop=True)

        inserted_age_count = 0
        for index, row in age_df.iterrows():
            age_group = clean_val(row['카테고리'])
            gubun = clean_val(row['구분'])
            ranking = clean_val(row['순위'])
            name_val = clean_val(row['이름'])
            reg_count = clean_val(row['등록량'])

            if age_group in ['연령대', '카테고리'] or name_val in ['브랜드명', '모델명', '이름'] or ranking == '순위':
                continue

            b_id = brand_map.get(name_val) if gubun == '브랜드' else None
            m_id = model_map.get(name_val) if gubun == '모델' else None

            inserted_age_count += 1
            sql = """
                  INSERT IGNORE INTO Age_Registration (age_reg_id, brand_id, model_id, age_group, ranking, age_reg_count)
                  VALUES (%s, %s, %s, %s, %s, %s) \
                  """
            cursor.execute(sql, (inserted_age_count, b_id, m_id, age_group, ranking, reg_count))

        print(f"   - Age_Registration 완료 (실제 데이터 {inserted_age_count}개 적재)")

        # --------------------------------------------------------
        # 4. 성별 통계 적재
        # --------------------------------------------------------
        print("▶ 4. Gender_Registration 테이블 적재 중...")
        gender_df = pd.read_csv(gender_path)

        if len(gender_df) > 0 and (gender_df.iloc[0]['카테고리'] == '성별' or gender_df.iloc[0]['카테고리'] == '카테고리'):
            gender_df = gender_df.drop(gender_df.index[0]).reset_index(drop=True)

        inserted_gender_count = 0
        for index, row in gender_df.iterrows():
            gender = clean_val(row['카테고리'])
            gubun = clean_val(row['구분'])
            ranking = clean_val(row['순위'])
            name_val = clean_val(row['이름'])
            reg_count = clean_val(row['등록량'])

            if gender in ['성별', '카테고리'] or name_val in ['브랜드명', '모델명', '이름'] or ranking == '순위':
                continue

            b_id = brand_map.get(name_val) if gubun == '브랜드' else None
            m_id = model_map.get(name_val) if gubun == '모델' else None

            inserted_gender_count += 1
            sql = """
                  INSERT IGNORE INTO Gender_Registration (gender_reg_id, brand_id, model_id, gender, ranking, gender_reg_count)
                  VALUES (%s, %s, %s, %s, %s, %s) \
                  """
            cursor.execute(sql, (inserted_gender_count, b_id, m_id, gender, ranking, reg_count))

        print(f"   - Gender_Registration 완료 (실제 데이터 {inserted_gender_count}개 적재)")

        # --------------------------------------------------------
        # 5. 월별 판매 통계 적재 (ERD 컬럼명 반영 완료)
        # --------------------------------------------------------
        print("▶ 5. Monthly_Registration 테이블 적재 중...")

        monthly_count = 0
        for index, row in model_df.iterrows():
            year_val = clean_val(row['년'])
            month_val = clean_val(row['월'])
            m_name = clean_val(row['모델'])
            sales_val = clean_val(row['판매량'])

            m_id = model_map.get(m_name)

            if not m_id:
                continue

            monthly_count += 1
            sql = """
                  INSERT IGNORE INTO Monthly_Registration (reg_id, model_id, year, month, monthly_reg_count)
                  VALUES (%s, %s, %s, %s, %s) \
                  """
            cursor.execute(sql, (monthly_count, m_id, year_val, month_val, sales_val))

        print(f"   - Monthly_Registration 완료 (실제 데이터 {monthly_count}개 적재)")

        # 모든 작업 완료 시 최종 데이터베이스 저장
        conn.commit()
        print("🎉 [성공] 5개 테이블에 모든 데이터가 완벽하게 적재되었습니다!")

    except Exception as e:
        conn.rollback()
        print(f"❌ 작업 중 에러 발생: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    insert_all_project_data()


