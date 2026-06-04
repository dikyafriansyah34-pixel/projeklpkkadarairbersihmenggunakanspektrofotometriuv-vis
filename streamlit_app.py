import streamlit as st
import pandas as pd
import mount/src/projeklpkkadarairbersihmenggunakanspektrofotometriuv-vis/streamlit_app.py"
import numpy as np
import math

# ==========================================================
# KONFIGURASI HALAMAN
# ==========================================================
st.set_page_config(
    page_title="LPK - Kadar Fe (UV-Vis)",
    page_icon="🧪",
    layout="wide"
)

# ==========================================================
# 1. SIDEBAR - PENGATURAN & BAKU MUTU
# ==========================================================
st.sidebar.header("⚙️ Pengaturan & Baku Mutu")

# Input Parameter Analisis
st.sidebar.subheader("Parameter Analisis")
fp_input = st.sidebar.number_input("Faktor Pengenceran (x)", min_value=1.0, value=2.0, step=0.5)
vol_sampel = st.sidebar.number_input("Volume Sampel Diambil (mL)", min_value=1.0, value=50.0)

# Input Baku Mutu
st.sidebar.subheader("Baku Mutu (mg/L)")
bm_minum = st.sidebar.number_input("Air Minum (PerMenKes 492/2010)", value=0.3)
bm_bersih = st.sidebar.number_input("Air Bersih", value=1.0)
bm_sungai = st.sidebar.number_input("Air Sungai Kelas I (PP 22/2021)", value=0.3)

# ==========================================================
# 2. MAIN AREA - INPUT DATA
# ==========================================================
st.title("🧪 LPK : Perhitungan Kadar Fe (Metode Fenantrolin)")
st.markdown("---")

# Kolom Input Data
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Data Kurva Kalibrasi")
    # Data Default
    data_kalibrasi = pd.DataFrame({
        'Konsentrasi (mg/L)': [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        'Absorbansi (AU)': [0.000, 0.085, 0.172, 0.258, 0.341, 0.430]
    })
    
    # Editor Tabel Kalibrasi
    df_kalibrasi = st.data_editor(
        data_kalibrasi,
        num_rows="dynamic",
        key="kalibrasi_editor",
        use_container_width=True,
        help="Edit data kurva kalibrasi standar di sini."
    )

with col2:
    st.subheader("💧 Data Sampel Uji")
    # Data Default Sampel
    data_sampel = pd.DataFrame({
        'Nama Sampel': ['Sampel A (Air Sumur)', 'Sampel B (Air Sungai)', 'Sampel C (Air PDAM)'],
        'Absorbansi (AU)': [0.215, 0.318, 0.042],
        'Kategori Baku Mutu': ['Air Bersih', 'Air Sungai', 'Air Minum']
    })
    
    # Editor Tabel Sampel
    df_sampel = st.data_editor(
        data_sampel,
        num_rows="dynamic",
        key="sampel_editor",
        use_container_width=True
    )

# ==========================================================
# 3. PERHITUNGAN REGRESI LINEAR
# ==========================================================
st.markdown("---")
st.subheader("📈 Hasil Regresi Linear (Kurva Kalibrasi)")

# Ekstrak data dari dataframe
x_data = df_kalibrasi['Konsentrasi (mg/L)'].values
y_data = df_kalibrasi['Absorbansi (AU)'].values

# Validasi data tidak boleh 0 semua
if len(x_data) < 2 or len(y_data) < 2:
    st.error("Data kalibrasi tidak cukup untuk dilakukan regresi linear.")
    st.stop()

# Menghitung Regresi (Least Squares)
n = len(x_data)
sum_x = np.sum(x_data)
sum_y = np.sum(y_data)
sum_xy = np.sum(x_data * y_data)
sum_x2 = np.sum(x_data ** 2)

# Slope (m) dan Intercept (b)
if (n * sum_x2 - sum_x ** 2) != 0:
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
    intercept = (sum_y - slope * sum_x) / n
else:
    st.error("Terjadi kesalahan perhitungan: Pembagian dengan nol (Data tidak valid).")
    st.stop()

# Hitung R-squared
mean_x = sum_x / n
mean_y = sum_y / n
num = np.sum((x_data - mean_x) * (y_data - mean_y))
den = np.sqrt(np.sum((x_data - mean_x)**2) * np.sum((y_data - mean_y)**2))
R = num / den
R2 = R ** 2

# Tampilkan Persamaan
st.info(f"**Persamaan Regresi:** y = {slope:.4f}x + {intercept:.4f}")
st.success(f"**R² (Koefisien Determinasi):** {R2:.5f}")

# ==========================================================
# 4. PLOT VISUALISASI KURVA KALIBRASI
# ==========================================================
fig, ax = plt.subplots()
# Plot titik data aktual
ax.scatter(x_data, y_data, color='blue', label='Data Standar', zorder=5)
# Plot garis regresi
x_line = np.linspace(min(x_data), max(x_data), 100)
y_line = slope * x_line + intercept
ax.plot(x_line, y_line, color='red', linestyle='--', label=f'Garis Regresi')

ax.set_xlabel("Konsentrasi Fe (mg/L)")
ax.set_ylabel("Absorbansi (AU)")
ax.set_title("Grafik Kurva Kalibrasi")
ax.legend()
ax.grid(True, linestyle=':', alpha=0.6)

st.pyplot(fig)

# ==========================================================
# 5. PERHITUNGAN KADAR SAMPEL
# ==========================================================
st.markdown("---")
st.subheader("🔬 Hasil Perhitungan Kadar Fe Sampel")

# Proses Hitung
list_nama = df_sampel['Nama Sampel'].values
list_abs = df_sampel['Absorbansi (AU)'].values
list_kat = df_sampel['Kategori Baku Mutu'].values

results = []

for i in range(len(list_nama)):
    A = list_abs[i]
    # Menghitung Konsentrasi
    c_terukur = (A - intercept) / slope
    c_aktual = c_terukur * fp_input
    
    # Tentukan Baku Mutu berdasarkan Kategori
    kat = str(list_kat[i]).upper() # Mengubah menjadi uppercase untuk避免 salah eja
    
    if "MINUM" in kat:
        bm = bm_minum
    elif "SUNGAI" in kat:
        bm = bm_sungai
    else:
        # Default menggunakan Baku Mutu Air Bersih
        bm = bm_bersih
        
    # Status
    status = "✓ AMAN" if c_aktual <= bm else "✗ TIDAK AMAN"
    
    # Persen
    pct = (c_aktual / bm) * 100
    
    results.append({
        "Nama Sampel": list_nama[i],
        "Absorbansi": A,
        "Konsentrasi Terukur (mg/L)": c_terukur,
        "Konsentrasi Akhir (mg/L)": round(c_aktual, 4),
        "Baku Mutu (mg/L)": bm,
        "Persentase Baku Mutu (%)": round(pct, 2),
        "Status": status
    })

# Membuat DataFrame Hasil
df_hasil = pd.DataFrame(results)

# ==========================================================
# 6. TAMPILAN TABEL
