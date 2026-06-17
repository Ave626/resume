from fastapi import APIRouter
from app.presentation.api.routes.admin import router as admin_router
from app.presentation.api.routes.content import router as content_router
from app.infrastructure.config import get_settings


settings = get_settings()

router = APIRouter(prefix=settings.api.prefix)
router.include_router(content_router)
router.include_router(admin_router)
