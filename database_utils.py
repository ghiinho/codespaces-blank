import streamlit as st
import pandas as pd
import os

# CONFIGURA QUESTI DUE VALORI CON I TUOI DATI REALI
FILE_EXCEL = "gestionale.xlsx"
NOME_SCHEDA = "Iscritti"  # <-- Sostituisci questo con il nome reale della tua scheda Excel (es. "Iscritti")

def inizializza_database_in_memoria():
    """Carica il tuo file Excel reale e lo mette nella memoria temporanea dell'app"""
    if "iscritti" not in st.session_state:
        if os.path.exists(FILE_EXCEL):
            try:
                # Carica il file Excel originale mantenendo intatte tutte le colonne da A ad AH
                st.session_state.iscritti = pd.read_excel(FILE_EXCEL, sheet_name=NOME_SCHEDA)
            except Exception as e:
                st.error(f"Errore nel caricamento del file Excel: {e}")
                st.session_state.iscritti = pd.DataFrame()
        else:
            st.error(f"Attenzione: il file '{FILE_EXCEL}' non è stato trovato su GitHub. Trascinalo nella cartella dei file.")
            st.session_state.iscritti = pd.DataFrame()

def ottieni_iscritti():
    """Restituisce il tuo tabellone con tutte le colonne da A ad AH"""
    inizializza_database_in_memoria()
    return st.session_state.iscritti

def salva_modifiche_simulazione(df_aggiornato):
    """Aggiorna i dati nella memoria dell'app per vedere le modifiche grafiche in tempo reale"""
    st.session_state.iscritti = df_aggiornato