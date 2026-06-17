from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="Domestic Car Sales",
    layout="wide"
)

# -------------------------
# CSS
# -------------------------
st.markdown("""
<style>

/* Sidebar */
[data-testid="stSidebar"]{
    background:#000000 !important;
}

/* 기본 페이지 목록 숨김 */
[data-testid="stSidebarNav"]{
    display:none !important;
}

/* 글자 */
[data-testid="stSidebar"] *{
    color:white !important;
}

/* 버튼 */
div.stButton > button{
    background:#000000 !important;
    color:white !important;
    border:none !important;
    width:100%;
    text-align:left;
    padding:15px;
    font-size:20px;
}

/* selectbox */
div[data-baseweb="select"] > div{
    background:#333333 !important;
    border-radius:10px;
    min-height:55px;
}

hr {
    height: 3px !important;
    border: none !important;
    background: linear-gradient(
        90deg,
        #ff0000,
        #ff7f00,
        #ffff00,
        #00ff00,
        #0000ff,
        #4b0082,
        #9400d3
    ) !important;
    margin: 1em 0 !important;
}

[data-testid="stSidebarContent"] {
    padding-top: 0rem !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Sidebar
# -------------------------
with st.sidebar:

    st.markdown("## Dashboard Menu")

    if st.button("🏠 Home"):
        st.switch_page("app.py")

    st.divider()

    # -------------------------
    # Brand
    # -------------------------
    st.subheader("Brand")

    brand = st.selectbox(
        "브랜드 분석",
        [
            "선택",
            "연도별",
            "월별",
            "TOP10"
        ]
    )

    if brand != "선택":
        st.switch_page("pages/brand.py")

    st.divider()

    # -------------------------
    # Age
    # -------------------------
    st.subheader("Age")

    age = st.selectbox(
        "연령 분석",
        [
            "선택",
            "브랜드 순위",
            "차종 순위"
        ]
    )

    if age != "선택":
        st.switch_page("pages/age_gender.py")

    st.divider()

    # -------------------------
    # Gender
    # -------------------------
    st.subheader("Gender")

    gender = st.selectbox(
        "성별 분석",
        [
            "선택",
            "브랜드 순위",
            "차종 순위"
        ]
    )

    if gender != "선택":
        st.switch_page("pages/age_gender.py")


# -------------------------
# Main
# -------------------------

st.title("🚗 Domestic Car Sales Dashboard")

st.subheader("국내 자동차 판매 데이터 분석")

st.write("환영합니다.")

st.write("""
좌측 메뉴를 이용하여

- 브랜드 분석
- 연령별 분석
- 성별 분석

을 확인할 수 있습니다.
""")