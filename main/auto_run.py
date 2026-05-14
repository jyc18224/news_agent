import asyncio
import time
import datetime
import pytz
import schedule

from main.run_graph import main


def daily_task():
    """执行每日新闻任务"""
    beijing_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
    print(f"\n⏰ 【北京时间】定时任务执行：{beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🕒 UTC 当前时间：{datetime.datetime.utcnow()}")

    try:
        asyncio.run(main())
        print("✅ 每日任务执行完成")
        return True  # 任务完成后退出程序
    except Exception as e:
        print(f"❌ 任务失败：{e}")
        return False


def get_beijing_time():
    """获取当前北京时间"""
    return datetime.datetime.now(pytz.timezone('Asia/Shanghai'))

def clear_all_jobs():
    """安全清除所有定时任务"""
    try:
        schedule.cancel_pending()
        print("✅ 已清除所有定时任务")
    except Exception as e:
        print(f"⚠️ 清除任务时出错：{e}")

if __name__ == "__main__":
    # 清空所有任务
    clear_all_jobs()

    # ✅ 关键修复1：使用北京时间
    TARGET_TIME = "19:22"  # 北京时间
    try:
        schedule.every().day.at(TARGET_TIME).do(daily_task)
        print(f"✅ 已设置每日任务：每天 {TARGET_TIME} (北京时间) 自动运行")
    except Exception as e:
        print(f"❌ 设置定时任务失败：{e}")
        print("💡 提示：确保时间格式为 HH:MM（英文冒号）")
        exit(1)

    # ✅ 关键修复2：添加立即执行检查（避免无限等待）
    start_time = get_beijing_time()
    print(f"🚀 程序启动时间 (北京时间)：{start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # ✅ 关键修复3：设置超时机制（避免 GitHub Actions 超时）
    MAX_WAIT_HOURS = 1  # 最多等待1小时

    try:
        while True:
            beijing_now = get_beijing_time()
            current_time = beijing_now.strftime("%H:%M")

            # 调试信息：每分钟显示当前时间
            print(f"⏳ 等待中... 当前北京时间: {current_time} | 目标时间: {TARGET_TIME}")

            # 检查是否已过目标时间（防止错过）
            if beijing_now.hour > int(TARGET_TIME.split(':')[0]) or \
                    (beijing_now.hour == int(TARGET_TIME.split(':')[0]) and
                     beijing_now.minute >= int(TARGET_TIME.split(':')[1])):
                print("⏰ 已到目标时间，执行任务...")
                if daily_task():
                    print("🎉 任务完成，程序退出")
                    break

            # 超时检查：避免无限等待
            elapsed_hours = (beijing_now - start_time).total_seconds() / 3600
            if elapsed_hours > MAX_WAIT_HOURS:
                print(f"⚠️ 超时警告：已等待 {elapsed_hours:.1f} 小时，强制退出")
                break

            # 每分钟检查一次
            time.sleep(60)

    except KeyboardInterrupt:
        print("\n🛑 程序被手动终止")
    except Exception as e:
        print(f"💥 严重错误：{e}")
    finally:
        print("🏁 程序结束")