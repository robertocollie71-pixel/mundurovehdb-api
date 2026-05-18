from sqlalchemy.orm import Session
from sqlalchemy import text

def get_vehicle_by_registration(db: Session, numer_rejestracyjny: str, access_level: int):
    """Zwraca pojazd + pełne dane właściciela (z telefonem)"""
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
    
    result = db.execute(query, {"rej": numer_rejestracyjny.upper(), "access_level": access_level}).fetchone()
    
    if not result:
        return None
    
    print("=== DEBUG CRUD === phone z bazy =", result[7] if result else "BRAK")
    
    return {
        "numer_rejestracyjny": result[0],
        "vin": result[1],
        "marka_model": result[2],
        "rok_produkcji": result[3],
        "data_waznosci_badania": result[4],
        "wlasciciel": {
            "imie": result[5],
            "nazwisko": result[6],
            "phone": result[7] if result[7] is not None else ""
        }
    }