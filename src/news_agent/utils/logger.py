# 导入Python内置的日志模块
import logging
# 导入os模块，用来创建日志文件夹
import os
# 导入datetime模块，用来给日志文件加上日期
from datetime import datetime

# 日志文件夹不存在就创建
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 日志文件名按日期
log_file = os.path.join(LOG_DIR, f"rss_{datetime.now().strftime('%Y%m%d')}.log")

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    # 格式：时间 - 模块名 - 日志级别 - 日志内容
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # 写入文件
        logging.FileHandler(log_file, encoding="utf-8"),
        # 同时输出到终端
        logging.StreamHandler()
    ]
)

# 给外面使用的日志工具（所有节点都用这个）
logger = logging.getLogger("news_agent")