import streamlit as st
from src.utils.config_manager import carica_configurazione 

def disegna_sidebar():
    config = carica_configurazione()
    
    # Titolo del Campus nella Sidebar
    st.sidebar.title(config["general"].get("nome_campus", "Campus Estivo"))
    st.sidebar.markdown("---")
    
    # Generiamo la lista dinamica dei moduli attivi
    pagine_disponibili = [("🏠 Home Page", "Home Page")]
    
    if config["moduli"]["anagrafiche"]["attivo"]:
        pagine_disponibili.append(("👤 Anagrafiche", "Anagrafiche Iscritti"))
    if config["moduli"]["presenze"]["attivo"]:
        pagine_disponibili.append(("📝 Presenze", "Registro Presenze"))
    if config["moduli"]["pagamenti"]["attivo"]:
        pagine_disponibili.append(("💰 Pagamenti", "Gestione Pagamenti"))
    if config["moduli"]["statistiche"]["attivo"]:
        pagine_disponibili.append(("📊 Statistiche", "Statistiche"))
        
    pagine_disponibili.append(("⚙️ Impostazioni", "Impostazioni"))
    
    st.sidebar.write("**Menu di Navigazione**")
    
    # Creiamo un bottone per ciascuna pagina disponibile
    for etichetta, nome_pagina in pagine_disponibili:
        # Controlliamo se la pagina del bottone è quella attualmente attiva per darle risalto visivo
        e_attiva = st.session_state.pagina_corrente == nome_pagina
        tipo_bottone = "primary" if e_attiva else "secondary"
        
        if st.sidebar.button(
            etichetta, 
            key=f"nav_btn_{nome_pagina}", 
            use_container_width=True, 
            type=tipo_bottone
        ):

            # --- RESET DELLE RICERCHE E FILTRI ---
            if "ricerca_iscritti" in st.session_state:
                st.session_state["ricerca_iscritti"] = ""
            
            if "settimana_selezionata" in st.session_state:
                del st.session_state["settimana_selezionata"]
                
            st.session_state.pagina_corrente = nome_pagina
            st.rerun()