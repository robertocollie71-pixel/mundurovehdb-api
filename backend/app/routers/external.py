from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.session import get_db
import traceback

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

        query = text("""
            INSERT INTO owners (nr_telefonu_enc, imie, nazwisko, pesel_hash)
            VALUES (:phone, :imie, :nazwisko, '')
            ON CONFLICT (nr_telefonu_enc) 
            DO UPDATE SET imie = excluded.imie, nazwisko = excluded.nazwisko
        """)
        db.execute(query, {"phone": phone, "imie": imie, "nazwisko": nazwisko})
        db.commit()
        return {"status": "success", "message": "Dane zapisane"}
    except Exception as e:
        db.rollback()
        traceback.print_exc()
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
            "facebook": facebook or None,
            "instagram": instagram or None,
            "x": x or None,
            "linkedin": linkedin or None
        })
        db.commit()
        return {"status": "success", "message": "Social media zapisane"}
    except Exception as e:
        db.rollback()
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

        return {"status": "success", "message": f"Pojazd {plate} dodany"}
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ====================== CITIZENS (z soft-delete) ======================
@router.get("/citizens")
async def get_all_citizens_endpoint(request: Request, db: Session = Depends(get_db)):
    try:
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
                    (SELECT json_agg(v.numer_rejestracyjny)
                     FROM vehicles v 
                     WHERE v.owner_id = o.id 
                       AND v.is_deleted = false),
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
    
# ====================== EDYCJA NUMERU REJESTRACYJNEGO ======================
@router.put("/vehicles/update")
async def update_vehicle_plate(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        old_plate = data.get("old_plate")
        new_plate = data.get("new_plate")

        if not old_plate or not new_plate:
            raise HTTPException(status_code=400, detail="Brak starych/nowych danych")

        new_plate = new_plate.upper().strip()

        query = text("""
            UPDATE vehicles 
            SET numer_rejestracyjny = :new_plate
            WHERE numer_rejestracyjny = :old_plate
        """)
        result = db.execute(query, {"old_plate": old_plate, "new_plate": new_plate})
        db.commit()

        if result.rowcount == 0:
            return {"status": "warning", "message": "Nie znaleziono pojazdu"}

        print(f"[DEBUG VEHICLE UPDATE] {old_plate} → {new_plate}")
        return {"status": "success", "message": f"Pojazd zmieniony na {new_plate}"}

    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
# ====================== USUWANIE POJAZDU Z PERSPEKTYWY OBYWATELA (SOFT-DELETE) ======================
@router.delete("/vehicles/{plate}")
async def delete_vehicle_for_owner(plate: str, request: Request, db: Session = Depends(get_db)):
    try:
        plate = plate.upper().strip()

        result = db.execute(text("""
            UPDATE vehicles 
            SET is_deleted = true,
                deleted_by = 'citizen',
                deleted_at = CURRENT_TIMESTAMP
            WHERE numer_rejestracyjny = :plate
              AND is_deleted = false
        """), {"plate": plate})

        db.commit()

        if result.rowcount == 0:
            return {"status": "warning", "message": "Pojazd nie znaleziony lub już usunięty"}

        print(f"[DEBUG SOFT-DELETE] Pojazd {plate} oznaczony jako usunięty przez obywatela")
        return {"status": "success", "message": f"Pojazd {plate} usunięty z Twojego rejestru"}

    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))