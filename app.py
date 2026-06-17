import sys
from pathlib import Path

import plotly.express as px
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from database.query import (  # noqa: E402
    get_brand_monthly_sales,
    get_brand_total_sales,
    get_summary_metrics,
    get_top_models,
)


st.set_page_config(
    page_title="자동차 등록 통계 대시보드",
    layout="wide",
)

st.title("자동차 등록 통계 대시보드")
st.caption("현대, 기아, 테슬라 중심의 월별 판매량과 등록 통계를 확인합니다.")

metrics = get_summary_metrics()

col1, col2, col3, col4 = st.columns(4)
col1.metric("브랜드 수", f"{int(metrics.get('brand_count') or 0):,}")
col2.metric("모델 수", f"{int(metrics.get('model_count') or 0):,}")
col3.metric("전체 등록량", f"{int(metrics.get('total_registration') or 0):,}")

min_year = metrics.get("min_year")
max_year = metrics.get("max_year")
period = "-" if min_year is None or max_year is None else f"{int(min_year)} - {int(max_year)}"
col4.metric("분석 기간", period)

st.divider()

monthly_df = get_brand_monthly_sales()
brand_df = get_brand_total_sales()

if monthly_df.empty:
    st.warning("표시할 월별 등록 데이터가 없습니다. DB 또는 CSV 데이터를 먼저 확인해 주세요.")
else:
    monthly_df["period"] = (
        monthly_df["year"].astype(str)
        + "-"
        + monthly_df["month"].astype(int).astype(str).str.zfill(2)
    )

    left, right = st.columns([2, 1])

    with left:
        st.subheader("월별 브랜드 등록 추이")
        fig = px.line(
            monthly_df,
            x="period",
            y="registration_count",
            color="brand_name",
            markers=True,
            labels={
                "period": "기간",
                "registration_count": "등록량",
                "brand_name": "브랜드",
            },
        )
        fig.update_layout(legend_title_text="브랜드", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("브랜드별 누적 등록량")
        fig = px.pie(
            brand_df,
            names="brand_name",
            values="registration_count",
            hole=0.45,
        )
        st.plotly_chart(fig, use_container_width=True)

st.subheader("전체 모델 TOP 10")
top_models = get_top_models(limit=10)

if top_models.empty:
    st.info("표시할 모델 데이터가 없습니다.")
else:
    fig = px.bar(
        top_models.sort_values("registration_count"),
        x="registration_count",
        y="model_name",
        color="brand_name",
        orientation="h",
        labels={
            "registration_count": "등록량",
            "model_name": "모델",
            "brand_name": "브랜드",
        },
    )
    fig.update_layout(yaxis_title=None, legend_title_text="브랜드")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(top_models, use_container_width=True, hide_index=True)
