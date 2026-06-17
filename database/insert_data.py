import pandas as pd
import os
from db_connection import get_connection


def insert_all_project_data():
    conn = get_connection()
    if not conn:
        print("❌ DB 연결 실패")
        return

    cursor = conn.cursor()

    try:
        # ==============================
        # CSV 경로
        # ==============================
        base_path = '../data/processed/'

        brand_path = os.path.join(base_path, 'danawa_brand_clean.csv')
        model_path = os.path.join(base_path, 'danawa_model_clean.csv')
        age_path = os.path.join(base_path, 'nice_age_clean.csv')
        gender_path = os.path.join(base_path, 'nice_gender_clean.csv')

        # ==============================
        # 공통 빈값 및 공백 처리 함수
        # ==============================
        def clean_val(value):
            if pd.isna(value):
                return None
            if isinstance(value, str):
                value = value.strip()
                if value in ['', 'NULL', '-', 'NaN']:
                    return None
            return value

        # ==============================
        # 1. Brand
        # ==============================
        print("▶ Brand 적재")
        brand_df = pd.read_csv(brand_path)
        brand_df = brand_df[brand_df['브랜드'] != '브랜드']

        brand_map = {}
        for idx, brand in enumerate(brand_df['브랜드'].unique(), start=1):
            brand = clean_val(brand)
            if not brand or brand in ['브랜드', '이름', '브랜드명']:
                continue

        # --------------------------------------------------------
        # 2. Car_Model 적재
        # --------------------------------------------------------
        print("▶ 2. Car_Model 테이블 적재 중...")
        model_df = pd.read_csv(model_path)
        model_df = model_df[~((model_df['모델'] == '모델') | (model_df['브랜드'] == '브랜드'))]

        model_map = {}
        model_id = 0
        unique_models = model_df[['모델', '브랜드']].drop_duplicates()

        for row in unique_models.itertuples(index=False):
            model_name = clean_val(row[0])
            brand_name = clean_val(row[1])

            if model_name in ['모델', '모델명'] or brand_name in ['브랜드', '브랜드명']:
                continue

            brand_id = brand_map.get(brand_name)
            if not brand_id:
                continue

            model_id += 1
            sql = "INSERT IGNORE INTO Car_Model (model_id, brand_id, model_name) VALUES (%s,%s,%s)"
            cursor.execute(sql, (model_id, brand_id, model_name))
            model_map[model_name] = model_id
        print(f"   - Car_Model 완료 ({model_id}개)")

        # ==============================
        # 3. Age_Registration (진짜 데이터 컬럼 매칭 완료)
        # ==============================
        print("▶ Age_Registration 적재")
        age_df = pd.read_csv(age_path)
        age_id = 0

        for _, row in age_df.iterrows():
            # 💡 파일 헤더 순서 고정: 구분(0), 타입(1), 순위(2), 브랜드명(3), 모델명(4), 등록량(5)
            age_group = clean_val(row.iloc[0])   # 0번째 열: 파일의 '구분' ➡️ DB의 'age_group' (예: 20대 이하)
            gubun = clean_val(row.iloc[1])       # 1번째 열: 파일의 '타입' ➡️ DB의 'gubun'     (예: 모델, 브랜드) 👈 정답!
            ranking = clean_val(row.iloc[2])     # 2번째 열: 파일의 '순위' ➡️ DB의 'ranking'
            brand_name = clean_val(row.iloc[3])  # 3번째 열: 파일의 '브랜드명'
            model_name = clean_val(row.iloc[4])  # 4번째 열: 파일의 '모델명'
            count = clean_val(row.iloc[5])       # 5번째 열: 파일의 '등록량' ➡️ DB의 'age_reg_count'

            # 💡 [추가] 모델명이 없거나 "-" 인 브랜드 전체 통계 행은 아예 디비에 넣지 않고 스킵합니다!
            if not model_name or model_name == '-':
                continue

        if len(age_df) > 0 and (age_df.iloc[0]['카테고리'] == '연령대' or age_df.iloc[0]['카테고리'] == '카테고리'):
            age_df = age_df.drop(age_df.index[0]).reset_index(drop=True)

            # 💡 [최종 업그레이드] 한글/영어(Model/모델) 및 띄어쓰기 불일치 완벽 해결
            model_id = None
            if model_name:
                # 1. NICE 파일의 모델명(예: '모델 Y')에서 띄어쓰기를 지웁니다 ➡️ '모델Y'
                clean_nice_model = model_name.replace(" ", "")

                for danawa_model, d_id in model_map.items():
                    # 2. 다나와 모델명(예: 'Model Y')의 영어 'Model'을 '모델'로 바꾸고 띄어쓰기를 지웁니다 ➡️ '모델Y'
                    clean_danawa_model = danawa_model.upper().replace("MODEL", "모델").replace(" ", "")

                    # 3. 양쪽이 서로를 포함하고 있는지 유연하게 검사합니다.
                    if clean_danawa_model in clean_nice_model or clean_nice_model in clean_danawa_model:
                        model_id = d_id
                        break

            age_id += 1
            sql = """
                INSERT IGNORE INTO Age_Registration
                (age_reg_id, brand_id, model_id, age_group, gubun, ranking, age_reg_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (age_id, brand_id, model_id, age_group, gubun, ranking, count))
        print(f"   - Age 완료 ({age_id}개)")

        # ==============================
        # 4. Gender_Registration (진짜 데이터 컬럼 매칭 완료)
        # ==============================
        print("▶ Gender_Registration 적재")
        gender_df = pd.read_csv(gender_path)
        gender_id = 0

        for _, row in gender_df.iterrows():
            # 💡 동일하게 헤더 순서 고정: 구분(0), 타입(1), 순위(2), 브랜드명(3), 모델명(4), 등록량(5)
            gender = clean_val(row.iloc[0])      # 0번째 열: 파일의 '구분' ➡️ DB의 'gender'    (예: 남성, 여성)
            gubun = clean_val(row.iloc[1])       # 1번째 열: 파일의 '타입' ➡️ DB의 'gubun'     (예: 모델, 브랜드) 👈 정답!
            ranking = clean_val(row.iloc[2])     # 2번째 열: 파일의 '순위' ➡️ DB의 'ranking'
            brand_name = clean_val(row.iloc[3])  # 3번째 열: 파일의 '브랜드명'
            model_name = clean_val(row.iloc[4])  # 4번째 열: 파일의 '모델명'
            count = clean_val(row.iloc[5])       # 5번째 열: 파일의 '등록량' ➡️ DB의 'gender_reg_count'

            # 💡 [추가] 모델명이 없거나 "-" 인 브랜드 전체 통계 행은 아예 디비에 넣지 않고 스킵합니다!
            if not model_name or model_name == '-':
                continue

            if gubun in ['구분', '타입', '종류'] or ranking in ['순위', '랭킹'] or not ranking:
                continue

            brand_id = brand_map.get(brand_name)
            # 💡 성별 적재 영역도 동일하게 최종 버전으로 업데이트합니다.
            model_id = None
            if model_name:
                clean_nice_model = model_name.replace(" ", "")

                for danawa_model, d_id in model_map.items():
                    clean_danawa_model = danawa_model.upper().replace("MODEL", "모델").replace(" ", "")

                    if clean_danawa_model in clean_nice_model or clean_nice_model in clean_danawa_model:
                        model_id = d_id
                        break

            gender_id += 1
            sql = """
                INSERT IGNORE INTO Gender_Registration
                (gender_reg_id, brand_id, model_id, gender, gubun, ranking, gender_reg_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (gender_id, brand_id, model_id, gender, gubun, ranking, count))
        print(f"   - Gender 완료 ({gender_id}개)")

        # ==============================
        # 5. Monthly_Registration
        # ==============================
        print("▶ Monthly_Registration 적재")
        monthly_id = 0
        for _, row in model_df.iterrows():
            year = clean_val(row['년'])
            month = clean_val(row['월'])
            model_name = clean_val(row['모델'])
            sales = clean_val(row['판매량'])

            if not model_name or not year:
                continue

            model_id = model_map.get(model_name)
            if not model_id:
                continue

            monthly_id += 1
            sql = """
                INSERT IGNORE INTO Monthly_Registration
                (reg_id, model_id, year, month, monthly_reg_count)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (monthly_id, model_id, year, month, sales))
        print(f"   - Monthly 완료 ({monthly_id}개)")

        conn.commit()
        print("🎉 모든 데이터 적재 완료!")

    except Exception as e:
        conn.rollback()
        print(f"❌ 오류 발생 : {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    insert_all_project_data()