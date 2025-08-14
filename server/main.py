from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Ensure environment variables are loaded before importing modules that use them
load_dotenv()

from controllers.chat_controller import router as chat_router
from controllers.auth_controller import router as auth_router


def create_app() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Type"],
    )

    app.include_router(chat_router)
    app.include_router(auth_router)

    return app


app = create_app()


