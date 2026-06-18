
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)
sys.path.append(os.path.join(root, "database"))

from sidebar_utils import render_sidebar
from query import get_all_brands, get_models_by_brand, get_monthly_reg_by_model

st.set_page_config(page_title="월별 분석 | Domestic Car Sales", layout="wide")

render_sidebar(active_section="brand", active_menu="월별 분석")

# ── 브랜드 목록 로드 ──────────────────────────────────────────
@st.cache_data
def load_brands():
    return get_all_brands()

@st.cache_data
def load_models(brand_id):
    return get_models_by_brand(brand_id)

try:
    brands = load_brands()
except Exception as e:
    st.error(f"DB 연결 실패: {e}")
    st.stop()

brand_names = [b["brand_name"] for b in brands]
brand_ids   = {b["brand_name"]: b["brand_id"] for b in brands}

# ── Main ──────────────────────────────────────────────────────
st.markdown('<div style="font-size:3.5rem;font-weight:800;line-height:1.2;color:rgba(255,255,255,0.95);margin-bottom:0.5rem;">📈 월별 분석</div>', unsafe_allow_html=True)
st.subheader("브랜드별로 월별에 따른 기업 별/모델 별 자동차 판매량과 월 별 누적 상세 데이터량으로 더 자세히 비교할 수 있습니다. ")
st.divider()

PLACEHOLDER = "── 선택하세요 ──"

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    selected_brands = st.multiselect(
        "브랜드 선택 (복수 선택 가능)",
        brand_names,
        placeholder="브랜드를 선택하세요"
    )

# 선택된 브랜드들의 모델 목록 통합
all_model_options = []   # "브랜드 - 모델" 레이블 목록
model_id_map = {}        # 레이블 → model_id

if selected_brands:
    for brand_name in selected_brands:
        bid = brand_ids[brand_name]
        try:
            models = load_models(bid)
        except Exception as e:
            st.error(f"{brand_name} 모델 로드 오류: {e}")
            st.stop()
        for m in (models or []):
            label = m["model_name"]          # 브랜드명 제거, 모델명만 표시
            all_model_options.append(label)
            model_id_map[label] = m["model_id"]

with col2:
    selected_model_labels = st.multiselect(
        "모델 선택 (복수 선택 가능)",
        all_model_options,
        placeholder="모델을 선택하세요",
        disabled=(not selected_brands)
    )

with col3:
    year_opt = st.selectbox("연도 선택", [PLACEHOLDER, 2026, 2025, 2024])

st.divider()

if not selected_brands or not selected_model_labels or year_opt == PLACEHOLDER:
    st.info("📌 브랜드, 모델, 연도를 모두 선택하면 결과가 표시됩니다.")
    st.stop()

selected_year = year_opt

# ── 1. 오버레이 월별 라인차트 ─────────────────────────────────
st.subheader(f"📈 모델별 월별 등록 추이 비교 ({selected_year}년)")

fig_overlay = go.Figure()
df_all_monthly = {}   # label → DataFrame (월별 분석용)

for label in selected_model_labels:
    model_id = model_id_map[label]
    try:
        data = get_monthly_reg_by_model(model_id, year=selected_year)
    except Exception as e:
        st.error(f"{label} 데이터 로드 오류: {e}")
        continue
    if data:
        df = pd.DataFrame(data)
        df["월"] = df["month"].astype(str) + "월"
        df_all_monthly[label] = df
        fig_overlay.add_trace(go.Scatter(
            x=df["월"],
            y=df["monthly_reg_count"],
            mode="lines+markers",
            name=label,
            line=dict(width=2),
            marker=dict(size=6)
        ))

if fig_overlay.data:
    fig_overlay.update_layout(
        xaxis_tickangle=0,
        xaxis_title="월",
        yaxis_title="등록 수",
        legend_title="모델",
        height=480,
        plot_bgcolor="white",
        hovermode="x unified"
    )
    st.plotly_chart(fig_overlay, use_container_width=True)
else:
    st.info("선택한 모델의 해당 연도 데이터가 없습니다.")

# ── 2. 월 선택 합계 분석 ─────────────────────────────────────
if df_all_monthly:
    st.divider()
    st.subheader("📊 월별 구간 합계 분석")

    # 전체 월 옵션 (데이터 있는 월 기준)
    all_months = sorted(
        set(m for df in df_all_monthly.values() for m in df["월"].tolist()),
        key=lambda x: int(x.replace("월", ""))
    )
    selected_months = st.multiselect(
        "기간(월) 선택 (복수 선택 가능)",
        all_months,
        placeholder="합계를 볼 기간(월)을 선택하세요"
    )

    if selected_months:
        # 모델별 선택 월 합계 집계
        agg_rows = []
        for label, df in df_all_monthly.items():
            df_sel = df[df["월"].isin(selected_months)]
            total = int(df_sel["monthly_reg_count"].sum())
            agg_rows.append({"모델": label, "합계 등록 수": total})

        df_agg = pd.DataFrame(agg_rows)
        df_agg = df_agg[df_agg["합계 등록 수"] > 0]  # 데이터 없는 모델 제외

        if df_agg.empty:
            st.info("선택한 기간(월)에 데이터가 있는 모델이 없습니다.")
        else:
            grand_total = int(df_agg["합계 등록 수"].sum())
            months_label = ", ".join(selected_months)
            st.caption(f"전체 합계 ({months_label}): **{grand_total:,} 대**")

            # 등록 수 기준 내림차순 정렬 (아래 → 위로 표시)
            df_agg_sorted = df_agg.sort_values("합계 등록 수", ascending=True)
            fig_agg = px.bar(
                df_agg_sorted,
                y="모델",
                x="합계 등록 수",
                orientation="h",
                color="모델",
                text="합계 등록 수",
                title=f"선택 월({months_label}) 모델별 합계",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_agg.update_traces(
                texttemplate="%{text:,}",
                textposition="outside",
            )
            fig_agg.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                height=max(380, len(df_agg_sorted) * 48),
                showlegend=False,
                yaxis_title="모델",
                xaxis_title="합계 등록 수",
                xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
                margin=dict(r=120),
            )
            st.plotly_chart(fig_agg, use_container_width=True)
    else:
        st.info("📌 합계를 볼 기간(월)을 선택하세요.")

st.divider()
