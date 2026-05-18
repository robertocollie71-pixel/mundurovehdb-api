from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.session import get_db

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

@router.get("/{numer_rejestracyjny}")
async def get_vehicle(numer_rejestracyjny: str, request: Request, db: Session = Depends(get_db)):
    # Ignorujemy favicon.ico – nie ma sensu szukać w bazie
    if numer_rejestracyjny.upper() == "FAVICON.ICO":
        return {"status": "ignored"}

    try:
        query = text("""
            SELECT 
                v.numer_rejestracyjny,
                v.vin,
                v.marka_model,
                v.rok_produkcji,
                v.data_waznosci_badania_technicznej,
                o.imie,
                o.nazwisko,
                o.nr_telefonu_enc
            FROM vehicles v
            LEFT JOIN owners o ON v.owner_id = o.id
            WHERE v.numer_rejestracyjny = :rej
              AND (o.access_level IS NULL OR o.access_level <= :access_level)
            LIMIT 1
        """)
        result = db.execute(query, {"rej": numer_rejestracyjny.upper(), "access_level": 3}).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Pojazd nie znaleziony")
        return dict(result._mapping)
    except Exception as e:
        print("[ERROR vehicles]", str(e))
        raise HTTPException(status_code=500, detail=str(e))
