
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)
sys.path.append(os.path.join(root, "database"))

from sidebar_utils import render_sidebar
from query import get_top_brands_by_gender

st.set_page_config(page_title="성별 브랜드 순위 | Domestic Car Sales", layout="wide")

render_sidebar(active_section="gender", active_menu="브랜드 순위")

st.markdown('<div style="font-size:3.5rem;font-weight:800;line-height:1.2;color:rgba(255,255,255,0.95);margin-bottom:0.5rem;">👫 성별 브랜드 순위</div>', unsafe_allow_html=True)
st.markdown('<div style="color:rgba(255,255,255,0.45);font-size:1rem;margin-bottom:1rem;">성별로 선호하는 브랜드 순위와 판매량을 확인합니다.</div>', unsafe_allow_html=True)
st.divider()

main_col, _ = st.columns([3, 2])

with main_col:
    gender = st.radio("성별 선택", ["남성", "여성"], index=None, horizontal=True)
    st.divider()

    if gender is None:
        st.info("📌 성별을 선택하면 브랜드 순위가 표시됩니다.")
        st.stop()

    st.subheader(f"🏅 {gender} 브랜드 순위 (판매량 기준)")

    try:
        data = get_top_brands_by_gender(gender, limit=10)
        if data:
            df = pd.DataFrame(data)[["brand_name", "gender_reg_count"]]
            df.columns = ["브랜드", "판매량"]
            # 브랜드 중복 제거 (같은 브랜드 다중 행 → 최대값 유지)
            df = df.groupby("브랜드", as_index=False)["판매량"].max()
            df = df.sort_values("판매량", ascending=False).reset_index(drop=True)
            df.insert(0, "순위", range(1, len(df) + 1))

            y_max = df["판매량"].max()
            fig = px.bar(
                df, x="브랜드", y="판매량",
                color_discrete_sequence=["#636EFA"],
                text="판매량",
            )
            fig.update_traces(texttemplate="%{text:,}", textposition="outside",
                              constraintext="none")
            fig.update_layout(
                xaxis_tickangle=0,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                height=420,
                showlegend=False,
                margin=dict(t=40, b=20),
                yaxis=dict(gridcolor="rgba(255,255,255,0.08)",
                           range=[0, y_max * 1.18]),
            )
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                df.style.set_properties(**{"text-align": "center"}),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("데이터가 없습니다.")
    except Exception as e:
        st.error(f"오류: {e}")
