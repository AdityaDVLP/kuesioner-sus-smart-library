# Kuesioner SUS - Smart Library RFID

Aplikasi web Flask untuk kuesioner System Usability Scale (SUS) dengan penyimpanan data ke CSV.

## Struktur Project

```
project/
├── app.py
├── requirements.txt
├── database_kuesioner.csv   (otomatis dibuat saat submit pertama)
├── Procfile
├── README.md
└── templates/
    └── index.html
```

## Cara Menjalankan Lokal

1. Buka terminal di folder `project`.

2. (Opsional) Buat virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependensi:

```powershell
pip install -r requirements.txt
```

4. Jalankan aplikasi:

```powershell
python app.py
```

5. Buka browser: http://127.0.0.1:5000

**Tips:**
- Jangan buka `database_kuesioner.csv` di Excel saat submit (hindari file lock).
- Untuk mode development: `$env:FLASK_DEBUG="1"; python app.py`

## Cara Deploy ke Render.com

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/AdityaDVLP/kuesioner-sus-smart-library)

1. Repository GitHub: https://github.com/AdityaDVLP/kuesioner-sus-smart-library

2. Klik tombol **Deploy to Render** di atas (atau buat **New Web Service** / **New Blueprint** di dashboard).

3. Pengaturan:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app` (atau biarkan Render membaca `Procfile`)

4. Tambahkan environment variable:
   - `SECRET_KEY` = string acak panjang

5. Klik **Deploy**.

**Catatan:** Filesystem di Render tidak permanen. Data CSV bisa hilang saat redeploy. Untuk penyimpanan jangka panjang, gunakan Persistent Disk di Render atau backup CSV secara berkala.
