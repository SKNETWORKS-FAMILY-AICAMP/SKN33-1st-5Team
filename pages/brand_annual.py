
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)
sys.path.append(os.path.join(root, "database"))

from sidebar_utils import render_sidebar
from query import get_annual_reg_by_brand

st.set_page_config(page_title="연도별 분석 | Domestic Car Sales", layout="wide")

render_sidebar(active_section="brand", active_menu="연도별 분석")

st.markdown('<div style="font-size:3.5rem;font-weight:800;line-height:1.2;color:rgba(255,255,255,0.95);margin-bottom:0.5rem;">📅 연도별 분석</div>', unsafe_allow_html=True)
st.markdown('<div style="color:rgba(255,255,255,0.45);font-size:1rem;margin-bottom:1rem;">연도별 브랜드 판매량을 누적 막대차트로 비교합니다.</div>', unsafe_allow_html=True)
st.divider()

YEARS = [2024, 2025, 2026]
BRAND_OPTIONS = ["전체", "현대", "기아", "테슬라"]

@st.cache_data
def load_all_years():
    rows = []
    for yr in YEARS:
        data = get_annual_reg_by_brand(yr)
        for row in data:
            rows.append({
                "연도":     yr,
                "기업명":   row["brand_name"],
                "등록 대수": int(row["total_reg"]),
            })
    return pd.DataFrame(rows)

try:
    df_all = load_all_years()
except Exception as e:
    st.error(f"데이터 로드 오류: {e}")
    st.stop()

if df_all.empty:
    st.info("데이터가 없습니다.")
    st.stop()

main_col, _ = st.columns([3, 2])

with main_col:
    selected_brand = st.selectbox("기업 선택", BRAND_OPTIONS)
    st.divider()

    df = df_all[df_all["기업명"] == selected_brand].copy() if selected_brand != "전체" else df_all.copy()

    if df.empty:
        st.info(f"'{selected_brand}' 데이터가 없습니다.")
        st.stop()

    # ── 누적 막대차트 ──────────────────────────────────────────
    fig = px.bar(
        df,
        x="연도",
        y="등록 대수",
        color="기업명",
        text="등록 대수",
        barmode="stack",
        labels={"연도": "연도", "기업명": "기업명", "등록 대수": "등록 대수"},
        color_discrete_map={"현대": "#10B981", "기아": "#60A5FA", "테슬라": "#F9A8D4"},
    )
    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(size=11),
    )
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=df["연도"].unique().tolist(),
            ticktext=[str(y) for y in sorted(df["연도"].unique())],
            title="연도",
            color="rgba(255,255,255,0.7)",
            gridcolor="rgba(255,255,255,0.05)",
        ),
        yaxis=dict(
            title="판매량",
            color="rgba(255,255,255,0.7)",
            gridcolor="rgba(255,255,255,0.08)",
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", size=13),
        legend_title_text="기업명",
        legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
        height=480,
        margin=dict(t=30, b=40),
        uniformtext_minsize=8,
        uniformtext_mode="show",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── 피벗 테이블 ─────────────────────────────────────────────
    st.subheader("📋 상세 데이터")
    df_pivot = df.pivot_table(
        index="기업명", columns="연도", values="등록 대수", aggfunc="sum"
    ).reset_index()
    df_pivot.columns.name = None
    df_pivot = df_pivot.fillna(0)
    for c in df_pivot.columns:
        if c != "기업명":
            df_pivot[c] = df_pivot[c].astype(int)
    st.dataframe(
        df_pivot.style.set_properties(**{"text-align": "center"}),
        use_container_width=True,
        hide_index=True,
    )
