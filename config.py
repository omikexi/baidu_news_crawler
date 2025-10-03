# ===================== 分词配置 =====================
# 过滤字词,如['1','2']
stopwords = []

# 自定义分词,如['00','01']
custom_words = []

# ===================== 爬虫配置 =====================
# Chrome浏览器及ChromeDrive路径配置
CHROMEDRIVER_PATH = r'D:\code\谷歌浏览器插件\chromedriver.exe'
CHROME_BINARY_LOCATION = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

# 数据存储配置
CSV_FILE_NAME = "百度新闻.csv"

# ===================== 爬取参数 =====================
# 目标爬取新闻数量
TARGET_NEWS_COUNT = 51
# 目标筛选日期（格式:YYYY-MM-DD）
TARGET_QUERY_DATE = "2025-10-03"
# Chrome浏览器导航栏输入 https://httpbin.org/user-agent 获取user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"

# ===================== 反爬配置 =====================
# 随机滚动间隔（秒），避免固定频率被识别
SCROLL_INTERVAL = (2, 5)
# 最大滚动次数
MAX_SCROLL_TIMES = 10
# 爬取超时时间（秒）
TIMEOUT = 60
# 核心请求重试次数
RETRY_TIMES = 3