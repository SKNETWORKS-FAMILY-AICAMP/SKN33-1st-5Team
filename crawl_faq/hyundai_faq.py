import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_hyundai_faq():
    print("▶ [현대자동차] FAQ 크롤링 시작")

    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)

    hyun_url = "https://www.hyundai.com/kr/ko/e/customer/center/faq"
    driver.get(hyun_url)
    time.sleep(4)

    hyun_question = []
    hyun_answer = []
    hyun_category = []

    tab_buttons = driver.find_elements(By.CSS_SELECTOR, 'div.tab-menu > ul > li > button')
    category_names = []
    for btn in tab_buttons:
        if btn.is_displayed():
            name = btn.text.strip()
            if name and name not in ["전체", "일반"] and name not in category_names:
                category_names.append(name)

    print(f"[-] 총 {len(category_names)}개 카테고리: {category_names}")

    for cat_name in category_names:
        try:
            print(f"\n📌 카테고리 이동: [{cat_name}]")

            tab_xpath = f"//div[contains(@class, 'tab-menu')]//button[normalize-space()='{cat_name}']"
            tab_btn = driver.find_element(By.XPATH, tab_xpath)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tab_btn)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", tab_btn)
            time.sleep(3)

            page_num = 1

            while True:
                print(f"  -> {page_num}페이지 수집 중...")

                items = driver.find_elements(By.CSS_SELECTOR, "div.list-wrap div.list-item")
                print(f"     항목 수: {len(items)}개")

                for idx in range(len(items)):
                    try:
                        # 매번 새로 찾기 (DOM 변경 대응)
                        items = driver.find_elements(By.CSS_SELECTOR, "div.list-wrap div.list-item")
                        item = items[idx]

                        q_btn = item.find_element(By.CSS_SELECTOR, "button.list-title")
                        q_text = q_btn.find_element(By.CSS_SELECTOR, "span.list-content").text.strip()
                        if not q_text:
                            continue

                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", q_btn)
                        time.sleep(0.3)

                        # ✅ 핵심: 이미 열려있는지 확인
                        is_active = "active" in (item.get_attribute("class") or "")

                        if not is_active:
                            # 닫혀있으면 클릭해서 열기
                            driver.execute_script("arguments[0].click();", q_btn)

                        # 답변 대기 및 추출
                        try:
                            wait.until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, "div.list-item.active div.conts")
                                )
                            )
                            active_conts = driver.find_element(
                                By.CSS_SELECTOR, "div.list-item.active div.conts"
                            )
                            a_text = active_conts.get_attribute("innerText").strip()
                        except:
                            a_text = ""

                        hyun_question.append(q_text)
                        hyun_answer.append(a_text)
                        hyun_category.append(cat_name)
                        print(f"     Q: {q_text[:20]}... / A: {a_text[:20]}...")

                        # 이미 열려있었으면 닫지 않음, 클릭해서 연 경우만 닫기
                        if not is_active:
                            driver.execute_script("arguments[0].click();", q_btn)
                            time.sleep(0.5)

                    except Exception as e:
                        print(f"     [!] 항목 {idx} 에러: {e}")
                        continue

                # 페이지네이션
                next_page_num = page_num + 1
                next_btns = driver.find_elements(
                    By.XPATH,
                    f"//div[contains(@class, 'pagenation')]//button[normalize-space()='{next_page_num}']"
                )

                if next_btns:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btns[0])
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", next_btns[0])
                    time.sleep(2)
                    page_num += 1
                else:
                    next_block_btns = driver.find_elements(By.CSS_SELECTOR, "button.btn-pager.next")
                    if next_block_btns:
                        btn = next_block_btns[0]
                        is_disabled = "disabled" in (btn.get_attribute("class") or "") or btn.get_property("disabled")
                        if is_disabled:
                            print(f"  ✅ [{cat_name}] 수집 완료!")
                            break
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(2)
                        page_num += 1
                    else:
                        print(f"  ✅ [{cat_name}] 수집 완료!")
                        break

        except Exception as e:
            print(f"  [!] [{cat_name}] 에러: {e}")
            continue

    driver.quit()

    df = pd.DataFrame({
        "브랜드": "현대",
        "카테고리": hyun_category,
        "질문": hyun_question,
        "답변": hyun_answer
    })

    return df


# if __name__ == "__main__":
#     df = get_hyundai_faq()
#     print("\n🎉 [현대 테스트 실행 결과 미리보기]")
#     print(df.head(10))
#     print(f"\n✅ 총 수집된 FAQ 개수: {len(df)}개")
#     empty_answers = df['답변'].isna().sum() + (df['답변'] == '').sum()
#     print(f"⚠️  답변 비어있는 항목: {empty_answers}개")