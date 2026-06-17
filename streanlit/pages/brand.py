import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------
# MUST BE FIRST
# ---------------------------------
st.set_page_config(
    page_title="Brand Analysis",
    layout="wide"
)

# ---------------------------------
# Sidebar CSS
# ---------------------------------
st.markdown("""
<style>

/* Sidebar */
[data-testid="stSidebar"]{
    background:#000000 !important;
}

/* Hide Streamlit page list (THIS FIXES IT) */
[data-testid="stSidebarNav"]{
    display:none !important;
}

/* Sidebar text */
[data-testid="stSidebar"] *{
    color:white !important;
}

/* Reset spacing */
[data-testid="stSidebarContent"]{
    padding-top:20px;python app.py
}

/* Button */
div.stButton > button{

    background:#000000 !important;

    color:white !important;

    border:none !important;

    width:100%;
    

    padding:15px;

    text-align:left;

    font-size:20px;
}

/* Divider */
hr {
        height: 3px !important;     /* 두께 조절 */
        border: none !important;    /* 기존 테두리 제거 */
        background: linear-gradient(90deg, 
            #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3
        ) !important;
        margin: 1em 0 !important;
}
/* 사이드바의 최상단 여백을 강제로 0으로 설정 */
[data-testid="stSidebarContent"] {
    padding-top: 0rem !important;
}

/* 자동 네비게이션 영역의 높이를 0으로 만들어 레이아웃 밀림 방지 */
[data-testid="stSidebarNav"] {
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}
/* Selectbox */
div[data-baseweb="select"] > div{

    background:#333333 !important;

    border-radius:10px !important;

    min-height:55px;

    border:1px solid #555 !important;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------
# Sidebar
# ---------------------------------

with st.sidebar:

    st.markdown(
        "## Dashboard Menu"
    )

    if st.button("Home"):
        st.switch_page("app.py")

    st.divider()

    st.subheader("Brand")

    selected = st.selectbox(
        "",
        [
            "연도 별",
            "월 별",
            "TOP 10"
        ],
        label_visibility="collapsed"
    )

# ---------------------------------
# YEAR
# ---------------------------------


if selected == "연도 별":

    st.title("📈 Yearly Sales")

    st.subheader("Brand Sales by Year")

    st.write(
        "Annual sales comparison."
    )

    df = pd.DataFrame({
        "Year":[2021,2022,2023,2024],
        "Hyundai":[68,72,76,82],
        "Kia":[55,59,63,66],
        "Tesla":[10,13,18,24]
    })

    col1, col2 = st.columns([2,1])

    with col1:
        fig, ax = plt.subplots(figsize=(5, 3))
        # 색상과 스타일을 명시적으로 지정
        ax.plot(df["Year"], df["Hyundai"], color='#e63946', linewidth=1, label="Hyundai")
        ax.plot(df["Year"], df["Kia"], color='#457b9d', linewidth=2, label="Kia")
        ax.plot(df["Year"], df["Tesla"], color='#f1faee', linewidth=2, label="Tesla")

        # 제목 및 축 이름 설정
        ax.set_title("Annual Sales Analysis", fontsize=12)
        ax.set_xlabel("Year", fontsize=10)
        ax.set_ylabel("Sales Count", fontsize=10)

        # 범례(Legend) 글자 크기 조절
        ax.legend(fontsize=5)

        # 눈금 크기 조절
        ax.tick_params(labelsize=10)

        st.pyplot(fig)
        st.info("최근 4년간 연도별 판매량 추이입니다.")
        st.dataframe(df, use_container_width=True)

# ---------------------------------
# MONTH
# ---------------------------------
elif selected == "월 별":

    st.title("📊 Monthly Sales")

    st.subheader(
        "Monthly Trend"
    )

    df = pd.DataFrame({

        "Month":[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun"
        ],

        "Sales":[
            12000,
            13000,
            14000,
            15000,
            18000,
            20000
        ]

    })

    col1, col2 = st.columns([2,1])

    with col1:

        fig, ax = plt.subplots(
            figsize=(6,4)
        )

        ax.bar(
            df["Month"],
            df["Sales"]
        )

        st.pyplot(fig)

        st.dataframe(
            df,
            use_container_width=True
        )


# ---------------------------------
# TOP10
# ---------------------------------
elif selected == "TOP 10":

    st.title("🏆 TOP 10 Sales")

    st.subheader(
        "Top Brand Ranking"
    )

    df = pd.DataFrame({

        "Brand":[
            "Hyundai",
            "Kia",
            "Tesla"
        ],

        "Sales":[
            82000,
            66000,
            24000
        ]

    })

    col1, col2 = st.columns([2,1])

    with col1:

        fig, ax = plt.subplots(
            figsize=(6,4)
        )

        ax.barh(
            df["Brand"],
            df["Sales"]
        )

        st.pyplot(fig)

        st.dataframe(
            df,
            use_container_width=True
        )
