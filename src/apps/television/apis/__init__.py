from ninja import Router

from .public import router as public_router


# 对外只接入只读 API；旧的后台 CRUD 模块保留在代码库中但不再暴露给匿名客户端。
router = Router(tags=['今日视线'])
router.add_router('', public_router)
