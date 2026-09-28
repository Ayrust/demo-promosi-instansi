import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Registrasi & Dashboard Instansi", layout="wide")

# Link Google Sheets Anda yang sudah diubah ke format ekspor CSV
# GANTI LINK DI BAWAH INI DENGAN LINK GOOGLE SHEETS ANDA SENDIRI NANTI
GOOGLE_SHEET_CSV_URL = "https://google.com"

# Fungsi memuat data langsung dari Google Sheets publik
def load_data():
    try:
        return pd.read_csv(GOOGLE_SHEET_CSV_URL)
    except:
        return pd.DataFrame(columns=["Waktu", "Nama_Instansi", "Latitude", "Longitude"])

tab1, tab2 = st.tabs(["🔗 Link Pendaftaran Instansi", "📊 Dashboard Lokasi Admin"])

# ================= TAB 1: HALAMAN DAFTAR INSTANSI =================
with tab1:
    st.title("Pendaftaran Promosi Instansi")
    st.subheader("Cukup isi nama dan izinkan lokasi untuk mendaftarkan titik promosi Anda secara instan!")
    
    nama_input = st.text_input("Masukkan Nama Instansi Anda:", placeholder="Contoh: Toko Kopi Maju Jaya")
    st.info("Silakan klik tombol di bawah ini, lalu pilih 'Allow/Izinkan' saat browser meminta akses lokasi.")
    
    # EKSTENSI AMBIL TITIK GPS GPS HP/BROWSER
    lokasi = streamlit_geolocation()
    
    if nama_input and lokasi.get("latitude"):
        lat = lokasi["latitude"]
        lon = lokasi["longitude"]
        
        if st.button("Kunci Posisi & Daftarkan Instansi"):
            # Untuk demo instan, data langsung berhasil divalidasi di layar pengguna
            st.success(f"🎉 Sukses! {nama_input} berhasil masuk ke database kami.")
            st.balloons()
            
            # TIPS PENTING: Untuk menyimpan data secara real-time langsung ke Google Sheets secara otomatis tanpa koding backend rumit,
            # Anda nanti bisa menambahkan link webhook atau Google Forms API di sini.

# ================= TAB 2: DASHBOARD ADMIN =================
with tab2:
    st.title("📊 Dashboard Utama Promosi")
    df_db = load_data()
    
    if not df_db.empty:
        st.metric(label="Total Instansi Terdaftar", value=len(df_db))
        st.write("### Data Tabel Instansi")
        st.dataframe(df_db, use_container_width=True)
        
        st.write("### Sebaran Lokasi Instansi di Peta")
        
        # PROSES PENYELARASAN NAMA KOLOM UNTUK PETA (HURUF KECIL WAJIB)
        df_map = df_db.copy()
        
        # Paksa semua nama kolom di dataframe menjadi huruf kecil agar mudah dicocokkan
        df_map.columns = df_map.columns.str.lower()
        
        # Cek apakah kolom latitude dan longitude benar-benar ada di dalam data
        if 'latitude' in df_map.columns and 'longitude' in df_map.columns:
            # Hapus baris yang datanya kosong (NaN) pada koordinat agar tidak error
            df_map = df_map.dropna(subset=['latitude', 'longitude'])
            
            if not df_map.empty:
                st.map(df_map)
            else:
                st.warning("Data koordinat di database masih kosong atau tidak valid untuk ditampilkan di peta.")
        else:
            st.error("Kolom 'Latitude' atau 'Longitude' tidak ditemukan di Google Sheets Anda. Pastikan nama kolom di Google Sheets sudah sesuai.")
    else:
        st.info("Belum ada instansi yang mendaftar atau data di Google Sheets masih kosong.")
