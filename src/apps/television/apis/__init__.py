from ninja import Router


from .tv_program.apis import router as tv_program_router

from .video.apis import router as video_router


router = Router(tags=['television'])


router.add_router('tv_program', tv_program_router)

router.add_router('video', video_router)
