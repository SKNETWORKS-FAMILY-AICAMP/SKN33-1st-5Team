import pandas as pd
import sys
import os

# 현재 파일(sql/sample_query.py)의 상위 폴더를 파이썬 경로에 추가하여
# database 폴더 안의 db_connection을 정확히 인식하게 만듭니다.
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from database.db_connection import get_connection


def fetch_age_ranking():
    # 1. DB 연결 열기
    conn = get_connection()
    if not conn:
        print(" DB 연결에 실패했습니다.")
        return                 

    try:
        # 2. 20대 브랜드 선호도를 뽑아오는 SQL 문
        sql = """
              SELECT a.age_group     AS '연령대', \
                     b.brand_name    AS '브랜드명', \
                     a.ranking       AS '순위', \
                     a.age_reg_count AS '등록대수'
              FROM Age_Registration a
                       JOIN Brand b ON a.brand_id = b.brand_id
              WHERE a.age_group = '~20대' \
                AND a.brand_id IS NOT NULL
              ORDER BY a.ranking ASC; \
              """

        # 3. pandas 경고창을 방지하기 위해 conn을 직접 넣는 대신
        # sql과 conn을 구조에 맞게 전달합니다.
        df = pd.read_sql(sql, con=conn)

        print("\n📊 [조회 결과] 20대 브랜드 선호도 데이터가 정상 출력되었습니다!")
        print("-" * 50)
        print(df)
        print("-" * 50)

        df = pd.DataFrame(rows, columns=["gender", "brand_name", "model_name", "ranking", "gender_reg_count"])
        df = df.rename(columns={
            "gender": "성별",
            "brand_name": "브랜드명",
            "model_name": "모델명",
            "ranking": "순위",
            "gender_reg_count": "등록대수"
        })

        print("\n👫 [분석 2] 성별 자동차 모델 선호도 TOP 5")
        print("-" * 75)
        print(df.to_string(index=False))
        print("-" * 75)
        return df
    except Exception as e:
        print(f"데이터 조회 중 오류 발생: {e}")
    finally: conn.close()


def fetch_monthly_sales_trend():
    """3. 월별 전체 자동차 판매량 추이 조회"""
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        sql = """
              SELECT year, month, SUM(monthly_reg_count) AS total_sales
              FROM Monthly_Registration
              GROUP BY year, month ORDER BY year, month 
              """
        cursor.execute(sql)
        rows = cursor.fetchall()

        if not rows:
            print("\n📈 [분석 3] 월별 전체 자동차 판매량 추이 ➡️ 데이터가 없습니다.")
            return None

        df = pd.DataFrame(rows, columns=["year", "month", "total_sales"])
        df = df.rename(columns={"year": "연도", "month": "월", "total_sales": "총판매량"})
        print("\n📈 [분석 3] 월별 전체 자동차 판매량 추이")
        print("-" * 50)
        print(df.to_string(index=False))
        print("-" * 50)
        return df
    except Exception as e:
        print(f" 데이터 조회 중 오류 발생: {e}")
    finally:
        # 4. 연결 닫기
        conn.close()


if __name__ == "__main__":
    print("🚀 데이터 분석용 쿼리 조회를 시작합니다.")
    fetch_age_ranking()
    fetch_gender_model_ranking()
    fetch_monthly_sales_trend()
    fetch_brand_market_share()