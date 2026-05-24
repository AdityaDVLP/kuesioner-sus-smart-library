import csv
import os
import threading
import time
from datetime import datetime

import pandas as pd
from flask import Flask, flash, redirect, render_template, request, send_file, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ganti-dengan-string-rahasia-untuk-production")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", BASE_DIR)
CSV_FILE = os.path.join(DATA_DIR, "database_kuesioner.csv")
CSV_COLUMNS = ["Nama", "Role", "Tanggal"] + [f"P{i}" for i in range(1, 21)]
_csv_lock = threading.Lock()

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


def hitung_statistik(filter_role=None):
    if not os.path.exists(CSV_FILE):
        return {"total": 0, "mahasiswa": 0, "pustakawan": 0}

    try:
        df = pd.read_csv(CSV_FILE)
    except Exception:
        return {"total": 0, "mahasiswa": 0, "pustakawan": 0}

    if df.empty or "Role" not in df.columns:
        return {"total": 0, "mahasiswa": 0, "pustakawan": 0}

    total = len(df)
    mahasiswa = len(df[df["Role"] == "Mahasiswa"])
    pustakawan = len(df[df["Role"] == "Pustakawan"])

    if filter_role == "Mahasiswa":
        total = mahasiswa
    elif filter_role == "Pustakawan":
        total = pustakawan

    return {"total": total, "mahasiswa": mahasiswa, "pustakawan": pustakawan}


def _csv_perlu_header():
    return not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0


def simpan_ke_csv(data_dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    row = {col: data_dict.get(col, "") for col in CSV_COLUMNS}
    max_retry = 5

    with _csv_lock:
        for percobaan in range(max_retry):
            try:
                tulis_header = _csv_perlu_header()
                with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
                    if tulis_header:
                        writer.writeheader()
                    writer.writerow(row)
                    f.flush()
                    os.fsync(f.fileno())
                return True, "Data berhasil disimpan."
            except PermissionError:
                if percobaan < max_retry - 1:
                    time.sleep(0.3)
                    continue
                return (
                    False,
                    "File sedang digunakan. Tutup database_kuesioner.csv di Excel lalu coba lagi.",
                )
            except OSError as e:
                return False, f"Gagal menyimpan data: {e}"

    return False, "Gagal menyimpan setelah beberapa percobaan."


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
        berhasil, pesan = simpan_ke_csv(data)
        if berhasil:
            flash("Terima kasih. Kuesioner berhasil dikirim.", "success")
        else:
            flash(pesan, "danger")
    except Exception as e:
        flash(f"Terjadi kesalahan: {str(e)}", "danger")

    return redirect(url_for("index", role=role))


@app.route("/download")
def download_csv():
    if not os.path.exists(CSV_FILE):
        flash("Belum ada data untuk diunduh.", "warning")
        return redirect(url_for("index"))

    response = send_file(
        CSV_FILE,
        as_attachment=True,
        download_name="database_kuesioner.csv",
        mimetype="text/csv",
    )
    response.headers["Cache-Control"] = "no-store"
    return response


def ensure_csv_exists():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
        return
    with _csv_lock:
        if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
            return
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=CSV_COLUMNS).writeheader()


ensure_csv_exists()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
