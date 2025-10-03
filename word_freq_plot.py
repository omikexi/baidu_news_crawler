import jieba
from collections import Counter
import logging
import re
import matplotlib.pyplot as plt
import math
import pandas as pd
import os
from config import stopwords, custom_words, CSV_FILE_NAME


def setup_jieba():
    jieba.setLogLevel(logging.WARNING)
    for word in custom_words:
        jieba.add_word(word)


def detect_csv_encoding(file_path):
    encodings = ['utf-8-sig', 'gbk', 'gb2312', 'utf-8']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read(1024)
            return encoding
        except UnicodeDecodeError:
            continue
    return 'utf-8-sig'


def fetch_news_titles_from_csv(csv_file):
    if not os.path.exists(csv_file):
        return []
    encoding = detect_csv_encoding(csv_file)
    try:
        df = pd.read_csv(csv_file, encoding=encoding)
    except Exception:
        return []
    if "新闻标题" not in df.columns:
        return []
    return df["新闻标题"].dropna().drop_duplicates().tolist()


def filter_words(titles, stopwords):
    word_list = []
    for title in titles:
        title_str = str(title).strip()
        if not title_str:
            continue
        words = jieba.lcut(title_str)
        for word in words:
            word = word.strip()
            if word and word not in stopwords and not word.isnumeric() and not re.search(r'[^\w\s]', word):
                word_list.append(word)
    return word_list


def get_top_10_words(word_list):
    if not word_list:
        return [], []
    word_freq = Counter(word_list)
    high_freq_words = word_freq.most_common(10)[::-1]
    return [word for word, freq in high_freq_words], [freq for word, freq in high_freq_words]


def plot_top_words(words, frequencies):
    if not words or not frequencies:
        return
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    max_freq = math.ceil(max(frequencies) / 100) * 100
    bars = plt.bar(words, frequencies, color='skyblue')

    # 增大labelpad值（从15调整为25），进一步上移y轴标签，可根据实际显示效果微调
    plt.xlabel('', fontsize=12, fontweight='bold')
    plt.ylabel('频次', fontsize=12, fontweight='bold', labelpad=25)
    plt.title('新闻标题词频柱形图（前10高频词）', fontsize=14, fontweight='bold')

    plt.xticks(rotation=45, fontsize=7, ha='right')

    for bar, freq in zip(bars, frequencies):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height, str(freq),
                 ha='center', va='bottom', color='black', fontsize=8)

    plt.ylim(0, max_freq)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.show()


def main():
    setup_jieba()
    titles = fetch_news_titles_from_csv(CSV_FILE_NAME)
    if not titles:
        return
    word_list = filter_words(titles, stopwords)
    words, frequencies = get_top_10_words(word_list)
    plot_top_words(words, frequencies)


if __name__ == "__main__":
    main()