import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def get_kia_faq():
    print("▶ [기아] FAQ 크롤링 시작")

    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    kia_url = "https://www.kia.com/kr/customer-service/center/faq#none"
    driver.get(kia_url)
    time.sleep(5)

    kia_question = []
    kia_answer = []
    kia_category = []

    target_categories = ["차량 구매", "차량 정비", "기아멤버스", "홈페이지", "PBV", "기타"]

    for cat_name in target_categories:
        try:
            print(f"\n📌 카테고리 이동: [{cat_name}]")

            # ✅ 핵심: button.tabs__btn 안의 span.name 텍스트로 찾기
            tab_btn = driver.find_element(
                By.XPATH,
                f"//button[contains(@class,'tabs__btn')]//span[contains(@class,'name') and normalize-space()='{cat_name}']/ancestor::button"
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tab_btn)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", tab_btn)
            time.sleep(3)

            page_num = 1

            while True:
                print(f"  -> {page_num}페이지 수집 중...")

                q_btns = driver.find_elements(By.CSS_SELECTOR, "button.cmp-accordion__button")
                print(f"     항목 수: {len(q_btns)}개")

                for i, q_btn in enumerate(q_btns):
                    try:
                        q_text = q_btn.find_element(By.CSS_SELECTOR, "span.cmp-accordion__title").text.strip()
                        if not q_text:
                            continue

                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", q_btn)
                        time.sleep(0.3)
                        driver.execute_script("arguments[0].click();", q_btn)
                        time.sleep(1)

                        # aria-expanded='true'인 버튼의 부모에서 패널 추출
                        try:
                            expanded_btn = driver.find_element(
                                By.CSS_SELECTOR,
                                "button.cmp-accordion__button[aria-expanded='true']"
                            )
                            parent_item = expanded_btn.find_element(
                                By.XPATH, "./ancestor::div[contains(@class,'cmp-accordion__item')]"
                            )
                            a_panel = parent_item.find_element(By.CSS_SELECTOR, "div.cmp-accordion__panel")
                            a_text = a_panel.get_attribute("innerText").strip()
                        except:
                            a_text = ""

                        kia_question.append(q_text)
                        kia_answer.append(a_text)
                        kia_category.append(cat_name)
                        print(f"     Q{i+1}: {q_text[:30]}...")

                        # 닫기
                        driver.execute_script("arguments[0].click();", q_btn)
                        time.sleep(0.3)

                    except Exception as e:
                        print(f"     [!] 항목 {i+1} 에러: {e}")
                        continue

                # 페이지네이션: ul.paging-list 안의 a 태그
                next_page_num = page_num + 1
                next_btns = driver.find_elements(
                    By.XPATH,
                    f"//ul[contains(@class,'paging-list')]//a[normalize-space()='{next_page_num}']"
                )

                if next_btns:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btns[0])
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", next_btns[0])
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
        "브랜드": "기아",
        "카테고리": kia_category,
        "질문": kia_question,
        "답변": kia_answer
    })

    return df


# if __name__ == "__main__":
#     df = get_kia_faq()
#     print("\n🎉 [기아 테스트 실행 결과 미리보기]")
#     print(df.head(10))
#     print(f"\n✅ 총 수집된 FAQ 개수: {len(df)}개")