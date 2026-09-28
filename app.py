import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import pandas as pd
import os
import datetime

st.set_page_config(page_title="Pelacak Lokasi Instan", layout="centered")

# File database internal di server web (tidak butuh Google Sheets lagi)
LOCAL_DB = "data_lokasi_instansi.csv"

def muat_data():
    if os.path.exists(LOCAL_DB):
        return pd.read_csv(LOCAL_DB)
    return pd.DataFrame(columns=["waktu", "latitude", "longitude"])

def simpan_data(lat, lon):
    df = muat_data()
    waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_baru = pd.DataFrame([[waktu, lat, lon]], columns=["waktu", "latitude", "longitude"])
    df = pd.concat([df, data_baru], ignore_index=True)
    df.to_csv(LOCAL_DB, index=False)
    return df

st.title("📍 Aktivasi Promosi Instansi")
st.write("Klik tombol di bawah ini untuk mendaftarkan posisi instansi Anda ke dalam peta promosi kami secara instan.")

# TOMBOL SEKALI KLIK UTAMA (Mengaktifkan GPS HP/Browser)
st.write("### Langkah 1: Klik tombol target di bawah ini 👇")
lokasi = streamlit_geolocation()

# Sistem mendeteksi jika tombol lokasi sudah ditekan dan GPS didapatkan
if lokasi.get("latitude") and lokasi.get("longitude"):
    lat = lokasi["latitude"]
    lon = lokasi["longitude"]
    
    # Cek apakah koordinat ini sudah pernah disimpan di sesi ini agar tidak duplikat
    if "terdaftar" not in st.session_state:
        df_terbaru = simpan_data(lat, lon)
        st.session_state["terdaftar"] = True
        st.session_state["database_aktif"] = df_terbaru
    
    st.success(f"🎉 SUKSES! Lokasi Anda berhasil dikunci pada koordinat: {lat}, {lon}")
    st.balloons()

# ================= DASHBOARD ADMIN (Di Halaman yang Sama, Bagian Bawah) =================
st.markdown("---")
st.subheader("📊 Dashboard Hasil Pelacakan (Admin)")

# Memuat data terbaru untuk ditampilkan ke peta
df_tampil = muat_data()

if not df_tampil.empty:
    st.metric(label="Total Lokasi Terlacak", value=len(df_tampil))
    
    # Tampilkan Peta Digital
    st.write("### Peta Sebaran Lokasi")
    st.map(df_tampil)
    
    # Tampilkan Tabel Data
    st.write("### Log Database")
    st.dataframe(df_tampil, use_container_width=True)
else:
    st.info("Belum ada lokasi yang masuk. Sebarkan link di atas untuk mencoba!")
