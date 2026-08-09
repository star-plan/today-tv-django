# 今日视线 Today TV

一个面向普通观众与客户端开发者的《今日视线》节目索引产品：自动同步公开节目页面的元数据，在网页上直接播放，并提供稳定的只读 API。

## 功能

- 自动采集节目列表、节目详情页、封面和可播放地址；不下载或重新分发视频文件。
- 使用来源详情页哈希做增量去重，重复调度和分页重叠都不会产生重复记录。
- 面向观众的首页、日期归档、播放页、同日选集和自动连播。
- 面向客户端的只读 JSON API，以及自动生成的 OpenAPI 文档。
- Celery Beat 每日自动同步，也可通过管理命令或 Windows 任务计划程序手动执行。

## 本地启动

项目要求 Python 3.11 和 Redis。使用 PDM 安装依赖后，在 PowerShell 中执行：

```powershell
pdm install
Push-Location src
pdm run python manage.py migrate
pdm run python manage.py sync_today_tv --pages 3
pdm run python manage.py runserver
```

打开 `http://127.0.0.1:8000/` 浏览节目，打开 `http://127.0.0.1:8000/api/docs` 查看交互式接口文档。

## 自动同步

生产环境同时启动 Web、Celery Worker 与 Celery Beat：

```powershell
Push-Location src
pdm run celery -A config worker -l INFO --pool=solo
pdm run celery -A config beat -l INFO
```

`--pool=solo` 适合 Windows；Linux 容器可省略。默认每天 `23:15`（Asia/Shanghai）同步，可用以下环境变量调整：

```powershell
$env:TODAY_TV_SYNC_HOUR = '23'
$env:TODAY_TV_SYNC_MINUTE = '15'
$env:TODAY_TV_CRAWL_PAGES = '3'
```

如果节目发布平台改版，可不改代码直接覆盖来源地址；页面分页规则仍沿用当前大华网栏目结构：

```powershell
$env:TODAY_TV_SOURCE_ROOT = 'https://新的节目源域名'
$env:TODAY_TV_LISTING_URL = 'https://新的节目源域名/节目列表地址'
```

默认值已指向当前可访问的《今日视线》栏目 `https://strtv.strtv.cn/b/a/list_dahua.shtml`。源站再次迁移后，先在演练模式确认新列表页仍包含节目标题、详情页链接和 `video` 播放器元素，再启用定时同步。

若不使用 Celery，可在 Windows 任务计划程序中创建每日任务，执行：

```powershell
Push-Location C:\code\today-tv\src
pdm run python manage.py sync_today_tv --pages 3
```

先用演练模式检查源站结构和解析结果：

```powershell
pdm run python manage.py sync_today_tv --pages 1 --dry-run
```

## 客户端 API

所有响应均使用 `{ "code", "success", "data" }` 包装。

| 方法 | 地址 | 用途 |
| --- | --- | --- |
| `GET` | `/api/today-tv/program` | 节目库存、最近节目与同步状态 |
| `GET` | `/api/today-tv/episodes?publish_date=YYYY-MM-DD&limit=24&offset=0` | 按日期可选的节目分页列表 |
| `GET` | `/api/today-tv/episodes/{episode_id}` | 单条节目的播放地址与项目播放页 |

`playback_url` 是来源页面提供的播放地址，`source_url` 可用于展示内容出处，`webpage_url` 可用于在浏览器中打开本项目的完整播放页。

## Docker

```powershell
Push-Location src
docker compose up --build
```

Docker Compose 会启动 Redis、Web、Worker 和 Beat 四个服务，Web 服务会在启动时执行迁移。正式部署前请设置 `DEBUG=false`、受限的 `ALLOWED_HOSTS`、持久化数据库与媒体存储。
