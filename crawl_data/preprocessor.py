import pandas as pd


def clean_danawa_brand(df):
    """1. 다나와 전체 브랜드 데이터 전처리"""
    if df.empty: return df
    df['브랜드'] = df['브랜드'].astype(str).str.strip()
    df['판매량'] = df['판매량'].astype(str).str.strip()

    target_brands = ['현대', '기아', '테슬라', 'Tesla', 'Hyundai', 'Kia']
    df = df[df['브랜드'].isin(target_brands)]
    df = df[~df['브랜드'].str.contains('합계|총합|기타', na=False)]

    df['판매량'] = df['판매량'].replace(['-', '', 'nan', 'NaN'], '0').fillna('0')
    df['판매량'] = df['판매량'].str.replace(',', '', regex=False).astype(int)
    return df


def clean_danawa_models(df):
    """2. 다나와 모델 TOP 10 데이터 전처리"""
    if df.empty: return df
    df['브랜드'] = df['브랜드'].astype(str).str.strip()
    df['모델'] = df['모델'].astype(str).str.strip()
    df['판매량'] = df['판매량'].astype(str).str.strip()

    df['판매량'] = df['판매량'].replace(['-', '', 'nan', 'NaN'], '0').fillna('0')
    df['판매량'] = df['판매량'].str.replace(',', '', regex=False).astype(int)
    return df


def clean_nice_demographics(df):
    """3. 나이스블루마크 연령/성별 데이터 전처리"""
    if df.empty: return df

    # 💡 [핵심 수정] 새롭게 바뀐 컬럼명들로 리스트 업데이트! (에러 원인 해결)
    cols_to_strip = ['분류', '구분', '타입', '순위', '브랜드명', '모델명', '등록량']
    for col in cols_to_strip:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # 등록량에서 '대' 글자 및 쉼표 제거 후 숫자로 변환
    df['등록량'] = df['등록량'].replace(['-', '', 'nan', 'NaN'], '0').fillna('0')
    df['등록량'] = df['등록량'].str.replace(',', '', regex=False)
    df['등록량'] = df['등록량'].str.replace('대', '', regex=False)
    df['등록량'] = df['등록량'].astype(int)
    return df