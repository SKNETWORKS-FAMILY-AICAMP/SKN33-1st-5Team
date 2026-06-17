from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time


def setup_driver():
    options = webdriver.ChromeOptions()
    # 💡 [핵심 1] 브라우저가 조그맣게 켜져서 모바일 화면으로 찌그러지는 것을 방지!
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def get_danawa_brand_sales(start_year, end_year):
    """1. 다나와 자동차: 브랜드별 총 판매량"""
    driver = setup_driver()
    all_data = []

    target_months = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if year == 2026 and month > 5: break
            target_months.append(f"{year}-{month:02d}-00")

    for month in target_months:
        url = f"https://auto.danawa.com/auto/?Work=record&Tab=Grand&Month={month}&MonthTo="
        driver.get(url)
        time.sleep(2)
        print(f"다나와 브랜드 전체 [{month}] 수집 중...")

        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "table.recordTable tbody tr")
            for row in rows:
                try:
                    brand = row.find_element(By.CSS_SELECTOR, ".title").text
                    sales = row.find_element(By.CSS_SELECTOR, ".num").text
                    all_data.append({"연월": month, "브랜드": brand, "판매량": sales})
                except Exception:
                    continue  # 데이터가 없는 빈 줄이면 조용히 패스!
        except Exception as e:
            pass

    driver.quit()
    return pd.DataFrame(all_data)


def get_danawa_model_top10(start_year, end_year):
    """2. 다나와 자동차: 모델별 TOP 10 (유령 줄 방어 추가)"""
    driver = setup_driver()
    all_data = []

    target_months = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if year == 2026 and month > 5: break
            target_months.append(f"{year}-{month:02d}-00")

    brand_codes = {"현대": "303", "기아": "307", "테슬라": "611"}

    for month in target_months:
        for brand_name, brand_code in brand_codes.items():
            url = f"https://auto.danawa.com/auto/?Work=record&Tab=Model&Brand={brand_code}&Month={month}&MonthTo="
            driver.get(url)
            time.sleep(2)
            print(f"다나와 모델별 [{month} - {brand_name}] 수집 중...")

            try:
                # sub_model은 제외하고 줄을 가져옵니다.
                rows = driver.find_elements(By.CSS_SELECTOR, "table.recordTable.model tbody tr:not(.sub_model)")
                valid_rank = 1

                for row in rows:
                    if valid_rank > 10: break  # 딱 10위까지만!
                    try:
                        # .strip()을 붙여서 쓸데없는 띄어쓰기를 날려버립니다.
                        model_name = row.find_element(By.CSS_SELECTOR, ".title").text.strip()
                        sales = row.find_element(By.CSS_SELECTOR, ".num").text.strip()

                        # 💡 [핵심 방어막] 글자가 없는 텅 빈 유령 줄은 순위에서 아예 제외하고 무시합니다!
                        if not model_name or not sales:
                            continue

                        # 진짜 글자가 있을 때만 데이터를 저장하고 순위를 1등 올립니다.
                        all_data.append(
                            {"연월": month, "브랜드": brand_name, "순위": valid_rank, "모델": model_name, "판매량": sales})
                        valid_rank += 1
                    except Exception:
                        continue
            except Exception as e:
                print(f"다나와 모델별 [{month} - {brand_name}] 에러 무시됨: {e}")

    driver.quit()
    return pd.DataFrame(all_data)


def get_nice_demographics():
    print("▶ [나이스블루마크] 연령/성별 TOP 30 수집 시작...")
    driver = setup_driver()
    all_data = []
    base_url = "https://www.nicebluemark.co.kr/stat/statisticsCenter"

    def extract_tabs(target_type):
        data = []
        table_id = "#modelTable" if target_type == "모델" else "#brandTable"

        # 💡 [핵심] 화면에 여러 탭이 숨겨져 있을 수 있으므로, '현재 눈에 보이는(is_displayed)' 탭만 찾아 누릅니다.
        def safe_click(selector):
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                if elem.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", elem)
                    time.sleep(2)  # 데이터가 바뀔 때까지 대기
                    return
            print(f"  [!] {selector} 버튼을 화면에서 찾을 수 없습니다.")

        # --- 1. 성별 탭 순회 ---
        try:
            safe_click("li.tab-bar__item[data-name='gender']")
        except Exception as e:
            print(f"  [!] 성별 메인 탭 클릭 에러: {e}")

        gender_values = {"M": "남성", "F": "여성"}
        for val, label in gender_values.items():
            safe_click(f"li.c-chip__item[data-value='{val}']")

            rows = driver.find_elements(By.CSS_SELECTOR, f"{table_id} tbody tr")
            print(f"  -> [{target_type} - 성별({label})] 표에서 찾은 줄 개수: {len(rows)}")

            valid_count = 0
            for row in rows:
                if valid_count >= 30: break

                try:
                    sales = row.find_element(By.CSS_SELECTOR, ".cell--sales").text.strip()
                    rank = str(valid_count + 1)

                    if target_type == "모델":
                        brand = row.find_element(By.CSS_SELECTOR, ".brand").text.strip()
                        model = row.find_element(By.CSS_SELECTOR, ".name").text.strip()
                        data.append(
                            {"분류": "성별", "구분": label, "타입": target_type, "순위": rank, "브랜드명": brand, "모델명": model,
                             "등록량": sales})
                    else:
                        brand = row.find_element(By.CSS_SELECTOR, ".name").text.strip()
                        data.append({"분류": "성별", "구분": label, "타입": target_type, "순위": rank, "브랜드명": brand, "모델명": "-",
                                     "등록량": sales})

                    valid_count += 1
                except Exception:
                    continue

        # --- 2. 연령대 탭 순회 ---
        try:
            safe_click("li.tab-bar__item[data-name='age']")
        except Exception as e:
            print(f"  [!] 연령대 메인 탭 클릭 에러: {e}")

        age_values = {"20": "20대 이하", "30": "30대", "40": "40대", "50": "50대", "60": "60대", "70": "70대 이상"}
        for val, label in age_values.items():
            safe_click(f"li.c-chip__item[data-value='{val}']")

            rows = driver.find_elements(By.CSS_SELECTOR, f"{table_id} tbody tr")
            print(f"  -> [{target_type} - 연령대({label})] 표에서 찾은 줄 개수: {len(rows)}")

            valid_count = 0
            for row in rows:
                if valid_count >= 30: break

                try:
                    sales = row.find_element(By.CSS_SELECTOR, ".cell--sales").text.strip()
                    rank = str(valid_count + 1)

                    if target_type == "모델":
                        brand = row.find_element(By.CSS_SELECTOR, ".brand").text.strip()
                        model = row.find_element(By.CSS_SELECTOR, ".name").text.strip()
                        data.append(
                            {"분류": "연령대", "구분": label, "타입": target_type, "순위": rank, "브랜드명": brand, "모델명": model,
                             "등록량": sales})
                    else:
                        brand = row.find_element(By.CSS_SELECTOR, ".name").text.strip()
                        data.append({"분류": "연령대", "구분": label, "타입": target_type, "순위": rank, "브랜드명": brand, "모델명": "-",
                                     "등록량": sales})

                    valid_count += 1
                except Exception:
                    continue

        return data

    # 🏎️ 1. 신차 모델 순위 수집
    print("  [1] 신차 모델 TOP 30 수집 진입 중...")
    try:
        # 요약본 메인 화면으로 먼저 들어갑니다.
        driver.get(base_url)
        time.sleep(3)

        # 💡 [작성자님 분석 적용] "더 많은 모델 보기" 글자가 포함된 버튼을 찾아 무조건 클릭!
        more_model_btn = driver.find_element(By.XPATH, "//*[contains(text(), '더 많은 모델')]")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_model_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", more_model_btn)
        print("    -> '더 많은 모델 보기' 클릭 완료! 상세 페이지로 이동합니다.")
        time.sleep(3)  # 상세 페이지(#newCarModel)로 화면이 완전히 넘어갈 때까지 넉넉히 대기

        all_data.extend(extract_tabs("모델"))
    except Exception as e:
        print(f"  [!] 모델 상세 페이지 진입 실패: {e}")

    # 🚗 2. 신차 브랜드 순위 수집
    print("  [2] 신차 브랜드 TOP 30 수집 진입 중...")
    try:
        # 다시 요약본 메인 화면으로 돌아갑니다.
        driver.get(base_url)
        time.sleep(3)

        # 💡 [작성자님 분석 적용] 이번엔 "더 많은 브랜드 보기" 버튼을 클릭!
        more_brand_btn = driver.find_element(By.XPATH, "//*[contains(text(), '더 많은 브랜드')]")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_brand_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", more_brand_btn)
        print("    -> '더 많은 브랜드 보기' 클릭 완료! 상세 페이지로 이동합니다.")
        time.sleep(3)  # 상세 페이지(#newCarBrand)로 화면이 완전히 넘어갈 때까지 넉넉히 대기

        all_data.extend(extract_tabs("브랜드"))
    except Exception as e:
        print(f"  [!] 브랜드 상세 페이지 진입 실패: {e}")

    driver.quit()
    return pd.DataFrame(all_data)