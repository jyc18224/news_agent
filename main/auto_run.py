import asyncio
import time
from datetime import datetime, timezone
import pytz
import schedule

from main.run_graph import main


def daily_task():
    """执行每日新闻任务"""
    beijing_time = datetime.now(pytz.timezone('Asia/Shanghai'))
    print(f"\n⏰ 【北京时间】定时任务执行：{beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🕒 UTC 当前时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}")

    try:
        asyncio.run(main())
        print("✅ 每日任务执行完成")
        return True
    except Exception as e:
        print(f"❌ 任务失败：{e}")
        return False


if __name__ == "__main__":
    # ✅ 关键设置：确保时间格式正确（24小时制，两位数字）
    TARGET_TIME = "09:22"  # 北京时间

    try:
        # 设置每日定时任务
        schedule.every().day.at(TARGET_TIME).do(daily_task)
        print(f"✅ 已设置每日任务：每天 {TARGET_TIME} (北京时间) 自动运行")

        # 获取当前北京时间
        beijing_now = datetime.now(pytz.timezone('Asia/Shanghai'))
        print(f"🚀 程序启动时间 (北京时间)：{beijing_now.strftime('%Y-%m-%d %H:%M:%S')}")

        # ✅ 核心逻辑：让 schedule 库自动处理时间判断
        print("⏳ 程序正在运行，等待定时任务执行...")
        while True:
            schedule.run_pending()  # 自动检查并执行到期任务
            time.sleep(60)  # 每分钟检查一次

    except KeyboardInterrupt:
        print("\n🛑 程序被手动终止")
    except Exception as e:
        print(f"💥 严重错误：{e}")
    finally:
        print("🏁 程序结束")