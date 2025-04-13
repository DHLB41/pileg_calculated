import streamlit as st
import pandas as pd

# Konfigurasi halaman
st.set_page_config(page_title="Kalkulator Kebutuhan Suara Pemilu 2029", layout="wide")

# Load data dari Excel
file_path = "data_calculated.xlsx"
df_suara = pd.read_excel(file_path, sheet_name="perolehan_suara")
df_kursi = pd.read_excel(file_path, sheet_name="hasil_sl")
df_dapil = pd.read_excel(file_path, sheet_name="dapil")

def format_ribuan(x):
    try:
        return f"{int(x):,}".replace(",", ".")
    except:
        return x

# Daftar partai yang lolos
partai_terpilih = ["PKB", "GERINDRA", "PDIP", "GOLKAR", "NASDEM", "PKS", "PAN", "DEMOKRAT"]

# Fungsi total suara & kursi nasional
def get_total_suara(partai):
    return df_suara[partai].sum() if partai in df_suara.columns else 0

def get_total_kursi(partai):
    return df_kursi[partai].sum() if partai in df_kursi.columns else 0

# Fungsi Sainte-Lague
def simulasi_sainte_lague(dapil_nama, alokasi_kursi, df_suara, partai_lolos):
    alokasi_kursi = int(alokasi_kursi)  # ⬅️ Perbaikan WAJIB
    baris = df_suara[df_suara["DAPIL"] == dapil_nama]
    if baris.empty:
        return [], {}
    hasil_bagi = []
    for partai in partai_lolos:
        try:
            suara = int(baris[partai].values[0])
        except (KeyError, ValueError, TypeError):
            continue  # skip partai tidak valid
        alokasi_kursi = int(alokasi_kursi)
        for pembagi in range(1, alokasi_kursi * 2, 2):
            hasil_bagi.append((partai, suara / pembagi))
    hasil_bagi.sort(key=lambda x: x[1], reverse=True)
    alokasi = hasil_bagi[:alokasi_kursi]
    hasil_akhir = {}
    for partai, _ in alokasi:
        hasil_akhir[partai] = hasil_akhir.get(partai, 0) + 1
    urutan_kursi = [p[0] for p in alokasi]
    return urutan_kursi, hasil_akhir

def partai_kursi_ke_2_terbawah(dapil_nama, alokasi_kursi):
    urutan_kursi, _ = simulasi_sainte_lague(dapil_nama, alokasi_kursi, df_suara, partai_terpilih)
    return urutan_kursi[-2] if len(urutan_kursi) >= 2 else None

# UI - Bagian 1: Data Umum Partai
st.title("PERHITUNGAN KEBUTUHAN SUARA PEMILU LEGISLATIF 2029")
st.header("1. Data Umum Partai")
partai_list = df_suara.columns[1:].tolist()
selected_party = st.selectbox("Partai", partai_list)

votes_2024 = get_total_suara(selected_party)
seats_2024 = get_total_kursi(selected_party)

st.text_input("Perolehan Suara Pemilu 2024", value=f"{votes_2024:,}".replace(",", "."), disabled=False)
st.text_input("Perolehan Kursi Pemilu 2024", value=f"{seats_2024:,}".replace(",", "."), disabled=False)

st.markdown("<br>", unsafe_allow_html=True)  # Spasi vertikal

# UI - Bagian 2: Sebaran Suara & Kursi per Dapil
st.header("2. Sebaran Perolehan Suara dan Kursi Tiap Dapil Pemilu 2024")

def get_suara_per_dapil(partai):
    return df_suara.set_index("DAPIL")[partai].to_dict() if partai in df_suara.columns else {}

def get_kursi_per_dapil(partai):
    return df_kursi.set_index("DAPIL")[partai].to_dict() if partai in df_kursi.columns else {}

suara_dapil = get_suara_per_dapil(selected_party)
kursi_dapil = get_kursi_per_dapil(selected_party)

tabel_dapil = df_dapil.copy()
tabel_dapil["Perolehan Suara"] = tabel_dapil["DAPIL"].map(suara_dapil).fillna(0).astype(int)
tabel_dapil["Perolehan Kursi"] = tabel_dapil["DAPIL"].map(kursi_dapil).fillna(0).astype(int)
tabel_dapil["Persentase Perolehan Suara"] = (
    (tabel_dapil["Perolehan Suara"] / tabel_dapil["TOTAL DPT"]) * 100
).round(2).astype(str) + " %"
tabel_dapil["TOTAL DPT"] = tabel_dapil["TOTAL DPT"].apply(lambda x: f"{x:,}".replace(",", "."))
tabel_dapil["Perolehan Suara"] = tabel_dapil["Perolehan Suara"].apply(lambda x: f"{x:,}".replace(",", "."))
tabel_dapil["No"] = range(1, len(tabel_dapil) + 1)
tabel_dapil = tabel_dapil[["No", "DAPIL", "ALOKASI KURSI", "TOTAL DPT", "Perolehan Suara", "Perolehan Kursi", "Persentase Perolehan Suara"]]

# Pagination
per_page = 10
if "current_page" not in st.session_state:
    st.session_state.current_page = 1
start_idx = (st.session_state.current_page - 1) * per_page
end_idx = start_idx + per_page
tabel_page = tabel_dapil.iloc[start_idx:end_idx]

st.markdown("""
<style>
.scrollable-table { overflow-x: auto; overflow-y: auto; max-height: 600px; width: 100%; border: 1px solid #333; border-radius: 8px; background-color: rgba(255,255,255,0.02); margin-bottom: 0.5rem; }
.centered-table { width: 100% !important; table-layout: fixed; font-family: "Segoe UI", "Roboto", sans-serif; border-collapse: collapse; text-align: center; }
.centered-table th, .centered-table td { text-align: center !important; vertical-align: middle !important; font-size: 14px; white-space: nowrap; padding: 10px 8px; border-bottom: 1px solid #2c2c2c; }
.centered-table th { background-color: #1f1f1f; color: #ffffff; text-transform: uppercase; }
.centered-table tr:hover td { background-color: rgba(255,255,255,0.05); }
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="scrollable-table">{tabel_page.to_html(index=False, classes="centered-table", escape=False)}</div>', unsafe_allow_html=True)
# Navigasi setelah tabel sebaran dapil
col_prev, col_center, col_next = st.columns([1, 6, 1])

with col_prev:
    if st.session_state.current_page > 1:
        if st.button("← Sebelumnya", key="prev_page"):
            st.session_state.current_page -= 1

with col_next:
    if st.session_state.current_page < (len(tabel_dapil) - 1) // per_page + 1:
        if st.button("Berikutnya →", key="next_page"):
            st.session_state.current_page += 1

st.caption(f"Menampilkan halaman ke-{st.session_state.current_page} dari {(len(tabel_dapil) - 1) // per_page + 1}")

st.markdown("<br>", unsafe_allow_html=True)  # Spasi vertikal


# UI - Bagian 3: Target Kursi dan Proporsi
st.header("3. Target Perolehan Kursi & Proporsi Kenaikan Suara")
target_kursi_2029 = st.number_input("Target Perolehan Kursi Pemilu 2029", min_value=0, step=1, value=0)

st.subheader("Proporsi Target Kenaikan Suara Tiap Kursi Per Dapil")
kursi_input = {}
kursi_labels = ["Kursi Ke-1", "Kursi Ke-2", "Kursi Ke-3", "Kursi Ke-4"]
rows = ["1", "2", "3", "4"]
for row in rows:
    st.markdown(f"**Target Penambahan {row} Kursi**")
    col1, col2, col3, col4 = st.columns(4)
    for idx, col in enumerate([col1, col2, col3, col4]):
        with col:
            key = f"proporsi_{row}_{idx+1}"
            kursi_input[key] = st.number_input(label=kursi_labels[idx], key=key, min_value=0.0, max_value=200.0, step=1.0, format="%.2f")

with st.expander("Faktor Pengurang dan Target Suara", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        kehilangan_2024 = st.number_input("Potensi Kehilangan Suara 2029 (%)", min_value=0.0, max_value=200.0, step=1.0, format="%.2f")
    with col2:
        kehilangan_sp = st.number_input("Potensi Kehilangan SP (%)", min_value=0.0, max_value=200.0, step=1.0, format="%.2f")
    with col3:
        target_suara_2029 = st.number_input("Proporsi Target Suara 2029 (%)", min_value=0.0, max_value=200.0, step=1.0, format="%.2f")

kriteria1_dapil = []

for dapil in df_suara["DAPIL"].tolist():
    alokasi_row = df_dapil[df_dapil["DAPIL"] == dapil]
    if alokasi_row.empty:
        continue

    alokasi = int(alokasi_row["ALOKASI KURSI"].values[0])
    kursi_partai = df_kursi[df_kursi["DAPIL"] == dapil]
    suara_partai = df_suara[df_suara["DAPIL"] == dapil]

    if kursi_partai.empty or suara_partai.empty:
        continue

    kursi = int(kursi_partai.get(selected_party, pd.Series([0])).values[0])
    suara = int(suara_partai.get(selected_party, pd.Series([0])).values[0])

    if kursi != 0:
        continue  # hanya ambil dapil dengan perolehan kursi = 0

    # Jalankan simulasi Sainte-Laguë
    partai_lolos = partai_terpilih.copy()
    if selected_party not in partai_lolos:
        partai_lolos.append(selected_party)

    urutan_kursi, _ = simulasi_sainte_lague(dapil, alokasi, df_suara, partai_lolos)

    if len(urutan_kursi) < 2:
        continue

    partai_k2 = urutan_kursi[-2]  # kursi ke-2 terakhir
    suara_k2 = int(suara_partai[partai_k2].values[0])

    total_target_suara = int(suara_k2 * 1.1)  # naik 10%

    kriteria1_dapil.append({
        "DAPIL": dapil,
        "PARTAI": selected_party,
        "ALOKASI_KURSI": alokasi,
        "SUARA_2024": suara,
        "KURSI_2024": kursi,
        "TARGET_TAMBAHAN_KURSI": 1,
        "PARTAI_K2_TERENDAH": partai_k2,
        "SUARA_K2": suara_k2,
        "TOTAL_TARGET_SUARA_2029": total_target_suara
    })

# Konversi ke DataFrame
df_kriteria1 = pd.DataFrame(kriteria1_dapil)

# Kriteria 2: Kursi = 1 & Kursi ke-2 terbawah adalah PAN/DEMOKRAT
kriteria2_dapil = []

for dapil in df_suara["DAPIL"].tolist():
    alokasi_row = df_dapil[df_dapil["DAPIL"] == dapil]
    if alokasi_row.empty:
        continue

    alokasi = int(alokasi_row["ALOKASI KURSI"].values[0])
    kursi_partai = df_kursi[df_kursi["DAPIL"] == dapil]
    suara_partai = df_suara[df_suara["DAPIL"] == dapil]

    if kursi_partai.empty or suara_partai.empty:
        continue

    kursi = int(kursi_partai.get(selected_party, pd.Series([0])).values[0])
    suara = int(suara_partai.get(selected_party, pd.Series([0])).values[0])

    if kursi != 1:
        continue

    urutan_kursi, _ = simulasi_sainte_lague(dapil, alokasi, df_suara, partai_terpilih)
    if len(urutan_kursi) < 2:
        continue

    partai_k2 = urutan_kursi[-2]
    if partai_k2 not in ["PAN", "DEMOKRAT"]:
        continue

    suara_k2 = int(suara_partai[partai_k2].values[0])
    total_target_suara = int(suara_k2 * 3 * 1.1)

    # REVISI TARGET TAMBAHAN KURSI
    if alokasi <= 4:
        target_kursi = 1
    else:
        target_kursi = 1 + kursi

    kriteria2_dapil.append({
        "DAPIL": dapil,
        "PARTAI": selected_party,
        "ALOKASI_KURSI": alokasi,
        "SUARA_2024": suara,
        "KURSI_2024": kursi,
        "TARGET_TAMBAHAN_KURSI": target_kursi,
        "PARTAI_K2_TERENDAH": partai_k2,
        "SUARA_K2": suara_k2,
        "TOTAL_TARGET_SUARA_2029": total_target_suara
    })

df_kriteria2 = pd.DataFrame(kriteria2_dapil)

# Kriteria 3: Kursi = 1 (umum)
kriteria3_dapil = []

for dapil in df_suara["DAPIL"].tolist():
    alokasi_row = df_dapil[df_dapil["DAPIL"] == dapil]
    if alokasi_row.empty:
        continue

    alokasi = int(alokasi_row["ALOKASI KURSI"].values[0])
    kursi_partai = df_kursi[df_kursi["DAPIL"] == dapil]
    suara_partai = df_suara[df_suara["DAPIL"] == dapil]

    if kursi_partai.empty or suara_partai.empty:
        continue

    kursi = int(kursi_partai.get(selected_party, pd.Series([0])).values[0])
    suara = int(suara_partai.get(selected_party, pd.Series([0])).values[0])

    if kursi != 1:
        continue

    urutan_kursi, _ = simulasi_sainte_lague(dapil, alokasi, df_suara, partai_terpilih)
    if len(urutan_kursi) < 2:
        continue

    partai_k2 = urutan_kursi[-2]
    suara_k2 = int(suara_partai[partai_k2].values[0])
    total_target_suara = int(suara_k2 * 3 * 1.1)

    # REVISI TARGET TAMBAHAN KURSI
    if alokasi <= 4:
        target_kursi = 1
    else:
        target_kursi = 1 + kursi

    kriteria3_dapil.append({
        "DAPIL": dapil,
        "PARTAI": selected_party,
        "ALOKASI_KURSI": alokasi,
        "SUARA_2024": suara,
        "KURSI_2024": kursi,
        "TARGET_TAMBAHAN_KURSI": target_kursi,
        "PARTAI_K2_TERENDAH": partai_k2,
        "SUARA_K2": suara_k2,
        "TOTAL_TARGET_SUARA_2029": total_target_suara
    })

df_kriteria3 = pd.DataFrame(kriteria3_dapil)

# Bagian kalkulasi untuk Kriteria 4: Kursi > 1 (Target Kursi 2029 = Kursi 2024)
kriteria4_dapil = []

for dapil in df_suara["DAPIL"].tolist():
    alokasi_row = df_dapil[df_dapil["DAPIL"] == dapil]
    if alokasi_row.empty:
        continue

    alokasi = int(alokasi_row["ALOKASI KURSI"].values[0])
    kursi_partai = df_kursi[df_kursi["DAPIL"] == dapil]
    suara_partai = df_suara[df_suara["DAPIL"] == dapil]

    if kursi_partai.empty or suara_partai.empty:
        continue

    kursi = int(kursi_partai.get(selected_party, pd.Series([0])).values[0])
    suara = int(suara_partai.get(selected_party, pd.Series([0])).values[0])

    if kursi <= 1:
        continue  # hanya untuk dapil dengan kursi > 1

    # Ambil partai ke-2 terakhir dari simulasi Sainte-Laguë
    urutan_kursi, _ = simulasi_sainte_lague(dapil, alokasi, df_suara, partai_terpilih)
    if len(urutan_kursi) < 2:
        continue

    partai_k2 = urutan_kursi[-2]
    suara_k2 = int(suara_partai[partai_k2].values[0])
    total_target_suara = int(suara_k2 * 3 * 1.1)

    kriteria4_dapil.append({
        "DAPIL": dapil,
        "PARTAI": selected_party,
        "ALOKASI_KURSI": alokasi,
        "SUARA_2024": suara,
        "KURSI_2024": kursi,
        "TARGET_TAMBAHAN_KURSI": kursi,  # Target sama dengan jumlah kursi 2024
        "PARTAI_K2_TERENDAH": partai_k2,
        "SUARA_K2": suara_k2,
        "TOTAL_TARGET_SUARA_2029": total_target_suara
    })

df_kriteria4 = pd.DataFrame(kriteria4_dapil)
df_kriteria4["KRITERIA"] = 4

# 1. Gabungkan seluruh df_kriteria1, df_kriteria2, df_kriteria3, df_kriteria4
for df_k, k in zip([df_kriteria1, df_kriteria2, df_kriteria3, df_kriteria4], [1, 2, 3, 4]):
    df_k["KRITERIA"] = k

# Gabungkan dan urutkan
df_all_kriteria = pd.concat([df_kriteria1, df_kriteria2, df_kriteria3, df_kriteria4], ignore_index=True)
df_all_kriteria = df_all_kriteria.sort_values(by="TOTAL_TARGET_SUARA_2029", ascending=True)

# Hapus duplikat berdasarkan DAPIL → prioritas kriteria terendah
df_all_kriteria = df_all_kriteria.drop_duplicates(subset=["DAPIL"], keep="first")

# 2. Seleksi Dapil Sesuai Target Kursi
selected_rows = []
total_kursi = 0
for _, row in df_all_kriteria.iterrows():
    if total_kursi >= target_kursi_2029:
        break
    selected_rows.append(row.to_dict())  # ✅ Penting agar semua kolom terbawa
    total_kursi += row["TARGET_TAMBAHAN_KURSI"]

# 3. Bentuk df_terpilih dari selected_rows
df_terpilih = pd.DataFrame(selected_rows).reset_index(drop=True)

# 4. Validasi kolom
if "TOTAL_TARGET_SUARA_2029" not in df_terpilih.columns:
    st.error("SILAHKAN ISI TOTAL TARGET PEROLEHAN KURSI PEMILU 2029 TERLEBIH DAHULU")
    st.stop()

# ============================
# Perhitungan SP & SP per Kursi
# ============================

# Pastikan TARGET_KEBUTUHAN sudah dihitung sebelumnya
df_terpilih["TARGET_KEBUTUHAN"] = df_terpilih["TOTAL_TARGET_SUARA_2029"]

# Hitung SUARA TAMBAHAN
def hitung_suara_tambahan(row):
    if row["TARGET_TAMBAHAN_KURSI"] == 0:
        return 0
    elif row["TARGET_KEBUTUHAN"] < row["SUARA_2024"]:
        return 0
    return row["TARGET_KEBUTUHAN"] - row["SUARA_2024"]

df_terpilih["SUARA_TAMBAHAN"] = df_terpilih.apply(hitung_suara_tambahan, axis=1)

# Hitung TOTAL SUARA TAMBAHAN
def hitung_total_suara_tambahan(row):
    if row["SUARA_TAMBAHAN"] == 0:
        return 0
    return row["SUARA_TAMBAHAN"] + (row["SUARA_2024"] * (kehilangan_2024 / 100))

df_terpilih["TOTAL_SUARA_TAMBAHAN"] = df_terpilih.apply(hitung_total_suara_tambahan, axis=1)

# Hitung SP
def hitung_sp(row):
    if row["TOTAL_SUARA_TAMBAHAN"] == 0:
        return 0
    return row["TOTAL_SUARA_TAMBAHAN"] * (1 + kehilangan_sp / 100)

df_terpilih["SP"] = df_terpilih.apply(hitung_sp, axis=1)

# SP per Kursi
for i in range(1, 5):
    df_terpilih[f"SP_KURSI_{i}"] = 0.0

def hitung_sp_per_kursi(row):
    jumlah_kursi = int(row["TARGET_TAMBAHAN_KURSI"])
    total_sp = row["SP"]
    hasil = [0.0, 0.0, 0.0, 0.0]

    if jumlah_kursi == 1:
        hasil[0] = total_sp
    elif jumlah_kursi in [2, 3, 4]:
        for i in range(jumlah_kursi):
            proporsi_key = f"proporsi_{jumlah_kursi}_{i+1}"
            proporsi = kursi_input.get(proporsi_key, 0)
            hasil[i] = (total_sp / jumlah_kursi) * (proporsi / 100)
    return pd.Series(hasil)

sp_result = df_terpilih.apply(hitung_sp_per_kursi, axis=1)
df_terpilih[["SP_KURSI_1", "SP_KURSI_2", "SP_KURSI_3", "SP_KURSI_4"]] = sp_result

st.markdown("<br>", unsafe_allow_html=True)  # Spasi vertikal

# Gabungkan Sebaran Dapil Potensial dan SP Tiap Kursi (dengan tampilan tabel rapi)
st.header("4. Sebaran Dapil Potensial dan SP Tiap Kursi")

if "dapil_page" not in st.session_state:
    st.session_state.dapil_page = 0

total_dapil = len(df_terpilih)

if total_dapil == 0:
    st.warning("Tidak ada dapil yang memenuhi kriteria atau target kursi.")
else:
    dapil = df_terpilih.iloc[st.session_state.dapil_page]

    st.markdown(f"### DAPIL: **{dapil['DAPIL']}**")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Alokasi Kursi", value=format_ribuan(dapil['ALOKASI_KURSI']), disabled=False)
    with col2:
        st.text_input("Perolehan Suara Pemilu 2024", value=f"{dapil['SUARA_2024']:,}".replace(",", "."), disabled=False)
    with col3:
        st.text_input("Perolehan Kursi Pemilu 2024", value=format_ribuan(dapil['KURSI_2024']), disabled=False)

    col4, col5, col6 = st.columns(3)
    with col4:
        st.text_input("Target Tambahan Kursi 2029", value=format_ribuan(dapil['TARGET_TAMBAHAN_KURSI']), disabled=False)
    with col5:
        st.text_input("Total Target Suara 2029", value=f"{dapil['TOTAL_TARGET_SUARA_2029']:,}".replace(",", "."), disabled=False)
    with col6:
        st.text_input("Partai Kursi Ke-2 Terbawah", value=f"{dapil['PARTAI_K2_TERENDAH']} ({dapil['SUARA_K2']:,} suara)".replace(",", "."), disabled=False)

    # Tabel distribusi SP per kursi (per dapil)
    st.markdown("#### Tabel Distribusi SP per Kursi")

    sp_kolom = ["SP", "SP_KURSI_1", "SP_KURSI_2", "SP_KURSI_3", "SP_KURSI_4"]
    df_single = dapil[sp_kolom].to_frame().T.copy()
    df_single.columns = ["TOTAL SP", "SP Kursi 1", "SP Kursi 2", "SP Kursi 3", "SP Kursi 4"]

    for col in df_single.columns:
        df_single[col] = df_single[col].apply(lambda x: f"{int(x):,}".replace(",", ".") if x > 0 else "0")

    st.markdown("""
    <style>
    .scrollable-table {
        overflow-x: auto;
        overflow-y: auto;
        max-height: 600px;
        width: 100%;
        border: 1px solid #333;
        border-radius: 8px;
        background-color: rgba(255,255,255,0.02);
        margin-bottom: 0.5rem;
    }
    .centered-table {
        width: 100% !important;
        table-layout: fixed;
        font-family: "Segoe UI", "Roboto", sans-serif;
        border-collapse: collapse;
        text-align: center;
    }
    .centered-table th, .centered-table td {
        text-align: center !important;
        vertical-align: middle !important;
        font-size: 14px;
        white-space: nowrap;
        padding: 10px 8px;
        border-bottom: 1px solid #2c2c2c;
    }
    .centered-table th {
        background-color: #1f1f1f;
        color: #ffffff;
        text-transform: uppercase;
    }
    .centered-table tr:hover td {
        background-color: rgba(255,255,255,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<div class="scrollable-table">{df_single.to_html(index=False, classes="centered-table", escape=False)}</div>',
        unsafe_allow_html=True
    )

    # Input angka psikologis
    angka_psikologis = st.number_input("Angka Psikologis", min_value=0, value=0, step=1000, format="%d")

    # Hitung RAB SP per kursi
    rab_sp_kursi = []
    for i in range(1, 5):
        sp = dapil.get(f"SP_KURSI_{i}", 0)
        rab = int(sp * angka_psikologis)
        rab_sp_kursi.append(rab)

    df_rab = pd.DataFrame([rab_sp_kursi], columns=["RAB Kursi 1", "RAB Kursi 2", "RAB Kursi 3", "RAB Kursi 4"])
    for col in df_rab.columns:
        df_rab[col] = df_rab[col].apply(lambda x: f"{x:,}".replace(",", "."))

    st.markdown("#### Tabel RAB SP per Kursi")
    st.markdown(
        f'<div class="scrollable-table">{df_rab.to_html(index=False, classes="centered-table", escape=False)}</div>',
        unsafe_allow_html=True
    )

    # Input Manajemen dan Pendampingan
    col_mgmt, col_pdmp = st.columns(2)
    with col_mgmt:
        biaya_manajemen = st.number_input("Biaya Manajemen", min_value=0, value=0, step=100000, format="%d")
    with col_pdmp:
        biaya_pendampingan = st.number_input("Biaya Pendampingan", min_value=0, value=0, step=100000, format="%d")

    # Hitung total RAB per kursi hanya jika SP tidak nol
    rab_numerik = [int(r.replace(".", "")) for r in df_rab.iloc[0]]
    total_rab_kursi = [rab + biaya_manajemen + biaya_pendampingan if rab > 0 else 0 for rab in rab_numerik]
    total_rab_all = sum(total_rab_kursi)

    df_total_rab = pd.DataFrame([total_rab_kursi + [total_rab_all]],
        columns=["Total RAB Kursi 1", "Total RAB Kursi 2", "Total RAB Kursi 3", "Total RAB Kursi 4", "TOTAL RAB"])
    for col in df_total_rab.columns:
        df_total_rab[col] = df_total_rab[col].apply(lambda x: f"{x:,}".replace(",", "."))

    st.markdown("#### Total RAB (SP + Manajemen + Pendampingan)")
    st.markdown(
        f'<div class="scrollable-table">{df_total_rab.to_html(index=False, classes="centered-table", escape=False)}</div>',
        unsafe_allow_html=True
    )

    # Navigasi
    col_prev, _, col_next = st.columns([1, 8, 1])
    with col_prev:
        if st.session_state.dapil_page > 0:
            if st.button("← Sebelumnya"):
                st.session_state.dapil_page -= 1
    with col_next:
        if st.session_state.dapil_page < total_dapil - 1:
            if st.button("Berikutnya →"):
                st.session_state.dapil_page += 1

    st.caption(f"Menampilkan dapil ke-{st.session_state.dapil_page + 1} dari {total_dapil}")

# Pop-up hasil Sainte-Laguë di UI Dapil (dalam expander per dapil)
urutan_kursi, hasil_akhir = simulasi_sainte_lague(dapil['DAPIL'], dapil['ALOKASI_KURSI'], df_suara, partai_terpilih)

if urutan_kursi:
    hasil_sl_detail = []
    baris = df_suara[df_suara["DAPIL"] == dapil["DAPIL"]]
    alokasi = dapil["ALOKASI_KURSI"]

    for partai in partai_terpilih:
        suara = int(baris[partai].values[0])
        alokasi = int(alokasi)
        for pembagi in range(1, alokasi * 2, 2):
            hasil_sl_detail.append({
                "Partai": partai,
                "Suara": suara,
                "Pembagi": pembagi,
                "Hasil Bagi": suara / pembagi
            })

    # Sort dan ambil kursi terbanyak
    df_sl = pd.DataFrame(hasil_sl_detail).sort_values(by="Hasil Bagi", ascending=False).reset_index(drop=True)
    df_sl["DAPIL"] = dapil["DAPIL"]
    df_sl["ALOKASI KURSI"] = alokasi

    # Tambahkan nomor kursi ke- untuk alokasi terbanyak
    df_sl["KURSI KE-"] = ""
    for i in range(min(alokasi, len(df_sl))):
        df_sl.at[i, "KURSI KE-"] = i + 1

    df_sl = df_sl[["DAPIL", "ALOKASI KURSI", "KURSI KE-", "Partai", "Suara", "Pembagi"]]

    # Format angka
    df_sl["Suara"] = df_sl["Suara"].apply(lambda x: f"{x:,}".replace(",", "."))
    df_sl["Pembagi"] = df_sl["Pembagi"].astype(int)

    with st.expander("📊 Lihat Detail Hasil Sainte-Laguë"):
        st.markdown("##### Tabel Pembagian Kursi Berdasarkan Metode Sainte-Laguë")
        st.markdown(
            f'<div class="scrollable-table">{df_sl.to_html(index=False, classes="centered-table", escape=False)}</div>',
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)  # Spasi vertikal
st.markdown("<br>", unsafe_allow_html=True)  # Spasi vertikal

# === PART 5: RANGKUMAN PERHITUNGAN AKHIR ===
st.header("5. Rangkuman Hasil Akhir Kalkulasi")

# Ringkasan Angka Total
col1, col2, col3 = st.columns(3)
with col1:
    total_suara_2029 = df_terpilih['TOTAL_TARGET_SUARA_2029'].sum()
    st.metric("Total Target Suara 2029", f"{int(total_suara_2029):,}".replace(",", "."))

with col2:
    total_kursi_2029 = df_terpilih['TARGET_TAMBAHAN_KURSI'].sum()
    st.metric("Target Kursi 2029", int(total_kursi_2029))

with col3:
    total_rab = df_terpilih["TOTAL_RAB"].sum() if "TOTAL_RAB" in df_terpilih.columns else 0
    st.metric("Total RAB (Rp)", f"{int(total_rab):,}".replace(",", "."))

st.markdown("---")
st.subheader("Tabel Rangkuman Persebaran Dapil Potensial")

# Siapkan data untuk tabel rangkuman dapil potensial
df_summary_display = df_terpilih[[
    "DAPIL", "ALOKASI_KURSI", "SUARA_2024", "KURSI_2024",
    "TARGET_TAMBAHAN_KURSI", "TOTAL_TARGET_SUARA_2029"
]].copy()

df_summary_display.columns = [
    "DAPIL", "Alokasi Kursi", "Suara 2024", "Kursi 2024",
    "Target Kursi 2029", "Target Suara 2029"
]

# Format angka
for col in ["Suara 2024", "Target Suara 2029"]:
    df_summary_display[col] = df_summary_display[col].apply(lambda x: f"{int(x):,}".replace(",", "."))

# Pagination
per_page = 10
total_pages = (len(df_summary_display) - 1) // per_page + 1
if "summary_page" not in st.session_state:
    st.session_state.summary_page = 1
start_idx = (st.session_state.summary_page - 1) * per_page
end_idx = start_idx + per_page
df_page = df_summary_display.iloc[start_idx:end_idx]

# Tabel HTML + CSS
st.markdown("""
<style>
.scrollable-table { overflow-x: auto; overflow-y: auto; max-height: 600px; width: 100%; border: 1px solid #333; border-radius: 8px; background-color: rgba(255,255,255,0.02); margin-bottom: 0.5rem; }
.centered-table { width: 100% !important; table-layout: fixed; font-family: "Segoe UI", "Roboto", sans-serif; border-collapse: collapse; text-align: center; }
.centered-table th, .centered-table td { text-align: center !important; vertical-align: middle !important; font-size: 14px; white-space: nowrap; padding: 10px 8px; border-bottom: 1px solid #2c2c2c; }
.centered-table th { background-color: #1f1f1f; color: #ffffff; text-transform: uppercase; }
.centered-table tr:hover td { background-color: rgba(255,255,255,0.05); }
</style>
""", unsafe_allow_html=True)

st.markdown(
    f'<div class="scrollable-table">{df_page.to_html(index=False, classes="centered-table", escape=False)}</div>',
    unsafe_allow_html=True
)

# Navigasi bawah tabel
col_prev, col_mid, col_next = st.columns([1, 6, 1])
with col_prev:
    if st.session_state.summary_page > 1:
        if st.button("← Sebelumnya", key="summary_prev"):
            st.session_state.summary_page -= 1
with col_next:
    if st.session_state.summary_page < total_pages:
        if st.button("Selanjutnya →", key="summary_next"):
            st.session_state.summary_page += 1

st.caption(f"Menampilkan halaman {st.session_state.summary_page} dari {total_pages}")