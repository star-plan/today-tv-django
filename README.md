# ⚒️ Today TV 今日电视 🛠️

## celery

启动

```bash
celery -A config worker -l INFO
```

### Questions

#### 在 Windows 上执行并行任务报错

```
    tasks, accept, hostname = _loc
    ^^^^^^^^^^^^^^^^^^^^^^^
ValueError: not enough values to unpack (expected 3, got 0)
```

解决方式1，增加 `--pool=solo` 参数

```bash
celery -A config worker -l INFO --pool=solo
```

解决方式2，使用 `eventlet` 作为 pool

安装 `pdm add eventlet`

```bash
celery -A config worker -l INFO --pool=eventlet
```

#### 无法获取任务结果问题

```
No result backend is configured
```

https://stackoverflow.com/questions/76901297/celery-no-result-backend-is-configured