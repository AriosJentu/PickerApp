from fastapi import APIRouter


router = APIRouter()

@router.get("/")
def get_lobbies():
    return {"lobbies": []}
