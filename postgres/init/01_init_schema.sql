-- =============================================
-- MUNDUROVEHDB – SCHEMAT BAZY v1.1 (PoC)
-- PostgreSQL 16 + PostGIS + TimescaleDB + pgcrypto
-- =============================================

-- 1. Włączamy potrzebne rozszerzenia
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 2. Tabela audytu (immutable – nie da się zmodyfikować/usunąć rekordów)
CREATE TABLE audit_log (
    id              BIGSERIAL PRIMARY KEY,
    request_id      UUID NOT NULL,
    user_id         TEXT NOT NULL,                    -- login funkcjonariusza / służba
    service         TEXT NOT NULL,                    -- Policja / Żandarmeria / SG
    action          TEXT NOT NULL,                    -- SEARCH / LOCATION / etc.
    table_name      TEXT,
    record_id       UUID,
    old_data        JSONB,
    new_data        JSONB,
    ip_address      INET,
    user_agent      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Tworzymy partycjonowanie (TimescaleDB)
SELECT create_hypertable('audit_log', 'created_at', chunk_time_interval => INTERVAL '1 day');

-- 3. Właściciele (dane wrażliwe)
CREATE TABLE owners (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pesel_hash          TEXT UNIQUE NOT NULL,                  -- hash SHA-256 + salt
    imie                TEXT,
    nazwisko            TEXT,
    nr_telefonu_enc     BYTEA,                                 -- AES-256 encrypted
    data_urodzenia      DATE,
    access_level        SMALLINT DEFAULT 1,                    -- 1=podstawowy, 2=rozszerzony, 3=pełny
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Pojazdy
CREATE TABLE vehicles (
    id                              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numer_rejestracyjny             TEXT UNIQUE NOT NULL,
    vin                             TEXT UNIQUE,
    owner_id                        UUID REFERENCES owners(id) ON DELETE SET NULL,
    marka_model                     TEXT,
    rok_produkcji                   INT,
    data_waznosci_badania_technicznego DATE,
    created_at                      TIMESTAMPTZ DEFAULT NOW(),
    updated_at                      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_vehicles_rej ON vehicles(numer_rejestracyjny);
CREATE INDEX idx_vehicles_vin ON vehicles(vin);

-- 5. Ubezpieczenia (cache UFG)
CREATE TABLE insurance (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id      UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    nr_polisy       TEXT,
    towarzystwo     TEXT,
    rodzaj          TEXT,                    -- OC / AC / NNW / Assistance
    data_od         DATE,
    data_do         DATE,
    status          TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Lokalizacje (hypertybale – TimescaleDB)
CREATE TABLE owner_locations (
    id              BIGSERIAL,
    owner_id        UUID REFERENCES owners(id),
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    timestamp       TIMESTAMPTZ NOT NULL,
    request_id      UUID NOT NULL,           -- link do audytu
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('owner_locations', 'timestamp', chunk_time_interval => INTERVAL '1 day');

CREATE INDEX idx_location_gist ON owner_locations USING GIST (ST_MakePoint(longitude, latitude));
CREATE INDEX idx_owner_locations_request ON owner_locations(request_id);

-- 7. Funkcje pomocnicze – szyfrowanie/dekryptowanie telefonu
CREATE OR REPLACE FUNCTION encrypt_phone(p_phone TEXT) RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(p_phone, current_setting('mundurovehdb.encryption_key'));
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION decrypt_phone(p_enc BYTEA) RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(p_enc, current_setting('mundurovehdb.encryption_key'));
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 8. Row Level Security + mechanizm DYSKRYMINATORA
ALTER TABLE owners ENABLE ROW LEVEL SECURITY;
ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;
ALTER TABLE insurance ENABLE ROW LEVEL SECURITY;
ALTER TABLE owner_locations ENABLE ROW LEVEL SECURITY;

-- Przykładowa polityka RLS (można rozbudować o ABAC)
CREATE POLICY munduro_rls_owners ON owners
    USING (access_level <= (current_setting('mundurovehdb.user_access_level')::int));

CREATE POLICY munduro_rls_vehicles ON vehicles
    USING (EXISTS (
        SELECT 1 FROM owners o 
        WHERE o.id = vehicles.owner_id 
          AND o.access_level <= (current_setting('mundurovehdb.user_access_level')::int)
    ));

-- Analogiczne polityki dla pozostałych tabel...

-- 9. Trigger do audytu (przykład dla vehicles)
CREATE OR REPLACE FUNCTION audit_trigger() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (request_id, user_id, service, action, table_name, record_id, old_data, new_data, ip_address)
    VALUES (
        current_setting('mundurovehdb.request_id')::uuid,
        current_setting('mundurovehdb.user_id'),
        current_setting('mundurovehdb.service'),
        TG_OP,
        TG_TABLE_NAME,
        NEW.id,
        row_to_json(OLD),
        row_to_json(NEW),
        inet_client_addr()
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_vehicles
    AFTER INSERT OR UPDATE OR DELETE ON vehicles
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();

-- (podobne triggery dla pozostałych tabel)

-- =============================================
-- Gotowe do uruchomienia
-- =============================================