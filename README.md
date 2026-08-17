# 🐾 CATography
> **"Find Your Purr-fect Business Location."**

![CATography Banner](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Backend-Python%20%7C%20Flask-blue)
![TailwindCSS](https://img.shields.io/badge/Frontend-Tailwind%20CSS-06B6D4)
![Google Maps API](https://img.shields.io/badge/API-Google%20Places%20API-4285F4)
![License](https://img.shields.io/badge/License-MIT-orange)

**CATography** adalah platform **Business Intelligence & Geolocation Analytics** berbasis web yang dirancang untuk membantu pengusaha, UMKM, dan pengambil keputusan menemukan **lokasi bisnis paling strategis & menguntungkan**. Menggabungkan kecanggihan Google Maps Places API dengan antarmuka menggemaskan bertema kucing (*cute & smart*), CATography menyajikan analisis pasar geografis dengan cara yang intuitif, interaktif, dan menyenangkan!

---

## ✨ Fitur-Fitur Utama

* 🗺️ **GIS Map Explorer & Density Heatmap**: Visualisasi lokasi kompetitor secara presisi di peta GIS interaktif (Leaflet.js) dengan opsi tampilan *Pin View* atau *Heatmap Kepadatan Usaha*.
* 📊 **Rating Distribution Analytics**: Grafik sebaran rating kompetitor menggunakan Chart.js untuk menganalisis tingkat kepuasan dan celah kualitas layanan di suatu wilayah.
* 💬 **On-Demand Review Scraping**: Mengambil dan merender teks ulasan detail pelanggan secara otomatis (*on-demand*) begitu lokasi diklik, menghemat penggunaan kuota API.
* 📸 **Google Places Photo Gallery**: Menampilkan galeri foto tempat (tampak depan toko, suasana interior, hingga produk) langsung dari server Google Maps.
* 🐱 **Interactive Lottie Animations**: Antarmuka responsif yang dilengkapi animasi Lottie kucing (*CatHome.json* & *CatLoading.json*) untuk pengalaman pengoperasian yang ceria dan ramah pengguna.
* 🔗 **Direct Google Maps Link & "See More"**: Membuka langsung halaman lokasi usaha di Google Maps resmi dengan satu klik melalui tombol aksi *Buka Google Maps* dan *See More ↗*.
* 📥 **Export Data to CSV**: Mengunduh seluruh data riset lokasi, koordinat latitude/longitude, rating, ulasan, hingga link foto sampul ke dalam berkas CSV yang siap diolah di Excel / Google Sheets.
* 📜 **Riwayat Pencarian & Modal Drawer**: Menyimpan dan mengelola riwayat berkas pencarian sebelumnya sehingga Anda bisa mengunduh ulang hasil riset kapan saja.

---

## 🛠️ Teknologi yang Digunakan

* **Backend**: Python 3.12, Flask Framework, Requests
* **Frontend**: HTML5, Vanilla JavaScript, Tailwind CSS (Design System Oranye `#e47127`)
* **GIS & Data Visualization**: Leaflet.js, Leaflet.heat, Chart.js
* **Animation & UX Icons**: Lottie Player, Google Material Symbols Outlined, Google Fonts (*Outfit* & *Plus Jakarta Sans*)
* **API Integration**: Google Places API (New) `searchText` & Legacy Place Details API `details/json`

---

## 🚀 Panduan Penggunaan & Instalasi Lokal

### 1. Prasyarat
* Python versi 3.10 atau yang lebih baru
* Google Places API Key (Gratis $200 kredit bulanan dari Google Cloud Console)

### 2. Kloning Repository
```bash
git clone https://github.com/prabowows/CATography.git
cd CATography
```

### 3. Install Dependensi
```bash
pip install flask requests
```

### 4. Jalankan Aplikasi
```bash
python app.py
```

Buka peramban (browser) Anda dan akses:
👉 **`http://localhost:5001`**

---

## 🔑 Cara Mendapatkan Google Places API Key Gratis

1. Buka [Google Cloud Console](https://console.cloud.google.com/).
2. Buat proyek baru dan aktifkan **Places API (New)** serta **Places API**.
3. Buat Credentials (API Key) dan masukkan ke kolom **Google Places API Key** di header atas aplikasi CATography.
4. *Catatan:* Google memberikan kredit gratis sebesar **$200 USD setiap bulan** secara otomatis, setara dengan ~20.000+ pencarian lokasi gratis setiap bulannya.

---

## 🤝 Kontribusi & Lisensi

Proyek ini dibuat untuk tujuan riset intelijen bisnis geografis & pemetaan lokasi usaha. Anda bebas untuk mengkloning, memodifikasi, dan mengembangkannya kembali.

Dibuat dengan ❤️ & 🐾 oleh **[Prabowo](https://github.com/prabowows)**.
