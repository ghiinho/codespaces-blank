import streamlit as st
import pandas as pd
import database_utils as db_utils

# IMPORTIAMO I NUOVI MODULI
from src.sidebar import disegna_sidebar
from src.views.home import mostra_home
from src.views.anagrafiche import mostra_anagrafiche
from src.utils.config_manager import carica_configurazione
from src.views.impostazioni import mostra_impostazioni
from src.views.elenchi import mostra_elenchi_settimanali
from src.views.pagamenti import mostra_pagamenti

# 1. Configurazione della pagina Streamlit (DEVE ESSERE LA PRIMA ISTRUZIONE STREAMLIT)
st.set_page_config(page_title="Gestionale Camp", layout="wide")

# 2. Inizializzazione Database / Caricamento Dati
if "df_iscritti" not in st.session_state:
    db_utils.inizializza_database_in_memoria()
    df_caricato = db_utils.ottieni_iscritti()
    
    if df_caricato is None or df_caricato.empty:
        df_caricato = pd.read_excel("iscrizioni.xlsx")
        
    st.session_state.df_iscritti = df_caricato.astype(object)

df_iscritti = st.session_state.df_iscritti

# --- INIZIALIZZAZIONE STATO PAGINE E GRUPPI ---
if "pagina_corrente" not in st.session_state:
    st.session_state.pagina_corrente = "Home Page"

if "lista_gruppi" not in st.session_state:
    st.session_state.lista_gruppi = ["Nessun Gruppo"]

# 3. Disegniamo la barra laterale di navigazione
disegna_sidebar()

# 💡 Gestione Svuotamento Ricerca fuori dalle Anagrafiche
# (Azzeriamo le ricerche solo se non c'è un id_bambino_corrente impostato da un reindirizzamento esterno)
if st.session_state.pagina_corrente != "Anagrafiche Iscritti":
    st.session_state.risultato_ricerca = None
    if "ricerca_cognome" in st.session_state and not st.session_state.get("id_bambino_corrente"):
        st.session_state["ricerca_cognome"] = ""

# Rileviamo cambi di pagina
pagina_precedente = st.session_state.get("pagina_precedente")
if st.session_state.pagina_corrente == "Anagrafiche Iscritti" and pagina_precedente != "Anagrafiche Iscritti":
    # Se proveniamo da un'altra pagina e NON c'è già una scheda specifica richiesta (es. "settimane"):
    if "scheda_attiva" not in st.session_state or not st.session_state.scheda_attiva:
        st.session_state.scheda_attiva = "bambino"
    st.session_state.modalita_modifica = False

st.session_state.pagina_precedente = st.session_state.pagina_corrente

# --- ROUTING PAGINE ---
if st.session_state.pagina_corrente == "Home Page":
    mostra_home()

elif st.session_state.pagina_corrente == "Anagrafiche Iscritti":
    mostra_anagrafiche(st.session_state.df_iscritti)

elif st.session_state.pagina_corrente == "Registro Presenze":
    config = carica_configurazione()
    st.session_state.lista_gruppi = config.get("gruppi_camp", ["Nessun Gruppo"])  
    mapping = config.get("mappatura_colonne", {})
    prefisso = str(config.get("prefisso_settimane", "PERIODI DISPONIBILI")).strip()
    
    col_cognome = mapping.get("cognome", "COGNOME MINORE")
    col_nome = mapping.get("nome", "NOME MINORE")
    col_allergie = mapping.get("allergie", "ALLERGIE O INTOLLERANZE?")
    col_quali = mapping.get("note_allergie", "SE SI, INDICA QUALI")
    col_g_tel = mapping.get("recapito", "TELEFONO GENITORE")

    mostra_elenchi_settimanali(
        df_iscritti=st.session_state.df_iscritti,
        col_cognome=str(col_cognome).strip(),
        col_nome=str(col_nome).strip(),
        col_allergie=str(col_allergie).strip(),
        col_quali=str(col_quali).strip(),
        col_g_tel=str(col_g_tel).strip(),
        prefisso_settimane=prefisso
    )

elif st.session_state.pagina_corrente == "Impostazioni":
    mostra_impostazioni()
    
elif st.session_state.pagina_corrente == "Gestione Pagamenti":
    mostra_pagamenti(st.session_state.df_iscritti)