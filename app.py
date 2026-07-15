import streamlit as st
import pandas as pd
import database_utils as db_utils

# Configurazione della pagina
st.set_page_config(page_title="Gestionale Centro Estivo", layout="wide")

# Inizializza i dati dal tuo Excel
db_utils.inizializza_database_in_memoria()
df_iscritti = db_utils.ottieni_iscritti()

# Gestione della navigazione (se non esiste, parte dalla Home)
if "pagina_corrente" not in st.session_state:
    st.session_state.pagina_corrente = "Home"

# Funzione rapida per cambiare pagina
def naviga_a(nome_pagina):
    st.session_state.pagina_corrente = nome_pagina
    st.rerun()

# ==========================================
# SIDEBAR: NAVIGAZIONE A PULSANTI
# ==========================================
st.sidebar.title("Navigation")
st.sidebar.write("Seleziona la sezione desiderata:")

# Inizializziamo la pagina corrente se non esiste nello stato
if "pagina_corrente" not in st.session_state:
    st.session_state.pagina_corrente = "Home Page"

# --- PULSANTE 1: TORNA ALLA HOME PAGE ---
if st.sidebar.button("🏠 Torna alla Home Page", use_container_width=True):
    st.session_state.pagina_corrente = "Home Page"
    st.rerun()

# --- PULSANTE 2: VAI ALLE ANAGRAFICHE ---
# Quando viene cliccato, oltre a cambiare pagina, azzera attivamente la ricerca
if st.sidebar.button("👤 Vai alle anagrafiche", use_container_width=True):
    # RESET STATO RICERCA ANAGRAFICA
    st.session_state.id_bambino_corrente = None
    st.session_state.risultato_ricerca = None
    st.session_state.scheda_attiva = "bambino"
    
    # Questo svuota fisicamente il testo digitato nel campo di ricerca!
    if "ricerca_cognome" in st.session_state:
        st.session_state.ricerca_cognome = ""
    
    st.session_state.pagina_corrente = "Anagrafiche Iscritti"
    st.rerun()

# --- PULSANTE 3: VAI AGLI ELENCHI SETTIMANALI ---
if st.sidebar.button("📅 Vai agli elenchi settimanali", use_container_width=True):
    st.session_state.pagina_corrente = "Elenchi Settimanali"
    st.rerun()

# --- PULSANTE 4: VAI AI PAGAMENTI ---
if st.sidebar.button("💳 Vai ai pagamenti", use_container_width=True):
    st.session_state.pagina_corrente = "Gestione Pagamenti"
    st.rerun()

# ==========================================
# 1. PAGINA PRINCIPALE: HOME PAGE A RIQUADRI
# ==========================================
if st.session_state.pagina_corrente == "Home Page":
    st.title("Gestionale Centro Estivo")
    st.write("Benvenuto nel gestionale. Clicca su uno dei riquadri qui sotto per accedere alle funzioni specifiche:")
    st.markdown("---")

    # Creiamo una griglia di riquadri (3 colonne)
    ric1, ric2, ric3 = st.columns(3)

    with ric1:
        st.markdown(
            """
            <div style="background-color: #e0f2fe; padding: 20px; border-radius: 10px; border-left: 5px solid #0284c7; min-height: 140px;">
                <h3 style="color: #0369a1; margin-top: 0;">👤 Anagrafiche Iscritti</h3>
                <p style="color: #0c4a6e; font-size: 14px;">Visualizza le schede personali di ogni bambino, modifica dati personali e settimane iscritte.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button("Apri Anagrafiche →", key="btn_anagrafica", use_container_width=True):
            naviga_a("Anagrafiche Iscritti")

    with ric2:
        st.markdown(
            """
            <div style="background-color: #fef3c7; padding: 20px; border-radius: 10px; border-left: 5px solid #d97706; min-height: 140px;">
                <h3 style="color: #b45309; margin-top: 0;">📅 Elenchi Settimanali</h3>
                <p style="color: #78350f; font-size: 14px;">Controlla chi è presente nella Settimana 1, 2, 3... Genera i registri di presenza e i totali per la mensa.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button("Apri Elenchi →", key="btn_elenchi", use_container_width=True):
            naviga_a("Elenchi Settimanali")

    with ric3:
        st.markdown(
            """
            <div style="background-color: #dcfce7; padding: 20px; border-radius: 10px; border-left: 5px solid #22c55e; min-height: 140px;">
                <h3 style="color: #15803d; margin-top: 0;">💰 Gestione Pagamenti</h3>
                <p style="color: #14532d; font-size: 14px;">Vedi la situazione economica complessiva, le quote da riscuotere, i saldi e gli acconti ricevuti.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button("Apri Pagamenti →", key="btn_pagamenti", use_container_width=True):
            naviga_a("Gestione Pagamenti")


import streamlit as st
import database_utils as db_utils  # Le tue utility esistenti

# IMPORTIAMO I NUOVI MODULI CHE ABBIAMO CREATO
from src.sidebar import disegna_sidebar
from src.views.home import mostra_home
from src.views.anagrafiche import mostra_anagrafiche

# 1. Configurazione della pagina Streamlit
st.set_page_config(page_title="Gestionale Camp", layout="wide")

# 2. Inizializzazione e caricamento dati (usando il tuo metodo originale!)
db_utils.inizializza_database_in_memoria()
df_iscritti = db_utils.ottieni_iscritti()

# 3. Disegniamo la barra laterale di navigazione
disegna_sidebar()

# 4. Mostriamo la schermata corretta in base alla pagina selezionata
if st.session_state.pagina_corrente == "Home Page":
    mostra_home()

elif st.session_state.pagina_corrente == "Anagrafiche Iscritti":
    # Passiamo df_iscritti alla vista in modo che possa lavorarci direttamente
    mostra_anagrafiche(df_iscritti)

elif st.session_state.pagina_corrente == "Elenchi Settimanali":
    st.title("📅 Elenchi Settimanali")
    st.info("Questa sezione sarà implementata nei prossimi passaggi...")


# ==========================================
# 3. SEZIONE: ELENCHI SETTIMANALI (Futura)
# ==========================================
elif st.session_state.pagina_corrente == "Elenchi Settimanali":
    st.title("📅 Elenchi Settimanali")
    st.info("🚧 Questa sezione è in fase di sviluppo. Qui potrai visualizzare e gestire le presenze e i gruppi settimana per settimana.")


# ==========================================
# 4. SEZIONE: GESTIONE PAGAMENTI (Futura)
# ==========================================
elif st.session_state.pagina_corrente == "Gestione Pagamenti":
    st.title("💳 Gestione Pagamenti")
    st.info("🚧 Questa sezione è in fase di sviluppo. Qui potrai monitorare le quote di iscrizione, i saldi e registrare i pagamenti ricevuti.")