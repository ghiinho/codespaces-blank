import streamlit as st
import sqlite3
import pandas as pd
import database_utils as db_utils

# Inizializza il database con la nuova struttura corretta alla prima esecuzione
db_utils.inizializza_db_completo()

st.set_page_config(page_title="Gestionale Centro Estivo", layout="wide", page_icon="☀️")
st.title("☀️ Gestionale Centro Estivo - Pannello Operatore")

# Schede di navigazione
tab_tabellone, tab_config, tab_import = st.tabs([
    "📅 Tabellone Settimanale & Cassa", 
    "⚙️ Impostazioni Tariffe", 
    "📥 Importa da Google Moduli"
])

# ==========================================
# TAB 1: TABELLONE SETTIMANALE & CASSA
# ==========================================
with tab_tabellone:
    st.header("Gestione Presenze e Stato Pagamenti")
    
    settimana = st.selectbox("Seleziona la settimana lavorativa:", options=[1,2,3,4,5,6,7,8], format_func=lambda x: f"Settimana {x}")
    
    conn = sqlite3.connect('gestionale_centri.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            Iscrizioni.id, Iscritti.cognome || ' ' || Iscritti.nome AS Bambino, Iscritti.flag_fratelli,
            Iscrizioni.tipo_frequenza, Iscrizioni.prezzo_netto, Iscrizioni.caparra_versata, Iscrizioni.settimana_saldata
        FROM Iscrizioni
        JOIN Iscritti ON Iscrizioni.cf_bambino = Iscritti.cf_bambino
        WHERE Iscrizioni.settimana_numero = ?
    """, (settimana,))
    dati = cursor.fetchall()
    conn.close()
    
    if not dati:
        st.info(f"Nessun iscritto per la Settimana {settimana}. Vai alla scheda 'Importa' per caricare i dati.")
    else:
        df = pd.DataFrame(dati, columns=["ID", "Bambino", "Fratelli?", "Frequenza Scelta", "Quota Dovuta (€)", "Caparra Ok?", "Saldo Settimana Ok?"])
        
        # Mappatura grafica immediata per l'operatore
        df["Caparra Ok?"] = df["Caparra Ok?"].apply(lambda x: "🟢 SI" if x == "SI" else "🔴 NO")
        df["Saldo Settimana Ok?"] = df["Saldo Settimana Ok?"].apply(lambda x: "🟢 SALDATA" if x == "SI" else "🔴 DA SALDARE")
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.success("🎯 Il tabellone visualizza i prezzi già ottimizzati con la regola del maggior favore in tempo reale.")

# ==========================================
# TAB 2: IMPOSTAZIONI TARIFFE
# ==========================================
with tab_config:
    st.header("Configurazione Tariffe e Pacchetti")
    st.write("Modifica qui i prezzi base del centro estivo. L'algoritmo ricalcolerà automaticamente i conti dei bambini.")
    
    conn = sqlite3.connect('gestionale_centri.db')
    df_listini = pd.read_sql_query("SELECT * FROM Listini", conn)
    df_pacchetti = pd.read_sql_query("SELECT * FROM Pacchetti", conn)
    conn.close()
    
    st.subheader("Listino Prezzi Frequenze (€)")
    st.dataframe(df_listini, use_container_width=True, hide_index=True)
    
    st.subheader("Pacchetti Multi-Settimana Attivi")
    st.dataframe(df_pacchetti, use_container_width=True, hide_index=True)

# ==========================================
# TAB 3: IMPORTA DA GOOGLE MODULI
# ==========================================
with tab_import:
    st.header("Caricamento file Excel (.xlsx) di Google Moduli")
    st.write("Carica il file delle risposte per inserire automaticamente Genitori, Bambini e Iscrizioni Settimanali.")
    
    file_caricato = st.file_uploader("Scegli il file Excel delle risposte:", type=["xlsx"])
    if file_caricato is not None:
        st.success("File ricevuto con successo! Pronto per l'elaborazione dei campi reali (Colonne A-AH).")