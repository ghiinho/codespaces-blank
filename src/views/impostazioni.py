import streamlit as st
from src.utils.config_manager import carica_configurazione, salva_configurazione

def mostra_impostazioni():
    st.title("⚙️ Pannello di Controllo")
    st.write("Personalizza la tua dashboard gestendo impostazioni, moduli attivi, gruppi e listino prezzi.")
    st.markdown("---")

    # Carica la configurazione corrente
    config = carica_configurazione()

    # Creazione delle schede (Tab) per dividere i contenuti
    tab_generali, tab_moduli, tab_gruppi, tab_tariffe = st.tabs([
        "🏫 Generali", 
        "🔌 Moduli Attivi", 
        "👥 Gruppi Camp",
        "💰 Tariffe & Sconti"
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
                st.write("") 
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

        if "gruppi_camp" not in config:
            config["gruppi_camp"] = ["Nessun Gruppo"]

        st.session_state.lista_gruppi = config["gruppi_camp"]

        col_nuovo, col_lista = st.columns([2, 2])

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

        with col_lista:
            st.markdown("**Gruppi Attuali:**")
            
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
                        
                        salva_configurazione(config)
                        st.success(f"Gruppo '{grp}' eliminato!")
                        st.rerun()

    # =====================================================================
    # TAB 4: LISTINO TARIFFE, SCONTI E PACCHETTI (PULITO / SENZA DEFAULT)
    # =====================================================================
    with tab_tariffe:
        st.subheader("💰 Gestione Listino Prezzi & Sconti")
        st.write("Configura i costi per tipologia di frequenza, attiva sconti automatici o regola i pacchetti.")

        # Inizializziamo le strutture vuote (senza dati di default)
        if "tariffe" not in config:
            config["tariffe"] = {}
            salva_configurazione(config)
            
        if "sconti" not in config:
            config["sconti"] = []
            salva_configurazione(config)
            
        if "pacchetti" not in config:
            config["pacchetti"] = []
            salva_configurazione(config)

        # --- SEZIONE 4.1: TIPOLOGIE DI FREQUENZA (OPZIONI MODULO GOOGLE) ---
        st.markdown("### 📋 1. Tipologie di Frequenza & Prezzo Settimanale")
        st.caption("Queste diciture devono corrispondere a quelle usate nelle opzioni del tuo Modulo Google.")

        col_t1, col_t2 = st.columns([2, 2])

        with col_t1:
            with st.form(key="form_nuova_tariffa", clear_on_submit=True):
                nome_freq = st.text_input("✍️ Nome Opzione (come da Modulo Google):", placeholder="Es. Tempo Pieno (Con Pranzo)").strip()
                prezzo_freq = st.number_input("💶 Costo Settimanale (€):", min_value=0.0)
                btn_add_tariffa = st.form_submit_button("➕ Aggiungi / Aggiorna Frequenza", use_container_width=True)

            if btn_add_tariffa:
                if nome_freq:
                    config["tariffe"][nome_freq] = prezzo_freq
                    salva_configurazione(config)
                    st.success(f"Tariffa per '{nome_freq}' salvata ({prezzo_freq}€)!")
                    st.rerun()
                else:
                    st.error("❌ Inserisci il nome dell'opzione!")

        with col_t2:
            st.markdown("**Listino Prezzi Corrente:**")
            if not config["tariffe"]:
                st.info("Nessuna tariffa impostata.")
            else:
                for tf, prz in list(config["tariffe"].items()):
                    c_tf_nome, c_tf_prezzo, c_tf_del = st.columns([3, 2, 1])
                    c_tf_nome.write(f"• **{tf}**")
                    c_tf_prezzo.write(f"**{prz:.2f} €** / sett")
                    if c_tf_del.button("🗑️", key=f"del_tf_{tf}"):
                        del config["tariffe"][tf]
                        salva_configurazione(config)
                        st.rerun()

        st.markdown("---")

        # --- SEZIONE 4.2: GESTIONE SCONTI ---
        st.markdown("### 🏷️ 2. Sconti & Riduzioni")
        st.caption("Crea regole di sconto applicabili ai conteggi (es. Sconto Fratello, Iscrizione Anticipata).")

        # Recuperiamo la lista delle tariffe disponibili per la selectbox
        opzioni_frequenze_sconto = ["Tutte (Generico)"] + list(config.get("tariffe", {}).keys())

        col_sc1, col_sc2 = st.columns([2, 2])

        with col_sc1:
            with st.form(key="form_nuovo_sconto", clear_on_submit=True):
                nome_sconto = st.text_input("✍️ Nome Sconto:", placeholder="Es. Sconto Fratello").strip()
                
                # 🎯 NUOVO CAMPO: Selezione della Frequenza Target
                freq_target_sconto = st.selectbox(
                    "Frequenza / Tariffa Applicabile:",
                    options=opzioni_frequenze_sconto,
                    help="Seleziona 'Tutte' per applicare lo sconto sul totale oppure una frequenza specifica."
                )

                tipo_sconto = st.selectbox("Tipo Sconto:", ["Fisso (€)", "Percentuale (%)"])
                valore_sconto = st.number_input("Valore Sconto:", min_value=0.0, step=1.0)
                btn_add_sconto = st.form_submit_button("➕ Aggiungi Sconto", use_container_width=True)

            if btn_add_sconto:
                if nome_sconto:
                    nuovo_sc = {
                        "nome": nome_sconto,
                        "frequenza_target": "generica" if freq_target_sconto == "Tutte (Generico)" else freq_target_sconto,
                        "tipo": "percentuale" if "Percentuale" in tipo_sconto else "fisso",
                        "valore": valore_sconto
                    }
                    
                    if "sconti" not in config:
                        config["sconti"] = []
                        
                    config["sconti"].append(nuovo_sc)
                    salva_configurazione(config)
                    st.success(f"Sconto '{nome_sconto}' aggiunto con successo!")
                    st.rerun()
                else:
                    st.error("❌ Inserisci il nome dello sconto!")

        with col_sc2:
            st.markdown("**Sconti Attivi:**")
            sconti_salvati = config.get("sconti", [])
            
            if not sconti_salvati:
                st.info("Nessun sconto salvato.")
            else:
                for idx_sc, sc in enumerate(sconti_salvati):
                    c_sc_nome, c_sc_val, c_sc_del = st.columns([3, 2, 1])
                    
                    # Formattazione target frequenza
                    target_display = sc.get("frequenza_target", "generica")
                    target_label = "Tutte" if target_display == "generica" else target_display

                    c_sc_nome.write(f"• **{sc['nome']}**\n  *(Applica a: {target_label})*")
                    
                    unita = "%" if sc.get("tipo") == "percentuale" else "€"
                    c_sc_val.write(f"**-{sc['valore']} {unita}**")
                    
                    if c_sc_del.button("🗑️", key=f"del_sc_{idx_sc}"):
                        config["sconti"].pop(idx_sc)
                        salva_configurazione(config)
                        st.rerun()

        st.markdown("---")

        # --- SEZIONE 4.3: PACCHETTI MULTI-SETTIMANA ---
        st.markdown("### 📦 3. Pacchetti Promozionali (Multi-Settimana)")
        st.caption("Configura gli sconti progressivi in base al numero di settimane prenotate.")
    
        # 1. Recuperiamo le frequenze disponibili e la lista dei pacchetti dal config
        # Se non esistono ancora nel config, usiamo liste vuote
        tariffe = config.get("tariffe", {})  # es. {"GIORNATA INTERA": 135, ...}
        pacchetti = config.get("pacchetti_promozionali", [])   # lista dei pacchetti salvati
        
        opzioni_frequenza = [f for f in tariffe.keys() if f != "NON ISCRITTO ❌"]

        if not opzioni_frequenza:
            st.warning("⚠️ Imposta prima le tariffe singole per ciascuna frequenza per poter creare i pacchetti.")
            return

        # --- FORM CREAZIONE DINAMICA PACCHETTO ---
        st.write("#### Aggiungi Nuovo Pacchetto")
        with st.form("form_nuovo_pacchetto", clear_on_submit=True):
            col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
            
            with col1:
                nome_p = st.text_input("Nome Pacchetto", placeholder="es. Promo 4 Settimane Full")
            
            with col2:
                # Scegli a quale frequenza attiva applicare il pacchetto
                freq_target = st.selectbox("Si applica a:", options=opzioni_frequenza)
                
            with col3:
                num_sett = st.number_input("N° Settimane", min_value=2, max_value=12, value=4, step=1)
                
            with col4:
                prezzo_p = st.number_input("Prezzo Totale (€)", min_value=0.0, value=0.0, step=10.0)

            submit_p = st.form_submit_button("➕ Salva Pacchetto", type="primary", use_container_width=True)

            if submit_p:
                if nome_p.strip():
                    nuovo_pacchetto = {
                        "id": f"pck_{len(pacchetti) + 1}",
                        "nome": nome_p.strip(),
                        "frequenza_target": freq_target,
                        "num_settimane": int(num_sett),
                        "prezzo_pacchetto": float(prezzo_p)
                    }
                    pacchetti.append(nuovo_pacchetto)
                    config["pacchetti_promozionali"] = pacchetti
                    salva_configurazione(config)
                    st.success(f"✅ Pacchetto '{nome_p}' salvato con successo!")
                    st.rerun()
                else:
                    st.error("Inserisci un nome per il pacchetto.")

        # --- TABELLA / LISTA PACCHETTI ESISTENTI CON POSSIBILITÀ DI ELIMINARE ---
        if pacchetti:
            st.markdown("---")
            st.write("#### Pacchetti Attivi")
            
            idx_da_eliminare = None
            for i, p in enumerate(pacchetti):
                col_info, col_del = st.columns([5, 1])
                with col_info:
                    st.info(
                        f"**{p['nome']}** — Valido per **{p['num_settimane']} settimane** di tipo "
                        f"`{p['frequenza_target']}` a **{p['prezzo_pacchetto']:.2f} €**"
                    )
                with col_del:
                    if st.button("🗑️", key=f"del_pck_{i}"):
                        idx_da_eliminare = i

            if idx_da_eliminare is not None:
                pacchetti.pop(idx_da_eliminare)
                config["pacchetti_promozionali"] = pacchetti
                salva_configurazione(config)
                st.success("Pacchetto rimosso!")
                st.rerun()