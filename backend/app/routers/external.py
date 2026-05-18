from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.session import get_db

router = APIRouter(prefix="/external", tags=["external"])

# ====================== PHONE ======================
@router.post("/phone")
@router.patch("/phone")
async def update_or_create_phone(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        phone = data.get("phone")
        imie = data.get("imie")
        nazwisko = data.get("nazwisko")

        print(f"[DEBUG PHONE] Otrzymano: phone={phone}, imie={imie}, nazwisko={nazwisko}")

        # SQLite-safe upsert
        query = text("""
            INSERT INTO owners (nr_telefonu_enc, imie, nazwisko)
            VALUES (:phone, :imie, :nazwisko)
            ON CONFLICT (nr_telefonu_enc) 
            DO UPDATE SET imie = excluded.imie, nazwisko = excluded.nazwisko
        """)
        db.execute(query, {"phone": phone, "imie": imie, "nazwisko": nazwisko})
        db.commit()

        return {"status": "success", "message": "Dane zapisane"}
    except Exception as e:
        db.rollback()
        print("[ERROR PHONE]", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ====================== SOCIAL MEDIA ======================
@router.post("/social")
async def save_social_media(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        phone = data.get("phone")
        facebook = data.get("facebook")
        instagram = data.get("instagram")
        x = data.get("x")
        linkedin = data.get("linkedin")

        print(f"[DEBUG SOCIAL] Zapisuję social dla {phone}")

        # Dodaj kolumny jeśli nie istnieją (bezpieczne)
        for col in ["facebook", "instagram", "x_handle", "linkedin"]:
            try:
                db.execute(text(f"ALTER TABLE owners ADD COLUMN {col} TEXT"))
                db.commit()
            except:
                pass  # kolumna już istnieje

        query = text("""
            UPDATE owners 
            SET facebook = :facebook,
                instagram = :instagram,
                x_handle = :x,
                linkedin = :linkedin
            WHERE nr_telefonu_enc = :phone
        """)
        db.execute(query, {
            "phone": phone,
            "facebook": facebook,
            "instagram": instagram,
            "x": x,
            "linkedin": linkedin
        })
        db.commit()

        return {"status": "success", "message": "Social media zapisane"}
    except Exception as e:
        db.rollback()
        print("[ERROR SOCIAL]", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ====================== CITIZENS ======================
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
