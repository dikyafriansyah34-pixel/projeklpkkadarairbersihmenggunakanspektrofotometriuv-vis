import streamlit as st
import pandas as pd
import numpy as np

# ==========================================================
# KONFIGURASI
# ==========================================================
st.set_page_config(page_title="LPK Kadar Fe", page_icon="💧")

st.title("LPK Kadar Besi (Fe)")
st.markdown("---")

# ==========================================================
# SIDEBAR
# ==========================================================
st.sidebar.header("Pengaturan")
fp = st.sidebar.number_input("Faktor Pengenceran", value=2.0, step=0.5)
bm_minum = st.sidebar.number_input("Baku Mutu Air Minum", value=0.3)
bm_bersih = st.sidebar.number_input("Baku Mutu Air Bersih", value=1.0)
bm_sungai = st.sidebar.number_input("Baku Mutu Air Sungai", value=0.3)

# ==========================================================
# DATA KURVA KALIBRASI
# ==========================================================
st.subheader("Data Kurva Kalibrasi")

kalibrasi = pd.DataFrame({
    "Konsentrasi (mg/L)": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    "Absorbansi (AU)": [0.000, 0.085, 0.172, 0.258, 0.341, 0.430]
})

df_kal = st.data_editor(kalibrasi, num_rows="dynamic", key="kal")

# ==========================================================
# REGRESI LINEAR
# ==========================================================
x = df_kal["Konsentrasi (mg/L)"].values
y = df_kal["Absorbansi (AU)"].values

n = len(x)
sum_x = np.sum(x)
sum_y = np.sum(y)
sum_xy = np.sum(x * y)
sum_x2 = np.sum(x ** 2)

m = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
b = (sum_y - m * sum_x) / n

mean_x = sum_x / n
mean_y = sum_y / n
num = np.sum((x - mean_x) * (y - mean_y))
den = np.sqrt(np.sum((x - mean_x)**2) * np.sum((y - mean_y)**2))
r = num / den if den != 0 else 0
r2 = r ** 2

col1, col2, col3 = st.columns(3)
col1.metric("Slope", f"{m:.4f}")
col2.metric("Intercept", f"{b:.4f}")
col3.metric("R2", f"{r2:.5f}")

# ==========================================================
# DATA SAMPEL
# ==========================================================
st.markdown("---")
st.subheader("Data Sampel")

sampel = pd.DataFrame({
    "Nama Sampel": ["Air Sumur", "Air Sungai", "Air PDAM"],
    "Absorbansi": [0.215, 0.318, 0.042],
    "Kategori": ["Air Bersih", "Air Sungai", "Air Minum"]
})

df_samp = st.data_editor(sampel, num_rows="dynamic", key="samp")

# ==========================================================
# HASIL PERHITUNGAN
# ==========================================================
st.markdown("---")
st.subheader("Hasil Perhitungan")

hasil = []

for i in range(len(df_samp)):
    nama = df_samp.loc[i, "Nama Sampel"]
    absorb = df_samp.loc[i, "Absorbansi"]
    kat = df_samp.loc[i, "Kategori"]
    
    c_ter = (absorb - b) / m
    c_akt = c_ter * fp
    
    if "Minum" in kat:
        bm = bm_minum
    elif "Sungai" in kat:
        bm = bm_sungai
    else:
        bm = bm_bersih
    
    if c_akt <= bm:
        status = "AMAN"
    else:
        status = "TIDAK AMAN"
    
    hasil.append({
        "Nama": nama,
        "Absorbansi": absorb,
        "Kadar (mg/L)": round(c_akt, 4),
        "Baku Mutu": bm,
        "Status": status
    })

df_hasil = pd.DataFrame(hasil)
st.dataframe(df_hasil, use_container_width=True)

# ==========================================================
# KESIMPULAN
# ==========================================================
st.subheader("Kesimpulan")

for _, row in df_hasil.iterrows():
    if row["Status"] == "AMAN":
        st.success(f"AMAN - {row['Nama']}: {row['Kadar (mg/L)']} mg/L")
    else:
        st.error(f"TIDAK AMAN - {row['Nama']}: {row['Kadar (mg/L)']} mg/L")
