from fastapi import APIRouter


router = APIRouter()

@router.get("/")
def read_pick_ban():
    return {"detail": "Pick and Ban endpoints"}
