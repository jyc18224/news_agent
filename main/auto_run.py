import asyncio
import time
from datetime import datetime
import pytz
from main.run_graph import main

def run_task():
    beijing_time = datetime.now(pytz.timezone('Asia/Shanghai'))
    print(f"\n⏰ 【北京时间】任务开始执行：{beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        asyncio.run(main())
        print("✅ 任务执行完毕，程序退出。")
    except Exception as e:
        print(f"❌ 任务失败：{e}")
        exit(1)

if __name__ == "__main__":
    run_task()