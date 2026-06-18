
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)
sys.path.append(os.path.join(root, "database"))

from sidebar_utils import render_sidebar
from query import get_top_models_total

st.set_page_config(page_title="TOP10 분석 | Domestic Car Sales", layout="wide")

render_sidebar(active_section="brand", active_menu="TOP10 분석")

st.markdown('<div style="font-size:3.5rem;font-weight:800;line-height:1.2;color:rgba(255,255,255,0.95);margin-bottom:0.5rem;">🏆 TOP10 분석</div>', unsafe_allow_html=True)
st.divider()

# ── 브랜드 옵션 ─────────────────────────────────────────────────
BRAND_OPTIONS = ["── 선택하세요 ──", "전체", "현대", "기아", "테슬라"]

selected_brand = st.selectbox("기업 선택", BRAND_OPTIONS)

if selected_brand == "── 선택하세요 ──":
    st.info("📌 기업을 선택하면 TOP 10 데이터가 표시됩니다.")
    st.stop()

st.divider()

brand_label = selected_brand if selected_brand != "전체" else "전체"
st.subheader(f"{brand_label} 모델 TOP 10")

try:
    data = get_top_models_total(limit=10, brand_name=selected_brand)
    if data:
        df = pd.DataFrame(data)
        df.columns = ["모델명", "기업명", "등록 대수"]
        df = df.sort_values("등록 대수", ascending=True)  # 가로 막대용 오름차순

        fig = px.bar(
            df,
            x="등록 대수",
            y="모델명",
            color="기업명",
            text="등록 대수",
            orientation="h",
            labels={"모델명": "", "등록 대수": "등록 대수", "기업명": "기업명"},
        )
        fig.update_traces(
            texttemplate="%{text:,}",
            textposition="outside",
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white", size=13),
            height=520,
            legend_title_text="기업명",
            xaxis=dict(
                gridcolor="rgba(255,255,255,0.08)",
                tickformat=",",
                color="rgba(255,255,255,0.6)",
            ),
            yaxis=dict(color="rgba(255,255,255,0.9)"),
            legend=dict(
                font=dict(color="white"),
                bgcolor="rgba(0,0,0,0)",
            ),
            margin=dict(l=20, r=80, t=20, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("데이터가 없습니다.")
except Exception as e:
    st.error(f"오류: {e}")
