
import streamlit as st

SIDEBAR_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Noto+Sans+KR:wght@400;500;700&display=swap');

/* ── 오로라 블롭 ── */
@keyframes auroraFloat1 {
    0%,100% { transform: translate(0,0) scale(1); opacity:0.13; }
    33%      { transform: translate(-40px,-30px) scale(1.08); opacity:0.18; }
    66%      { transform: translate(30px,20px) scale(0.94); opacity:0.1; }
}
@keyframes auroraFloat2 {
    0%,100% { transform: translate(0,0) scale(1); opacity:0.1; }
    33%      { transform: translate(50px,40px) scale(1.06); opacity:0.16; }
    66%      { transform: translate(-20px,-30px) scale(0.92); opacity:0.08; }
}
@keyframes auroraFloat3 {
    0%,100% { transform: translate(0,0) scale(1); opacity:0.22; }
    50%      { transform: translate(-20px,40px) scale(1.05); opacity:0.22; }
}
.aurora-bg {
    position: fixed; inset: 0;
    pointer-events: none; z-index: 0; overflow: hidden;
}
.aurora-blob {
    position: absolute; border-radius: 50%;
    filter: blur(100px);
}
.aurora-1 {
    width: 700px; height: 700px;
    background: radial-gradient(circle, #5b21b6 0%, #7c3aed 40%, transparent 70%);
    top: -250px; left: -150px;
    animation: auroraFloat1 18s ease-in-out infinite;
}
.aurora-2 {
    width: 550px; height: 550px;
    background: radial-gradient(circle, #0e7490 0%, #0891b2 40%, transparent 70%);
    bottom: -150px; right: -100px;
    animation: auroraFloat2 22s ease-in-out infinite;
}
.aurora-3 {
    width: 560px; height: 560px;
    background: radial-gradient(circle, #dc2626 0%, #ef4444 30%, #b91c1c 55%, transparent 75%);
    top: 30%; left: 30%;
    opacity: 0.22;
}

/* ── 사이드바 배경 ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07071e 0%, #0c0b1f 60%, #090818 100%) !important;
    border-right: 1px solid rgba(139,92,246,0.2) !important;
}
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stSidebar"] * { color: white !important; }

/* 사이드바 최상단 오로라 라인 */
[data-testid="stSidebar"]::before {
    content: '';
    display: block;
    height: 3px;
    background: linear-gradient(90deg, #7C3AED, #DC2626, #0891B2, #DC2626, #7C3AED);
    background-size: 300% 100%;
    animation: raceStripe 4s linear infinite;
}
@keyframes raceStripe {
    0%   { background-position: 0% 50%; }
    100% { background-position: 300% 50%; }
}

/* 사이드바 버튼 */
div.stButton > button {
    background: transparent !important;
    color: rgba(255,255,255,0.7) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    width: 100%;
    text-align: left;
    padding: 12px 16px;
    font-size: 0.95rem;
    font-family: 'Noto Sans KR', sans-serif;
    transition: all 0.25s ease;
    letter-spacing: 0.3px;
}
div.stButton > button:hover {
    background: rgba(139,92,246,0.12) !important;
    border-color: rgba(139,92,246,0.4) !important;
    color: white !important;
    transform: translateX(4px);
}

/* 사이드바 서브헤더 */
[data-testid="stSidebar"] h3 {
    font-size: 0.7rem !important;
    letter-spacing: 3px !important;
    text-transform: uppercase;
    color: rgba(167,139,250,0.85) !important;
    font-weight: 700 !important;
    margin-bottom: 6px !important;
}

/* 사이드바 구분선 */
[data-testid="stSidebar"] hr {
    border-color: rgba(139,92,246,0.08) !important;
    margin: 10px 0 !important;
}

/* 전체 selectbox */
div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div > div {
    background-color: #13103a !important;
    border: 1px solid rgba(139,92,246,0.18) !important;
    border-radius: 8px !important;
    transition: border-color 0.2s;
}
div[data-baseweb="select"] > div:hover {
    border-color: rgba(139,92,246,0.5) !important;
}
div[data-baseweb="select"] * { color: white !important; }
div[data-baseweb="select"] svg { fill: rgba(255,255,255,0.6) !important; }

/* 본문 폰트 */
section[data-testid="stMain"] p,
section[data-testid="stMain"] span,
section[data-testid="stMain"] label,
section[data-testid="stMain"] td,
section[data-testid="stMain"] th {
    font-size: 1.05rem !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}

/* 전체 앱 다크 배경 (몽환적 인디고) */
[data-testid="stAppViewContainer"],
section[data-testid="stMain"] {
    background: #06060f !important;
}

/* 상단 바 */
[data-testid="stHeader"] {
    background: #06060f !important;
    border-bottom: 1px solid rgba(139,92,246,0.08) !important;
}
[data-testid="stHeader"] * { color: rgba(255,255,255,0.5) !important; }
[data-testid="stToolbar"] { background: #06060f !important; }
.stAppDeployButton { filter: invert(0.8); }

/* 본문 텍스트 다크모드 보정 */
section[data-testid="stMain"] h2,
section[data-testid="stMain"] h3 {
    color: rgba(255,255,255,0.9) !important;
}
section[data-testid="stMain"] p,
section[data-testid="stMain"] label {
    color: rgba(255,255,255,0.75) !important;
}

/* 서브헤더 퍼플 강조선 */
section[data-testid="stMain"] h2 {
    border-left: 3px solid #7C3AED !important;
    padding-left: 12px !important;
}

/* 구분선 다크 */
hr { border-color: rgba(139,92,246,0.1) !important; }

/* 라디오 버튼 */
[data-testid="stRadio"] label { color: rgba(255,255,255,0.8) !important; }

/* 멀티셀렉트 다크 */
[data-baseweb="tag"] {
    background: rgba(124,58,237,0.18) !important;
    border-color: rgba(124,58,237,0.4) !important;
}
[data-baseweb="tag"] span { color: white !important; }

/* 데이터프레임 다크 */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(139,92,246,0.12) !important;
    border-radius: 10px !important;
}

/* info 박스 다크 */
[data-testid="stAlertContainer"] {
    background: rgba(139,92,246,0.06) !important;
    border-color: rgba(139,92,246,0.18) !important;
    color: rgba(255,255,255,0.6) !important;
}
</style>
"""

AURORA_BG = """
<div class="aurora-bg">
  <div class="aurora-blob aurora-1"></div>
  <div class="aurora-blob aurora-2"></div>
  <div class="aurora-blob aurora-3"></div>
</div>
"""

BRAND_MENUS  = ["선택", "연도별 분석", "월별 분석", "TOP10 분석"]
GENDER_MENUS = ["선택", "브랜드 순위", "선호 모델 순위"]
AGE_MENUS    = ["선택", "브랜드 순위", "선호 모델 순위"]
FAQ_MENUS    = ["선택", "FAQ 검색"]

BRAND_PAGES  = {
    "연도별 분석": "pages/brand_annual.py",
    "월별 분석":   "pages/brand_monthly.py",
    "TOP10 분석":  "pages/brand_top10.py",
}
GENDER_PAGES = {
    "브랜드 순위":    "pages/gender_brand.py",
    "선호 모델 순위": "pages/gender_model.py",
}
AGE_PAGES = {
    "브랜드 순위":    "pages/age_brand.py",
    "선호 모델 순위": "pages/age_model.py",
}
FAQ_PAGES = {
    "FAQ 검색": "pages/faq.py",
}

SIDEBAR_HEADER = """
<div style="padding: 20px 0 8px 0; text-align:center;">
  <div style="font-family:'Rajdhani',sans-serif; font-size:1.6rem; font-weight:700;
              letter-spacing:4px; color:white; line-height:1;">
    🏎 AUTO<span style="color:#DC2626;">STATS</span>
  </div>
  <div style="font-size:0.65rem; color:rgba(255,255,255,0.35); letter-spacing:3px;
              text-transform:uppercase; margin-top:4px;">
    국내 자동차 판매 분석
  </div>
</div>
"""


def render_sidebar(active_section: str = "", active_menu: str = "선택"):
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)
    st.markdown(AURORA_BG, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(SIDEBAR_HEADER, unsafe_allow_html=True)
        st.markdown("---")

        if st.button("🏠 HOME "):
            st.switch_page("app.py")

        st.markdown("---")

        # ── 브랜드별 ───────────────────────────────────────────
        st.subheader("📊  브랜드별")
        b_idx = BRAND_MENUS.index(active_menu) if active_section == "brand" and active_menu in BRAND_MENUS else 0
        brand_sel = st.selectbox("", BRAND_MENUS, index=b_idx, key="sb_brand", label_visibility="collapsed")
        if brand_sel != "선택" and (active_section != "brand" or brand_sel != active_menu):
            st.switch_page(BRAND_PAGES[brand_sel])

        st.markdown("---")

        # ── 성별 ───────────────────────────────────────────────
        st.subheader("👥  성별")
        g_idx = GENDER_MENUS.index(active_menu) if active_section == "gender" and active_menu in GENDER_MENUS else 0
        gender_sel = st.selectbox("", GENDER_MENUS, index=g_idx, key="sb_gender", label_visibility="collapsed")
        if gender_sel != "선택" and (active_section != "gender" or gender_sel != active_menu):
            st.switch_page(GENDER_PAGES[gender_sel])

        st.markdown("---")

        # ── 연령별 ─────────────────────────────────────────────
        st.subheader("🎂  연령별")
        a_idx = AGE_MENUS.index(active_menu) if active_section == "age" and active_menu in AGE_MENUS else 0
        age_sel = st.selectbox("", AGE_MENUS, index=a_idx, key="sb_age", label_visibility="collapsed")
        if age_sel != "선택" and (active_section != "age" or age_sel != active_menu):
            st.switch_page(AGE_PAGES[age_sel])

        st.markdown("---")

        # ── FAQ ────────────────────────────────────────────────
        st.subheader("❓  FAQ")
        f_idx = FAQ_MENUS.index(active_menu) if active_section == "faq" and active_menu in FAQ_MENUS else 0
        faq_sel = st.selectbox("", FAQ_MENUS, index=f_idx, key="sb_faq", label_visibility="collapsed")
        if faq_sel != "선택" and (active_section != "faq" or faq_sel != active_menu):
            st.switch_page(FAQ_PAGES[faq_sel])

        # 하단 버전 표시
        st.markdown("""
        <div style="position:fixed; bottom:20px; left:0; width:230px;
                    text-align:center; color:rgba(255,255,255,0.15);
                    font-size:0.65rem; letter-spacing:1px;">
            AUTOSTATS v1.0 · SKN33-5Team
        </div>
        """, unsafe_allow_html=True)
