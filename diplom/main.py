import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from service.test_service import get_all_tests_db

from api.test_api import test_router
from api.user_api import user_router
from database.basa import Base, engine

# антиспам
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from limiter_config import limiter

templates = Jinja2Templates(directory="templates")

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


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    all_tests = get_all_tests_db()
    return templates.TemplateResponse(request=request,
                                      name="home.html",
                                      context={"all_tests": all_tests})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
