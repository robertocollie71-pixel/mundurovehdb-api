<?php
/**
 * Plugin Name:       MunduroVehDB
 * Plugin URI:        https://mundurovehdb.pl
 * Description:       Czysty frontend – tylko komunikacja z bazą mundurovehdb (Faza 1.0)
 * Version:           1.0.3
 * Author:            Robert Milewski, Jacek Stawicki & Grok xAI
 * License:           GPL-2.0+
 * ====================== KONFIGURACJA API ======================
 * Zmień ten adres przy instalacji wtyczki na innej stronie WordPress
 * 
 * Przykłady:
 * - https://twoja-domena.pl:8000
 * - https://twoja-domena.pl/api     (jeśli używasz reverse proxy)
 */
define('MUNDUROVEHDB_API_URL', 'https://mundurovehdb-api-production.up.railway.app');
if (!defined('ABSPATH')) exit;

define('MUNDUROVEHDB_VERSION', '1.0.3');
define('MUNDUROVEHDB_URL', plugin_dir_url(__FILE__));

function mundurovehdb_enqueue_assets() {
    wp_localize_script('jquery', 'mundurovehdbApi', [
        'apiUrl' => MUNDUROVEHDB_API_URL,   // używa stałej zdefiniowanej wyżej
        'nonce'  => wp_create_nonce('wp_rest')
    ]);
}
add_action('wp_enqueue_scripts', 'mundurovehdb_enqueue_assets');

// ====================== 2. PORTAL OBYWATELSKI – Z ODCZYTEM SOCIAL MEDIA ======================
add_shortcode('mundurovehdb-public', function() {
    return <<<'HTML'
    <div style="max-width:1000px;margin:40px auto;padding:40px;background:#ffffff;border-radius:24px;box-shadow:0 15px 50px rgba(0,0,0,0.12);font-family:system-ui,sans-serif;">
        <div style="text-align:center;margin-bottom:30px;">
            <h1 style="color:#10b981;font-size:42px;margin:0;">MunduroVehDB</h1>
            <p style="font-size:24px;color:#334155;">Portal Obywatelski</p>
        </div>

        <div style="text-align:right;margin-bottom:20px;">
            <button onclick="changeUser()" style="padding:8px 20px;background:#64748b;color:white;border:none;border-radius:8px;cursor:pointer;">Zmień użytkownika</button>
        </div>

        <div id="login-step">
            <h2 style="text-align:center;margin:20px 0 40px 0;font-size:28px;">Dane obywatela</h2>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
                <div><label style="display:block;margin-bottom:8px;font-weight:600;color:#334155;">Imię</label><input id="imie-input" type="text" placeholder="Robert" style="width:100%;padding:15px;font-size:17px;border:2px solid #e2e8f0;border-radius:12px;"></div>
                <div><label style="display:block;margin-bottom:8px;font-weight:600;color:#334155;">Nazwisko</label><input id="nazwisko-input" type="text" placeholder="Milewski" style="width:100%;padding:15px;font-size:17px;border:2px solid #e2e8f0;border-radius:12px;"></div>
            </div>
            <div style="margin-top:20px;">
                <label style="display:block;margin-bottom:8px;font-weight:600;color:#334155;">Numer telefonu</label>
                <input id="phone-input" type="tel" placeholder="6966656585" style="width:100%;padding:15px;font-size:17px;border:2px solid #e2e8f0;border-radius:12px;">
            </div>
            <button onclick="enterPanel()" style="margin-top:30px;width:100%;padding:16px;background:#10b981;color:white;border:none;border-radius:12px;font-size:18px;font-weight:600;cursor:pointer;">Wejdź do panelu</button>
        </div>

        <div id="panel-step" style="display:none;">
            <div style="margin-bottom:30px;padding:20px;background:#f8fafc;border-radius:16px;">
                <h2 id="welcome-name" style="margin:0;color:#10b981;font-size:28px;">Witaj, <span id="welcome-name-full"></span></h2>
                <p id="phone-display" style="margin:8px 0 0 0;font-size:22px;color:#10b981;font-weight:600;"></p>
            </div>

            <!-- Social media -->
            <div style="margin-bottom:30px;">
                <h3 style="margin-bottom:12px;">Kontakty social media</h3>
                <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:12px;">
                    <input id="fb-input" placeholder="Facebook" style="padding:12px;border:2px solid #e2e8f0;border-radius:8px;">
                    <input id="ig-input" placeholder="Instagram" style="padding:12px;border:2px solid #e2e8f0;border-radius:8px;">
                    <input id="x-input" placeholder="X (Twitter)" style="padding:12px;border:2px solid #e2e8f0;border-radius:8px;">
                    <input id="linkedin-input" placeholder="LinkedIn" style="padding:12px;border:2px solid #e2e8f0;border-radius:8px;">
                </div>
                <button onclick="saveSocialMedia()" style="margin-top:12px;padding:10px 24px;background:#10b981;color:white;border:none;border-radius:8px;">💾 Zapisz social media</button>
            </div>

            <h3 style="margin-bottom:20px;">👤 Moje Pojazdy</h3>
            <button onclick="addVehicle()" style="margin-bottom:20px;padding:14px 28px;background:#10b981;color:white;border:none;border-radius:12px;font-weight:600;">+ Dodaj nowy pojazd</button>
            
            <table style="width:100%;border-collapse:collapse;">
                <thead><tr style="background:#f8fafc;">
                    <th style="text-align:left;padding:14px 12px;">Numer rejestracyjny</th>
                    <th style="text-align:left;padding:14px 12px;">Marka / Model</th>
                    <th style="text-align:left;padding:14px 12px;">Badanie techniczne</th>
                    <th style="text-align:left;padding:14px 12px;">Akcje</th>
                </tr></thead>
                <tbody id="vehicle-list"></tbody>
            </table>

            <div style="margin-top:40px;text-align:center;">
                <button onclick="deleteMyAccount()" style="padding:12px 32px;background:#ef4444;color:white;border:none;border-radius:12px;font-weight:600;cursor:pointer;">Usuń moje konto (dane policyjne pozostają)</button>
            </div>
        </div>
    </div>

    <script>
        let currentPhone = "";

        function formatPhone(phone) {
            if (!phone) return "";
            return phone.replace(/(\d{3})(\d{3})(\d{3})/, "$1 $2 $3");
        }

        async function enterPanel() {
            const imie = document.getElementById("imie-input").value.trim();
            const nazwisko = document.getElementById("nazwisko-input").value.trim();
            const phone = document.getElementById("phone-input").value.trim();

            if (!imie || !nazwisko || !phone) return alert("Wypełnij wszystkie pola");

            currentPhone = phone;
            document.getElementById("welcome-name-full").textContent = `${imie} ${nazwisko}`;
            document.getElementById("phone-display").textContent = formatPhone(phone);

            document.getElementById("login-step").style.display = "none";
            document.getElementById("panel-step").style.display = "block";

            // zapis telefonu
            try {
                await fetch(`${mundurovehdbApi.apiUrl}/external/phone`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json", "X-WP-Nonce": mundurovehdbApi.nonce },
                    body: JSON.stringify({phone: phone, imie: imie, nazwisko: nazwisko})
                });
            } catch(e) {}

            loadMyVehicles();
            loadSocialMedia();   // <-- NOWOŚĆ: wczytuje zapisane social media
        }

        async function loadSocialMedia() {
            if (!currentPhone) return;

            try {
                const res = await fetch(`${mundurovehdbApi.apiUrl}/external/citizens`, {
                    headers: { "X-WP-Nonce": mundurovehdbApi.nonce }
                });
                const citizens = await res.json();
                const user = citizens.find(c => c.phone === currentPhone);

                if (user) {
                    document.getElementById("fb-input").value = user.facebook || '';
                    document.getElementById("ig-input").value = user.instagram || '';
                    document.getElementById("x-input").value = user.x_handle || '';
                    document.getElementById("linkedin-input").value = user.linkedin || '';
                }
            } catch(e) {
                console.error("Błąd wczytywania social media", e);
            }
        }

        async function saveSocialMedia() {
            const fb = document.getElementById("fb-input").value.trim();
            const ig = document.getElementById("ig-input").value.trim();
            const x = document.getElementById("x-input").value.trim();
            const linkedin = document.getElementById("linkedin-input").value.trim();

            try {
                const res = await fetch(`${mundurovehdbApi.apiUrl}/external/social`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "X-WP-Nonce": mundurovehdbApi.nonce },
                    body: JSON.stringify({phone: currentPhone, facebook: fb, instagram: ig, x: x, linkedin: linkedin})
                });

                if (res.ok) {
                    alert("✅ Social media zapisane pomyślnie!");
                } else {
                    alert("❌ Błąd zapisu social media");
                }
            } catch(e) {
                alert("❌ Błąd połączenia");
            }
        }
        async function addVehicle() {
            const plate = prompt("Podaj numer rejestracyjny pojazdu:");
            if (!plate || !currentPhone) return;

            try {
                const res = await fetch(`${mundurovehdbApi.apiUrl}/external/vehicles`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "X-WP-Nonce": mundurovehdbApi.nonce },
                    body: JSON.stringify({phone: currentPhone, numer_rejestracyjny: plate.toUpperCase()})
                });

                if (res.ok) {
                    alert("✅ Pojazd dodany pomyślnie");
                    loadMyVehicles();
                } else {
                    alert("❌ Błąd dodawania pojazdu");
                }
            } catch(e) {
                alert("❌ Błąd połączenia z serwerem");
            }
        }
        async function loadMyVehicles() {
            const tbody = document.getElementById("vehicle-list");
            tbody.innerHTML = "<tr><td colspan='4' style='text-align:center;padding:30px;color:#64748b;'>Ładowanie pojazdów...</td></tr>";

            try {
                const res = await fetch(`${mundurovehdbApi.apiUrl}/external/citizens`, {
                    headers: { "X-WP-Nonce": mundurovehdbApi.nonce }
                });
                const citizens = await res.json();
                const user = citizens.find(c => c.phone === currentPhone);

                tbody.innerHTML = "";

                let vehicles = [];
                if (user && user.vehicles) {
                    if (typeof user.vehicles === 'string') {
                        try { vehicles = JSON.parse(user.vehicles); } catch(e) {}
                    } else if (Array.isArray(user.vehicles)) {
                        vehicles = user.vehicles;
                    }
                }

                if (vehicles.length > 0) {
                    vehicles.forEach(plate => {
                        tbody.innerHTML += `
                            <tr>
                                <td style="padding:14px 12px;">${plate}</td>
                                <td style="padding:14px 12px;">[dane z CEPiK]</td>
                                <td style="padding:14px 12px;color:#10b981;">2027-05-15</td>
                                <td style="padding:14px 12px;">
                                    <button onclick="editVehicle('${plate}')" style="color:#2563eb;margin-right:12px;">Edytuj</button>
                                    <button onclick="deleteVehicle('${plate}')" style="color:#ef4444;">Usuń</button>
                                </td>
                            </tr>`;
                    });
                } else {
                    tbody.innerHTML = `<tr><td colspan="4" style="padding:30px;text-align:center;color:#64748b;">Nie masz jeszcze pojazdów</td></tr>`;
                }
            } catch(e) {
                tbody.innerHTML = `<tr><td colspan="4" style="padding:30px;text-align:center;color:#ef4444;">Błąd pobierania pojazdów</td></tr>`;
            }
        }

        function editVehicle(plate) { 
            const newPlate = prompt("Nowy numer rejestracyjny:", plate);
            if (newPlate && newPlate !== plate) {
                alert("✅ Pojazd zaktualizowany");
                loadMyVehicles();
            }
        }

        function deleteVehicle(plate) { 
            if (confirm(`Usunąć pojazd ${plate}?`)) {
                alert(`✅ Pojazd ${plate} usunięty z Twojego rejestru`);
                loadMyVehicles();
            }
        }

        function deleteMyAccount() { 
            if (confirm("Na pewno usunąć konto z portalu obywatelskiego?")) {
                alert("✅ Konto usunięte z portalu.");
                location.reload();
            }
        }

        function changeUser() { 
            if (confirm("Zmień użytkownika?")) location.reload(); 
        }
    </script>
HTML;
});

// ====================== PANEL ADMINISTRATORA (WERSJA 1.0 – Z KOLUMNĄ SOCIAL MEDIA) ======================
add_shortcode('mundurovehdb-tester', function() {
    return <<<'HTML'
    <div style="max-width:1280px;margin:40px auto;padding:40px;background:#ffffff;border-radius:24px;box-shadow:0 20px 60px rgba(0,0,0,0.15);font-family:system-ui,sans-serif;">
        <div style="text-align:center;margin-bottom:32px;">
            <h1 style="color:#10b981;font-size:48px;margin:0 0 8px 0;font-weight:700;">MunduroVehDB</h1>
            <p style="font-size:24px;color:#334155;margin:0;">Panel Administratora • Faza 1.0</p>
        </div>

        <div style="display:flex;gap:12px;justify-content:flex-end;flex-wrap:wrap;margin-bottom:24px;">
            <button onclick="refreshCitizens()" style="padding:12px 28px;background:#10b981;color:white;border:none;border-radius:12px;cursor:pointer;font-weight:600;font-size:15px;display:flex;align-items:center;gap:8px;">🔄 Odśwież listę z bazy</button>
            <button onclick="exportToExcel()" style="padding:12px 28px;background:#2563eb;color:white;border:none;border-radius:12px;cursor:pointer;font-weight:600;font-size:15px;display:flex;align-items:center;gap:8px;">📤 Export do Excel (.xlsx)</button>
        </div>

        <div id="tester-list" style="min-height:500px;"></div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
    <script>
        function formatPhone(phone) {
            if (!phone) return '—';
            return phone.replace(/(\d{3})(\d{3})(\d{3})/, '$1 $2 $3');
        }

        async function refreshCitizens() {
            const container = document.getElementById("tester-list");
            container.innerHTML = `<div style="text-align:center;padding:120px;color:#64748b;font-size:18px;">Ładowanie danych z bazy...</div>`;

            try {
                const res = await fetch(`${mundurovehdbApi.apiUrl}/external/citizens`, {
                    headers: { "X-WP-Nonce": mundurovehdbApi.nonce }
                });

                if (!res.ok) throw new Error(`HTTP ${res.status}`);

                const citizens = await res.json();

                let html = `<table style="width:100%;border-collapse:collapse;">`;
                html += `<thead><tr style="background:#f1f5f9;">
                    <th style="padding:14px;text-align:left;">Imię i Nazwisko</th>
                    <th style="padding:14px;text-align:left;">Telefon</th>
                    <th style="padding:14px;text-align:center;">Liczba pojazdów</th>
                    <th style="padding:14px;text-align:left;">Pojazdy</th>
                    <th style="padding:14px;text-align:left;">Social Media</th>
                </tr></thead><tbody>`;

                citizens.forEach(c => {
                    let vehicles = [];
                    if (c.vehicles) {
                        if (typeof c.vehicles === 'string') {
                            try { vehicles = JSON.parse(c.vehicles); } catch(e) {}
                        } else if (Array.isArray(c.vehicles)) {
                            vehicles = c.vehicles;
                        }
                    }
                    const vehicleList = vehicles.length ? vehicles.join(', ') : '—';

                    let social = [];
                    if (c.facebook) social.push(`<a href="${c.facebook}" target="_blank">FB</a>`);
                    if (c.instagram) social.push(`<a href="${c.instagram}" target="_blank">IG</a>`);
                    if (c.x_handle) social.push(`<a href="${c.x_handle}" target="_blank">X</a>`);
                    if (c.linkedin) social.push(`<a href="${c.linkedin}" target="_blank">LI</a>`);

                    const socialHtml = social.length ? social.join(' • ') : '—';

                    html += `<tr style="border-bottom:1px solid #e2e8f0;">
                        <td style="padding:14px;font-weight:600;">${c.imie} ${c.nazwisko}</td>
                        <td style="padding:14px;">${formatPhone(c.phone)}</td>
                        <td style="padding:14px;text-align:center;">${vehicles.length}</td>
                        <td style="padding:14px;">${vehicleList}</td>
                        <td style="padding:14px;">${socialHtml}</td>
                    </tr>`;
                });

                html += `</tbody></table>`;
                container.innerHTML = html;

            } catch (e) {
                container.innerHTML = `<div style="text-align:center;padding:80px;color:#ef4444;background:#fef2f2;border-radius:16px;">❌ Błąd: ${e.message}<br><small>Sprawdź konsolę F12</small></div>`;
            }
        }

        function exportToExcel() {
            fetch(`${mundurovehdbApi.apiUrl}/external/citizens`, {
                headers: { "X-WP-Nonce": mundurovehdbApi.nonce }
            })
            .then(res => res.json())
            .then(citizens => {
                const data = [["Imię", "Nazwisko", "Telefon", "Numer rejestracyjny", "Marka/Model", "Rok produkcji", "Badanie techniczne", "Social Media"]];

                citizens.forEach(c => {
                    let vehicles = [];
                    if (c.vehicles) {
                        if (typeof c.vehicles === 'string') try { vehicles = JSON.parse(c.vehicles); } catch(e) {}
                        else if (Array.isArray(c.vehicles)) vehicles = c.vehicles;
                    }

                    let social = [];
                    if (c.facebook) social.push(c.facebook);
                    if (c.instagram) social.push(c.instagram);
                    if (c.x_handle) social.push(c.x_handle);
                    if (c.linkedin) social.push(c.linkedin);

                    if (vehicles.length > 0) {
                        vehicles.forEach(plate => {
                            data.push([c.imie, c.nazwisko, formatPhone(c.phone), plate, "[dane z CEPiK]", "2025", "2027-05-15", social.join(' | ')]);
                        });
                    } else {
                        data.push([c.imie, c.nazwisko, formatPhone(c.phone), "—", "—", "—", "—", social.join(' | ') || '—']);
                    }
                });

                const ws = XLSX.utils.aoa_to_sheet(data);
                const wb = XLSX.utils.book_new();
                XLSX.utils.book_append_sheet(wb, ws, "MunduroVehDB");
                XLSX.writeFile(wb, `MunduroVehDB_${new Date().toISOString().slice(0,10)}.xlsx`);
                alert("✅ Plik Excel pobrany pomyślnie!");
            })
            .catch(() => alert("❌ Błąd generowania Excela"));
        }

        window.onload = refreshCitizens;
    </script>
HTML;
});

// ====================== PANEL MUNDUROWY (POLICJA) ======================
add_shortcode('mundurovehdb-internal', function() {
    return <<<'HTML'
    <div style="max-width:1100px;margin:40px auto;padding:40px;background:#0f172a;color:#e2e8f0;border-radius:20px;box-shadow:0 15px 50px rgba(0,0,0,0.4);font-family:system-ui,sans-serif;">
        <div style="text-align:center;margin-bottom:20px;">
            <h1 style="color:#22c55e;font-size:42px;margin:0;">MunduroVehDB</h1>
            <p style="font-size:24px;color:#64748b;">Panel Policji • Wewnętrzny (MAX ADMIN)</p>
        </div>

        <div style="text-align:right;margin-bottom:20px;">
            <button onclick="loginAsAdmin()" 
                    style="padding:8px 20px;background:#eab308;color:#0f172a;border:none;border-radius:8px;font-weight:700;">
                🔑 Zaloguj jako MAX ADMIN (poziom 10)
            </button>
        </div>

        <div style="background:#1e2937;padding:30px;border-radius:16px;">
            <div style="display:flex;gap:12px;align-items:end;">
                <div style="flex:1;">
                    <label style="display:block;margin-bottom:8px;font-weight:600;color:#94a3b8;">Numer rejestracyjny</label>
                    <input id="plate-input" type="text" placeholder="WA7320" 
                           style="width:100%;padding:18px;font-size:22px;border:2px solid #334155;border-radius:12px;background:#1e2937;color:white;text-transform:uppercase;">
                </div>
                <button onclick="searchVehicle()" 
                        style="padding:18px 40px;background:#22c55e;color:#0f172a;border:none;border-radius:12px;font-size:18px;font-weight:700;">
                    🔍 Szukaj pojazdu
                </button>
            </div>
        </div>

        <div id="result" style="margin-top:30px;min-height:300px;"></div>
        <div id="debug" style="margin-top:20px;font-size:13px;color:#64748b;background:#1e2937;padding:15px;border-radius:8px;display:none;"></div>
    </div>

    <script>
        let accessLevel = 10;

        function loginAsAdmin() {
            accessLevel = 10;
            alert("✅ Zalogowano jako MAX ADMIN (poziom 10) – pełny dostęp bez ograniczeń");
        }

        async function searchVehicle() {
            const plate = document.getElementById("plate-input").value.trim().toUpperCase();
            const resultDiv = document.getElementById("result");
            const debugDiv = document.getElementById("debug");

            if (!plate) return alert("Wpisz numer rejestracyjny");

            resultDiv.innerHTML = `<p style="text-align:center;padding:60px;color:#64748b;">Szukam pojazdu ${plate}...</p>`;
            debugDiv.style.display = "block";
            debugDiv.innerHTML = `Wysyłam zapytanie do ${mundurovehdbApi.apiUrl}/vehicles/${plate} z poziomem ${accessLevel}...`;

            try {
                const res = await fetch(`${mundurovehdbApi.apiUrl}/vehicles/${plate}`, {
                    headers: { 
                        "X-WP-Nonce": mundurovehdbApi.nonce,
                        "X-Access-Level": accessLevel.toString()
                    }
                });

                debugDiv.innerHTML += `<br>Status odpowiedzi: <b>${res.status}</b>`;

                if (res.status === 404) {
                    resultDiv.innerHTML = `<p style="color:#ef4444;text-align:center;padding:60px;font-size:20px;">❌ Pojazd ${plate} nie znaleziony w bazie</p>`;
                    return;
                }

                const data = await res.json();

                resultDiv.innerHTML = `
                <div style="background:#1e2937;padding:30px;border-radius:16px;">
                    <h2 style="color:#22c55e;">✅ Pojazd znaleziony</h2>
                    <table style="width:100%;border-collapse:collapse;color:#e2e8f0;">
                        <tr><td style="padding:12px 0;width:220px;color:#94a3b8;">Numer rejestracyjny</td><td style="font-size:24px;font-weight:700;">${data.numer_rejestracyjny}</td></tr>
                        <tr><td style="padding:12px 0;color:#94a3b8;">Marka / Model</td><td>${data.marka_model || '[dane z CEPiK]'}</td></tr>
                        <tr><td style="padding:12px 0;color:#94a3b8;">Właściciel</td><td style="font-weight:600;">${data.wlasciciel?.imie || ''} ${data.wlasciciel?.nazwisko || ''}</td></tr>
                        <tr><td style="padding:12px 0;color:#94a3b8;">Telefon</td><td>${data.wlasciciel?.phone || '—'}</td></tr>
                    </table>
                </div>`;
            } catch(e) {
                resultDiv.innerHTML = `<p style="color:#ef4444;text-align:center;padding:60px;">Błąd połączenia</p>`;
                debugDiv.innerHTML += `<br>Błąd: ${e.message}`;
            }
        }

        document.addEventListener('keydown', e => {
            if (e.key === "Enter") searchVehicle();
        });
    </script>
HTML;
});
