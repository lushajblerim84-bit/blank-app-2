import streamlit as st
import pandas as pd
import os

# -------------------------------------------------------------
# 1. ZUGRIFFSSCHUTZ (Nur berechtigte Nutzer)
# -------------------------------------------------------------
# Tragen Sie hier die E-Mail-Adressen ein, die die App nutzen dürfen
ERLAUBTE_NUTZER = ["ihre-email@gmail.com", "mitarbeiter@firma.de"]

# Streamlit prüft beim privaten Deployment automatisch die E-Mail des angemeldeten Nutzers
user_email = st.user.email


if not user_email or user_email not in ERLAUBTE_NUTZER:
    st.error("🔒 Zugriff verweigert. Sie haben keine Berechtigung für diese App.")
    st.stop() # Stoppt die App sofort hier

# -------------------------------------------------------------
# 2. LAGER-LOGIK (Wird nur ausgeführt, wenn der Login stimmt)
# -------------------------------------------------------------
DB_FILE = "lager_daten_final.csv"

if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=["Artikel-ID", "Artikelname", "Ist-Bestand", "Soll-Bestand"])
    df.to_csv(DB_FILE, index=False)
else:
    df = pd.read_csv(DB_FILE, dtype={"Artikel-ID": str})

st.set_page_config(page_title="Interne Lagerverwaltung", layout="centered")
st.title("📦 Internes Lager")
st.caption(f"Angemeldet als: {user_email}")

# --- 3. LIEFERSCHEIN-SCANNER ---
st.subheader("📸 Lieferschein automatisch einscannen")
uploaded_file = st.file_uploader("Foto oder PDF hochladen", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.info("Analysiere Lieferschein...")
    # Automatische Erkennungs-Simulation
    scanned_items = [
        {"Artikel-ID": "SCAN-2001", "Artikelname": "Kabeltrommel 25m", "Menge": 5},
        {"Artikel-ID": "SCAN-2002", "Artikelname": "Schraubendreher-Set", "Menge": 12}
    ]
    
    st.success(f"{len(scanned_items)} Artikel erkannt!")
    scan_df = pd.DataFrame(scanned_items)
    st.dataframe(scan_df, hide_index=True)
    
    if st.button("🚀 Artikel einbuchen"):
        for item in scanned_items:
            if item["Artikel-ID"] in df["Artikel-ID"].values:
                idx = df[df["Artikel-ID"] == item["Artikel-ID"]].index
                df.at[idx, "Ist-Bestand"] += item["Menge"]
            else:
                new_row = pd.DataFrame([{"Artikel-ID": item["Artikel-ID"], "Artikelname": item["Artikelname"], "Ist-Bestand": item["Menge"], "Soll-Bestand": 10}])
                df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DB_FILE, index=False)
        st.success("Lager aktualisiert!")
        st.rerun()

st.markdown("---")

# --- 4. LAGERBESTAND ANZEIGEN ---
st.subheader("📋 Aktueller Bestand")

if df.empty:
    st.info("Das Lager ist leer.")
else:
    def highlight_low_stock(row):
        color = 'background-color: #ffcccc; color: #cc0000; font-weight: bold;' if int(row['Ist-Bestand']) < int(row['Soll-Bestand']) else ''
        return [color] * len(row)

    styled_df = df.style.apply(highlight_low_stock, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
