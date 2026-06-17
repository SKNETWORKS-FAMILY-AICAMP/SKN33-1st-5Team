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

        return df

    except Exception as e:
        print(f" 데이터 조회 중 오류 발생: {e}")
    finally:
        # 4. 연결 닫기
        conn.close()


if __name__ == "__main__":
    fetch_age_ranking()