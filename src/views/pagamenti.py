import streamlit as st
import pandas as pd
from datetime import datetime, date
from src.utils.config_manager import carica_configurazione, salva_configurazione

def mostra_pagamenti(df_iscritti):
    st.title("💳 Gestione Pagamenti & Incassi")
    st.caption("Cerca un iscritto per aprire la sua scheda contabile dettagliata o consulta il registro generale.")
    st.markdown("---")

    config = carica_configurazione()
    tariffe = config.get("tariffe", {})
    pacchetti = config.get("pacchetti", [])
    sconti_disponibili = config.get("sconti", [])

    if not tariffe:
        st.warning("⚠️ Non hai ancora configurato le tariffe nel pannello Impostazioni!")

    # --- 1. MAPPATURA E PREPARAZIONE DATI ---
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

    # Costruzione struttura dati contabili per ogni iscritto
    elenco_iscritti_dettaglio = {}
    dati_contabili_lista = []

    for idx, row in df_iscritti.iterrows():
        cognome = str(row.get(col_cognome, "")).strip().upper()
        nome = str(row.get(col_nome, "")).strip().title()
        
        if not cognome or not nome or cognome == "NAN":
            continue

        chiave = f"{cognome}_{nome}".upper()
        etichetta_ricerca = f"{cognome} {nome}"

        dati_salvati = st.session_state.registro_pagamenti.get(chiave, {
            "acconto": 0.0,
            "saldo_versato": 0.0,
            "sconto_selezionato": "Nessuno (Standard)",
            "sconto_extra": 0.0,
            "metodo_pagamento": "Contanti",
            "data_saldo": None,
            "note": ""
        })

        acconto = float(dati_salvati.get("acconto", 0.0))
        saldo_versato = float(dati_salvati.get("saldo_versato", 0.0))
        sconto_scelto_utente = dati_salvati.get("sconto_selezionato", "Nessuno (Standard)")
        sconto_extra = float(dati_salvati.get("sconto_extra", 0.0))
        metodo_pago = dati_salvati.get("metodo_pagamento", "Contanti")
        note = dati_salvati.get("note", "")
        
        data_s = dati_salvati.get("data_saldo")
        if data_s and isinstance(data_s, str):
            try:
                data_s = datetime.strptime(data_s, "%Y-%m-%d").date()
            except ValueError:
                data_s = None
        elif not isinstance(data_s, date):
            data_s = None

        # Conteggio frequenze e Lordo
        dettaglio_frequenze = {}
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
                        costo_sett = prezzo
                        break
                
                if costo_sett == 0.0 and tariffe:
                    tipo_trovato = list(tariffe.keys())[0]
                    costo_sett = list(tariffe.values())[0]

                dettaglio_frequenze[tipo_trovato] = dettaglio_frequenze.get(tipo_trovato, 0) + 1
                totale_lordo += costo_sett

        stringa_frequenze = ", ".join([f"{v}x {k}" for k, v in dettaglio_frequenze.items()]) if dettaglio_frequenze else "Nessuna"

        # Calcolo Miglior Sconto
        valore_pacchetto = 0.0
        nome_pacchetto = ""
        for pk in sorted(pacchetti, key=lambda x: x.get("min_settimane", 0), reverse=True):
            if num_settimane_tot >= pk.get("min_settimane", 0):
                perc = pk.get("sconto_percentuale", 0.0)
                valore_pacchetto = (totale_lordo * perc) / 100.0
                nome_pacchetto = f"📦 {pk.get('nome')} (-{perc}%)"
                break

        valore_sconto_convenzione = 0.0
        if sconto_scelto_utente != "Nessuno (Standard)":
            for sc in sconti_disponibili:
                if sc["nome"] == sconto_scelto_utente:
                    if sc["tipo"] == "percentuale":
                        valore_sconto_convenzione = (totale_lordo * sc["valore"]) / 100.0
                    else:
                        valore_sconto_convenzione = float(sc["valore"])
                    break

        if valore_pacchetto >= valore_sconto_convenzione and valore_pacchetto > 0:
            sconto_applicato = valore_pacchetto
            descrizione_sconto = nome_pacchetto
        elif valore_sconto_convenzione > 0:
            sconto_applicato = valore_sconto_convenzione
            descrizione_sconto = f"🏷️ {sconto_scelto_utente}"
        else:
            sconto_applicato = 0.0
            descrizione_sconto = "Nessuno"

        totale_sconti = sconto_applicato + sconto_extra
        netto_da_pagare = max(0.0, totale_lordo - totale_sconti)

        totale_incassato = acconto + saldo_versato
        rimanente = netto_da_pagare - totale_incassato

        if netto_da_pagare == 0:
            stato = "🟢 Esente"
        elif rimanente <= 0:
            stato = "🟢 Saldato"
        elif totale_incassato > 0:
            stato = "🟡 Acconto"
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
            "sconto_extra": sconto_extra,
            "sconto_selezionato": sconto_scelto_utente,
            "netto_da_pagare": netto_da_pagare,
            "acconto": acconto,
            "saldo_versato": saldo_versato,
            "totale_incassato": totale_incassato,
            "rimanente": rimanente,
            "stato": stato,
            "metodo_pagamento": metodo_pago,
            "data_saldo": data_s,
            "note": note
        }

        elenco_iscritti_dettaglio[etichetta_ricerca] = info_iscritto
        dati_contabili_lista.append(info_iscritto)

    if not elenco_iscritti_dettaglio:
        st.info("Nessun iscritto trovato nel database.")
        return

    # --- 2. SCHERMATA A TAB (SCHEDA DETTAGLIO vs TABELLA GENERALE) ---
    tab_scheda, tab_generale = st.tabs(["🔍 Scheda Singolo Iscritto", "📊 Panoramica Registro Completo"])

    # ==========================================
    # TAB 1: SCHEDA DETTAGLIO ISCRITTO
    # ==========================================
    with tab_scheda:
        st.subheader("🔍 Ricerca e Gestione Scheda Iscritto")
        
        opzioni_ricerca = sorted(list(elenco_iscritti_dettaglio.keys()))
        
        # Barra di ricerca autocompletante
        nome_selezionato = st.selectbox(
            "Cerca iscritto (digita Cognome o Nome):",
            options=opzioni_ricerca,
            index=0,
            help="Inizia a digitare il cognome o nome dell'iscritto per aprire la sua scheda contabile"
        )

        if nome_selezionato:
            iscritto = elenco_iscritti_dettaglio[nome_selezionato]
            chiave_iscritto = iscritto["chiave"]

            st.markdown("---")
            
            # Intestazione Scheda
            col_head1, col_head2 = st.columns([3, 1])
            with col_head1:
                st.markdown(f"## 👤 {iscritto['cognome']} {iscritto['nome']}")
                st.write(f"🗓️ **Frequenze Svolte ({iscritto['num_settimane']} sett.):** {iscritto['frequenze_str']}")
            with col_head2:
                st.markdown(f"### Stato: {iscritto['stato']}")

            st.markdown("<br>", unsafe_allow_html=True)

            # Riepilogo Economico a Card (KPI)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Lordo Listino", f"{iscritto['totale_lordo']:.2f} €")
            c2.metric("Sconto Applicato", f"{(iscritto['sconto_applicato'] + iscritto['sconto_extra']):.2f} €", delta=iscritto['descrizione_sconto'])
            c3.metric("Netto Dovuto", f"{iscritto['netto_da_pagare']:.2f} €")
            c4.metric("Rimanente da Pagare", f"{iscritto['rimanente']:.2f} €", delta_color="inverse")

            st.markdown("---")

            # Form d'Incasso e Gestione Sconti
            st.markdown("### 📝 Aggiorna Incasso e Convenzioni")
            
            with st.form(f"form_pagamento_{chiave_iscritto}"):
                col_f1, col_f2 = st.columns(2)
                
                with col_f1:
                    st.markdown("##### 🏷️ Convenzioni & Sconti Extra")
                    
                    opzioni_sconto = ["Nessuno (Standard)"] + [s["nome"] for s in sconti_disponibili]
                    idx_sconto = opzioni_sconto.index(iscritto["sconto_selezionato"]) if iscritto["sconto_selezionato"] in opzioni_sconto else 0
                    
                    nuovo_sconto_sel = st.selectbox(
                        "Seleziona Convenzione/Categoria:",
                        options=opzioni_sconto,
                        index=idx_sconto,
                        help="Il sistema confronterà la convenzione con i pacchetti promozionali per applicare il prezzo migliore."
                    )

                    nuovo_sconto_extra = st.number_input(
                        "Sconto Extra Manuale (€):",
                        min_value=0.0,
                        value=float(iscritto["sconto_extra"]),
                        step=5.0
                    )

                    nuove_note = st.text_area("Note / Ragione Sconto:", value=iscritto["note"], height=100)

                with col_f2:
                    st.markdown("##### 💵 Registrazione Importi e Saldo")

                    nuovo_acconto = st.number_input(
                        "Acconto Versato (€):",
                        min_value=0.0,
                        value=float(iscritto["acconto"]),
                        step=10.0
                    )

                    nuovo_saldo = st.number_input(
                        "Saldo Versato (€):",
                        min_value=0.0,
                        value=float(iscritto["saldo_versato"]),
                        step=10.0
                    )

                    opzioni_metodo = ["Contanti", "POS", "Bonifico", "Satispay"]
                    idx_metodo = opzioni_metodo.index(iscritto["metodo_pagamento"]) if iscritto["metodo_pagamento"] in opzioni_metodo else 0
                    
                    nuovo_metodo = st.selectbox(
                        "Metodo di Pagamento:",
                        options=opzioni_metodo,
                        index=idx_metodo
                    )

                    valore_data_def = iscritto["data_saldo"] if iscritto["data_saldo"] else date.today()
                    nuova_data = st.date_input(
                        "Data Saldo:",
                        value=valore_data_def
                    )

                st.markdown("<br>", unsafe_allow_html=True)
                btn_salva = st.form_submit_button("💾 Salva Scheda Iscritto", type="primary", use_container_width=True)

                if btn_salva:
                    d_saldo_str = nuova_data.strftime("%Y-%m-%d") if nuova_data else None

                    st.session_state.registro_pagamenti[chiave_iscritto] = {
                        "acconto": float(nuovo_acconto),
                        "saldo_versato": float(nuovo_saldo),
                        "sconto_selezionato": nuovo_sconto_sel,
                        "sconto_extra": float(nuovo_sconto_extra),
                        "metodo_pagamento": nuovo_metodo,
                        "data_saldo": d_saldo_str,
                        "note": nuove_note
                    }

                    config["registro_pagamenti"] = st.session_state.registro_pagamenti
                    if salva_configurazione(config):
                        st.success(f"🎉 Pagamento di {iscritto['cognome']} {iscritto['nome']} salvato con successo!")
                        st.rerun()
                    else:
                        st.error("❌ Errore durante il salvataggio.")

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
        m1.metric("Totale Dovuto", f"{tot_dovuto:.2f} €")
        m2.metric("Totale Incassato", f"{tot_incassato:.2f} €", delta=f"{(tot_incassato/tot_dovuto*100 if tot_dovuto>0 else 0):.1f}%")
        m3.metric("Rimanente Da Incassare", f"{tot_rimanente:.2f} €", delta_color="inverse")

        st.markdown("---")

        st.dataframe(
            df_gen[[
                "cognome", "nome", "frequenze_str", "descrizione_sconto",
                "netto_da_pagare", "acconto", "saldo_versato", "rimanente",
                "stato", "metodo_pagamento", "data_saldo"
            ]],
            use_container_width=True,
            column_config={
                "cognome": "Cognome",
                "nome": "Nome",
                "frequenze_str": "Frequenze",
                "descrizione_sconto": "Sconto / Promo",
                "netto_da_pagare": st.column_config.NumberColumn("Totale Dovuto (€)", format="%.2f €"),
                "acconto": st.column_config.NumberColumn("Acconto (€)", format="%.2f €"),
                "saldo_versato": st.column_config.NumberColumn("Saldo (€)", format="%.2f €"),
                "rimanente": st.column_config.NumberColumn("Rimanente (€)", format="%.2f €"),
                "stato": "Stato",
                "metodo_pagamento": "Metodo",
                "data_saldo": st.column_config.DateColumn("Data Saldo", format="DD/MM/YYYY")
            },
            hide_index=True
        )