import streamlit as st
import pandas as pd
import os
# Assicurati che questo import corrisponda a dove si trova la tua funzione di caricamento config
from src.utils.config_manager import carica_configurazione 

def inizializza_database_in_memoria():
    """Carica il file Excel reale prendendo i parametri dal config.json"""
    if "iscritti" not in st.session_state:
        # 1. Leggiamo i dati del file dal config.json
        config = carica_configurazione()
        db_config = config.get("database", {})
        
        # Recuperiamo i valori o usiamo dei "salvagente" di default se mancano nel json
        file_excel = db_config.get("file_excel", "Iscrizioni.xlsx")
        nome_scheda = db_config.get("nome_scheda", "Risposte del modulo 1")

        if os.path.exists(file_excel):
            try:
                # 2. Carichiamo l'Excel dinamicamente: prende TUTTE le colonne presenti, 
                # senza limiti fissi (da A a dove arrivano le risposte del modulo)
                st.session_state.iscritti = pd.read_excel(file_excel, sheet_name=nome_scheda)
                
                # Pulizia di sicurezza: rimuoviamo eventuali spazi vuoti accidentali nei nomi delle colonne
                st.session_state.iscritti.columns = st.session_state.iscritti.columns.str.strip()
                
            except Exception as e:
                st.error(f"Errore nel caricamento del file Excel '{file_excel}' (Scheda: '{nome_scheda}'): {e}")
                st.session_state.iscritti = pd.DataFrame()
        else:
            st.error(f"Attenzione: il file Excel '{file_excel}' impostato nel config.json non è stato trovato nella cartella del progetto.")
            st.session_state.iscritti = pd.DataFrame()

def ottieni_iscritti():
    """Restituisce il tabellone completo con tutte le colonne reali del modulo"""
    inizializza_database_in_memoria()
    return st.session_state.iscritti

def salva_modifiche_simulazione(df_aggiornato):
    """Aggiorna i dati nella memoria dell'app per vedere le modifiche grafiche in tempo reale"""
    st.session_state.iscritti = df_aggiornato