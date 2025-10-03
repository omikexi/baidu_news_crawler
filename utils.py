import os
import logging
import jieba
import pandas as pd


def detect_csv_encoding(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在：{file_path}")

    encodings = ['utf-8-sig', 'gbk', 'gb2312', 'utf-8']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read(1024)
            return encoding
        except UnicodeDecodeError:
            continue
    raise ValueError(f"文件 {file_path} 无法通过以下编码读取：{encodings}，可能文件损坏")


def setup_jieba(custom_words):
    jieba.setLogLevel(logging.WARNING)
    for word in custom_words:
        if word.strip():  # 过滤空字符串
            jieba.add_word(word.strip())