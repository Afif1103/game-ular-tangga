# game-ular-tangga
Proyek Capstone Game Ular Tangga

# Capstone Project: Ular Tangga Cerdas

Game Ular Tangga klasik yang dibangun ulang untuk web, dengan sentuhan modern berupa tantangan berhitung untuk bisa maju.

Deployment Link: [Mainkan Gamenya di Sini!]([https://nama-unik-anda.netlify.app](https://candid-beijinho-460830.netlify.app)) 

---

Deskripsi

Proyek ini adalah implementasi dari permainan papan klasik, Ular Tangga, yang dapat dimainkan langsung di browser. Berbeda dari versi tradisional, game ini menambahkan elemen edukatif di mana pemain harus menjawab pertanyaan penjumlahan sederhana dengan benar untuk dapat menggerakkan pionnya. Jika jawaban salah, pemain akan kehilangan gilirannya.

Game ini dibangun sepenuhnya menggunakan HTML, CSS, dan Python melalui pustaka Brython, yang memungkinkan eksekusi kode Python secara *native* di sisi klien (browser).

Teknologi yang Digunakan

*   HTML5: Sebagai struktur dasar halaman web dan elemen-elemen UI (tombol, input).
*   CSS3: Untuk styling dan tata letak agar tampilan game menarik dan responsif.
*   Python 3: Sebagai bahasa pemrograman utama untuk semua logika permainan.
*   Brython: Pustaka kunci yang berfungsi sebagai "penerjemah" Python ke JavaScript, memungkinkan kode Python untuk memanipulasi elemen HTML (DOM) dan berjalan di browser.

Fitur

*   Papan Permainan Dinamis: Papan 10x10 digambar secara otomatis menggunakan elemen HTML Canvas.
*   Multiplayer: Mendukung permainan untuk 2 hingga 4 pemain secara lokal.
*   Animasi Dadu & Pion: Dadu memiliki animasi kocokan visual, dan pion bergerak selangkah demi selangkah untuk pengalaman bermain yang lebih baik.
*   Mekanisme Kuis Cerdas: Setelah melempar dadu, pemain dihadapkan dengan pertanyaan penjumlahan untuk bisa maju.
*   Visual Ular & Tangga: Ular dan tangga digambar dengan jelas di atas papan.
*   Deteksi Kemenangan: Sistem secara otomatis mendeteksi ketika seorang pemain mencapai kotak 100 dan mengumumkan pemenangnya.

Setup Instructions (Cara Menjalankan)

1. Melalui Link Deployment (Direkomendasikan):**
   *   Cukup buka [Deployment Link](https://candid-beijinho-460830.netlify.app) di browser modern seperti Chrome atau Firefox. Game akan langsung dimuat dan siap dimainkan.

2. Secara Lokal (Untuk Development):**
   *   Pastikan Anda memiliki Python terinstal.
   *   Unduh atau *clone* repositori ini.
   *   Buka terminal atau command prompt di dalam folder proyek.
   *   Jalankan server lokal dengan perintah: `python -m http.server`
   *   Buka browser dan kunjungi alamat `http://localhost:8000`.

Penjelasan Dukungan AI (AI Support Explanation)

Sesuai dengan brief proyek, **AI (Google Gemini)** digunakan secara ekstensif **selama fase pengembangan** untuk mempercepat, meningkatkan, dan mendokumentasikan proses pembuatan kode. AI tidak menjadi bagian dari produk akhir, melainkan sebagai alat bantu developer.

Berikut adalah peran AI dalam proyek ini:
1.  Konversi Logika Awal: AI membantu menerjemahkan konsep dari kode game desktop (seperti Pygame) ke dalam paradigma web (Brython dan HTML Canvas), terutama pada bagian *game loop* dan *event handling*.
2.  Debugging & Pemecahan Masalah: AI sangat membantu dalam mengidentifikasi masalah-masalah spesifik di lingkungan web, seperti *browser caching* (yang menyebabkan animasi tidak berjalan) dan masalah pada generator angka acak (`random.seed`).
3.  Brainstorming Fitur: Ide untuk menambahkan mekanisme **kuis penjumlahan** adalah hasil diskusi dan brainstorming dengan AI untuk membuat game ini lebih unik dari versi standarnya.
4. Refactoring & Optimalisasi: AI memberikan saran untuk menstrukturkan ulang kode agar lebih bersih dan mudah dibaca, misalnya dengan memisahkan logika animasi dari logika utama permainan.

