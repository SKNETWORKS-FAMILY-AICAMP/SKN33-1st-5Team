import time
import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

TESLA_PAGES = [
    {"카테고리": "소프트웨어 업데이트",    "대분류": "기능 및 충전",       "url": "https://www.tesla.com/ko_KR/support/software-updates"},
    {"카테고리": "보안 기능",              "대분류": "기능 및 충전",       "url": "https://www.tesla.com/ko_KR/support/vehicle-safety-security-features"},
    {"카테고리": "DIY 매뉴얼",             "대분류": "기능 및 충전",       "url": "https://www.tesla.com/ko_KR/support/do-it-yourself-guides"},
    {"카테고리": "수퍼차저",               "대분류": "기능 및 충전",       "url": "https://www.tesla.com/ko_kr/support/charging/supercharging"},
    {"카테고리": "홈차징",                 "대분류": "기능 및 충전",       "url": "https://www.tesla.com/ko_KR/support/charging/home-charging"},
    {"카테고리": "충전 및 어댑터",          "대분류": "기능 및 충전",       "url": "https://www.tesla.com/ko_kr/support/charging/product-guides"},
    {"카테고리": "공공충전소 이용",          "대분류": "기능 및 충전",       "url": "https://www.tesla.com/ko_kr/support/charging/public-charging"},
    {"카테고리": "한국공인연비",             "대분류": "기능 및 충전",       "url": "https://www.tesla.com/ko_KR/support/range-calculator-ref"},
    {"카테고리": "커넥티비티",              "대분류": "기능 및 충전",       "url": "https://www.tesla.com/ko_KR/support/connectivity"},
    {"카테고리": "서비스 방문 예약하기",     "대분류": "서비스 및 차체 수리", "url": "https://www.tesla.com/ko_KR/support/service-visits"},
    {"카테고리": "사고 수리센터 찾기",       "대분류": "서비스 및 차체 수리", "url": "https://www.tesla.com/ko_KR/support/body-shop-support"},
    {"카테고리": "긴급 출동 서비스",         "대분류": "서비스 및 차체 수리", "url": "https://www.tesla.com/ko_KR/support/roadside-assistance"},
    {"카테고리": "차량 유지 보수",           "대분류": "서비스 및 차체 수리", "url": "https://www.tesla.com/ko_KR/support/vehicle-maintenance"},
    {"카테고리": "차량 보증",               "대분류": "서비스 및 차체 수리", "url": "https://www.tesla.com/ko_KR/support/vehicle-warranty"},
    {"카테고리": "EWI",                    "대분류": "서비스 및 차체 수리", "url": "https://www.tesla.com/ko_KR/support/extended-warranty"},
    {"카테고리": "서비스 자료 제공",         "대분류": "서비스 및 차체 수리", "url": "https://www.tesla.com/ko_KR/support/service-material"},
    {"카테고리": "테슬라 공인 바디샵 모집",  "대분류": "서비스 및 차체 수리", "url": "https://www.tesla.com/ko_KR/support/bodyshop-recruitment"},
    {"카테고리": "서비스 포털",              "대분류": "서비스 및 차체 수리", "url": "https://www.tesla.com/ko_KR/support/service-portal"},
    {"카테고리": "테슬라 앱",               "대분류": "Tesla 계정",         "url": "https://www.tesla.com/ko_KR/support/tesla-app"},
    {"카테고리": "Refer and Earn",          "대분류": "Tesla 계정",         "url": "https://www.tesla.com/ko_KR/support/refer-and-earn"},
    {"카테고리": "계정 지원",               "대분류": "Tesla 계정",         "url": "https://www.tesla.com/ko_KR/support/account-support"},
]


def extract_page_content(driver, page_info):
    results = []
    url = page_info["url"]
    sub_category = page_info["카테고리"]
    main_category = page_info["대분류"]

    try:
        driver.get(url)
        time.sleep(4)

        if "Access Denied" in driver.page_source[:500]:
            print(f"    [!] 여전히 Access Denied - 스킵")
            return results

        soup = BeautifulSoup(driver.page_source, "html.parser")
        content_area = soup.select_one("div#root") or soup.select_one("main") or soup.body
        if not content_area:
            return results

        h1 = content_area.select_one("h1")
        page_title = h1.text.strip() if h1 else sub_category

        all_tags = content_area.find_all(["h2", "h3", "h4", "p", "li"])
        current_heading = page_title
        current_content = []

        for tag in all_tags:
            if tag.name in ["h2", "h3", "h4"]:
                if current_content:
                    answer = " ".join(current_content).strip()
                    if answer:
                        results.append({
                            "브랜드": "테슬라",
                            "대분류": main_category,
                            "카테고리": sub_category,
                            "질문": current_heading,
                            "답변": answer
                        })
                current_heading = tag.text.strip()
                current_content = []
            elif tag.name in ["p", "li"]:
                text = tag.text.strip()
                if text:
                    current_content.append(text)

        if current_content:
            answer = " ".join(current_content).strip()
            if answer:
                results.append({
                    "브랜드": "테슬라",
                    "대분류": main_category,
                    "카테고리": sub_category,
                    "질문": current_heading,
                    "답변": answer
                })

        if not results:
            all_p = content_area.select("p")
            full_text = " ".join(p.text.strip() for p in all_p if p.text.strip())
            if full_text:
                results.append({
                    "브랜드": "테슬라",
                    "대분류": main_category,
                    "카테고리": sub_category,
                    "질문": page_title,
                    "답변": full_text
                })

    except Exception as e:
        print(f"    [!] 파싱 에러: {e}")

    return results


def get_tesla_faq():
    print("▶ [테슬라] undetected-chromedriver로 크롤링 시작\n")

    # ✅ 핵심: uc.Chrome() 사용
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    driver = uc.Chrome(options=options)

    all_data = []

    # 메인 페이지 먼저 방문해서 세션 확보
    print("[준비] 메인 페이지 방문 중...")
    driver.get("https://www.tesla.com/ko_KR/support")
    time.sleep(6)
    print("  -> 완료!\n")

    print(f"[수집] 총 {len(TESLA_PAGES)}개 페이지 순회 시작...")
    for i, page_info in enumerate(TESLA_PAGES, 1):
        print(f"  [{i}/{len(TESLA_PAGES)}] {page_info['대분류']} > {page_info['카테고리']}")
        page_data = extract_page_content(driver, page_info)
        all_data.extend(page_data)
        print(f"    -> {len(page_data)}개 항목 수집")
        time.sleep(2)

    driver.quit()
    return pd.DataFrame(all_data)


# if __name__ == "__main__":
#     df = get_tesla_faq()
#     print("\n🎉 [테슬라 테스트 실행 결과 미리보기]")
#     print(df.head(10))
#     print(f"\n✅ 총 수집된 항목 개수: {len(df)}개")