from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..crud.external import get_all_citizens_admin  # utworzymy za chwilę

router = APIRouter(prefix="/external", tags=["admin"])  # lub prefix="/admin"

@router.get("/citizens")
async def get_citizens_admin(
    request: Request,
    db: Session = Depends(get_db)
):
    # Szybka ochrona admina z WordPressa + fallback na poziom 3
    wp_nonce = request.headers.get("X-WP-Nonce")
    access_level = request.headers.get("X-Access-Level")
    
    if wp_nonce != "429f4538d5" and access_level != "3":
        raise HTTPException(status_code=403, detail="Brak uprawnień administratora")
    
    citizens = get_all_citizens_admin(db)
    return citizens