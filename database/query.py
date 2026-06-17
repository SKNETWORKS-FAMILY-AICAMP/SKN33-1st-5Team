import pandas as pd

from database.db_connection import get_connection


# ======================================
# 연령별 브랜드 순위 조회
# ======================================
def get_age_brand_rank(age_group):

    conn = get_connection()

    sql = """
    SELECT
        b.brand_name AS 브랜드명,
        a.age_reg_count AS 등록대수
    FROM Age_Registration a
    JOIN Brand b
        ON a.brand_id = b.brand_id
    WHERE a.age_group = %s
    ORDER BY a.ranking
    """

    df = pd.read_sql(
        sql,
        conn,
        params=[age_group]
    )

    conn.close()

    return df


# ======================================
# 성별 브랜드 순위 조회
# ======================================
def get_gender_brand_rank(gender):

    conn = get_connection()

    sql = """
    SELECT
        b.brand_name AS 브랜드명,
        g.gender_reg_count AS 등록대수
    FROM Gender_Registration g
    JOIN Brand b
        ON g.brand_id = b.brand_id
    WHERE g.gender = %s
    ORDER BY g.ranking
    """

    df = pd.read_sql(
        sql,
        conn,
        params=[gender]
    )

    conn.close()

    return df