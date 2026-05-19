from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.session import get_db

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

@router.get("/{numer_rejestracyjny}")
async def get_vehicle(numer_rejestracyjny: str, request: Request, db: Session = Depends(get_db)):
    if numer_rejestracyjny.upper() == "FAVICON.ICO":
        return {"status": "ignored"}

    plate = numer_rejestracyjny.upper().strip()

    try:
        query = text("""
            SELECT 
                v.numer_rejestracyjny,
                COALESCE(v.marka_model, '[dane z CEPiK]') as marka_model,
                o.imie,
                o.nazwisko,
                COALESCE(o.nr_telefonu_enc, '') as phone,
                COALESCE(o.facebook, '') as facebook,
                COALESCE(o.instagram, '') as instagram,
                COALESCE(o.x_handle, '') as x_handle,
                COALESCE(o.linkedin, '') as linkedin,
                COALESCE(
                    (SELECT json_agg(v2.numer_rejestracyjny) 
                     FROM vehicles v2 
                     WHERE v2.owner_id = o.id),
                    '[]'
                ) as vehicles
            FROM vehicles v
            LEFT JOIN owners o ON v.owner_id = o.id
            WHERE v.numer_rejestracyjny = :plate
            LIMIT 1
        """)

        result = db.execute(query, {"plate": plate}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Pojazd nie znaleziony")

        data = dict(result._mapping)
        data["wlasciciel"] = f"{data.get('imie') or ''} {data.get('nazwisko') or ''}".strip() or "Nieznany właściciel"

        print(f"[DEBUG VEHICLE] {plate} → wlasciciel: {data['wlasciciel']} | phone: {data.get('phone')} | vehicles: {data.get('vehicles')}")

        return data

    except Exception as e:
        print(f"[ERROR vehicles] {plate} → {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
