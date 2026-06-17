import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from database.db_connection import get_connection


def fetch_age_ranking():
    """1. 20대 이하 모델 선호도 조회 (판다스 변환 구조 완벽 보정)"""
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        # 💡 직관적인 매칭을 위해 SQL Select 절의 이름들을 깔끔하게 정리했습니다.
        sql = """
              SELECT a.age_group AS age_group, 
                     IFNULL(b.brand_name, '(확인 불가)') AS brand_name, 
                     IFNULL(m.model_name, '(이름 매칭 실패)') AS model_name,
                     a.ranking AS ranking, 
                     a.age_reg_count AS age_reg_count
              FROM Age_Registration a
                       LEFT JOIN Brand b ON a.brand_id = b.brand_id
                       LEFT JOIN Car_Model m ON a.model_id = m.model_id
              WHERE TRIM(a.age_group) LIKE '%20대 이하%'
                AND TRIM(a.gubun) = '모델'
              ORDER BY a.ranking 
              """
        cursor.execute(sql)
        rows = cursor.fetchall()

        if not rows:
            print("\n📊 [분석 1] 20대 이하 모델 선호도 ➡️ 조건에 맞는 데이터가 없습니다.")
            return None

        # 💡 [핵심 보정] 번호(0,1,2) 대신 실제 딕셔너리 형태의 컬럼명을 그대로 명시하여 프레임을 생성합니다.
        df = pd.DataFrame(rows, columns=["age_group", "brand_name", "model_name", "ranking", "age_reg_count"])
        df = df.rename(columns={
            "age_group": "연령대",
            "brand_name": "브랜드명",
            "model_name": "모델명",
            "ranking": "순위",
            "age_reg_count": "등록대수"
        })

        print("\n📊 [분석 1] 20대 이하 모델 선호도")
        print("-" * 75)
        print(df.to_string(index=False))
        print("-" * 75)
        return df
    except Exception as e:
        print(f"데이터 조회 중 오류 발생: {e}")
    finally: conn.close()


def fetch_gender_model_ranking():
    """2. 성별별 선호 자동차 모델 TOP 5 조회 (판다스 변환 구조 완벽 보정)"""
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        sql = """
              SELECT g.gender AS gender, 
                     IFNULL(b.brand_name, '(확인 불가)') AS brand_name, 
                     IFNULL(m.model_name, '(이름 매칭 실패)') AS model_name,
                     g.ranking AS ranking, 
                     g.gender_reg_count AS gender_reg_count
              FROM Gender_Registration g
                       LEFT JOIN Brand b ON g.brand_id = b.brand_id
                       LEFT JOIN Car_Model m ON g.model_id = m.model_id
              WHERE TRIM(g.gubun) = '모델'
                AND g.ranking <= 5
              ORDER BY g.gender, g.ranking 
              """
        cursor.execute(sql)
        rows = cursor.fetchall()

        if not rows:
            print("\n👫 [분석 2] 성별 자동차 모델 선호도 TOP 5 ➡️ 조건에 맞는 데이터가 없습니다.")
            return None

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
        print(f"데이터 조회 중 오류 발생: {e}")
    finally: conn.close()


def fetch_brand_market_share():
    """4. 브랜드별 누적 판매량 및 시장 점유율(%) 순위"""
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        sql = """
              SELECT b.brand_name AS brand_name, 
                     SUM(m.monthly_reg_count) AS total_sales, 
                     ROUND(SUM(m.monthly_reg_count) / (SELECT SUM(monthly_reg_count) FROM Monthly_Registration) * 100, 2) AS share_ratio
              FROM Monthly_Registration m
                       JOIN Car_Model cm ON m.model_id = cm.model_id
                       JOIN Brand b ON cm.brand_id = b.brand_id
              GROUP BY b.brand_id, b.brand_name ORDER BY total_sales DESC 
              """
        cursor.execute(sql)
        rows = cursor.fetchall()

        if not rows:
            print("\n🏆 [분석 4] 브랜드별 누적 시장 점유율 순위 ➡️ 데이터가 없습니다.")
            return None

        df = pd.DataFrame(rows, columns=["brand_name", "total_sales", "share_ratio"])
        df = df.rename(columns={"brand_name": "브랜드명", "total_sales": "총판매량", "share_ratio": "점유율(%)"})
        print("\n🏆 [분석 4] 브랜드별 누적 시장 점유율 순위")
        print("-" * 50)
        print(df.to_string(index=False))
        print("-" * 50)
        return df
    except Exception as e:
        print(f"데이터 조회 중 오류 발생: {e}")
    finally: conn.close()


if __name__ == "__main__":
    print("🚀 데이터 분석용 쿼리 조회를 시작합니다.")
    fetch_age_ranking()
    fetch_gender_model_ranking()
    fetch_monthly_sales_trend()
    fetch_brand_market_share()