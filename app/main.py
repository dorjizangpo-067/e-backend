from fastapi import FastAPI

from .routers import users, course

app = FastAPI(
    title="E-Learning Platform API",
    description="API for managing courses, users, and content in an e-learning platform.",
    version="1.0.0",
    contact={
        "name": "E-Learning Support",
        "email": "dorjizangpo75@gmail.com"
    }
)

app.include_router(users.router)
app.include_router(course.router)

@app.get("/")
async def read_root():
    return {"Hello": "World"}