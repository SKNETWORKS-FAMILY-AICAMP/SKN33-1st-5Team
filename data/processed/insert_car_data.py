from pathlib import Path
import csv
import os

import mysql.connector


BASE_DIR = Path(__file__).resolve().parent

DANAWA_MODEL_CSV = BASE_DIR / "danawa_model_clean.csv"
NICE_AGE_CSV = BASE_DIR / "nice_age_clean.csv"
NICE_GENDER_CSV = BASE_DIR / "nice_gender_clean.csv"

# 아래 3개 브랜드는 지정된 brand_id를 반드시 사용합니다.
FIXED_BRAND_ID_BY_NAME = {
    "기아": 1,
    "현대": 2,
    "테슬라": 3,
}

ROMAN_NUMBER_REPLACEMENTS = (
    ("Ⅲ", "3"),
    ("III", "3"),
    ("Ⅱ", "2"),
    ("II", "2"),
)

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "skn_ai"),
    "password": os.getenv("MYSQL_PASSWORD", "1234"),
    "database": os.getenv("MYSQL_DATABASE", "cardb"),
    "charset": "utf8mb4",
    "use_unicode": True,
}


def read_csv_rows(file_path):
    """UTF-8 BOM이 있는 CSV도 안전하게 읽고, 컬럼명/값의 공백을 정리합니다."""
    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        return [
            {
                (key or "").strip(): (value or "").strip()
                for key, value in row.items()
            }
            for row in reader
        ]


def to_int(value):
    """'1,234'처럼 쉼표가 들어간 숫자도 int로 변환합니다."""
    return int(str(value).replace(",", "").strip())


def normalize_model_name(brand_name, model_name):
    """
    파일마다 모델명 표기가 다르므로 비교 전에 Car_Model 기준으로 통일합니다.

    예)
    nice_age_clean.csv / nice_gender_clean.csv: 모델 3
    danawa_model_clean.csv / Car_Model: Model 3

    nice_age_clean.csv: 포터II, 더 뉴봉고Ⅲ화물
    danawa_model_clean.csv / Car_Model: 포터2, 봉고 3
    """
    model_name = (model_name or "").strip()

    if brand_name == "테슬라" and model_name.startswith("모델 "):
        model_name = model_name.replace("모델 ", "Model ", 1)

    for roman_number, arabic_number in ROMAN_NUMBER_REPLACEMENTS:
        model_name = model_name.replace(roman_number, arabic_number)

    if brand_name == "기아" and model_name.startswith("더 뉴봉고3"):
        return "봉고 3"

    return model_name


def get_unique_brand_names_from_nice_age():
    """nice_age_clean.csv에 등장한 브랜드명을 중복 없이 읽습니다."""
    brand_names = []
    seen = set()

    for row in read_csv_rows(NICE_AGE_CSV):
        brand_name = row["브랜드명"]

        if brand_name not in seen:
            brand_names.append(brand_name)
            seen.add(brand_name)

    return brand_names


def insert_brands(cursor):
    """
    nice_age_clean.csv의 브랜드명을 Brand 테이블에 넣습니다.

    단, 기아/현대/테슬라는 지정된 brand_id를 반드시 사용합니다.
    """
    cursor.execute("SELECT brand_id, TRIM(brand_name) FROM Brand")
    rows = cursor.fetchall()
    db_brand_id_by_name = {brand_name: brand_id for brand_id, brand_name in rows}
    db_brand_name_by_id = {brand_id: brand_name for brand_id, brand_name in rows}

    inserted = 0

    for brand_name, expected_brand_id in FIXED_BRAND_ID_BY_NAME.items():
        actual_brand_id = db_brand_id_by_name.get(brand_name)

        if actual_brand_id == expected_brand_id:
            continue

        if actual_brand_id is None:
            existing_name = db_brand_name_by_id.get(expected_brand_id)

            if existing_name is not None and existing_name != brand_name:
                raise ValueError(
                    f"Brand 테이블 확인 필요: brand_id={expected_brand_id}에는 "
                    f"{brand_name}이 들어가야 하는데 현재 값은 {existing_name}입니다."
                )

            cursor.execute(
                """
                INSERT INTO Brand (brand_id, brand_name)
                VALUES (%s, %s)
                """,
                (expected_brand_id, brand_name),
            )
            db_brand_id_by_name[brand_name] = expected_brand_id
            db_brand_name_by_id[expected_brand_id] = brand_name
            inserted += 1
            continue

        if actual_brand_id != expected_brand_id:
            raise ValueError(
                f"Brand 테이블 확인 필요: {brand_name}의 brand_id가 "
                f"{expected_brand_id}이어야 하는데 현재 값은 {actual_brand_id}입니다."
            )

    next_brand_id = max([0, *db_brand_name_by_id.keys()]) + 1

    for brand_name in get_unique_brand_names_from_nice_age():
        if brand_name in db_brand_id_by_name:
            continue

        while next_brand_id in db_brand_name_by_id:
            next_brand_id += 1

        cursor.execute(
            """
            INSERT INTO Brand (brand_id, brand_name)
            VALUES (%s, %s)
            """,
            (next_brand_id, brand_name),
        )
        db_brand_id_by_name[brand_name] = next_brand_id
        db_brand_name_by_id[next_brand_id] = brand_name
        next_brand_id += 1
        inserted += 1

    print("[Brand]", f"inserted={inserted}")

    return db_brand_id_by_name


def get_next_id(cursor, table_name, pk_column):
    cursor.execute(f"SELECT COALESCE(MAX({pk_column}), 0) + 1 FROM {table_name}")
    return cursor.fetchone()[0]


def load_existing_car_models(cursor):
    cursor.execute("SELECT model_id, brand_id, model_name FROM Car_Model")

    model_id_by_key = {}
    model_names = set()

    for model_id, brand_id, model_name in cursor.fetchall():
        model_id_by_key[(brand_id, model_name)] = model_id
        model_names.add(model_name)

    return model_id_by_key, model_names


def insert_car_models(cursor, brand_id_by_name):
    """
    danawa_model_clean.csv에서 브랜드/모델만 추출해 Car_Model에 넣습니다.

    - Brand에 없는 브랜드는 제외합니다.
    - 같은 모델명은 한 번만 넣습니다.
    - model_id는 테이블의 현재 MAX(model_id) 다음 번호부터 직접 부여합니다.
    """
    rows = read_csv_rows(DANAWA_MODEL_CSV)
    model_id_by_key, model_names = load_existing_car_models(cursor)
    next_model_id = get_next_id(cursor, "Car_Model", "model_id")

    inserted = 0
    skipped_unknown_brand = 0
    skipped_duplicate_model = 0

    for row in rows:
        brand_name = row["브랜드"]
        brand_id = brand_id_by_name.get(brand_name)

        if brand_id is None:
            skipped_unknown_brand += 1
            continue

        model_name = normalize_model_name(brand_name, row["모델"])

        if model_name in model_names:
            skipped_duplicate_model += 1
            continue

        cursor.execute(
            """
            INSERT INTO Car_Model (model_id, brand_id, model_name)
            VALUES (%s, %s, %s)
            """,
            (next_model_id, brand_id, model_name),
        )

        model_id_by_key[(brand_id, model_name)] = next_model_id
        model_names.add(model_name)
        next_model_id += 1
        inserted += 1

    print(
        "[Car_Model]",
        f"inserted={inserted}",
        f"skipped_duplicate_model={skipped_duplicate_model}",
        f"skipped_unknown_brand={skipped_unknown_brand}",
    )

    return model_id_by_key


def insert_monthly_registrations(cursor, model_id_by_key, brand_id_by_name):
    """
    danawa_model_clean.csv의 월별 판매량을 Monthly_Registration에 넣습니다.

    CSV의 '순위'는 Monthly_Registration 테이블에 대응 컬럼이 없으므로 저장하지 않습니다.
    """
    rows = read_csv_rows(DANAWA_MODEL_CSV)
    next_reg_id = get_next_id(cursor, "Monthly_Registration", "reg_id")

    cursor.execute(
        """
        SELECT model_id, year, month, monthly_reg_count
        FROM Monthly_Registration
        """
    )
    existing_rows = set(cursor.fetchall())

    inserted = 0
    skipped_no_model = 0
    skipped_existing = 0

    for row in rows:
        brand_name = row["브랜드"]
        brand_id = brand_id_by_name.get(brand_name)

        if brand_id is None:
            skipped_no_model += 1
            continue

        model_name = normalize_model_name(brand_name, row["모델"])
        model_id = model_id_by_key.get((brand_id, model_name))

        if model_id is None:
            skipped_no_model += 1
            continue

        year = to_int(row["년"])
        month = to_int(row["월"])
        monthly_reg_count = to_int(row["판매량"])
        natural_row = (model_id, year, month, monthly_reg_count)

        if natural_row in existing_rows:
            skipped_existing += 1
            continue

        cursor.execute(
            """
            INSERT INTO Monthly_Registration
                (reg_id, model_id, year, month, monthly_reg_count)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (next_reg_id, model_id, year, month, monthly_reg_count),
        )

        existing_rows.add(natural_row)
        next_reg_id += 1
        inserted += 1

    print(
        "[Monthly_Registration]",
        f"inserted={inserted}",
        f"skipped_existing={skipped_existing}",
        f"skipped_no_model={skipped_no_model}",
    )


def insert_age_registrations(cursor, model_id_by_key, brand_id_by_name):
    """
    nice_age_clean.csv에서 Car_Model과 모델명이 일치하는 '모델' 타입 데이터만 넣습니다.

    Age_Registration.age_reg_id는 AUTO_INCREMENT이므로 직접 넣지 않습니다.
    """
    rows = read_csv_rows(NICE_AGE_CSV)

    cursor.execute(
        """
        SELECT brand_id, model_id, age_group, gubun, ranking, age_reg_count
        FROM Age_Registration
        """
    )
    existing_rows = set(cursor.fetchall())

    inserted = 0
    skipped_unsupported_type = 0
    skipped_unknown_brand = 0
    skipped_no_model = 0
    skipped_existing = 0

    for row in rows:
        raw_model_name = row["모델명"]
        gubun = row["타입"]
        brand_name = row["브랜드명"]
        brand_id = brand_id_by_name.get(brand_name)

        if brand_id is None:
            skipped_unknown_brand += 1
            continue

        if raw_model_name == "-":
            gubun = "브랜드"
            model_id = None
        elif gubun == "모델":
            model_name = normalize_model_name(brand_name, raw_model_name)
            model_id = model_id_by_key.get((brand_id, model_name))

            if model_id is None:
                skipped_no_model += 1
                continue
        else:
            skipped_unsupported_type += 1
            continue

        age_group = row["구분"]
        ranking = to_int(row["순위"])
        age_reg_count = to_int(row["등록량"])
        natural_row = (brand_id, model_id, age_group, gubun, ranking, age_reg_count)

        if natural_row in existing_rows:
            skipped_existing += 1
            continue

        cursor.execute(
            """
            INSERT INTO Age_Registration
                (brand_id, model_id, age_group, gubun, ranking, age_reg_count)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            natural_row,
        )

        existing_rows.add(natural_row)
        inserted += 1

    print(
        "[Age_Registration]",
        f"inserted={inserted}",
        f"skipped_existing={skipped_existing}",
        f"skipped_unsupported_type={skipped_unsupported_type}",
        f"skipped_unknown_brand={skipped_unknown_brand}",
        f"skipped_no_model={skipped_no_model}",
    )


def insert_gender_registrations(cursor, model_id_by_key, brand_id_by_name):
    """
    nice_gender_clean.csv에서 Car_Model과 모델명이 일치하는 '모델' 타입 데이터만 넣습니다.

    Gender_Registration.gender_reg_id는 AUTO_INCREMENT가 아니므로 직접 번호를 부여합니다.
    """
    rows = read_csv_rows(NICE_GENDER_CSV)
    next_gender_reg_id = get_next_id(
        cursor,
        "Gender_Registration",
        "gender_reg_id",
    )

    cursor.execute(
        """
        SELECT brand_id, model_id, gender, gubun, ranking, gender_reg_count
        FROM Gender_Registration
        """
    )
    existing_rows = set(cursor.fetchall())

    inserted = 0
    skipped_unsupported_type = 0
    skipped_unknown_brand = 0
    skipped_no_model = 0
    skipped_existing = 0

    for row in rows:
        raw_model_name = row["모델명"]
        gubun = row["타입"]
        brand_name = row["브랜드명"]
        brand_id = brand_id_by_name.get(brand_name)

        if brand_id is None:
            skipped_unknown_brand += 1
            continue

        if raw_model_name == "-":
            gubun = "브랜드"
            model_id = None
        elif gubun == "모델":
            model_name = normalize_model_name(brand_name, raw_model_name)
            model_id = model_id_by_key.get((brand_id, model_name))

            if model_id is None:
                skipped_no_model += 1
                continue
        else:
            skipped_unsupported_type += 1
            continue

        gender = row["구분"]
        ranking = to_int(row["순위"])
        gender_reg_count = to_int(row["등록량"])
        natural_row = (
            brand_id,
            model_id,
            gender,
            gubun,
            ranking,
            gender_reg_count,
        )

        if natural_row in existing_rows:
            skipped_existing += 1
            continue

        cursor.execute(
            """
            INSERT INTO Gender_Registration
                (
                    gender_reg_id,
                    brand_id,
                    model_id,
                    gender,
                    gubun,
                    ranking,
                    gender_reg_count
                )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                next_gender_reg_id,
                brand_id,
                model_id,
                gender,
                gubun,
                ranking,
                gender_reg_count,
            ),
        )

        existing_rows.add(natural_row)
        next_gender_reg_id += 1
        inserted += 1

    print(
        "[Gender_Registration]",
        f"inserted={inserted}",
        f"skipped_existing={skipped_existing}",
        f"skipped_unsupported_type={skipped_unsupported_type}",
        f"skipped_unknown_brand={skipped_unknown_brand}",
        f"skipped_no_model={skipped_no_model}",
    )


def main():
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = None

    try:
        cursor = connection.cursor()

        brand_id_by_name = insert_brands(cursor)

        model_id_by_key = insert_car_models(cursor, brand_id_by_name)
        insert_monthly_registrations(cursor, model_id_by_key, brand_id_by_name)
        insert_age_registrations(cursor, model_id_by_key, brand_id_by_name)
        insert_gender_registrations(cursor, model_id_by_key, brand_id_by_name)

        connection.commit()
        print("CSV 데이터 삽입이 완료되었습니다.")

    except Exception:
        connection.rollback()
        print("오류가 발생하여 작업을 롤백했습니다.")
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
