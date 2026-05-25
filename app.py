import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ganti-dengan-string-rahasia-untuk-production")

# ---------------------------------------------------------------------------
# Supabase config
# ---------------------------------------------------------------------------
TABLE_NAME = "data_kuesionerblackbox"

_supabase_client = None


def get_supabase():
    """Return a cached Supabase client (singleton)."""
    global _supabase_client
    if _supabase_client is None:
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_KEY", "")
        if not url or not key:
            # Coba load ulang .env jika belum terbaca
            load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)
            url = os.environ.get("SUPABASE_URL", "")
            key = os.environ.get("SUPABASE_KEY", "")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL dan SUPABASE_KEY harus diset di environment variables."
            )
        _supabase_client = create_client(url, key)
    return _supabase_client



# ---------------------------------------------------------------------------
# Skala, Aspek, dan Pertanyaan
# ---------------------------------------------------------------------------
SKALA_LABEL = {
    1: "Sangat Tidak Setuju",
    2: "Tidak Setuju",
    3: "Netral",
    4: "Setuju",
    5: "Sangat Setuju",
}

ASPEK = [
    "Fungsionalitas Sistem",
    "Keandalan Sistem",
    "Kemudahan Penggunaan",
    "Kejelasan Antarmuka",
    "Kesesuaian Kebutuhan",
]

PERTANYAAN_MAHASISWA = [
    # Aspek 1: Fungsionalitas Sistem
    "Sistem dapat membaca KTM ITK saya dengan benar saat ditempelkan pada RFID reader.",
    "Sistem berhasil mendeteksi buku melalui tag RFID yang tertanam pada buku.",
    "Proses identifikasi KTM dan buku oleh sistem RFID berjalan sesuai dengan yang diharapkan.",
    "Sistem berhasil menampilkan data buku dan identitas mahasiswa setelah proses pemindaian.",
    # Aspek 2: Keandalan Sistem
    "Sistem tidak mengalami error atau kegagalan saat saya melakukan pemindaian KTM maupun buku.",
    "KTM saya selalu berhasil terbaca setiap kali ditempelkan pada reader tanpa perlu mengulang.",
    "Tag RFID buku selalu terdeteksi secara konsisten oleh sistem saat proses pemindaian.",
    "Sistem tetap berjalan stabil meskipun saya menggunakannya berulang kali dalam satu sesi.",
    # Aspek 3: Kemudahan Penggunaan
    "Saya dapat menggunakan sistem Smart Library RFID tanpa memerlukan bantuan orang lain.",
    "Langkah-langkah penggunaan sistem pemantauan mudah dipahami dan diikuti.",
    "Saya tidak merasa kesulitan saat pertama kali menggunakan sistem ini.",
    "Secara keseluruhan, sistem ini mudah dioperasikan oleh mahasiswa.",
    # Aspek 4: Kejelasan Antarmuka
    "Informasi yang ditampilkan pada layar sistem jelas dan mudah dibaca.",
    "Pesan konfirmasi dan notifikasi pada sistem mudah dipahami.",
    "Hasil pemantauan dan identifikasi buku ditampilkan dengan jelas di antarmuka.",
    "Pesan kesalahan yang muncul saat terjadi error memberikan informasi yang cukup jelas.",
    # Aspek 5: Kesesuaian Kebutuhan
    "Sistem Smart Library RFID membantu mempermudah proses pemantauan buku di perpustakaan.",
    "Sistem ini sesuai dengan kebutuhan saya sebagai mahasiswa dalam mengakses layanan perpustakaan.",
    "Penggunaan RFID membuat proses identifikasi buku lebih cepat dibandingkan cara manual.",
    "Secara keseluruhan, sistem ini memenuhi harapan saya terhadap layanan perpustakaan modern.",
]

PERTANYAAN_PUSTAKAWAN = [
    # Aspek 1: Fungsionalitas Sistem
    "Sistem dapat membaca UID KTM mahasiswa dengan benar dan menampilkan data yang sesuai.",
    "Sistem berhasil mendeteksi dan mengidentifikasi tag RFID buku sesuai data di database.",
    "Proses pencatatan data pemantauan buku oleh sistem berjalan sesuai fungsinya.",
    "Sistem berhasil mencatat log aktivitas identifikasi KTM dan buku secara otomatis.",
    # Aspek 2: Keandalan Sistem
    "Sistem tidak mengalami error atau crash saat digunakan secara berulang dalam satu sesi pengujian.",
    "HF RFID Reader membaca KTM secara konsisten tanpa kegagalan pembacaan.",
    "UHF RFID Reader mendeteksi tag buku secara konsisten pada setiap pemindaian.",
    "Data pemantauan yang dicatat oleh sistem selalu akurat dan tidak ada data yang hilang.",
    # Aspek 3: Kemudahan Penggunaan
    "Saya dapat mengoperasikan sistem Smart Library RFID tanpa kesulitan berarti.",
    "Menu dan fitur pada modul pustakawan mudah ditemukan dan diakses.",
    "Proses pendaftaran KTM atau tag RFID baru mudah dilakukan melalui sistem.",
    "Secara keseluruhan, sistem ini mudah digunakan dalam operasional perpustakaan sehari-hari.",
    # Aspek 4: Kejelasan Antarmuka
    "Data mahasiswa dan buku ditampilkan dengan jelas pada dashboard pustakawan.",
    "Laporan pemantauan dan ringkasan data mudah dibaca dan dipahami.",
    "Informasi status identifikasi buku terlihat jelas pada antarmuka sistem.",
    "Pesan error dan notifikasi sistem memberikan informasi yang mudah ditindaklanjuti.",
    # Aspek 5: Kesesuaian Kebutuhan
    "Sistem Smart Library RFID membantu meningkatkan efisiensi pemantauan koleksi perpustakaan.",
    "Fitur-fitur yang tersedia sesuai dengan kebutuhan operasional pustakawan.",
    "Sistem ini mengurangi pekerjaan manual dan mempercepat proses pemantauan.",
    "Secara keseluruhan, sistem ini memenuhi kebutuhan perpustakaan dalam memantau dan mengidentifikasi koleksi buku.",
]

def get_pertanyaan(role):
    if role == "Pustakawan":
        return PERTANYAAN_PUSTAKAWAN
    return PERTANYAAN_MAHASISWA


def build_aspek_groups(pertanyaan_list):
    groups = []
    idx = 0
    for aspek in ASPEK:
        items = []
        for _ in range(4):
            nomor = idx + 1
            items.append({
                "nomor": nomor,
                "kode": f"P{nomor}",
                "teks": pertanyaan_list[idx],
            })
            idx += 1
        groups.append({"nama": aspek, "pertanyaan": items})
    return groups


# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------
def hitung_statistik(filter_role=None):
    """Baca data dari Supabase dan hitung jumlah responden per role."""
    try:
        sb = get_supabase()
        response = sb.table(TABLE_NAME).select("role").execute()
        data = response.data or []
    except Exception:
        return {"total": 0, "mahasiswa": 0, "pustakawan": 0}

    if not data:
        return {"total": 0, "mahasiswa": 0, "pustakawan": 0}

    mahasiswa = sum(1 for row in data if row.get("role") == "Mahasiswa")
    pustakawan = sum(1 for row in data if row.get("role") == "Pustakawan")
    total = len(data)

    if filter_role == "Mahasiswa":
        total = mahasiswa
    elif filter_role == "Pustakawan":
        total = pustakawan

    return {"total": total, "mahasiswa": mahasiswa, "pustakawan": pustakawan}


def simpan_ke_supabase(data_dict):
    """Insert satu baris data kuesioner ke Supabase."""
    try:
        sb = get_supabase()
        # Supabase column names are lowercase
        row = {
            "nama": data_dict["Nama"],
            "role": data_dict["Role"],
            "tanggal": data_dict["Tanggal"],
        }
        for i in range(1, 21):
            row[f"p{i}"] = data_dict[f"P{i}"]

        sb.table(TABLE_NAME).insert(row).execute()
        return True, "Data berhasil disimpan."
    except Exception as e:
        return False, f"Gagal menyimpan data: {str(e)}"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    role = request.args.get("role", "Mahasiswa")
    if role not in ("Mahasiswa", "Pustakawan"):
        role = "Mahasiswa"

    filter_stat = request.args.get("filter", "")
    stat = hitung_statistik(filter_stat if filter_stat else None)

    pertanyaan = get_pertanyaan(role)
    aspek_groups = build_aspek_groups(pertanyaan)
    tanggal_hari_ini = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template(
        "index.html",
        role=role,
        aspek_groups=aspek_groups,
        skala=SKALA_LABEL,
        tanggal=tanggal_hari_ini,
        stat=stat,
        filter_stat=filter_stat,
    )


@app.route("/submit", methods=["POST"])
def submit():
    nama = (request.form.get("nama") or "").strip()
    role = request.form.get("role", "Mahasiswa")
    tanggal = request.form.get("tanggal") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not nama:
        flash("Nama wajib diisi.", "danger")
        return redirect(url_for("index", role=role))

    if role not in ("Mahasiswa", "Pustakawan"):
        flash("Role tidak valid.", "danger")
        return redirect(url_for("index"))

    jawaban = {}
    for i in range(1, 21):
        kode = f"P{i}"
        nilai_str = request.form.get(kode)
        if nilai_str is None or nilai_str == "":
            flash(f"Pertanyaan {kode} belum dijawab. Semua pertanyaan wajib diisi.", "danger")
            return redirect(url_for("index", role=role))

        try:
            nilai = int(nilai_str)
        except ValueError:
            flash(f"Jawaban {kode} tidak valid.", "danger")
            return redirect(url_for("index", role=role))

        if nilai < 1 or nilai > 5:
            flash(f"Jawaban {kode} harus antara 1 sampai 5.", "danger")
            return redirect(url_for("index", role=role))

        jawaban[kode] = nilai

    data = {"Nama": nama, "Role": role, "Tanggal": tanggal, **jawaban}

    try:
        berhasil, pesan = simpan_ke_supabase(data)
        if berhasil:
            flash("Terima kasih. Kuesioner berhasil dikirim.", "success")
        else:
            flash(pesan, "danger")
    except Exception as e:
        flash(f"Terjadi kesalahan: {str(e)}", "danger")

    return redirect(url_for("index", role=role))




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
