
import streamlit as st
import sys
import os
import re
import html

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)
sys.path.append(os.path.join(root, "database"))

from sidebar_utils import render_sidebar
from query import search_faq, get_faq_columns_debug

st.set_page_config(page_title="FAQ | Domestic Car Sales", layout="wide")

render_sidebar(active_section="faq", active_menu="FAQ 검색")

# ── 페이지 CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
.faq-card {
    background: linear-gradient(145deg, #0e0c22, #131130);
    border: 1px solid rgba(139,92,246,0.15);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 14px;
    position: relative;
}
.faq-card::before {
    content: '';
    position: absolute;
    left: 0; top: 12px; bottom: 12px;
    width: 3px;
    background: linear-gradient(180deg, #7C3AED, #0891B2);
    border-radius: 0 3px 3px 0;
}
.faq-brand-tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
}
.faq-category {
    color: rgba(167,139,250,0.7);
    font-size: 0.72rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.faq-question {
    color: rgba(255,255,255,0.95);
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 10px;
    line-height: 1.5;
}
.faq-answer {
    color: rgba(255,255,255,0.65);
    font-size: 0.92rem;
    line-height: 1.75;
    white-space: pre-wrap;
}
.brand-현대 { background: rgba(8,145,178,0.15); color: #38bdf8; border: 1px solid rgba(8,145,178,0.3); }
.brand-기아  { background: rgba(220,38,38,0.12); color: #f87171; border: 1px solid rgba(220,38,38,0.3); }
.brand-테슬라 { background: rgba(34,197,94,0.1); color: #4ade80; border: 1px solid rgba(34,197,94,0.25); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div style="font-size:3.5rem;font-weight:800;line-height:1.2;color:rgba(255,255,255,0.95);margin-bottom:0.5rem;">❓ FAQ 검색</div>', unsafe_allow_html=True)
st.markdown('<div style="color:rgba(255,255,255,0.45);font-size:1rem;margin-bottom:1.5rem;">현대 · 기아 · 테슬라 관련 자주 묻는 질문을 검색하세요</div>', unsafe_allow_html=True)
st.divider()

# ── 검색 필터 ────────────────────────────────────────────────────
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    keyword = st.text_input(
        "키워드 검색",
        placeholder="예: 보증, 충전, 할부, 리콜, 보험...",
        label_visibility="collapsed",
    )

with col2:
    brand_filter = st.selectbox(
        "브랜드",
        ["전체", "현대", "기아", "테슬라"],
        label_visibility="collapsed",
    )

with col3:
    search_btn = st.button("🔍  검색", use_container_width=True)

st.divider()

# ── 검색 실행 ────────────────────────────────────────────────────
# ── DB 컬럼 확인 (디버그) ─────────────────────────────────────
# with st.expander("🔧 DB 컬럼 확인 (문제 발생 시 펼쳐보세요)", expanded=False):
#     try:
#         schema = get_faq_columns_debug()
#         st.json(schema)
#     except Exception as ex:
#         st.error(f"FAQ 테이블 접근 실패: {ex}")

if not keyword and not search_btn:
    st.markdown("""
    <div style="text-align:center; padding: 60px 0; color:rgba(255,255,255,0.2);">
        <div style="font-size:4rem; margin-bottom:16px;">🔍</div>
        <div style="font-size:1.1rem; letter-spacing:1px;">키워드를 입력하고 검색하세요</div>
        <div style="font-size:0.85rem; margin-top:8px; color:rgba(255,255,255,0.12);">
            차량 구매 · 보증 · 충전 · 서비스 · 보험 등 다양한 주제를 검색할 수 있습니다
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not keyword:
    st.warning("검색할 키워드를 입력해주세요.")
    st.stop()

try:
    results = search_faq(keyword, brand_name=brand_filter, limit=30)
except Exception as e:
    st.error(f"DB 오류: {e}")
    st.stop()

# ── 결과 표시 ────────────────────────────────────────────────────
if not results:
    st.markdown(f"""
    <div style="text-align:center; padding:60px 0; color:rgba(255,255,255,0.25);">
        <div style="font-size:3rem; margin-bottom:12px;">😶</div>
        <div style="font-size:1rem;">
            <b style="color:rgba(167,139,250,0.7)">"{keyword}"</b> 에 해당하는 FAQ가 없습니다
        </div>
        <div style="font-size:0.85rem; margin-top:8px; color:rgba(255,255,255,0.15);">
            다른 키워드로 다시 검색해보세요
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

total = len(results)
brand_label = f" · {brand_filter}" if brand_filter != "전체" else ""
st.markdown(
    f'<div style="color:rgba(255,255,255,0.4);font-size:0.85rem;margin-bottom:16px;">'
    f'<b style="color:rgba(167,139,250,0.8)">"{keyword}"</b>{brand_label} — {total}개 결과</div>',
    unsafe_allow_html=True
)

def highlight_keyword(text: str, kw: str) -> str:
    """텍스트 내 키워드를 노란색 하이라이트로 감쌈 (HTML 이스케이프 후 처리)"""
    if not kw or not text:
        return html.escape(text)
    escaped_text = html.escape(text)
    escaped_kw   = re.escape(html.escape(kw))
    return re.sub(
        f"({escaped_kw})",
        r'<mark style="background:#FBBF24;color:#1a1a1a;border-radius:3px;'
        r'padding:0 2px;font-weight:700;">\1</mark>',
        escaped_text,
        flags=re.IGNORECASE,
    )

for row in results:
    brand = row.get("brand_name") or "공통"
    cat   = row.get("category") or ""
    q     = highlight_keyword(row.get("question", ""), keyword)
    a     = highlight_keyword(row.get("answer", ""), keyword)

    brand_cls = f"brand-{brand}" if brand in ["현대", "기아", "테슬라"] else ""

    st.markdown(f"""
    <div class="faq-card">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
            <span class="faq-brand-tag {brand_cls}">{html.escape(brand)}</span>
            {"<span class='faq-category'>· " + html.escape(cat) + "</span>" if cat else ""}
        </div>
        <div class="faq-question">Q. {q}</div>
        <div class="faq-answer">{a}</div>
    </div>
    """, unsafe_allow_html=True)
