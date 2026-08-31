from news_agent.storage import get_task_run, list_task_runs, save_task_run


def test_save_and_get_task_run(tmp_path):
    db_path = tmp_path / "news_agent.db"
    task_id = save_task_run(
        task_id="test-task",
        user_input="看今日简报",
        intent="daily_briefing",
        model_output="# 测试日报",
        duration_ms=123,
        status="success",
        db_path=db_path,
    )

    task = get_task_run(task_id, db_path=db_path)
    assert task["task_id"] == "test-task"
    assert task["user_input"] == "看今日简报"
    assert task["model_output"] == "# 测试日报"
    assert task["status"] == "success"


def test_list_task_runs_returns_latest_first(tmp_path):
    db_path = tmp_path / "news_agent.db"
    save_task_run(
        task_id="task-1",
        user_input="第一",
        intent="daily_briefing",
        model_output="out-1",
        duration_ms=1,
        status="success",
        db_path=db_path,
    )
    save_task_run(
        task_id="task-2",
        user_input="第二",
        intent="topic_search",
        model_output="out-2",
        duration_ms=2,
        status="success",
        db_path=db_path,
    )

    tasks = list_task_runs(db_path=db_path)
    assert tasks[0]["task_id"] == "task-2"
    assert tasks[1]["task_id"] == "task-1"
