import os
import pandas as pd
from hyundai_faq import get_hyundai_faq
from kia_faq import get_kia_faq
from tesla_faq import get_tesla_faq
from faq_preprocessor import clean_hyundai, clean_kia, clean_tesla


def main():
    # ✅ faq_data/raw 와 faq_data/processed 경로 설정
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "faq_data")
    raw_dir = os.path.join(base_dir, "raw")
    processed_dir = os.path.join(base_dir, "processed")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    # ================================
    # 1. 현대 FAQ 수집 → raw 저장 → 전처리 → processed 저장
    # ================================
    print("===================================")
    print(" 🚗 1. 현대자동차 FAQ 수집")
    print("===================================")
    df_hyundai_raw = get_hyundai_faq()

    if not df_hyundai_raw.empty:
        # Raw 저장
        df_hyundai_raw.to_csv(
            os.path.join(raw_dir, "hyundai_faq_raw.csv"),
            index=False, encoding="utf-8-sig"
        )
        print(f"  ✅ Raw 저장 완료: {len(df_hyundai_raw)}개")

        # 전처리 → Processed 저장
        df_hyundai_clean = clean_hyundai(df_hyundai_raw)
        df_hyundai_clean.to_csv(
            os.path.join(processed_dir, "hyundai_faq_clean.csv"),
            index=False, encoding="utf-8-sig"
        )
        print(f"  ✅ Processed 저장 완료: {len(df_hyundai_clean)}개\n")
    else:
        print("  [!] 현대 FAQ 데이터 없음\n")
        df_hyundai_clean = pd.DataFrame()

    # ================================
    # 2. 기아 FAQ 수집 → raw 저장 → 전처리 → processed 저장
    # ================================
    print("===================================")
    print(" 🚗 2. 기아자동차 FAQ 수집")
    print("===================================")
    df_kia_raw = get_kia_faq()

    if not df_kia_raw.empty:
        df_kia_raw.to_csv(
            os.path.join(raw_dir, "kia_faq_raw.csv"),
            index=False, encoding="utf-8-sig"
        )
        print(f"  ✅ Raw 저장 완료: {len(df_kia_raw)}개")

        df_kia_clean = clean_kia(df_kia_raw)
        df_kia_clean.to_csv(
            os.path.join(processed_dir, "kia_faq_clean.csv"),
            index=False, encoding="utf-8-sig"
        )
        print(f"  ✅ Processed 저장 완료: {len(df_kia_clean)}개\n")
    else:
        print("  [!] 기아 FAQ 데이터 없음\n")
        df_kia_clean = pd.DataFrame()

    # ================================
    # 3. 테슬라 FAQ 수집 → raw 저장 → 전처리 → processed 저장
    # ================================
    print("===================================")
    print(" ⚡ 3. 테슬라 FAQ 수집")
    print("===================================")
    df_tesla_raw = get_tesla_faq()

    if not df_tesla_raw.empty:
        df_tesla_raw.to_csv(
            os.path.join(raw_dir, "tesla_faq_raw.csv"),
            index=False, encoding="utf-8-sig"
        )
        print(f"  ✅ Raw 저장 완료: {len(df_tesla_raw)}개")

        df_tesla_clean = clean_tesla(df_tesla_raw)
        df_tesla_clean.to_csv(
            os.path.join(processed_dir, "tesla_faq_clean.csv"),
            index=False, encoding="utf-8-sig"
        )
        print(f"  ✅ Processed 저장 완료: {len(df_tesla_clean)}개\n")
    else:
        print("  [!] 테슬라 FAQ 데이터 없음\n")
        df_tesla_clean = pd.DataFrame()

    # ================================
    # 4. 전체 통합 all_faq_clean.csv → processed 저장
    # ================================
    print("===================================")
    print(" 📦 4. 전체 통합 CSV 저장")
    print("===================================")

    dfs = []
    for df, name in [(df_hyundai_clean, "현대"), (df_kia_clean, "기아")]:
        if not df.empty:
            df = df.copy()
            df.insert(1, "대분류", "")
            dfs.append(df)

    if not df_tesla_clean.empty:
        dfs.append(df_tesla_clean)

    if dfs:
        df_all = pd.concat(dfs, ignore_index=True)
        df_all.to_csv(
            os.path.join(processed_dir, "all_faq_clean.csv"),
            index=False, encoding="utf-8-sig"
        )
        print(f"  ✅ 전체 통합 저장 완료!")
        print(f"     - 현대: {len(df_hyundai_clean) if not df_hyundai_clean.empty else 0}개")
        print(f"     - 기아: {len(df_kia_clean) if not df_kia_clean.empty else 0}개")
        print(f"     - 테슬라: {len(df_tesla_clean) if not df_tesla_clean.empty else 0}개")
        print(f"     - 합계: {len(df_all)}개")

    print("\n🎉 FAQ 전체 파이프라인 완료!")
    print(f"\n📁 저장 위치:")
    print(f"   Raw     : {raw_dir}")
    print(f"   Processed: {processed_dir}")


if __name__ == "__main__":
    main()