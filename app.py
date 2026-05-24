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
    "Kemudahan Penggunaan",
    "Efisiensi Sistem",
    "Kejelasan Informasi",
    "Konsistensi Tampilan",
    "Kecepatan Akses",
]

PERTANYAAN_MAHASISWA = [
    "Saya merasa mudah memahami cara menggunakan Smart Library RFID sebagai mahasiswa.",
    "Antarmuka sistem mudah dipahami tanpa bantuan orang lain.",
    "Saya dapat menyelesaikan peminjaman buku dengan RFID tanpa kebingungan.",
    "Fitur utama sistem mudah ditemukan saat pertama kali digunakan.",
    "Proses peminjaman dan pengembalian buku berjalan efisien.",
    "Sistem mengurangi waktu antre di perpustakaan.",
    "Alur kerja peminjaman dari awal sampai selesai terasa singkat.",
    "Saya jarang mengulang langkah yang sama karena sistem tidak efisien.",
    "Informasi status peminjaman ditampilkan dengan jelas.",
    "Pesan kesalahan atau notifikasi sistem mudah dipahami.",
    "Informasi buku dan akun mahasiswa ditampilkan secara jelas.",
    "Petunjuk penggunaan di layar cukup membantu saya.",
    "Tampilan antarmuka konsisten di setiap halaman.",
    "Penempatan menu dan tombol terasa seragam di seluruh sistem.",
    "Warna, ikon, dan tipografi terasa konsisten.",
    "Navigasi antar halaman terasa teratur dan tidak membingungkan.",
    "Sistem merespons dengan cepat saat memindai kartu RFID.",
    "Proses login dan akses fitur berjalan cepat.",
    "Pencarian data buku tidak membuat saya menunggu lama.",
    "Secara keseluruhan, kecepatan sistem memuaskan saya.",
]

PERTANYAAN_PUSTAKAWAN = [
    "Saya merasa mudah mengoperasikan modul Smart Library RFID sebagai pustakawan.",
    "Antarmuka administrasi mudah dipelajari oleh staf perpustakaan.",
    "Saya dapat menangani transaksi sirkulasi tanpa kesulitan berarti.",
    "Menu fitur pustakawan mudah ditemukan saat dibutuhkan.",
    "Sistem membantu mempercepat proses layanan sirkulasi.",
    "Pencatatan peminjaman dan pengembalian terintegrasi dengan baik.",
    "Sistem mengurangi pekerjaan manual yang berulang.",
    "Alur kerja harian pustakawan menjadi lebih efisien.",
    "Data anggota dan transaksi ditampilkan dengan jelas.",
    "Laporan dan ringkasan informasi mudah dibaca.",
    "Pesan sistem saat terjadi kesalahan mudah ditindaklanjuti.",
    "Informasi status buku dan RFID terlihat jelas di layar.",
    "Tampilan modul pustakawan konsisten di seluruh menu.",
    "Penempatan tombol dan form input seragam di setiap halaman.",
    "Desain antarmuka terasa rapi dan konsisten.",
    "Navigasi antar modul administrasi terasa teratur.",
    "Sistem cepat merespons saat memproses data RFID.",
    "Pencarian data anggota atau buku tidak lambat.",
    "Proses update status buku berjalan dengan cepat.",
    "Secara keseluruhan, performa sistem memadai untuk operasional harian.",
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
