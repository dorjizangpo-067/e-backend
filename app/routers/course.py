from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(
    prefix="/courses",
    tags=["courses"]
)

@router.get("/")
async def get_courses():
    return {"message": "List of courses"}