import React, { useState } from 'react';

const App = () => {
  const [step, setStep] = useState('landing');
  const [phone, setPhone] = useState('');

  const handleRegister = () => {
    if (phone.trim()) {
      alert(`✅ Kod SMS wysłany na numer: ${phone}`);
      setStep('panel');
    } else {
      alert('Podaj numer telefonu');
    }
  };

  if (step === 'landing') {
    return (
      <div style={{ maxWidth: '640px', margin: '60px auto', padding: '40px', backgroundColor: 'white', borderRadius: '24px', boxShadow: '0 20px 40px rgba(0,0,0,0.1)' }}>
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <h1 style={{ fontSize: '42px', fontWeight: '700', color: '#10b981' }}>MunduroVehDB</h1>
          <p style={{ fontSize: '24px', color: '#334155' }}>Portal Obywatelski</p>
        </div>

        <h2 style={{ textAlign: 'center', marginBottom: '30px', fontSize: '28px' }}>
          Zarejestruj / zaktualizuj swoje dane
        </h2>

        <div style={{ marginBottom: '30px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#334155' }}>
            Numer telefonu
          </label>
          <input
            type="tel"
            placeholder="123 456 789"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            style={{ width: '100%', padding: '18px', fontSize: '18px', border: '2px solid #e2e8f0', borderRadius: '16px' }}
          />
        </div>

        <button
          onClick={handleRegister}
          style={{ width: '100%', backgroundColor: '#10b981', color: 'white', padding: '18px', fontSize: '20px', fontWeight: '600', border: 'none', borderRadius: '16px', cursor: 'pointer' }}
        >
          Wyślij kod SMS
        </button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1000px', margin: '40px auto', padding: '30px' }}>
      <h2 style={{ fontSize: '32px', fontWeight: '700', marginBottom: '20px' }}>👤 Moje Pojazdy</h2>
      <div style={{ backgroundColor: 'white', padding: '30px', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0,0,0,0.08)' }}>
        <button style={{ marginBottom: '20px', padding: '12px 24px', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '12px', fontWeight: '600' }}>
          + Dodaj nowy pojazd
        </button>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
              <th style={{ textAlign: 'left', padding: '16px 8px' }}>Numer rejestracyjny</th>
              <th style={{ textAlign: 'left', padding: '16px 8px' }}>Marka / Model</th>
              <th style={{ textAlign: 'left', padding: '16px 8px' }}>Badanie techniczne</th>
              <th style={{ textAlign: 'left', padding: '16px 8px' }}>Akcje</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
              <td style={{ padding: '20px 8px' }}>WA12345</td>
              <td style={{ padding: '20px 8px' }}>Toyota Corolla</td>
              <td style={{ padding: '20px 8px', color: '#10b981' }}>2027-03-15</td>
              <td style={{ padding: '20px 8px' }}>
                <button style={{ color: '#2563eb', marginRight: '16px' }}>Edytuj</button>
                <button style={{ color: '#ef4444' }}>Usuń</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default App;