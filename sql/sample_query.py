import pandas as pd
import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.abspath(
            os.path.dirname(__file__)
        )
    )
)

from database.db_connection import get_connection


def fetch_age_ranking():

    conn = get_connection()

    if not conn:
        print("❌ DB 연결 실패")
        return None

    try:

        cursor = conn.cursor()

        sql = """
        SELECT
            a.age_group,
            b.brand_name,
            a.ranking,
            a.age_reg_count
        FROM Age_Registration a
        JOIN Brand b
            ON a.brand_id = b.brand_id
        WHERE a.age_group = '~20대'
          AND a.brand_id IS NOT NULL
        ORDER BY a.ranking
        """

        cursor.execute(sql)

        rows = cursor.fetchall()

        df = pd.DataFrame(rows)

        df = df.rename(columns={
            "age_group": "연령대",
            "brand_name": "브랜드명",
            "ranking": "순위",
            "age_reg_count": "등록대수"
        })

        print("\n📊 [조회 결과]")
        print("-" * 50)
        print(df.to_string(index=False))
        print("-" * 50)

        return df

    except Exception as e:
        print(f"❌ 데이터 조회 중 오류 발생: {e}")

    finally:
        conn.close()


if __name__ == "__main__":
    fetch_age_ranking()