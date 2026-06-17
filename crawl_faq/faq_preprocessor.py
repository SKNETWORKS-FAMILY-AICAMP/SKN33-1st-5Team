import re
import pandas as pd


def clean_text(text):
    """공통 텍스트 정제 함수"""
    if pd.isna(text) or text == "":
        return ""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text


def clean_hyundai(df):
    """현대 FAQ 전처리"""
    df = df.copy()

    # 질문 앞 [차량구매]\n 같은 카테고리 prefix 제거
    df['질문'] = df['질문'].str.replace(r'^\[.*?\]\n', '', regex=True).str.strip()

    def clean_answer(text):
        if pd.isna(text) or text == "":
            return ""
        text = re.sub(r'.{0,15}바로가기\s*[▶>]?', '', text)
        text = re.sub(r'자세히\s*보기\s*[▶>]?', '', text)
        text = re.sub(r'자세한\s*사항은.*?확인해\s*주세요\.?', '', text)
        text = re.sub(r'^▶\s*', '', text, flags=re.MULTILINE)
        text = clean_text(text)
        return text

    df['답변'] = df['답변'].apply(clean_answer)
    df = df[df['답변'].str.strip() != ""].reset_index(drop=True)

    print(f"  [현대] 전처리 완료: {len(df)}개")
    return df


def clean_kia(df):
    """기아 FAQ 전처리"""
    df = df.copy()

    def clean_answer(text):
        if pd.isna(text) or text == "":
            return ""
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if len(stripped) <= 15 and not any(c in stripped for c in ['다', '요', '니', '.', '?', '!']):
                continue
            cleaned_lines.append(line)
        text = '\n'.join(cleaned_lines)
        text = clean_text(text)
        return text

    df['답변'] = df['답변'].apply(clean_answer)
    df = df[df['답변'].str.strip() != ""].reset_index(drop=True)

    print(f"  [기아] 전처리 완료: {len(df)}개")
    return df


def clean_tesla(df):
    """테슬라 FAQ 전처리 - 중복 내용 제거"""
    df = df.copy()

    def remove_duplicate_content(text):
        if pd.isna(text) or text == "":
            return ""
        sentences = re.split(r'(?<=[다요죠임])\.\s+|(?<=[?!])\s+', text)
        seen = set()
        unique_sentences = []
        for s in sentences:
            s_clean = s.strip()
            if s_clean and s_clean not in seen:
                seen.add(s_clean)
                unique_sentences.append(s_clean)
        text = ' '.join(unique_sentences)
        text = re.sub(r'위로 가기.*$', '', text, flags=re.DOTALL)
        text = re.sub(r'자주 묻는 질문\s*$', '', text)
        text = re.sub(r'이용 약관\s*$', '', text)
        text = re.sub(r'로열티 혜택 획득 방법.*$', '', text, flags=re.DOTALL)
        text = clean_text(text)
        return text

    df['답변'] = df['답변'].apply(remove_duplicate_content)
    df = df[df['답변'].str.strip() != ""].reset_index(drop=True)

    print(f"  [테슬라] 전처리 완료: {len(df)}개")
    return df