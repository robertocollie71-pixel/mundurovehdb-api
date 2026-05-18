from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from backend.app.db.session import get_db

router = APIRouter(prefix="/external", tags=["external"])

# ====================== PHONE (zapis / aktualizacja obywatela) ======================
@router.post("/phone")
@router.patch("/phone")
async def update_or_create_phone(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        phone = data.get("phone")
        imie = data.get("imie")
        nazwisko = data.get("nazwisko")

        print(f"[DEBUG PHONE] Otrzymano: {phone} | {imie} {nazwisko}")

        query = text("""
            INSERT INTO owners (nr_telefonu_enc, imie, nazwisko)
            VALUES (:phone, :imie, :nazwisko)
            ON CONFLICT (nr_telefonu_enc) 
            DO UPDATE SET imie = EXCLUDED.imie, nazwisko = EXCLUDED.nazwisko
        """)
        
        db.execute(query, {"phone": phone, "imie": imie, "nazwisko": nazwisko})
        db.commit()

        return {"status": "success", "message": "Dane obywatela zapisane"}
    except Exception as e:
        db.rollback()
        print("[ERROR PHONE]", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ====================== SOCIAL MEDIA (nowy endpoint) ======================
@router.post("/social")
async def save_social_media(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        phone = data.get("phone")
        facebook = data.get("facebook")
        instagram = data.get("instagram")
        x = data.get("x")
        linkedin = data.get("linkedin")

        print(f"[DEBUG SOCIAL] Zapisuję dla telefonu {phone} → FB:{facebook}, IG:{instagram}, X:{x}, LI:{linkedin}")

        query = text("""
            UPDATE owners 
            SET facebook = :facebook,
                instagram = :instagram,
                x_handle = :x,
                linkedin = :linkedin
            WHERE nr_telefonu_enc = :phone
        """)
        
        result = db.execute(query, {
            "phone": phone,
            "facebook": facebook or None,
            "instagram": instagram or None,
            "x": x or None,
            "linkedin": linkedin or None
        })
        db.commit()

        if result.rowcount == 0:
            return {"status": "warning", "message": "Nie znaleziono obywatela z tym telefonem"}
        
        return {"status": "success", "message": "Social media zapisane"}
    except Exception as e:
        db.rollback()
        print("[ERROR SOCIAL]", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ====================== CITIZENS (istniejący) ======================
@router.get("/citizens")
async def get_all_citizens_endpoint(request: Request, db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT
                o.id,
                o.imie,
                o.nazwisko,
                COALESCE(o.nr_telefonu_enc, '') as phone,
                COALESCE(
                    (SELECT json_group_array(v.numer_rejestracyjny)
                     FROM vehicles v WHERE v.owner_id = o.id),
                    '[]'
                ) as vehicles
            FROM owners o
            ORDER BY o.nazwisko, o.imie
        """)
        result = db.execute(query)
        citizens = [dict(row._mapping) for row in result]
        return citizens
    except Exception as e:
        print("[ERROR CITIZENS]", str(e))
        raise HTTPException(status_code=500, detail=str(e))
