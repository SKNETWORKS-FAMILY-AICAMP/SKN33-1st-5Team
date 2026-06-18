from pathlib import Path
import csv
import os

import mysql.connector

BASE_DIR = Path(__file__).resolve().parent
FAQ_CSV  = BASE_DIR / "../faq_data/processed/all_faq_clean.csv"

# Brand 테이블의 brand_id와 일치해야 합니다
BRAND_ID_BY_NAME = {
    "기아":   1,
    "현대":   2,
    "테슬라": 3,
}

DB_CONFIG = {
    "host":        os.getenv("MYSQL_HOST",     "localhost"),
    "port":        int(os.getenv("MYSQL_PORT", "3306")),
    "user":        os.getenv("MYSQL_USER",     "skn_ai"),
    "password":    os.getenv("MYSQL_PASSWORD", "1234"),
    "database":    os.getenv("MYSQL_DATABASE", "cardb"),
    "charset":     "utf8mb4",
    "use_unicode": True,
}


def read_csv_rows(file_path):
    with file_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [
            {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            for row in reader
        ]


def get_faq_columns(cursor):
    cursor.execute("SHOW COLUMNS FROM FAQ")
    cols = [row[0].lower() for row in cursor.fetchall()]
    print(f"  FAQ 테이블 실제 컬럼: {cols}")
    return cols


def insert_faq(cursor, rows):
    cols = get_faq_columns(cursor)

    has_brand_id = "brand_id" in cols
    has_category = "category" in cols
    has_question = "question" in cols
    has_answer   = "answer"   in cols

    if not has_question or not has_answer:
        raise RuntimeError(f"question/answer 컬럼을 찾을 수 없습니다. 실제 컬럼: {cols}")

    # INSERT 컬럼 동적 구성
    insert_cols = []
    if has_brand_id:
        insert_cols.append("brand_id")
    if has_category:
        insert_cols.append("category")
    insert_cols += ["question", "answer"]

    col_str      = ", ".join(f"`{c}`" for c in insert_cols)
    placeholders = ", ".join(["%s"] * len(insert_cols))
    sql = f"INSERT INTO FAQ ({col_str}) VALUES ({placeholders})"
    print(f"  사용할 INSERT: INSERT INTO FAQ ({col_str}) VALUES (...)")

    count = 0
    for row in rows:
        brand_name = row.get("브랜드", "").strip()
        category   = (row.get("카테고리") or row.get("대분류") or "기타").strip()
        question   = row.get("질문", "").strip()
        answer     = row.get("답변", "").strip()

        if not question or not answer:
            continue

        values = []
        if has_brand_id:
            values.append(BRAND_ID_BY_NAME.get(brand_name, None))
        if has_category:
            values.append(category or None)
        values += [question, answer]

        cursor.execute(sql, tuple(values))
        count += 1

    return count


def main():
    print("=== FAQ 데이터 삽입 시작 ===")

    rows = read_csv_rows(FAQ_CSV)
    print(f"CSV 읽기 완료: {len(rows)}개 행")

    conn   = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM FAQ")
        print("기존 FAQ 데이터 초기화 완료")

        count = insert_faq(cursor, rows)
        conn.commit()
        print(f"FAQ 삽입 완료: {count}개")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 삽입 중 오류 발생: {e}")
        raise

    finally:
        cursor.close()
        conn.close()

    print("=== FAQ 데이터 삽입 완료 ===")


if __name__ == "__main__":
    main()
