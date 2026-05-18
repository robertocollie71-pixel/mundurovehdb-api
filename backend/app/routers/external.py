from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.db.session import get_db

router = APIRouter(prefix="/external", tags=["external"])

@router.get("/citizens")
async def get_all_citizens_endpoint(request: Request, db: Session = Depends(get_db)):
    print("=== [DEBUG] Otrzymane nagłówki ===")
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
