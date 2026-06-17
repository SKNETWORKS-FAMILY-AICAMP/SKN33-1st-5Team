# database/query.py
import pandas as pd
import streamlit as st
from database.db_connection import get_connection

# 데이터를 숫자로 안전하게 변환하는 내부 유틸리티 함수
def _ensure_numeric(df, numeric_cols):
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

@st.cache_data(ttl=600)
def get_monthly_sales_data():
    conn = get_connection()
    if conn:
        query = """
        SELECT b.brand_name, m.model_name, r.year, r.month, r.monthly_reg_count
        FROM Monthly_Registration r
        JOIN Car_Model m ON r.model_id = m.model_id
        JOIN Brand b ON m.brand_id = b.brand_id
        """
        df = pd.read_sql(query, conn)
        conn.close()
        # 판매량 데이터를 숫자로 변환
        return _ensure_numeric(df, ['monthly_reg_count', 'year', 'month'])
    return pd.DataFrame()

@st.cache_data(ttl=600)
def get_age_stats_data():
    conn = get_connection()
    if conn:
        query = """
        SELECT a.age_group, b.brand_name, a.ranking, a.age_reg_count
        FROM Age_Registration a
        LEFT JOIN Brand b ON a.brand_id = b.brand_id
        """
        df = pd.read_sql(query, conn)
        conn.close()
        # ranking과 reg_count를 숫자로 변환
        return _ensure_numeric(df, ['ranking', 'age_reg_count'])
    return pd.DataFrame()

@st.cache_data(ttl=600)
def get_gender_stats_data():
    conn = get_connection()
    if conn:
        query = """
        SELECT g.gender, b.brand_name, g.ranking, g.gender_reg_count
        FROM Gender_Registration g
        LEFT JOIN Brand b ON g.brand_id = b.brand_id
        """
        df = pd.read_sql(query, conn)
        conn.close()
        # ranking과 reg_count를 숫자로 변환
        return _ensure_numeric(df, ['ranking', 'gender_reg_count'])
    return pd.DataFrame()

@st.cache_data(ttl=600)
def get_model_list():
    conn = get_connection()
    if conn:
        query = """
        SELECT m.model_name, b.brand_name 
        FROM Car_Model m
        JOIN Brand b ON m.brand_id = b.brand_id
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    return pd.DataFrame()