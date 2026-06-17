import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

from database.query import (
    get_age_brand_rank,
    get_gender_brand_rank
)

# =====================================
# 페이지 설정
# =====================================

st.set_page_config(
    page_title="Age & Gender Analysis",
    layout="wide"
)

st.title("👨‍👩‍👧‍👦 Age & Gender Analysis")

# 한글 깨짐 방지
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# =====================================
# 탭 생성
# =====================================

tab1, tab2 = st.tabs(
    [
        "Age",
        "Gender"
    ]
)

# =========================================
# AGE TAB
# =====================================

with tab1:

    st.header("연령별 브랜드 순위")

    selected_age = st.select_slider(
        "연령 선택",
        options=[
            "20대",
            "30대",
            "40대",
            "50대",
            "60대",
            "70대"
        ]
    )

    # DB 값 매핑
    age_map = {
        "20대": "~20대",
        "30대": "30대",
        "40대": "40대",
        "50대": "50대",
        "60대": "60대",
        "70대": "70대~"
    }

    df = get_age_brand_rank(
        age_map[selected_age]
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(
        df["브랜드명"],
        df["등록대수"]
    )

    ax.set_title(
        f"{selected_age} 브랜드 순위"
    )

    ax.set_xlabel("브랜드")

    ax.set_ylabel("등록대수")

    st.pyplot(fig)

# =====================================
# GENDER TAB
# =====================================

with tab2:

    st.header("성별 브랜드 순위")

    selected_gender = st.select_slider(
        "성별 선택",
        options=[
            "남성",
            "여성"
        ]
    )

    df = get_gender_brand_rank(
        selected_gender
    )

    df["등록대수"] = pd.to_numeric(
        df["등록대수"],
        errors="coerce"
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    fig, ax = plt.subplots(figsize=(8, 6))

    st.write(df.dtypes)
    st.dataframe(df)

    ax.pie(
        df["등록대수"],
        labels=df["브랜드명"],
        autopct="%1.1f%%"
    )

    ax.set_title(
        f"{selected_gender} 브랜드 순위"
    )

    st.pyplot(fig)