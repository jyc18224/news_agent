import asyncio
from datetime import datetime
import pytz
from main.run_graph import main

def run_task():
    """定时任务的主入口。"""
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    print(f"任务启动时间: {now.strftime('%Y-%m-%d %H:%M:%S')} (CST)")
    
    try:
        asyncio.run(main())
        print("任务运行成功。")
    except Exception as e:
        print(f"任务运行失败，错误信息: {e}")
        exit(1)

if __name__ == "__main__":
    run_task()