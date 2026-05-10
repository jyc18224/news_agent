import asyncio
import time
import datetime

try:
    import schedule
except ImportError:
    print("❌ 请先执行 uv pip install schedule")
    exit(1)

from main.run_graph import main

def daily_task():
    print(f"\n⏰ 定时任务执行：{datetime.datetime.now()}")
    try:
        asyncio.run(main())
        print("✅ 每日任务执行完成")
    except Exception as e:
        print(f"❌ 任务失败：{e}")

if __name__ == "__main__":
    # 先清空所有任务，避免冲突
    schedule.clear()

    # 测试用：设置为当前时间的下一分钟运行（方便你马上看到效果）
    now = datetime.datetime.now()
    next_minute = (now + datetime.timedelta(minutes=1)).strftime("%H:%M")
    schedule.every().day.at(next_minute).do(daily_task)
    print(f"✅ 已设置测试任务：{next_minute} 运行一次")

    # 正式任务：每天早上8点运行
    schedule.every().day.at("08:00").do(daily_task)
    print("✅ 已设置每日任务：每天 08:00 自动运行")

    print("💡 保持窗口开启，程序将在后台等待执行")
    while True:
        schedule.run_pending()
        time.sleep(60)