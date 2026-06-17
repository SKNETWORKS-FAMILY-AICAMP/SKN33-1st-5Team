import os
import pandas as pd
from crawlers import get_danawa_brand_sales, get_danawa_model_top10, get_nice_demographics
from preprocessor import clean_danawa_brand, clean_danawa_models, clean_nice_demographics


def format_date_for_db(df):
    # 다나와 데이터의 '연월'을 '년', '월' int형으로 분리합니다.
    if '연월' in df.columns:
        df['년'] = df['연월'].apply(lambda x: int(str(x).split('-')[0]))
        df['월'] = df['연월'].apply(lambda x: int(str(x).split('-')[1]))
        df = df.drop(columns=['연월'])
        cols = ['년', '월'] + [col for col in df.columns if col not in ['년', '월']]
        df = df[cols]
    return df


def main():
    # 💡 [핵심 수정] 데이터를 저장할 경로를 raw와 processed로 나누고, 없으면 생성합니다.
    raw_dir = "../data/raw"
    processed_dir = "../data/processed"
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    print("===================================")
    print(" 🚗 1. 다나와 브랜드별 총판매량 수집")
    print("===================================")
    df_brand_raw = get_danawa_brand_sales(2024, 2026)

    if not df_brand_raw.empty:
        # [1] Raw 데이터 저장 -> raw 폴더로
        df_brand_raw.to_csv(os.path.join(raw_dir, "danawa_brand_raw.csv"), index=False, encoding="utf-8-sig")

        # [2] 전처리 및 DB용 날짜 분리
        df_brand_clean = clean_danawa_brand(df_brand_raw)
        df_brand_clean = format_date_for_db(df_brand_clean)

        # [3] Clean 데이터 저장 -> processed 폴더로
        df_brand_clean.to_csv(os.path.join(processed_dir, "danawa_brand_clean.csv"), index=False, encoding="utf-8-sig")
        print("  ✅ 다나와 브랜드 데이터 (Raw/Processed 분리) 저장 완료!\n")

    print("===================================")
    print(" 🏎️ 2. 다나와 모델 TOP 10 수집")
    print("===================================")
    df_model_raw = get_danawa_model_top10(2024, 2026)

    if not df_model_raw.empty:
        # [1] Raw 데이터 저장 -> raw 폴더로
        df_model_raw.to_csv(os.path.join(raw_dir, "danawa_model_raw.csv"), index=False, encoding="utf-8-sig")

        # [2] 전처리 및 DB용 날짜 분리
        df_model_clean = clean_danawa_models(df_model_raw)
        df_model_clean = format_date_for_db(df_model_clean)

        # [3] Clean 데이터 저장 -> processed 폴더로
        df_model_clean.to_csv(os.path.join(processed_dir, "danawa_model_clean.csv"), index=False, encoding="utf-8-sig")
        print("  ✅ 다나와 모델 데이터 (Raw/Processed 분리) 저장 완료!\n")

    print("===================================")
    print(" 👥 3. 나이스블루마크 연령/성별 수집")
    print("===================================")
    df_nice_raw = get_nice_demographics()

    if not df_nice_raw.empty:
        # [1] Raw 데이터 저장 -> raw 폴더로
        df_nice_raw.to_csv(os.path.join(raw_dir, "nice_raw.csv"), index=False, encoding="utf-8-sig")

        # [2] 전처리 수행
        df_nice_clean = clean_nice_demographics(df_nice_raw)

        # [3] DB용 연령대 / 성별 분리 및 Clean 데이터 저장 -> processed 폴더로
        if '분류' in df_nice_clean.columns:
            df_age = df_nice_clean[df_nice_clean['분류'] == '연령대'].drop(columns=['분류'])
            df_age.to_csv(os.path.join(processed_dir, "nice_age_clean.csv"), index=False, encoding="utf-8-sig")

            df_gender = df_nice_clean[df_nice_clean['분류'] == '성별'].drop(columns=['분류'])
            df_gender.to_csv(os.path.join(processed_dir, "nice_gender_clean.csv"), index=False, encoding="utf-8-sig")

        print("  ✅ 나이스블루마크 데이터 (Raw 통합본 / Processed 분리본) 저장 완료!\n")

    print("🎉 모든 파이프라인 통합 실행이 완료되었습니다!")


if __name__ == "__main__":
    main()