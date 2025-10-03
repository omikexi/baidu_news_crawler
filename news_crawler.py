import os
import time
import random
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import (
    CHROMEDRIVER_PATH, CHROME_BINARY_LOCATION, CSV_FILE_NAME,
    TARGET_NEWS_COUNT, TARGET_QUERY_DATE, USER_AGENT,
    SCROLL_INTERVAL, MAX_SCROLL_TIMES, TIMEOUT, RETRY_TIMES
)
from utils import detect_csv_encoding


def setup_driver():
    try:
        service = Service(executable_path=CHROMEDRIVER_PATH)
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')  # 无头模式（不显示浏览器窗口）
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 屏蔽自动化检测
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_argument(f'user-agent={USER_AGENT}')
        chrome_options.binary_location = CHROME_BINARY_LOCATION

        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(TIMEOUT)  # 设置页面加载超时
        return driver
    except Exception as e:
        raise RuntimeError(f"ChromeDriver初始化失败：{str(e)}")


@retry(
    stop=stop_after_attempt(RETRY_TIMES),
    wait=wait_exponential(multiplier=1, min=2, max=10),  # 指数退避等待（2s→4s→8s）
    retry=retry_if_exception_type((RuntimeError, ConnectionError))  # 仅重试指定异常
)
def get_baidu_date_news(target_date):
    driver = None
    news_dict = {}
    try:
        driver = setup_driver()
        base_url = f"https://www.baidu.com/s?tn=news&ie=utf-8&wd=&y0={target_date}&y1={target_date}"
        driver.get(base_url)
        time.sleep(random.uniform(*SCROLL_INTERVAL))  # 随机等待，避免反爬

        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        start_time = time.time()

        while len(news_dict) < TARGET_NEWS_COUNT:
            if (time.time() - start_time) > TIMEOUT or scroll_count >= MAX_SCROLL_TIMES:
                break

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            news_elements = soup.find_all('div', class_='result-op c-container xpath-log new-pmd')

            for item in news_elements:
                title_elem = item.find('h3', class_='news-title_1YtI1')
                link_elem = title_elem.find('a', href=True) if title_elem else None
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem['href'].strip()
                    if title and link.startswith(('http', 'https')) and link not in news_dict:
                        news_dict[link] = {"title": title, "link": link}

            if len(news_dict) < TARGET_NEWS_COUNT:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                scroll_count += 1
                time.sleep(random.uniform(*SCROLL_INTERVAL))
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:  # 滚动到底部，无新内容
                    break
                last_height = new_height

        news_list = list(news_dict.values())[:TARGET_NEWS_COUNT]
        print(f"✅ 爬取完成，共获取 {len(news_list)} 条去重新闻（{target_date}）")
        return news_list
    except Exception as e:
        raise RuntimeError(f"爬取出错：{str(e)}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as close_e:
                os.system("taskkill /f /im chrome.exe >nul 2>&1")
                os.system("taskkill /f /im chromedriver.exe >nul 2>&1")
                print(f"⚠️  强制关闭浏览器残留进程：{str(close_e)}")


def save_news_to_csv(news_list, target_date):
    fixed_columns = ["日期", "新闻标题", "详情页链接"]
    has_new_content = False

    try:
        new_data = {
            "日期": [target_date] * len(news_list),
            "新闻标题": [item["title"] for item in news_list],
            "详情页链接": [item["link"] for item in news_list]
        }
        df_new = pd.DataFrame(new_data)

        if os.path.exists(CSV_FILE_NAME):
            encoding = detect_csv_encoding(CSV_FILE_NAME)
            df_existing = pd.read_csv(CSV_FILE_NAME, encoding=encoding)

            if list(df_existing.columns) != fixed_columns:
                raise ValueError(f"CSV列名不匹配，需为：{fixed_columns}")

            existing_links = set(df_existing["详情页链接"].dropna())
            df_new = df_new[~df_new["详情页链接"].isin(existing_links)]

            if not df_new.empty:
                df_updated = pd.concat([df_existing, df_new], ignore_index=True)
                df_updated.to_csv(CSV_FILE_NAME, index=False, encoding='utf-8-sig')
                print(f"✅ CSV更新成功，新增 {len(df_new)} 条新闻")
                has_new_content = True
            else:
                print("✅ CSV无新增内容（已去重）")
        else:
            # 新建CSV文件
            df_new.to_csv(CSV_FILE_NAME, index=False, encoding='utf-8-sig')
            print(f"✅ 新CSV创建成功，保存 {len(df_new)} 条新闻")
            has_new_content = True

        return has_new_content
    except Exception as e:
        print(f"❌ 保存CSV出错：{str(e)}")
        return has_new_content


if __name__ == "__main__":
    print("=" * 50)
    start_time = datetime.now()
    print(f"百度新闻爬取程序启动（{start_time.strftime('%Y-%m-%d %H:%M:%S')}）")
    print(f"目标日期：{TARGET_QUERY_DATE} | 目标数量：{TARGET_NEWS_COUNT}条")
    print("=" * 50)

    try:
        news_list = get_baidu_date_news(TARGET_QUERY_DATE)
        if not news_list:
            print("\n❌ 未获取到新闻数据，程序终止")
            exit()

        print("\n" + "-" * 30)
        has_new_content = save_news_to_csv(news_list, TARGET_QUERY_DATE)
        if not has_new_content:
            print("\n❌ 无新内容保存，程序终止")
            exit()

        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        print("\n" + "=" * 50)
        print(f"程序执行完成（{end_time.strftime('%Y-%m-%d %H:%M:%S')}）")
        print(f"总耗时：{elapsed:.2f}秒 | CSV路径：{os.path.abspath(CSV_FILE_NAME)}")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ 程序异常终止：{str(e)}")
        exit()