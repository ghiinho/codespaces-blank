import streamlit as st
from src.utils.config_manager import carica_configurazione

def mostra_home():
    config = carica_configurazione()
    nome_campus = config["general"].get("nome_campus", "Campus Estivo")
    
    st.title(f"☀️ {nome_campus}")
    st.write("Benvenuto nel pannello di controllo. Seleziona una funzionalità qui sotto o usa la barra laterale.")
    st.markdown("---")

    # Estraiamo solo i moduli attivi
    moduli_attivi = {k: v for k, v in config["moduli"].items() if v["attivo"]}

    if not moduli_attivi:
        st.warning("⚠️ Tutti i moduli sono disattivati. Vai nelle Impostazioni (nella sidebar) per attivare le funzioni del gestionale.")
        return

    # Trasformiamo i moduli attivi in una lista per poterli disporre in griglia
    lista_moduli = list(moduli_attivi.items())
    
    # Creiamo una griglia a 2 colonne dinamica
    for i in range(0, len(lista_moduli), 2):
        colonne = st.columns(2)
        
        # Primo elemento della riga
        chiave_1, info_1 = lista_moduli[i]
        with colonne[0]:
            st.markdown(
                f"""
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; min-height: 160px; margin-bottom: 10px;">
                    <h3 style="margin-top: 0; color: #0f172a; font-size: 18px;">{info_1['nome']}</h3>
                    <p style="color: #64748b; font-size: 14px;">{info_1['descrizione']}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            # Mappa il bottone per reindirizzare alla pagina corretta
            mappa_pagine = {
                "anagrafiche": "Anagrafiche Iscritti",
                "presenze": "Registro Presenze",
                "pagamenti": "Gestione Pagamenti",
                "statistiche": "Statistiche"
            }
            if st.button(f"Apri {info_1['nome'].split()[-1]} ➡️", use_container_width=True, key=f"home_btn_{chiave_1}"):
                st.session_state.pagina_corrente = mappa_pagine.get(chiave_1, "Home Page")
                st.rerun()

        # Secondo elemento della riga (se esiste)
        if i + 1 < len(lista_moduli):
            chiave_2, info_2 = lista_moduli[i+1]
            with colonne[1]:
                st.markdown(
                    f"""
                    <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; min-height: 160px; margin-bottom: 10px;">
                        <h3 style="margin-top: 0; color: #0f172a; font-size: 18px;">{info_2['nome']}</h3>
                        <p style="color: #64748b; font-size: 14px;">{info_2['descrizione']}</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                if st.button(f"Apri {info_2['nome'].split()[-1]} ➡️", use_container_width=True, key=f"home_btn_{chiave_2}"):
                    st.session_state.pagina_corrente = mappa_pagine.get(chiave_2, "Home Page")
                    st.rerun()