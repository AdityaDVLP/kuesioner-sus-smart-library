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

1. Push folder `project` ke repository GitHub.

2. Di [Render](https://render.com), buat **New Web Service** dan pilih repository.

3. Pengaturan:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app` (atau biarkan Render membaca `Procfile`)

4. Tambahkan environment variable:
   - `SECRET_KEY` = string acak panjang

5. Klik **Deploy**.

**Catatan:** Filesystem di Render tidak permanen. Data CSV bisa hilang saat redeploy. Untuk penyimpanan jangka panjang, gunakan Persistent Disk di Render atau backup CSV secara berkala.

## Cara Deploy ke Railway.app

### Prasyarat (sekali, di PowerShell interaktif)

```powershell
railway login
gh auth login
```

### Otomatis (setelah login)

```powershell
cd c:\Users\USER\project
.\deploy-railway.ps1
```

### Manual di dashboard Railway

1. **New Project** → **Deploy from GitHub repo** → pilih repo `kuesioner-sus-smart-library`
2. **Settings** → **Build Command:** `pip install -r requirements.txt`
3. **Settings** → **Start Command:** `gunicorn app:app` (atau biarkan `railway.json` / `nixpacks.toml`)
4. **Variables:**
   - `SECRET_KEY` = string acak panjang
   - `DATA_DIR` = `/data` (jika memakai Volume)
5. **Volumes** (Free Tier): mount path `/data`, size 1 GB — agar CSV tidak hilang saat redeploy
6. **Networking** → **Generate Domain**

### Optimasi Free Tier

- Python 3.11.9 via `runtime.txt`
- Gunicorn: 1 worker, 2 threads (`nixpacks.toml` / `railway.json`)
- Restart on failure, healthcheck `/`
