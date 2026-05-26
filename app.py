from flask import Flask, render_template, request

app = Flask(__name__)

questions = [

    # LOGIN
    {
        "kategori": "BLACKBOX TESTING HALAMAN LOGIN",
        "skenario": "Login dengan username dan password benar",
        "testcase": "Masukkan username dan password valid",
        "hasil_yang_diharapkan": "Sistem berhasil masuk ke dashboard"
    },
    {
        "kategori": "BLACKBOX TESTING HALAMAN LOGIN",
        "skenario": "Login dengan password salah",
        "testcase": "Masukkan username benar dan password salah",
        "hasil_yang_diharapkan": "Sistem menampilkan pesan error"
    },
    {
        "kategori": "BLACKBOX TESTING HALAMAN LOGIN",
        "skenario": "Kolom login kosong",
        "testcase": "Tidak mengisi username dan password",
        "hasil_yang_diharapkan": "Sistem menolak login"
    },
    {
        "kategori": "BLACKBOX TESTING HALAMAN LOGIN",
        "skenario": "Logout sistem",
        "testcase": "Klik tombol logout",
        "hasil_yang_diharapkan": "Sistem keluar dari akun"
    },
    {
        "kategori": "BLACKBOX TESTING HALAMAN LOGIN",
        "skenario": "Akses halaman tanpa login",
        "testcase": "Membuka dashboard tanpa autentikasi",
        "hasil_yang_diharapkan": "Sistem mengarahkan ke halaman login"
    },

    # DASHBOARD
    {
        "kategori": "BLACKBOX TESTING DASHBOARD",
        "skenario": "Menampilkan data dashboard",
        "testcase": "Membuka halaman dashboard",
        "hasil_yang_diharapkan": "Data dashboard tampil"
    },
    {
        "kategori": "BLACKBOX TESTING DASHBOARD",
        "skenario": "Navigasi menu dashboard",
        "testcase": "Klik menu navigasi",
        "hasil_yang_diharapkan": "Sistem berpindah halaman"
    },
    {
        "kategori": "BLACKBOX TESTING DASHBOARD",
        "skenario": "Refresh dashboard",
        "testcase": "Reload halaman dashboard",
        "hasil_yang_diharapkan": "Data diperbarui"
    },
    {
        "kategori": "BLACKBOX TESTING DASHBOARD",
        "skenario": "Tampilan grafik",
        "testcase": "Membuka dashboard",
        "hasil_yang_diharapkan": "Grafik tampil dengan benar"
    },
    {
        "kategori": "BLACKBOX TESTING DASHBOARD",
        "skenario": "Akses cepat menu",
        "testcase": "Klik shortcut menu",
        "hasil_yang_diharapkan": "Menu terbuka"
    },

    # PENDAFTARAN ANGGOTA
    {
        "kategori": "BLACKBOX TESTING PENDAFTARAN ANGGOTA",
        "skenario": "Tambah anggota baru",
        "testcase": "Isi form anggota dengan benar",
        "hasil_yang_diharapkan": "Data anggota tersimpan"
    },
    {
        "kategori": "BLACKBOX TESTING PENDAFTARAN ANGGOTA",
        "skenario": "Form anggota kosong",
        "testcase": "Tidak mengisi form",
        "hasil_yang_diharapkan": "Sistem menolak penyimpanan"
    },
    {
        "kategori": "BLACKBOX TESTING PENDAFTARAN ANGGOTA",
        "skenario": "Nomor anggota duplikat",
        "testcase": "Input nomor anggota yang sama",
        "hasil_yang_diharapkan": "Sistem menampilkan peringatan"
    },
    {
        "kategori": "BLACKBOX TESTING PENDAFTARAN ANGGOTA",
        "skenario": "Edit data anggota",
        "testcase": "Mengubah data anggota",
        "hasil_yang_diharapkan": "Perubahan tersimpan"
    },
    {
        "kategori": "BLACKBOX TESTING PENDAFTARAN ANGGOTA",
        "skenario": "Hapus anggota",
        "testcase": "Klik tombol hapus",
        "hasil_yang_diharapkan": "Data anggota terhapus"
    },

    # PENDAFTARAN BUKU
    {
        "kategori": "BLACKBOX TESTING PENDAFTARAN BUKU",
        "skenario": "Tambah buku baru",
        "testcase": "Isi data buku lengkap",
        "hasil_yang_diharapkan": "Data buku tersimpan"
    },
    {
        "kategori": "BLACKBOX TESTING PENDAFTARAN BUKU",
        "skenario": "Input data buku kosong",
        "testcase": "Tidak mengisi form buku",
        "hasil_yang_diharapkan": "Sistem menolak penyimpanan"
    },
    {
        "kategori": "BLACKBOX TESTING PENDAFTARAN BUKU",
        "skenario": "ISBN duplikat",
        "testcase": "Input ISBN yang sudah ada",
        "hasil_yang_diharapkan": "Sistem memberi notifikasi"
    },
    {
        "kategori": "BLACKBOX TESTING PENDAFTARAN BUKU",
        "skenario": "Edit data buku",
        "testcase": "Mengubah informasi buku",
        "hasil_yang_diharapkan": "Data berhasil diperbarui"
    },
    {
        "kategori": "BLACKBOX TESTING PENDAFTARAN BUKU",
        "skenario": "Hapus data buku",
        "testcase": "Klik tombol hapus buku",
        "hasil_yang_diharapkan": "Data buku terhapus"
    },

    # LAPORAN
    {
        "kategori": "BLACKBOX TESTING LAPORAN",
        "skenario": "Cetak laporan",
        "testcase": "Klik tombol cetak",
        "hasil_yang_diharapkan": "Laporan berhasil dicetak"
    },
    {
        "kategori": "BLACKBOX TESTING LAPORAN",
        "skenario": "Export laporan PDF",
        "testcase": "Klik export PDF",
        "hasil_yang_diharapkan": "File PDF terdownload"
    },
    {
        "kategori": "BLACKBOX TESTING LAPORAN",
        "skenario": "Filter laporan",
        "testcase": "Pilih filter tanggal",
        "hasil_yang_diharapkan": "Data laporan sesuai filter"
    },
    {
        "kategori": "BLACKBOX TESTING LAPORAN",
        "skenario": "Pencarian laporan",
        "testcase": "Input keyword pencarian",
        "hasil_yang_diharapkan": "Data laporan ditemukan"
    },
    {
        "kategori": "BLACKBOX TESTING LAPORAN",
        "skenario": "Refresh laporan",
        "testcase": "Reload halaman laporan",
        "hasil_yang_diharapkan": "Data laporan diperbarui"
    }
]


@app.route("/", methods=["GET", "POST"])
def index():

    hasil = []
    kesimpulan = []

    if request.method == "POST":

        hasil = request.form.getlist("hasil[]")

        for item in hasil:

            if item == "Berhasil":
                kesimpulan.append("Valid")

            elif item == "Gagal":
                kesimpulan.append("Tidak Valid")

            else:
                kesimpulan.append("")

    return render_template(
        "index.html",
        questions=questions,
        hasil=hasil,
        kesimpulan=kesimpulan
    )


if __name__ == "__main__":
    app.run(debug=True)