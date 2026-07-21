import streamlit as st
import pandas as pd
import os
from src.utils.config_manager import carica_configurazione 

def inizializza_database_in_memoria():
    """Carica il file Excel reale prendendo i parametri dal config.json"""
    if "df_iscritti" not in st.session_state:
        config = carica_configurazione()
        db_config = config.get("database", {})
        
        file_excel = db_config.get("file_excel", "Iscrizioni.xlsx")
        nome_scheda = db_config.get("nome_scheda", "Risposte del modulo 1")

        if os.path.exists(file_excel):
            try:
                # Carichiamo l'Excel dinamicamente
                df = pd.read_excel(file_excel, sheet_name=nome_scheda)
                df.columns = df.columns.str.strip()
                st.session_state.df_iscritti = df.astype(object)
            except Exception as e:
                st.error(f"Errore nel caricamento del file Excel '{file_excel}' (Scheda: '{nome_scheda}'): {e}")
                st.session_state.df_iscritti = pd.DataFrame()
        else:
            st.error(f"Attenzione: il file Excel '{file_excel}' non è stato trovato nella cartella del progetto.")
            st.session_state.df_iscritti = pd.DataFrame()

def ottieni_iscritti():
    """Restituisce il tabellone completo con tutte le colonne reali del modulo"""
    inizializza_database_in_memoria()
    return st.session_state.df_iscritti

def salva_modifiche_simulazione(df_aggiornato):
    """Aggiorna i dati nella memoria dell'app per vedere le modifiche grafiche in tempo reale"""
    st.session_state.df_iscritti = df_aggiornato.astype(object)

def salva_database_su_excel(df_da_salvare=None):
    """
    Scrive in modo permanente le modifiche sul file Excel specificato nel config.json.
    """
    if df_da_salvare is None:
        df_da_salvare = st.session_state.get("df_iscritti", pd.DataFrame())

    if df_da_salvare.empty:
        return False

    config = carica_configurazione()
    db_config = config.get("database", {})
    file_excel = db_config.get("file_excel", "Iscrizioni.xlsx")
    nome_scheda = db_config.get("nome_scheda", "Risposte del modulo 1")

    try:
        # Usiamo ExcelWriter per sovrascrivere il foglio mantenendo la struttura
        with pd.ExcelWriter(file_excel, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df_da_salvare.to_excel(writer, sheet_name=nome_scheda, index=False)
        return True
    except Exception as e:
        # Fallback se il file non esiste ancora o se openpyxl richiede creazione ex-novo
        try:
            df_da_salvare.to_excel(file_excel, sheet_name=nome_scheda, index=False)
            return True
        except Exception as e_sub:
            st.error(f"❌ Impossibile salvare su file Excel: {e_sub}")
            return False

def aggiungi_nuovo_iscritto(nuova_riga_dict):
    """
    Aggiunge una nuova riga al DataFrame in memoria e salva su Excel.
    """
    inizializza_database_in_memoria()
    df_attuale = st.session_state.df_iscritti

    # Convertiamo il dizionario della nuova riga in DataFrame
    df_nuovo = pd.DataFrame([nuova_riga_dict])

    # Uniamo al dataframe esistente
    df_aggiornato = pd.concat([df_attuale, df_nuovo], ignore_index=True).astype(object)
    
    # Aggiorniamo sia lo stato di sessione sia il file Excel fisico
    st.session_state.df_iscritti = df_aggiornato
    salva_database_su_excel(df_aggiornato)