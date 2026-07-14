import streamlit as st
import database_utils as db_utils

# Impostazione della pagina Streamlit
st.set_page_config(page_title="Gestionale Centro Estivo", layout="wide")

# Inizializza la lettura temporanea del tuo file Excel
db_utils.inizializza_database_in_memoria()

# Carica il tuo tabellone con tutte le colonne da A ad AH
df_iscritti = db_utils.ottieni_iscritti()

st.title("☀️ Dashboard Simulazione Centro Estivo")

# Test di visualizzazione grafica: mostra il tuo file Excel direttamente nell'app web
if not df_iscritti.empty:
    st.write(f"### Dati caricati dal tuo file Excel (Totale righe: {len(df_iscritti)})")
    st.dataframe(df_iscritti, use_container_width=True)
else:
    st.info("In attesa che il file 'gestionale.xlsx' venga letto correttamente.")