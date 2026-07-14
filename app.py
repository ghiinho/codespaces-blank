import streamlit as st
import database_utils as db_utils

# Impostazione della pagina
st.set_page_config(page_title="Gestionale Centro Estivo", layout="wide")

st.title("☀️ Dashboard Interattiva Centro Estivo")
st.write("Puoi modificare le settimane o i dati direttamente cliccando sulle celle della tabella qui sotto.")

# Inizializza e ottieni il tabellone dalla memoria temporanea
db_utils.inizializza_database_in_memoria()
df_iscritti = db_utils.ottieni_iscritti()

if not df_iscritti.empty:
    # --- IL TABELLONE INTERATTIVO ---
    # Usiamo st.data_editor invece di st.dataframe per abilitare la modifica diretta
    df_modificato = st.data_editor(
        df_iscritti, 
        use_container_width=True,
        num_rows="dynamic" # Consente anche di aggiungere o eliminare righe se necessario
    )
    
    # Controlla se l'utente ha modificato qualcosa rispetto al file originale
    if not df_modificato.equals(df_iscritti):
        # Salva temporaneamente le modifiche nella memoria di sessione dell'app
        db_utils.salva_modifiche_simulazione(df_modificato)
        st.success("🔄 Calcoli e dati aggiornati in tempo reale nella simulazione!")
        
        # Qui l'app si ricarica automaticamente applicando le modifiche ai tuoi grafici o filtri
        st.rerun()

else:
    st.info("In attesa che il file 'gestionale.xlsx' venga letto correttamente.")