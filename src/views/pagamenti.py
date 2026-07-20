import streamlit as st
import pandas as pd
from datetime import datetime, date
from src.utils.config_manager import carica_configurazione, salva_configurazione

def mostra_pagamenti(df_iscritti):
    st.title("💳 Gestione Pagamenti & Incassi")
    st.caption("Cerca un iscritto per visualizzare la sua scheda, registrare un versamento o consultare lo storico transazioni.")
    st.markdown("---")

    config = carica_configurazione()
    
    # 💡 Lettura dinamica di tariffe e pacchetti dal config
    tariffe = config.get("tariffe", {})
    pacchetti = config.get("pacchetti", [])

    if not tariffe:
        st.warning("⚠️ Non hai ancora configurato le tariffe nel pannello Impostazioni!")

    # --- 1. MAPPATURA COLONNE E PREPARAZIONE DATI ---
    mapping = config.get("mappatura_colonne", {})
    colonne_reali = list(df_iscritti.columns)

    col_cognome = mapping.get("cognome", "COGNOME MINORE")
    col_nome = mapping.get("nome", "NOME MINORE")
    
    prefisso = str(config.get("prefisso_settimane", "PERIODI DISPONIBILI")).strip().lower()
    colonne_settimane = [
        col for col in colonne_reali 
        if "settiman" in str(col).lower() or prefisso in str(col).lower()
    ]

    if "registro_pagamenti" not in st.session_state:
        st.session_state.registro_pagamenti = config.get("registro_pagamenti", {})

    elenco_iscritti_dettaglio = {}
    dati_contabili_lista = []

    for idx, row in df_iscritti.iterrows():
        cognome = str(row.get(col_cognome, "")).strip().upper()
        nome = str(row.get(col_nome, "")).strip().title()
        
        if not cognome or not nome or cognome == "NAN":
            continue

        chiave = f"{cognome}_{nome}".upper()
        etichetta_ricerca = f"{cognome} {nome}"

        dati_salvati = st.session_state.registro_pagamenti.get(chiave, {})
        transazioni = dati_salvati.get("transazioni", [])

        totale_incassato = sum(float(t.get("importo", 0.0)) for t in transazioni)

        import streamlit as st
import pandas as pd
from datetime import datetime, date
from src.utils.config_manager import carica_configurazione, salva_configurazione

def mostra_pagamenti(df_iscritti):
    st.title("💳 Gestione Pagamenti & Incassi")
    st.caption("Cerca un iscritto per visualizzare la sua scheda, registrare un versamento o consultare lo storico transazioni.")
    st.markdown("---")

    config = carica_configurazione()
    
    # 💡 Lettura dinamica di tariffe e pacchetti dal config
    tariffe = config.get("tariffe", {})
    pacchetti = config.get("pacchetti", [])

    if not tariffe:
        st.warning("⚠️ Non hai ancora configurato le tariffe nel pannello Impostazioni!")

    # --- 1. MAPPATURA COLONNE E PREPARAZIONE DATI ---
    mapping = config.get("mappatura_colonne", {})
    colonne_reali = list(df_iscritti.columns)

    col_cognome = mapping.get("cognome", "COGNOME MINORE")
    col_nome = mapping.get("nome", "NOME MINORE")
    
    prefisso = str(config.get("prefisso_settimane", "PERIODI DISPONIBILI")).strip().lower()
    colonne_settimane = [
        col for col in colonne_reali 
        if "settiman" in str(col).lower() or prefisso in str(col).lower()
    ]

    if "registro_pagamenti" not in st.session_state:
        st.session_state.registro_pagamenti = config.get("registro_pagamenti", {})

    elenco_iscritti_dettaglio = {}
    dati_contabili_lista = []

    for idx, row in df_iscritti.iterrows():
        cognome = str(row.get(col_cognome, "")).strip().upper()
        nome = str(row.get(col_nome, "")).strip().title()
        
        if not cognome or not nome or cognome == "NAN":
            continue

        chiave = f"{cognome}_{nome}".upper()
        etichetta_ricerca = f"{cognome} {nome}"

        dati_salvati = st.session_state.registro_pagamenti.get(chiave, {})
        transazioni = dati_salvati.get("transazioni", [])

        totale_incassato = sum(float(t.get("importo", 0.0)) for t in transazioni)

        # -------------------------------------------------------------
        # --- CALCOLO DINAMICO DELLE FREQUENZE E DEI PACCHETTI TARGET ---
        # -------------------------------------------------------------
        conteggio_frequenze = {}
        totale_lordo = 0.0
        num_settimane_tot = 0

        for col_s in colonne_settimane:
            valore_scelta = str(row.get(col_s, "")).strip()
            if valore_scelta and valore_scelta.lower() not in ["nan", "", "no", "non frequenta", "none"]:
                num_settimane_tot += 1
                
                tipo_trovato = "Generica"
                costo_sett = 0.0
                for opzione_tariffa, prezzo in tariffe.items():
                    if opzione_tariffa.lower() in valore_scelta.lower():
                        tipo_trovato = opzione_tariffa
                        costo_sett = float(prezzo)
                        break
                
                if costo_sett == 0.0 and tariffe:
                    tipo_trovato = list(tariffe.keys())[0]
                    costo_sett = float(list(tariffe.values())[0])

                conteggio_frequenze[tipo_trovato] = conteggio_frequenze.get(tipo_trovato, 0) + 1
                totale_lordo += costo_sett

        stringa_frequenze = ", ".join([f"{v}x {k}" for k, v in conteggio_frequenze.items()]) if conteggio_frequenze else "Nessuna"

        # --- APPLICAZIONE PACCHETTI PER SPECIFICA FREQUENZA ---
        totale_netto_calcolato = 0.0
        dettagli_pacchetti_applicati = []

        for freq_nome, quantita in conteggio_frequenze.items():
            prezzo_singolo_freq = float(tariffe.get(freq_nome, 0.0))
            
            # Filtriamo i pacchetti creati per QUESTA specifica frequenza
            # Supporta sia la chiave 'frequenza_target' sia 'frequenza'
            pacchetti_freq = [
                pk for pk in pacchetti 
                if pk.get("frequenza_target", pk.get("frequenza")) == freq_nome
            ]
            
            # Ordiniamo i pacchetti per numero di settimane decrescente (es. 8, poi 4)
            pacchetti_ordinati = sorted(
                pacchetti_freq, 
                key=lambda x: x.get("num_settimane", x.get("min_settimane", 0)), 
                reverse=True
            )

            quantita_rimanente = quantita
            costo_parziale_freq = 0.0

            for pk in pacchetti_ordinati:
                num_s = pk.get("num_settimane", pk.get("min_settimane", 0))
                prezzo_pk = float(pk.get("prezzo_pacchetto", 0.0))

                if num_s > 0 and quantita_rimanente >= num_s:
                    num_volte = quantita_rimanente // num_s
                    costo_parziale_freq += num_volte * prezzo_pk
                    quantita_rimanente = quantita_rimanente % num_s
                    
                    nome_pck = pk.get("nome", f"Pacchetto {num_s} sett.")
                    dettagli_pacchetti_applicati.append(f"📦 {nome_pck} ({prezzo_pk:.2f} €)")

            # Le settimane che avanzano fuori dal pacchetto pagano la tariffa singola
            costo_parziale_freq += quantita_rimanente * prezzo_singolo_freq
            totale_netto_calcolato += costo_parziale_freq

        # Calcolo sconto totale ed etichetta per l'interfaccia
        sconto_applicato = max(0.0, totale_lordo - totale_netto_calcolato)

        if sconto_applicato > 0 and dettagli_pacchetti_applicati:
            descrizione_sconto = " + ".join(dettagli_pacchetti_applicati)
        else:
            descrizione_sconto = "Standard (Nessuno)"

        netto_da_pagare = max(0.0, totale_netto_calcolato)
        rimanente = netto_da_pagare - totale_incassato

        # Stato del Pagamento
        if netto_da_pagare == 0:
            stato = "🟢 Esente"
        elif rimanente <= 0:
            stato = "🟢 Saldato"
        elif totale_incassato > 0:
            stato = "🟡 Acconto Versato"
        else:
            stato = "🔴 Da Pagare"

        info_iscritto = {
            "chiave": chiave,
            "cognome": cognome,
            "nome": nome,
            "frequenze_str": stringa_frequenze,
            "num_settimane": num_settimane_tot,
            "totale_lordo": totale_lordo,
            "descrizione_sconto": descrizione_sconto,
            "sconto_applicato": sconto_applicato,
            "netto_da_pagare": netto_da_pagare,
            "totale_incassato": totale_incassato,
            "rimanente": rimanente,
            "stato": stato,
            "transazioni": transazioni
        }

        elenco_iscritti_dettaglio[etichetta_ricerca] = info_iscritto
        dati_contabili_lista.append(info_iscritto)

    if not elenco_iscritti_dettaglio:
        st.info("Nessun iscritto trovato nel database.")
        return

    # --- 2. SCHERMATA A TAB ---
    tab_scheda, tab_generale = st.tabs(["🔍 Scheda Singolo Iscritto", "📊 Panoramica Registro Completo"])

    # ==========================================
    # TAB 1: SCHEDA DETTAGLIO ISCRITTO
    # ==========================================
    with tab_scheda:
        st.subheader("🔍 Cerca e Gestisci Iscritto")
        
        opzioni_ricerca = sorted(list(elenco_iscritti_dettaglio.keys()))
        
        nome_selezionato = st.selectbox(
            "Digitare il cognome o nome dell'iscritto:",
            options=opzioni_ricerca,
            index=None,
            placeholder="Inizia a digitare il cognome o il nome...",
            help="Seleziona un iscritto per aprire la sua scheda contabile e gestire i pagamenti."
        )

        if not nome_selezionato:
            st.info("💡 Inizia a digitare il nome dell'iscritto nella barra di ricerca in alto per caricare la scheda dettagliata.")
        else:
            iscritto = elenco_iscritti_dettaglio[nome_selezionato]
            chiave_iscritto = iscritto["chiave"]

            st.markdown("---")
            
            # Intestazione Scheda
            col_head1, col_head2 = st.columns([3, 1])
            with col_head1:
                st.markdown(f"## 👤 {iscritto['cognome']} {iscritto['nome']}")
                st.write(f"🗓️ **Frequenze ({iscritto['num_settimane']} sett.):** {iscritto['frequenze_str']}")
                st.write(f"🏷️ **Tariffa/Promo Applicata:** {iscritto['descrizione_sconto']}")
            with col_head2:
                st.markdown(f"### Status:\n### {iscritto['stato']}")

            st.markdown("<br>", unsafe_allow_html=True)

            # Card metriche
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Lordo Listino", f"{iscritto['totale_lordo']:.2f} €")
            c2.metric("Sconto Promo", f"{iscritto['sconto_applicato']:.2f} €")
            c3.metric("Netto Dovuto", f"{iscritto['netto_da_pagare']:.2f} €")
            c4.metric("Rimanente da Pagare", f"{iscritto['rimanente']:.2f} €", delta_color="inverse")

            st.markdown("---")

            # REGISTRA NUOVA TRANSAZIONE
            st.markdown("### ➕ Registra Nuovo Versamento")
            
            with st.form(f"form_nuovo_versamento_{chiave_iscritto}", clear_on_submit=True):
                col_v1, col_v2, col_v3 = st.columns(3)
                
                with col_v1:
                    importo_versato = st.number_input(
                        "Importo Versato (€):",
                        min_value=0.01,
                        max_value=max(0.01, float(iscritto["rimanente"] if iscritto["rimanente"] > 0 else 2000.0)),
                        value=float(iscritto["rimanente"]) if iscritto["rimanente"] > 0 else 10.0,
                        step=5.0
                    )
                    tipo_transazione = st.selectbox("Causale Versamento:", ["Acconto", "Saldo", "Integrazione", "Caparra"])

                with col_v2:
                    metodo_pago = st.selectbox("Metodo di Pagamento:", ["Contanti", "POS", "Bonifico", "Satispay"])
                    
                    data_transazione = st.date_input(
                        "Data Versamento:", 
                        value=date.today(),
                        format="DD/MM/YYYY"
                    )

                with col_v3:
                    note_transazione = st.text_area("Note / N. Ricevuta:", value="", height=100, placeholder="Es. Ricevuta N° 45, riferimento bonifico...")

                btn_registra = st.form_submit_button("💳 Salva e Registra Versamento", type="primary", use_container_width=True)

                if btn_registra:
                    nuova_tx = {
                        "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                        "data": data_transazione.strftime("%Y-%m-%d"),
                        "tipo": tipo_transazione,
                        "importo": float(importo_versato),
                        "metodo": metodo_pago,
                        "note": note_transazione
                    }

                    transazioni_attuali = st.session_state.registro_pagamenti.get(chiave_iscritto, {}).get("transazioni", [])
                    transazioni_attuali.append(nuova_tx)

                    st.session_state.registro_pagamenti[chiave_iscritto] = {
                        "transazioni": transazioni_attuali
                    }

                    config["registro_pagamenti"] = st.session_state.registro_pagamenti
                    if salva_configurazione(config):
                        st.success(f"🎉 Versamento di {importo_versato:.2f} € registrato con successo per {iscritto['cognome']} {iscritto['nome']}!")
                        st.rerun()
                    else:
                        st.error("❌ Errore durante il salvataggio.")

            st.markdown("<br>", unsafe_allow_html=True)

            # STORICO TRANSAZIONI
            st.markdown("### 📜 Storico Transazioni ed Incassi Effettuati")
            
            transazioni_list = iscritto["transazioni"]
            if not transazioni_list:
                st.info("Nessun versamento ancora registrato per questo iscritto.")
            else:
                df_tx = pd.DataFrame(transazioni_list)
                
                st.dataframe(
                    df_tx[["data", "tipo", "importo", "metodo", "note"]],
                    use_container_width=True,
                    column_config={
                        "data": st.column_config.DateColumn("Data Versamento", format="DD/MM/YYYY"),
                        "tipo": "Causale",
                        "importo": st.column_config.NumberColumn("Importo (€)", format="%.2f €"),
                        "metodo": "Metodo",
                        "note": "Note / Ricevuta"
                    },
                    hide_index=True
                )

                # Gestione eliminazione errore
                with st.expander("🗑️ Annulla o elimina una transazione errata"):
                    opzioni_tx = {}
                    for t in transazioni_list:
                        d_obj = datetime.strptime(t['data'], "%Y-%m-%d")
                        d_str_it = d_obj.strftime("%d/%m/%Y")
                        etichetta = f"{d_str_it} - {t['tipo']} di {t['importo']:.2f}€ ({t['metodo']})"
                        opzioni_tx[etichetta] = t["id"]

                    tx_da_eliminare = st.selectbox("Seleziona versamento da cancellare:", options=list(opzioni_tx.keys()))
                    
                    if st.button("❌ Elimina Transazione Selezionata", type="secondary"):
                        id_target = opzioni_tx[tx_da_eliminare]
                        nuove_tx = [t for t in transazioni_list if t["id"] != id_target]
                        
                        st.session_state.registro_pagamenti[chiave_iscritto]["transazioni"] = nuove_tx
                        config["registro_pagamenti"] = st.session_state.registro_pagamenti
                        salva_configurazione(config)
                        st.warning("Transazione eliminata ed importi ricalcolati.")
                        st.rerun()

    # ==========================================
    # TAB 2: TABELLA GENERALE
    # ==========================================
    with tab_generale:
        st.subheader("📊 Panoramica Generale Registro Contabile")
        
        df_gen = pd.DataFrame(dati_contabili_lista)
        
        tot_dovuto = df_gen["netto_da_pagare"].sum()
        tot_incassato = df_gen["totale_incassato"].sum()
        tot_rimanente = df_gen["rimanente"].sum()

        m1, m2, m3 = st.columns(3)
        m1.metric("Totale Atteso", f"{tot_dovuto:.2f} €")
        m2.metric("Totale Incassato", f"{tot_incassato:.2f} €", delta=f"{(tot_incassato/tot_dovuto*100 if tot_dovuto>0 else 0):.1f}%")
        m3.metric("Rimanente Da Incassare", f"{tot_rimanente:.2f} €", delta_color="inverse")

        st.markdown("---")

        st.dataframe(
            df_gen[[
                "cognome", "nome", "frequenze_str", "descrizione_sconto",
                "netto_da_pagare", "totale_incassato", "rimanente", "stato"
            ]],
            use_container_width=True,
            column_config={
                "cognome": "Cognome",
                "nome": "Nome",
                "frequenze_str": "Frequenze",
                "descrizione_sconto": "Sconto / Promo",
                "netto_da_pagare": st.column_config.NumberColumn("Totale Dovuto (€)", format="%.2f €"),
                "totale_incassato": st.column_config.NumberColumn("Totale Incassato (€)", format="%.2f €"),
                "rimanente": st.column_config.NumberColumn("Rimanente (€)", format="%.2f €"),
                "stato": "Stato"
            },
            hide_index=True
        )

        # Stato del Pagamento
        if netto_da_pagare == 0:
            stato = "🟢 Esente"
        elif rimanente <= 0:
            stato = "🟢 Saldato"
        elif totale_incassato > 0:
            stato = "🟡 Acconto Versato"
        else:
            stato = "🔴 Da Pagare"

        info_iscritto = {
            "chiave": chiave,
            "cognome": cognome,
            "nome": nome,
            "frequenze_str": stringa_frequenze,
            "num_settimane": num_settimane_tot,
            "totale_lordo": totale_lordo,
            "descrizione_sconto": descrizione_sconto,
            "sconto_applicato": sconto_applicato,
            "netto_da_pagare": netto_da_pagare,
            "totale_incassato": totale_incassato,
            "rimanente": rimanente,
            "stato": stato,
            "transazioni": transazioni
        }

        elenco_iscritti_dettaglio[etichetta_ricerca] = info_iscritto
        dati_contabili_lista.append(info_iscritto)

    if not elenco_iscritti_dettaglio:
        st.info("Nessun iscritto trovato nel database.")
        return

    # --- 2. SCHERMATA A TAB ---
    tab_scheda, tab_generale = st.tabs(["🔍 Scheda Singolo Iscritto", "📊 Panoramica Registro Completo"])

    # ==========================================
    # TAB 1: SCHEDA DETTAGLIO ISCRITTO
    # ==========================================
    with tab_scheda:
        st.subheader("🔍 Cerca e Gestisci Iscritto")
        
        opzioni_ricerca = sorted(list(elenco_iscritti_dettaglio.keys()))
        
        nome_selezionato = st.selectbox(
            "Digitare il cognome o nome dell'iscritto:",
            options=opzioni_ricerca,
            index=None,
            placeholder="Inizia a digitare il cognome o il nome...",
            help="Seleziona un iscritto per aprire la sua scheda contabile e gestire i pagamenti.",
            key="selectbox_ricerca_iscritto_pagamenti"
        )

        if not nome_selezionato:
            st.info("💡 Inizia a digitare il nome dell'iscritto nella barra di ricerca in alto per caricare la scheda dettagliata.")
        else:
            iscritto = elenco_iscritti_dettaglio[nome_selezionato]
            chiave_iscritto = iscritto["chiave"]

            st.markdown("---")
            
            # Intestazione Scheda
            col_head1, col_head2 = st.columns([3, 1])
            with col_head1:
                st.markdown(f"## 👤 {iscritto['cognome']} {iscritto['nome']}")
                st.write(f"🗓️ **Frequenze ({iscritto['num_settimane']} sett.):** {iscritto['frequenze_str']}")
                st.write(f"🏷️ **Tariffa/Promo Applicata:** {iscritto['descrizione_sconto']}")
            with col_head2:
                st.markdown(f"### Status:\n### {iscritto['stato']}")

            st.markdown("<br>", unsafe_allow_html=True)

            # Card metriche
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Lordo Listino", f"{iscritto['totale_lordo']:.2f} €")
            c2.metric("Sconto Promo", f"{iscritto['sconto_applicato']:.2f} €")
            c3.metric("Netto Dovuto", f"{iscritto['netto_da_pagare']:.2f} €")
            c4.metric("Rimanente da Pagare", f"{iscritto['rimanente']:.2f} €", delta_color="inverse")

            st.markdown("---")

            # REGISTRA NUOVA TRANSAZIONE
            st.markdown("### ➕ Registra Nuovo Versamento")
            
            with st.form(f"form_nuovo_versamento_{chiave_iscritto}", clear_on_submit=True):
                col_v1, col_v2, col_v3 = st.columns(3)
                
                with col_v1:
                    importo_versato = st.number_input(
                        "Importo Versato (€):",
                        min_value=0.01,
                        max_value=max(0.01, float(iscritto["rimanente"] if iscritto["rimanente"] > 0 else 2000.0)),
                        value=float(iscritto["rimanente"]) if iscritto["rimanente"] > 0 else 10.0,
                        step=5.0
                    )
                    tipo_transazione = st.selectbox("Causale Versamento:", ["Acconto", "Saldo", "Integrazione", "Caparra"])

                with col_v2:
                    metodo_pago = st.selectbox("Metodo di Pagamento:", ["Contanti", "POS", "Bonifico", "Satispay"])
                    
                    data_transazione = st.date_input(
                        "Data Versamento:", 
                        value=date.today(),
                        format="DD/MM/YYYY"
                    )

                with col_v3:
                    note_transazione = st.text_area("Note / N. Ricevuta:", value="", height=100, placeholder="Es. Ricevuta N° 45, riferimento bonifico...")

                btn_registra = st.form_submit_button("💳 Salva e Registra Versamento", type="primary", use_container_width=True)

                if btn_registra:
                    nuova_tx = {
                        "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                        "data": data_transazione.strftime("%Y-%m-%d"),
                        "tipo": tipo_transazione,
                        "importo": float(importo_versato),
                        "metodo": metodo_pago,
                        "note": note_transazione
                    }

                    transazioni_attuali = st.session_state.registro_pagamenti.get(chiave_iscritto, {}).get("transazioni", [])
                    transazioni_attuali.append(nuova_tx)

                    st.session_state.registro_pagamenti[chiave_iscritto] = {
                        "transazioni": transazioni_attuali
                    }

                    config["registro_pagamenti"] = st.session_state.registro_pagamenti
                    if salva_configurazione(config):
                        st.success(f"🎉 Versamento di {importo_versato:.2f} € registrato con successo per {iscritto['cognome']} {iscritto['nome']}!")
                        st.rerun()
                    else:
                        st.error("❌ Errore durante il salvataggio.")

            st.markdown("<br>", unsafe_allow_html=True)

            # STORICO TRANSAZIONI
            st.markdown("### 📜 Storico Transazioni ed Incassi Effettuati")
            
            transazioni_list = iscritto["transazioni"]
            if not transazioni_list:
                st.info("Nessun versamento ancora registrato per questo iscritto.")
            else:
                df_tx = pd.DataFrame(transazioni_list)
                
                st.dataframe(
                    df_tx[["data", "tipo", "importo", "metodo", "note"]],
                    use_container_width=True,
                    column_config={
                        "data": st.column_config.DateColumn("Data Versamento", format="DD/MM/YYYY"),
                        "tipo": "Causale",
                        "importo": st.column_config.NumberColumn("Importo (€)", format="%.2f €"),
                        "metodo": "Metodo",
                        "note": "Note / Ricevuta"
                    },
                    hide_index=True
                )

                # Gestione eliminazione errore
                with st.expander("🗑️ Annulla o elimina una transazione errata"):
                    opzioni_tx = {}
                    for t in transazioni_list:
                        d_obj = datetime.strptime(t['data'], "%Y-%m-%d")
                        d_str_it = d_obj.strftime("%d/%m/%Y")
                        etichetta = f"{d_str_it} - {t['tipo']} di {t['importo']:.2f}€ ({t['metodo']})"
                        opzioni_tx[etichetta] = t["id"]

                    tx_da_eliminare = st.selectbox("Seleziona versamento da cancellare:", options=list(opzioni_tx.keys()))
                    
                    if st.button("❌ Elimina Transazione Selezionata", type="secondary"):
                        id_target = opzioni_tx[tx_da_eliminare]
                        nuove_tx = [t for t in transazioni_list if t["id"] != id_target]
                        
                        st.session_state.registro_pagamenti[chiave_iscritto]["transazioni"] = nuove_tx
                        config["registro_pagamenti"] = st.session_state.registro_pagamenti
                        salva_configurazione(config)
                        st.warning("Transazione eliminata ed importi ricalcolati.")
                        st.rerun()

    # ==========================================
    # TAB 2: TABELLA GENERALE
    # ==========================================
    with tab_generale:
        st.subheader("📊 Panoramica Generale Registro Contabile")
        
        df_gen = pd.DataFrame(dati_contabili_lista)
        
        tot_dovuto = df_gen["netto_da_pagare"].sum()
        tot_incassato = df_gen["totale_incassato"].sum()
        tot_rimanente = df_gen["rimanente"].sum()

        m1, m2, m3 = st.columns(3)
        m1.metric("Totale Atteso", f"{tot_dovuto:.2f} €")
        m2.metric("Totale Incassato", f"{tot_incassato:.2f} €", delta=f"{(tot_incassato/tot_dovuto*100 if tot_dovuto>0 else 0):.1f}%")
        m3.metric("Rimanente Da Incassare", f"{tot_rimanente:.2f} €", delta_color="inverse")

        st.markdown("---")

        st.dataframe(
            df_gen[[
                "cognome", "nome", "frequenze_str", "descrizione_sconto",
                "netto_da_pagare", "totale_incassato", "rimanente", "stato"
            ]],
            use_container_width=True,
            column_config={
                "cognome": "Cognome",
                "nome": "Nome",
                "frequenze_str": "Frequenze",
                "descrizione_sconto": "Sconto / Promo",
                "netto_da_pagare": st.column_config.NumberColumn("Totale Dovuto (€)", format="%.2f €"),
                "totale_incassato": st.column_config.NumberColumn("Totale Incassato (€)", format="%.2f €"),
                "rimanente": st.column_config.NumberColumn("Rimanente (€)", format="%.2f €"),
                "stato": "Stato"
            },
            hide_index=True
        )