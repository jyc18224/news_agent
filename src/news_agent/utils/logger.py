import logging
import os
from datetime import datetime

# 初始化日志目录
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 根据当前日期生成日志文件名
log_filename = f"news_agent_{datetime.now().strftime('%Y%m%d')}.log"
log_path = os.path.join(LOG_DIR, log_filename)

# 配置全局日志设置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# 导出 logger 实例供全项目使用
logger = logging.getLogger("news_agent")