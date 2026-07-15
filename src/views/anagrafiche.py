import streamlit as st
import pandas as pd

def inizializza_stato():
    if "id_selezionato" not in st.session_state:
        st.session_state.id_selezionato = None
    if "scheda_attiva" not in st.session_state:
        st.session_state.scheda_attiva = "bambino"

def barra_ricerca(df):
    # Ordiniamo il dataframe per Cognome, poi Nome
    df_ordinato = df.sort_values(by=["Cognome", "Nome"])
    
    # Creiamo una lista leggibile: "COGNOME Nome (Codice Fiscale)"
    lista_opzioni = (
        df_ordinato["Cognome"].astype(str).str.upper() + " " + 
        df_ordinato["Nome"].astype(str).str.title() + " (" + 
        df_ordinato["Codice Fiscale"].astype(str).str.upper() + ")"
    ).tolist()
    
    # Mappiamo la stringa visualizzata all'indice originale del dataframe
    mappa = dict(zip(lista_opzioni, df_ordinato.index))
    
    # Determiniamo l'indice di default per la selectbox
    indice_default = None
    if st.session_state.id_selezionato is not None:
        # Troviamo la posizione dell'id corrente nella lista ordinata
        valore_corrente = lista_opzioni[list(mappa.values()).index(st.session_state.id_selezionato)]
        indice_default = lista_opzioni.index(valore_corrente)

    # Widget di ricerca
    scelta = st.selectbox(
        "Cerca un iscritto:",
        options=lista_opzioni,
        index=indice_default,
        placeholder="Digita il cognome...",
        key="input_ricerca"
    )
    
    # Logica di aggiornamento sicura
    if scelta:
        nuovo_id = mappa[scelta]
        if nuovo_id != st.session_state.id_selezionato:
            st.session_state.id_selezionato = nuovo_id
            st.session_state.scheda_attiva = "bambino" # Reset tab ad ogni nuova ricerca
            st.rerun()