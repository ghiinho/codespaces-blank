import streamlit as st
from src.utils.config_manager import carica_configurazione, salva_configurazione

def mostra_impostazioni():
    st.title("⚙️ Pannello di Controllo & Moduli")
    st.write("Personalizza la tua dashboard gestendo le impostazioni generali, i moduli e i gruppi.")
    st.markdown("---")

    # Carica la configurazione corrente
    config = carica_configurazione()

    # Creazione delle schede (Tab) per dividere i contenuti
    tab_generali, tab_moduli, tab_gruppi = st.tabs([
        "🏫 Generali", 
        "🔌 Moduli Attivi", 
        "👥 Gruppi Camp"
    ])

    # =====================================================================
    # TAB 1: IMPOSTAZIONI GENERALI
    # =====================================================================
    with tab_generali:
        st.subheader("🏫 Impostazioni Generali")
        nuovo_nome = st.text_input(
            "Nome del Campus / Associazione:", 
            value=config.get("general", {}).get("nome_campus", "Campus Estivo")
        )
        
        st.markdown("---")
        if st.button("💾 Salva Nome Campus", type="primary", key="btn_salva_generali"):
            if "general" not in config:
                config["general"] = {}
            config["general"]["nome_campus"] = nuovo_nome
            
            if salva_configurazione(config):
                st.session_state.config = config
                st.success("🎉 Nome del Campus aggiornato con successo!")
                st.rerun()
            else:
                st.error("❌ Si è verificato un errore durante il salvataggio.")

    # =====================================================================
    # TAB 2: ATTIVAZIONE MODULI
    # =====================================================================
    with tab_moduli:
        st.subheader("🔌 Gestione Moduli Attivi")
        st.info("I moduli disattivati verranno nascosti sia dalla Home Page a riquadri che dalla barra laterale di navigazione.")

        nuovi_moduli = {}
        
        for chiave_modulo, info in config.get("moduli", {}).items():
            col_info, col_toggle = st.columns([3, 1])
            with col_info:
                st.markdown(f"**{info['nome']}**")
                st.caption(info['descrizione'])
            with col_toggle:
                st.write("") # Spazio per allineare il toggle
                stato_attivo = st.toggle(
                    "Attivo", 
                    value=info['attivo'], 
                    key=f"toggle_{chiave_modulo}",
                    label_visibility="collapsed"
                )
            
            nuovi_moduli[chiave_modulo] = {
                "nome": info["nome"],
                "attivo": stato_attivo,
                "descrizione": info["descrizione"]
            }
            st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

        st.markdown("---")
        if st.button("💾 Salva Stato Moduli", type="primary", use_container_width=True, key="btn_salva_moduli"):
            config["moduli"] = nuovi_moduli
            
            if salva_configurazione(config):
                st.session_state.config = config
                st.success("🎉 Configurazione moduli salvata con successo!")
                st.rerun()
            else:
                st.error("❌ Si è verificato un errore durante il salvataggio.")

    # =====================================================================
    # TAB 3: GESTIONE GRUPPI CAMP
    # =====================================================================
    with tab_gruppi:
        st.subheader("👥 Configurazione Gruppi del Camp")
        st.write("Crea i gruppi in cui dividere i bambini (es. *Piccoli, Medi, Grandi* oppure *Squadra Rossa, Squadra Blu*).")

        # Inizializzazione della lista dei gruppi
        if "gruppi_camp" not in config:
            config["gruppi_camp"] = ["Nessun Gruppo"]

        st.session_state.lista_gruppi = config["gruppi_camp"]

        col_nuovo, col_lista = st.columns([2, 2])

        # --- Aggiunta Nuovo Gruppo ---
        with col_nuovo:
            with st.form(key="form_aggiungi_gruppo", clear_on_submit=True):
                nuovo_gruppo = st.text_input("✍️ Nome nuovo gruppo:", placeholder="Es. Lupi, Grandi...").strip()
                premuto_aggiungi = st.form_submit_button("➕ Aggiungi Gruppo", use_container_width=True)
                
            if premuto_aggiungi:
                if nuovo_gruppo:
                    config = carica_configurazione()
                    if "gruppi_camp" not in config:
                        config["gruppi_camp"] = ["Nessun Gruppo"]
                        
                    if nuovo_gruppo not in config["gruppi_camp"]:
                        config["gruppi_camp"].append(nuovo_gruppo)
                        st.session_state.lista_gruppi = config["gruppi_camp"]
                        
                        salva_configurazione(config)
                        st.success(f"🎉 Gruppo '{nuovo_gruppo}' aggiunto con successo!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Questo gruppo esiste già nella lista!")
                else:
                    st.error("❌ Digita un nome prima di cliccare aggiungi!")

        # --- Elenco ed Eliminazione Gruppi ---
        with col_lista:
            st.markdown("**Gruppi Attuali:**")
            
            # Filtriamo "Nessun Gruppo" per il conteggio
            gruppi_effettivi = [g for g in st.session_state.lista_gruppi if g != "Nessun Gruppo"]
            
            if not gruppi_effettivi:
                st.info("Nessun gruppo personalizzato creato.")
            else:
                for grp in st.session_state.lista_gruppi:
                    if grp == "Nessun Gruppo": 
                        continue
                    
                    c_nome, c_canc = st.columns([3, 1])
                    c_nome.write(f"• **{grp}**")
                    
                    if c_canc.button("🗑️", key=f"del_{grp}"):
                        st.session_state.lista_gruppi.remove(grp)
                        config["gruppi_camp"] = st.session_state.lista_gruppi
                        
                        # Salvataggio immediato sul file JSON anche durante la cancellazione
                        salva_configurazione(config)
                        st.success(f"Gruppo '{grp}' eliminato!")
                        st.rerun()