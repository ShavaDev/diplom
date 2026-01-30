from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.test_api import test_router
from api.user_api import user_router
from database.basa import Base, engine

# антиспам
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Создаем лимитер (определяет юзера по IP)
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(docs="/docs")

# Настраиваем лимитер в приложении
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(test_router)
app.include_router(user_router)

Base.metadata.create_all(bind=engine)
