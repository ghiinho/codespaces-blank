import streamlit as st
import pandas as pd
from src.utils.config_manager import carica_configurazione, salva_configurazione

def mostra_pagamenti(df_iscritti):
    st.title("💳 Gestione Pagamenti & Incassi")
    st.caption("Calcolo automatico con la regola del Prezzo Più Conveniente (Miglior Tariffa per l'iscritto).")
    st.markdown("---")

    config = carica_configurazione()
    tariffe = config.get("tariffe", {})
    pacchetti = config.get("pacchetti", [])
    sconti_disponibili = config.get("sconti", [])

    if not tariffe:
        st.warning("⚠️ Non hai ancora configurato le tariffe nel pannello Impostazioni! I calcoli automatici potrebbero risultare pari a 0 €.")

    # --- 1. MAPPATURA COLONNE ---
    mapping = config.get("mappatura_colonne", {})
    colonne_reali = list(df_iscritti.columns)

    col_cognome = mapping.get("cognome", "COGNOME MINORE")
    col_nome = mapping.get("nome", "NOME MINORE")
    
    prefisso = str(config.get("prefisso_settimane", "PERIODI DISPONIBILI")).strip().lower()
    colonne_settimane = [
        col for col in colonne_reali 
        if "settiman" in str(col).lower() or prefisso in str(col).lower()
    ]

    # Recupero o Inizializzazione registro pagamenti in session_state
    if "registro_pagamenti" not in st.session_state:
        st.session_state.registro_pagamenti = config.get("registro_pagamenti", {})

    # --- 2. ALGORITMO BEST PRICE PER CIASCUN ISCRITTO ---
    dati_contabili = []

    for idx, row in df_iscritti.iterrows():
        cognome = str(row.get(col_cognome, "")).strip().upper()
        nome = str(row.get(col_nome, "")).strip().title()
        
        if not cognome or not nome or cognome == "NAN":
            continue

        chiave_bambino = f"{cognome}_{nome}".upper()

        # Recupero dati di pagamento salvati
        dati_salvati = st.session_state.registro_pagamenti.get(chiave_bambino, {
            "acconto": 0.0,
            "saldo_versato": 0.0,
            "sconto_selezionato": "Nessuno (Standard)",
            "sconto_manuale_extra": 0.0,
            "note_sconto": ""
        })

        acconto = float(dati_salvati.get("acconto", 0.0))
        saldo_versato = float(dati_salvati.get("saldo_versato", 0.0))
        sconto_scelto_utente = dati_salvati.get("sconto_selezionato", "Nessuno (Standard)")
        sconto_extra = float(dati_salvati.get("sconto_manuale_extra", 0.0))
        note_sconto = dati_salvati.get("note_sconto", "")

        # A) CALCOLO TARIFFA BASE (LORDO)
        num_settimane = 0
        totale_lordo = 0.0

        for col_s in colonne_settimane:
            valore_scelta = str(row.get(col_s, "")).strip()
            if valore_scelta and valore_scelta.lower() not in ["nan", "", "no", "non frequenta", "none"]:
                num_settimane += 1
                
                costo_sett = 0.0
                for opzione_tariffa, prezzo in tariffe.items():
                    if opzione_tariffa.lower() in valore_scelta.lower():
                        costo_sett = prezzo
                        break
                
                if costo_sett == 0.0 and tariffe:
                    costo_sett = list(tariffe.values())[0]

                totale_lordo += costo_sett

        # B) SCENARIO 1: PACCHETTO PROMO MULTI-SETTIMANA
        valore_pacchetto = 0.0
        nome_pacchetto = "Nessun Pacchetto"
        for pk in sorted(pacchetti, key=lambda x: x.get("min_settimane", 0), reverse=True):
            if num_settimane >= pk.get("min_settimane", 0):
                perc = pk.get("sconto_percentuale", 0.0)
                valore_pacchetto = (totale_lordo * perc) / 100.0
                nome_pacchetto = f"{pk.get('nome')} (-{perc}%)"
                break

        # C) SCENARIO 2: SCONTO CONVENZIONE / SELEZIONATO
        valore_sconto_convenzione = 0.0
        if sconto_scelto_utente != "Nessuno (Standard)":
            for sc in sconti_disponibili:
                if sc["nome"] == sconto_scelto_utente:
                    if sc["tipo"] == "percentuale":
                        valore_sconto_convenzione = (totale_lordo * sc["valore"]) / 100.0
                    else:
                        valore_sconto_convenzione = float(sc["valore"])
                    break

        # D) VALUTAZIONE ALGORITMICA PREZZO PIÙ CONVENIENTE
        sconto_applicato = 0.0
        formula_applicata = ""

        # Confronto: Pacchetto Promo vs Sconto Convenzione Selezionato
        if valore_pacchetto >= valore_sconto_convenzione and valore_pacchetto > 0:
            sconto_applicato = valore_pacchetto
            formula_applicata = f"📦 {nome_pacchetto}"
        elif valore_sconto_convenzione > 0:
            sconto_applicato = valore_sconto_convenzione
            formula_applicata = f"🏷️ {sconto_scelto_utente}"
        else:
            sconto_applicato = 0.0
            formula_applicata = "Standard"

        # Totale Sconto Complessivo (Sconto Migliore + Eventuale Extra Manuale)
        totale_sconti_finali = sconto_applicato + sconto_extra
        netto_da_pagare = max(0.0, totale_lordo - totale_sconti_finali)
        
        totale_incassato = acconto + saldo_versato
        rimanente = netto_da_pagare - totale_incassato

        # Stato del Pagamento
        if netto_da_pagare == 0:
            stato = "🟢 Gratuito / Esente"
        elif rimanente <= 0:
            stato = "🟢 Saldato"
        elif totale_incassato > 0:
            stato = "🟡 Acconto Versato"
        else:
            stato = "🔴 Da Pagare"

        dati_contabili.append({
            "chiave": chiave_bambino,
            "Cognome": cognome,
            "Nome": nome,
            "Settimane": num_settimane,
            "Lordo (€)": totale_lordo,
            "Formula Applicata": formula_applicata,
            "Sconto Applicato (€)": sconto_applicato,
            "Sconto Extra (€)": sconto_extra,
            "Netto Dovuto (€)": netto_da_pagare,
            "Acconto (€)": acconto,
            "Saldo Versato (€)": saldo_versato,
            "Totale Incassato (€)": totale_incassato,
            "Rimanente (€)": rimanente,
            "Stato": stato,
            "Sconto_Selezionato_Ref": sconto_scelto_utente,
            "Note Sconto": note_sconto
        })

    df_pagamenti = pd.DataFrame(dati_contabili)

    if df_pagamenti.empty:
        st.info("Nessun iscritto trovato per la gestione dei pagamenti.")
        return

    # --- 3. METRICHE RIEPILOGATIVE (KPI CONTABILI) ---
    tot_lordo_camp = df_pagamenti["Lordo (€)"].sum()
    tot_sconti_camp = df_pagamenti["Sconto Applicato (€)"].sum() + df_pagamenti["Sconto Extra (€)"].sum()
    tot_netto_camp = df_pagamenti["Netto Dovuto (€)"].sum()
    tot_incassato_camp = df_pagamenti["Totale Incassato (€)"].sum()
    tot_rimanente_camp = df_pagamenti["Rimanente (€)"].sum()

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("💶 Netto Atteso", f"{tot_netto_camp:.2f} €", delta=f"Lordo: {tot_lordo_camp:.2f} €")
    col_m2.metric("🏷️ Risparmio Famiglie", f"{tot_sconti_camp:.2f} €")
    col_m3.metric("✅ Totale Incassato", f"{tot_incassato_camp:.2f} €", delta=f"{(tot_incassato_camp/tot_netto_camp*100 if tot_netto_camp>0 else 0):.1f}% del totale")
    col_m4.metric("⏳ Ancora Da Incassare", f"{tot_rimanente_camp:.2f} €", delta_color="inverse")

    st.markdown("---")

    # --- 4. FILTRI ED EDITOR INTERATTIVO ---
    col_f1, col_f2 = st.columns([2, 2])
    with col_f1:
        cerca = st.text_input("🔍 Cerca Minore (Cognome o Nome):", "").strip().lower()
    with col_f2:
        filtro_stato = st.selectbox("📌 Filtra per Stato Pagamento:", ["Tutti", "🔴 Da Pagare / Acconto Versato", "🟢 Saldato"])

    df_filtrato = df_pagamenti.copy()
    if cerca:
        df_filtrato = df_filtrato[
            df_filtrato["Cognome"].str.lower().str.contains(cerca) | 
            df_filtrato["Nome"].str.lower().str.contains(cerca)
        ]
    
    if filtro_stato == "🔴 Da Pagare / Acconto Versato":
        df_filtrato = df_filtrato[df_filtrato["Rimanente (€)"] > 0]
    elif filtro_stato == "🟢 Saldato":
        df_filtrato = df_filtrato[df_filtrato["Rimanente (€)"] <= 0]

    st.subheader("📝 Registro Contabile (Valutazione Miglior Tariffa)")
    st.caption("Il sistema applica automaticamente lo sconto più vantaggioso tra Pacchetti e Convenzioni. Puoi aggiungere uno Sconto Extra manuale, acconti e saldi.")

    # Opzioni sconti convenzione disponibili per il menu a tendina
    opzioni_sconto_dropdown = ["Nessuno (Standard)"] + [s["nome"] for s in sconti_disponibili]

    colonne_editabili = ["Sconto Convenzione", "Sconto Extra (€)", "Acconto (€)", "Saldo Versato (€)", "Note Sconto"]
    
    # Aggiungiamo la colonna per selezionare lo sconto dal menu
    df_filtrato["Sconto Convenzione"] = df_filtrato["Sconto_Selezionato_Ref"]

    df_editor = st.data_editor(
        df_filtrato[[
            "Cognome", "Nome", "Settimane", "Lordo (€)", "Formula Applicata",
            "Sconto Convenzione", "Sconto Applicato (€)", "Sconto Extra (€)",
            "Netto Dovuto (€)", "Acconto (€)", "Saldo Versato (€)", 
            "Totale Incassato (€)", "Rimanente (€)", "Stato", "Note Sconto"
        ]],
        use_container_width=True,
        column_config={
            "Lordo (€)": st.column_config.NumberColumn(format="%.2f €"),
            "Formula Applicata": st.column_config.TextColumn("Miglior Opzione Trova", help="Opzione applicata in automatico perché più conveniente"),
            "Sconto Convenzione": st.column_config.SelectboxColumn(
                "🏷️ Convenzione",
                options=opzioni_sconto_dropdown,
                help="Seleziona una convenzione (es. Fratello, Dipendente) da mettere a confronto",
                width="medium"
            ),
            "Sconto Applicato (€)": st.column_config.NumberColumn("✨ Sconto Migliore (€)", format="%.2f €"),
            "Sconto Extra (€)": st.column_config.NumberColumn("✏️ Extra Manuale (€)", format="%.2f €", min_value=0.0),
            "Netto Dovuto (€)": st.column_config.NumberColumn(format="%.2f €"),
            "Acconto (€)": st.column_config.NumberColumn("💵 Acconto (€)", format="%.2f €", min_value=0.0),
            "Saldo Versato (€)": st.column_config.NumberColumn("💳 Saldo (€)", format="%.2f €", min_value=0.0),
            "Totale Incassato (€)": st.column_config.NumberColumn(format="%.2f €"),
            "Rimanente (€)": st.column_config.NumberColumn(format="%.2f €"),
            "Stato": st.column_config.TextColumn("Status", width="medium"),
        },
        disabled=[col for col in df_filtrato.columns if col not in colonne_editabili],
        key="editor_pagamenti_best_price"
    )

    # --- 5. SALVATAGGIO MODIFICHE ---
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Salva Registro Incassi", type="primary", use_container_width=True):
        for idx_ed, row_ed in df_editor.iterrows():
            chiave = f"{row_ed['Cognome']}_{row_ed['Nome']}".upper()
            
            st.session_state.registro_pagamenti[chiave] = {
                "acconto": float(row_ed["Acconto (€)"]),
                "saldo_versato": float(row_ed["Saldo Versato (€)"]),
                "sconto_selezionato": str(row_ed["Sconto Convenzione"]),
                "sconto_manuale_extra": float(row_ed["Sconto Extra (€)"]),
                "note_sconto": str(row_ed["Note Sconto"])
            }

        config["registro_pagamenti"] = st.session_state.registro_pagamenti
        if salva_configurazione(config):
            st.success("🎉 Registro Pagamenti aggiornato e ricalcolato con successo!")
            st.rerun()
        else:
            st.error("❌ Errore durante il salvataggio dei dati.")