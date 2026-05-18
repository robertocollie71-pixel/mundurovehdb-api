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

        print(f"[DEBUG PHONE] Otrzymano: phone={phone}, imie={imie}, nazwisko={nazwisko}")

        # Prosty insert lub update
        query = text("""
            INSERT INTO owners (nr_telefonu_enc, imie, nazwisko, pesel_hash)
            VALUES (:phone, :imie, :nazwisko, 'placeholder')
            ON CONFLICT (nr_telefonu_enc) 
            DO UPDATE SET 
                imie = EXCLUDED.imie,
                nazwisko = EXCLUDED.nazwisko
            RETURNING id
        """)
        
        result = db.execute(query, {"phone": phone, "imie": imie, "nazwisko": nazwisko})
        owner_id = result.scalar()
        db.commit()

        print(f"[DEBUG PHONE] ✅ Zapisano owner ID={owner_id}")
        return {"status": "success", "message": "Dane zapisane", "owner_id": owner_id}

    except Exception as e:
        db.rollback()
        print("[ERROR PHONE]", str(e))
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ====================== CITIZENS (istniejący) ======================
@router.get("/citizens")
async def get_all_citizens_endpoint(request: Request, db: Session = Depends(get_db)):
    print("=== [DEBUG CITIZENS] Otrzymane nagłówki ===")
    print(dict(request.headers))
    print("=== END DEBUG ===")
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
        print(f"[SUCCESS] Zwrócono {len(citizens)} obywateli")
        return citizens
    except Exception as e:
        print("[ERROR] /external/citizens:", str(e))
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
