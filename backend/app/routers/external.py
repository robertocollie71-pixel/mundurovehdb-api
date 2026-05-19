from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.session import get_db
import traceback

router = APIRouter(prefix="/external", tags=["external"])

# ====================== PHONE (zawsze aktualizuj istniejący rekord) ======================
@router.post("/phone")
@router.patch("/phone")
async def update_or_create_phone(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        phone = data.get("phone")
        imie = data.get("imie")
        nazwisko = data.get("nazwisko")

        print(f"[DEBUG PHONE] Aktualizacja: {phone} | {imie} {nazwisko}")

        # Zawsze aktualizujemy po numerze telefonu (główna logika)
        query = text("""
            INSERT INTO owners (nr_telefonu_enc, imie, nazwisko, pesel_hash)
            VALUES (:phone, :imie, :nazwisko, '')
            ON CONFLICT (nr_telefonu_enc) 
            DO UPDATE SET 
                imie = excluded.imie,
                nazwisko = excluded.nazwisko
        """)
        db.execute(query, {"phone": phone, "imie": imie, "nazwisko": nazwisko})
        db.commit()

        print("[DEBUG PHONE] ✅ Zapisano pomyślnie (update)")
        return {"status": "success", "message": "Dane zapisane"}

    except Exception as e:
        db.rollback()
        print("[ERROR PHONE]", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ====================== SOCIAL MEDIA (zawsze aktualizuj istniejący rekord) ======================
@router.post("/social")
async def save_social_media(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        phone = data.get("phone")
        facebook = data.get("facebook")
        instagram = data.get("instagram")
        x = data.get("x")
        linkedin = data.get("linkedin")

        print(f"[DEBUG SOCIAL] Aktualizacja social dla {phone}")

        # Bezpieczne dodanie kolumn jeśli nie istnieją
        for col in ["facebook", "instagram", "x_handle", "linkedin"]:
            try:
                db.execute(text(f"ALTER TABLE owners ADD COLUMN {col} TEXT"))
                db.commit()
            except:
                pass

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

        print(f"[DEBUG SOCIAL] ✅ Zaktualizowano {result.rowcount} rekordów")
        return {"status": "success", "message": "Social media zapisane"}

    except Exception as e:
        db.rollback()
        print("[ERROR SOCIAL]", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ====================== DODAWANIE POJAZDU ======================
@router.post("/vehicles")
async def add_vehicle(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        phone = data.get("phone")
        plate = data.get("numer_rejestracyjny")

        if not phone or not plate:
            raise HTTPException(status_code=400, detail="Brak telefonu lub numeru rejestracyjnego")

        plate = plate.upper().strip()
        print(f"[DEBUG VEHICLE] Dodaję pojazd {plate} dla telefonu {phone}")

        # Upewnij się, że właściciel istnieje
        db.execute(text("""
            INSERT INTO owners (nr_telefonu_enc, imie, nazwisko, pesel_hash)
            VALUES (:phone, 'Nowy', 'Użytkownik', '')
            ON CONFLICT (nr_telefonu_enc) DO NOTHING
        """), {"phone": phone})

        owner_id = db.execute(text("SELECT id FROM owners WHERE nr_telefonu_enc = :phone"), {"phone": phone}).scalar()

        db.execute(text("""
            INSERT INTO vehicles (numer_rejestracyjny, owner_id)
            VALUES (:plate, :owner_id)
            ON CONFLICT (numer_rejestracyjny) DO NOTHING
        """), {"plate": plate, "owner_id": owner_id})
        db.commit()

        print(f"[DEBUG VEHICLE] ✅ Pojazd {plate} dodany")
        return {"status": "success", "message": f"Pojazd {plate} dodany"}

    except Exception as e:
        db.rollback()
        print("[ERROR VEHICLE]", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ====================== CITIZENS ======================
@router.get("/citizens")
async def get_all_citizens_endpoint(request: Request, db: Session = Depends(get_db)):
    try:
        for col in ["facebook", "instagram", "x_handle", "linkedin"]:
            try:
                db.execute(text(f"ALTER TABLE owners ADD COLUMN {col} TEXT"))
                db.commit()
            except:
                pass

        query = text("""
            SELECT
                o.id,
                o.imie,
                o.nazwisko,
                COALESCE(o.nr_telefonu_enc, '') as phone,
                COALESCE(o.facebook, '') as facebook,
                COALESCE(o.instagram, '') as instagram,
                COALESCE(o.x_handle, '') as x_handle,
                COALESCE(o.linkedin, '') as linkedin,
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
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
