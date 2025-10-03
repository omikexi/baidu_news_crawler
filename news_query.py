import pandas as pd
import os
from config import CSV_FILE_NAME, TARGET_QUERY_DATE
from utils import detect_csv_encoding

def query_news_by_date(target_date=None):
    if not os.path.exists(CSV_FILE_NAME):
        print(f"❌ 错误：CSV文件不存在 - {os.path.abspath(CSV_FILE_NAME)}")
        return
    try:
        encoding = detect_csv_encoding(CSV_FILE_NAME)
        df = pd.read_csv(CSV_FILE_NAME, encoding=encoding)
    except Exception as e:
        print(f"❌ 读取CSV失败：{str(e)}")
        return

    required_columns = ["日期", "新闻标题", "详情页链接"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"❌ 错误：CSV缺少必要列 - {', '.join(missing_columns)}（需包含：{required_columns}）")
        return

    query_date = target_date if target_date else TARGET_QUERY_DATE
    result_df = df[df["日期"] == query_date]

    if result_df.empty:
        available_dates = sorted(df["日期"].drop_duplicates().tolist())
        print(f"ℹ️  未查询到 {query_date} 的新闻数据")
        print(f"   可用日期范围：{available_dates[0]} ~ {available_dates[-1]}")
        print(f"   可用日期列表：{available_dates}")
    else:
        print(f"✅ 查询成功：{query_date} 共 {len(result_df)} 条新闻")
        print("\n" + "-" * 80)
        for idx, row in result_df.iterrows():
            print(f"[{idx+1}]标题：{row['新闻标题']}")
            print(f"   链接：{row['详情页链接']}")
            print("-" * 80)

if __name__ == "__main__":
    query_news_by_date()