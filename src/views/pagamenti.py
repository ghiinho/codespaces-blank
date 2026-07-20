import streamlit as st
import pandas as pd
from datetime import datetime, date
from src.utils.config_manager import carica_configurazione, salva_configurazione

def mostra_pagamenti(df_iscritti):
    st.title("💳 Gestione Pagamenti & Incassi")
    st.caption("Registro contabile essenziale per il monitoraggio dei saldi e l'incasso rapido.")
    st.markdown("---")

    config = carica_configurazione()
    tariffe = config.get("tariffe", {})
    pacchetti = config.get("pacchetti", [])
    sconti_disponibili = config.get("sconti", [])

    if not tariffe:
        st.warning("⚠️ Non hai ancora configurato le tariffe nel pannello Impostazioni! Configurale per avere i conteggi automatici.")

    # --- 1. MAPPATURA COLONNE E LETTURA DATI ---
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

    dati_contabili = []

    for idx, row in df_iscritti.iterrows():
        cognome = str(row.get(col_cognome, "")).strip().upper()
        nome = str(row.get(col_nome, "")).strip().title()
        
        if not cognome or not nome or cognome == "NAN":
            continue

        chiave_bambino = f"{cognome}_{nome}".upper()

        # Recupero registrazioni precedenti
        dati_salvati = st.session_state.registro_pagamenti.get(chiave_bambino, {
            "acconto": 0.0,
            "saldo_versato": 0.0,
            "sconto_selezionato": "Nessuno (Standard)",
            "sconto_extra": 0.0,
            "metodo_pagamento": "Contanti",
            "data_saldo": None
        })

        acconto = float(dati_salvati.get("acconto", 0.0))
        saldo_versato = float(dati_salvati.get("saldo_versato", 0.0))
        sconto_scelto_utente = dati_salvati.get("sconto_selezionato", "Nessuno (Standard)")
        sconto_extra = float(dati_salvati.get("sconto_extra", 0.0))
        metodo_pago = dati_salvati.get("metodo_pagamento", "Contanti")
        
        # Conversione data per st.data_editor
        data_s = dati_salvati.get("data_saldo")
        if data_s and isinstance(data_s, str):
            try:
                data_s = datetime.strptime(data_s, "%Y-%m-%d").date()
            except ValueError:
                data_s = None
        elif not isinstance(data_s, date):
            data_s = None

        # --- A) CONTEGGIO SETTIMANE DIVISE PER TIPOLOGIA ---
        dettaglio_frequenze = {}
        totale_lordo = 0.0
        num_settimane_tot = 0

        for col_s in colonne_settimane:
            valore_scelta = str(row.get(col_s, "")).strip()
            if valore_scelta and valore_scelta.lower() not in ["nan", "", "no", "non frequenta", "none"]:
                num_settimane_tot += 1
                
                # Identificazione tipologia di frequenza scelta
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

        # Formattazione stringa "3 Full-time, 1 Mattina"
        stringa_frequenze = ", ".join([f"{v}x {k}" for k, v in dettaglio_frequenze.items()]) if dettaglio_frequenze else "Nessuna"

        # --- B) CALCOLO BEST PRICE / SCONTI ---
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

        # Scelta del miglior sconto
        if valore_pacchetto >= valore_sconto_convenzione and valore_pacchetto > 0:
            sconto_applicato = valore_pacchetto
            descrizione_sconto = nome_pacchetto
        elif valore_sconto_convenzione > 0:
            sconto_applicato = valore_sconto_convenzione
            descrizione_sconto = f"🏷️ {sconto_scelto_utente}"
        else:
            sconto_applicato = 0.0
            descrizione_sconto = "Nessuno"

        if sconto_extra > 0:
            descrizione_sconto += f" (+{sconto_extra:.0f}€ extra)"

        # Prezzo finale Netto
        totale_sconti = sconto_applicato + sconto_extra
        netto_da_pagare = max(0.0, totale_lordo - totale_sconti)

        totale_incassato = acconto + saldo_versato
        rimanente = netto_da_pagare - totale_incassato

        # Flag grafico di feedback
        if netto_da_pagare == 0:
            stato = "🟢 Esente"
        elif rimanente <= 0:
            stato = "🟢 Saldato"
        elif totale_incassato > 0:
            stato = "🟡 Acconto"
        else:
            stato = "🔴 Da Pagare"

        dati_contabili.append({
            "Cognome": cognome,
            "Nome": nome,
            "Frequenze": stringa_frequenze,
            "Sconto / Promo": descrizione_sconto,
            "Netto da Pagare (€)": netto_da_pagare,
            "Acconto (€)": acconto,
            "Saldo Versato (€)": saldo_versato,
            "Rimanente (€)": rimanente,
            "Stato": stato,
            "Metodo Pagamento": metodo_pago,
            "Data Saldo": data_s,
            "Sconto_Selezionato_Ref": sconto_scelto_utente,
            "Sconto_Extra_Ref": sconto_extra
        })

    df_pagamenti = pd.DataFrame(dati_contabili)

    if df_pagamenti.empty:
        st.info("Nessun iscritto trovato per la gestione dei pagamenti.")
        return

    # --- 2. METRICHE RIEPILOGATIVE RAPIDE ---
    tot_netto = df_pagamenti["Netto da Pagare (€)"].sum()
    tot_incassato = df_pagamenti["Acconto (€)"].sum() + df_pagamenti["Saldo Versato (€)"].sum()
    tot_rimanente = df_pagamenti["Rimanente (€)"].sum()

    m1, m2, m3 = st.columns(3)
    m1.metric("💶 Totale Dovuto", f"{tot_netto:.2f} €")
    m2.metric("✅ Totale Incassato", f"{tot_incassato:.2f} €", delta=f"{(tot_incassato/tot_netto*100 if tot_netto>0 else 0):.1f}%")
    m3.metric("⏳ Rimanente Da Incassare", f"{tot_rimanente:.2f} €", delta_color="inverse")

    st.markdown("---")

    # --- 3. FILTRI DI RICERCA ---
    col_f1, col_f2 = st.columns([2, 2])
    with col_f1:
        cerca = st.text_input("🔍 Cerca Minore:", "").strip().lower()
    with col_f2:
        filtro_stato = st.selectbox("📌 Filtra per Stato:", ["Tutti", "🔴 Da Pagare / Acconto", "🟢 Saldato"])

    df_filtrato = df_pagamenti.copy()
    if cerca:
        df_filtrato = df_filtrato[
            df_filtrato["Cognome"].str.lower().str.contains(cerca) | 
            df_filtrato["Nome"].str.lower().str.contains(cerca)
        ]
    
    if filtro_stato == "🔴 Da Pagare / Acconto":
        df_filtrato = df_filtrato[df_filtrato["Rimanente (€)"] > 0]
    elif filtro_stato == "🟢 Saldato":
        df_filtrato = df_filtrato[df_filtrato["Rimanente (€)"] <= 0]

    st.subheader("📝 Registro Contabile")

    # --- 4. DATA EDITOR SNELLO E PULITO ---
    opzioni_metodo = ["Contanti", "POS", "Bonifico", "Satispay"]
    colonne_editabili = ["Acconto (€)", "Saldo Versato (€)", "Metodo Pagamento", "Data Saldo"]

    df_editor = st.data_editor(
        df_filtrato[[
            "Cognome", "Nome", "Frequenze", "Sconto / Promo", 
            "Netto da Pagare (€)", "Acconto (€)", "Saldo Versato (€)", 
            "Rimanente (€)", "Stato", "Metodo Pagamento", "Data Saldo"
        ]],
        use_container_width=True,
        column_config={
            "Frequenze": st.column_config.TextColumn("Frequenze Svolte", width="medium"),
            "Sconto / Promo": st.column_config.TextColumn("Sconto / Pacchetto", width="medium"),
            "Netto da Pagare (€)": st.column_config.NumberColumn("Totale (€)", format="%.2f €"),
            "Acconto (€)": st.column_config.NumberColumn("💵 Acconto (€)", format="%.2f €", min_value=0.0),
            "Saldo Versato (€)": st.column_config.NumberColumn("💳 Saldo (€)", format="%.2f €", min_value=0.0),
            "Rimanente (€)": st.column_config.NumberColumn("⏳ Rimanente (€)", format="%.2f €"),
            "Stato": st.column_config.TextColumn("Status", width="small"),
            "Metodo Pagamento": st.column_config.SelectboxColumn(
                "🏦 Metodo",
                options=opzioni_metodo,
                width="small",
                required=True
            ),
            "Data Saldo": st.column_config.DateColumn(
                "📅 Data Saldo",
                format="DD/MM/YYYY",
                width="small"
            )
        },
        disabled=[col for col in df_filtrato.columns if col not in colonne_editabili],
        key="editor_pagamenti_snello"
    )

    # --- 5. SALVATAGGIO ---
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Salva Modifiche Incassi", type="primary", use_container_width=True):
        for idx_ed, row_ed in df_editor.iterrows():
            chiave = f"{row_ed['Cognome']}_{row_ed['Nome']}".upper()
            
            # Formattazione data per il salvataggio in JSON
            d_saldo = row_ed["Data Saldo"]
            if isinstance(d_saldo, (date, datetime)):
                d_saldo_str = d_saldo.strftime("%Y-%m-%d")
            else:
                d_saldo_str = None

            # Manteniamo i rif degli sconti già impostati
            s_ref = df_filtrato.loc[df_filtrato["Cognome"] == row_ed["Cognome"], "Sconto_Selezionato_Ref"].values
            e_ref = df_filtrato.loc[df_filtrato["Cognome"] == row_ed["Cognome"], "Sconto_Extra_Ref"].values

            st.session_state.registro_pagamenti[chiave] = {
                "acconto": float(row_ed["Acconto (€)"]),
                "saldo_versato": float(row_ed["Saldo Versato (€)"]),
                "sconto_selezionato": s_ref[0] if len(s_ref) > 0 else "Nessuno (Standard)",
                "sconto_extra": float(e_ref[0]) if len(e_ref) > 0 else 0.0,
                "metodo_pagamento": str(row_ed["Metodo Pagamento"]),
                "data_saldo": d_saldo_str
            }

        config["registro_pagamenti"] = st.session_state.registro_pagamenti
        if salva_configurazione(config):
            st.success("🎉 Registro Pagamenti aggiornato con successo!")
            st.rerun()
        else:
            st.error("❌ Errore durante il salvataggio!")