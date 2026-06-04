"""
=========================================================
 LPK - Perhitungan Kadar Fe & Perbandingan dengan Baku Mutu
 Metode: Spektrofotometri UV-Vis (Fenantrolin)
=========================================================
"""

import math

# ─────────────────────────────────────────────────────────
# 1. DATA PERCOBAAN
# ─────────────────────────────────────────────────────────

# Kurva kalibrasi: konsentrasi (mg/L) vs absorbansi
konsentrasi_std = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]   # mg/L
absorbansi_std  = [0.000, 0.085, 0.172, 0.258, 0.341, 0.430]  # AU

# Sampel air (absorbansi terukur)
sampel = {
    "Sampel A (Air Sumur)"    : 0.215,
    "Sampel B (Air Sungai)"   : 0.318,
    "Sampel C (Air PDAM)"     : 0.042,
}

# Parameter pengenceran & volume
faktor_pengenceran = 2.0   # sampel diencerkan 2×
volume_sampel_mL   = 50.0  # volume sampel diambil (mL)

# Baku Mutu Fe (PerMenKes No. 492/2010 & PP No. 22/2021)
BAKU_MUTU_AIR_MINUM_MGL = 0.3   # mg/L  (air minum)
BAKU_MUTU_AIR_BERSIH_MGL = 1.0  # mg/L  (air bersih)
BAKU_MUTU_AIR_SUNGAI_MGL = 0.3  # mg/L  (Kelas I PP 22/2021)

# ─────────────────────────────────────────────────────────
# 2. REGRESI LINEAR (Metode Least Squares)
# ─────────────────────────────────────────────────────────

n   = len(konsentrasi_std)
sum_x  = sum(konsentrasi_std)
sum_y  = sum(absorbansi_std)
sum_xy = sum(x * y for x, y in zip(konsentrasi_std, absorbansi_std))
sum_x2 = sum(x ** 2 for x in konsentrasi_std)

slope     = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
intercept = (sum_y - slope * sum_x) / n

# Koefisien korelasi (R)
mean_x = sum_x / n
mean_y = sum_y / n
num    = sum((x - mean_x) * (y - mean_y) for x, y in zip(konsentrasi_std, absorbansi_std))
den    = math.sqrt(
    sum((x - mean_x) ** 2 for x in konsentrasi_std) *
    sum((y - mean_y) ** 2 for y in absorbansi_std)
)
R  = num / den
R2 = R ** 2

# ─────────────────────────────────────────────────────────
# 3. PERHITUNGAN KADAR Fe SAMPEL
# ─────────────────────────────────────────────────────────

def hitung_konsentrasi(absorbansi, slope, intercept, fp):
    """
    Hitung konsentrasi Fe dari absorbansi:
      C_terukur = (A - intercept) / slope
      C_aktual  = C_terukur × faktor_pengenceran
    """
    c_terukur = (absorbansi - intercept) / slope
    c_aktual  = c_terukur * fp
    return c_terukur, c_aktual

# ─────────────────────────────────────────────────────────
# 4. OUTPUT LAPORAN
# ─────────────────────────────────────────────────────────

garis = "=" * 60

print(garis)
print(" LPK — PERHITUNGAN KADAR Fe (SPEKTROFOTOMETRI UV-VIS)")
print(garis)

print("\n[1] DATA KURVA KALIBRASI")
print(f"  {'Konsentrasi (mg/L)':<22} {'Absorbansi (AU)':<18} {'A_hitung'}")
for x, y in zip(konsentrasi_std, absorbansi_std):
    y_fit = slope * x + intercept
    print(f"  {x:<22.1f} {y:<18.3f} {y_fit:.3f}")

print(f"\n[2] PERSAMAAN REGRESI LINEAR")
print(f"  y = {slope:.4f}x + {intercept:.4f}")
print(f"  Koefisien Korelasi (R)  = {R:.5f}")
print(f"  R²                      = {R2:.5f}")
print(f"  → Linieritas {'BAIK (R² ≥ 0.999)' if R2 >= 0.999 else 'PERLU DIPERIKSA'}")

print(f"\n[3] HASIL PERHITUNGAN KADAR Fe SAMPEL")
print(f"  Faktor Pengenceran : {faktor_pengenceran}×")
print(f"  {'Nama Sampel':<30} {'A_ukur':>7} {'C_terukur (mg/L)':>18} {'C_aktual (mg/L)':>16}")
print("  " + "-" * 74)

hasil_sampel = {}
for nama, absorb in sampel.items():
    c_ter, c_akt = hitung_konsentrasi(absorb, slope, intercept, faktor_pengenceran)
    hasil_sampel[nama] = {"absorbansi": absorb, "c_terukur": c_ter, "c_aktual": c_akt}
    print(f"  {nama:<30} {absorb:>7.3f} {c_ter:>18.4f} {c_akt:>16.4f}")

print(f"\n[4] PERBANDINGAN DENGAN BAKU MUTU")
print(f"  Baku Mutu Air Minum (PerMenKes 492/2010) : {BAKU_MUTU_AIR_MINUM_MGL} mg/L")
print(f"  Baku Mutu Air Bersih                      : {BAKU_MUTU_AIR_BERSIH_MGL} mg/L")
print(f"  Baku Mutu Air Sungai Kelas I (PP 22/2021) : {BAKU_MUTU_AIR_SUNGAI_MGL} mg/L")
print()

baku_per_sampel = {
    "Sampel A (Air Sumur)"  : BAKU_MUTU_AIR_BERSIH_MGL,
    "Sampel B (Air Sungai)" : BAKU_MUTU_AIR_SUNGAI_MGL,
    "Sampel C (Air PDAM)"   : BAKU_MUTU_AIR_MINUM_MGL,
}

for nama, data in hasil_sampel.items():
    bm  = baku_per_sampel.get(nama, BAKU_MUTU_AIR_BERSIH_MGL)
    c   = data["c_aktual"]
    sts = "✓ MEMENUHI BAKU MUTU" if c <= bm else "✗ MELEBIHI BAKU MUTU"
    pct = (c / bm) * 100
    print(f"  {nama}")
    print(f"    Kadar Fe      : {c:.4f} mg/L")
    print(f"    Baku Mutu     : {bm} mg/L")
    print(f"    Persentase BM : {pct:.1f}%")
    print(f"    Status        : {sts}")
    print()

print("[5] KESIMPULAN OTOMATIS")
for nama, data in hasil_sampel.items():
    bm = baku_per_sampel.get(nama, BAKU_MUTU_AIR_BERSIH_MGL)
    c  = data["c_aktual"]
    if c <= bm:
        print(f"  • {nama}: AMAN — kadar Fe {c:.4f} mg/L ≤ baku mutu {bm} mg/L")
    else:
        lebih = c - bm
        print(f"  • {nama}: TIDAK AMAN — kadar Fe {c:.4f} mg/L melebihi baku mutu {bm} mg/L "
              f"(selisih {lebih:.4f} mg/L)")

print(f"\n{garis}")
print(" Selesai. Gunakan data di atas untuk laporan LPK.")
print(garis)
