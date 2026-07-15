import streamlit as st
from src.utils.config_manager import carica_configurazione

def disegna_sidebar():
    config = carica_configurazione()
    
    st.sidebar.title(config["general"].get("nome_campus", "Campus Estivo"))
    
    # Costruisci le pagine disponibili dinamicamente
    pagine_disponibili = ["Home Page"]
    
    if config["moduli"]["anagrafiche"]["attivo"]:
        pagine_disponibili.append("Anagrafiche Iscritti")
    if config["moduli"]["presenze"]["attivo"]:
        pagine_disponibili.append("Registro Presenze")
    if config["moduli"]["pagamenti"]["attivo"]:
        pagine_disponibili.append("Gestione Pagamenti")
    if config["moduli"]["statistiche"]["attivo"]:
        pagine_disponibili.append("Statistiche")
        
    pagine_disponibili.append("Impostazioni")
    
    # Selettore della pagina corrente
    scelta = st.sidebar.radio("Navigazione", pagine_disponibili)
    return scelta