import streamlit as st
import pandas as pd
from src.utils.config_manager import carica_configurazione, salva_configurazione

def mostra_pagamenti(df_iscritti):
    st.title("💳 Gestione Pagamenti & Incassi")
    st.caption("Visualizza i conteggi automatici in base alle tariffe configurate, registra acconti e monitora i saldi.")
    st.markdown("---")

    config = carica_configurazione()
    tariffe = config.get("tariffe", {})
    pacchetti = config.get("pacchetti", [])
    sconti_disponibili = config.get("sconti", [])

    if not tariffe:
        st.warning("⚠️ Non hai ancora configurato le tariffe nel pannello Impostazioni! I calcoli automatici potrebbero risultare pari a 0 €.")

    # --- 1. MAPPATURA COLONNE ED ESTRAZIONE DATI ---
    mapping = config.get("mappatura_colonne", {})
    colonne_reali = list(df_iscritti.columns)

    col_cognome = mapping.get("cognome", "COGNOME MINORE")
    col_nome = mapping.get("nome", "NOME MINORE")
    
    # Riconoscimento colonne settimane
    prefisso = str(config.get("prefisso_settimane", "PERIODI DISPONIBILI")).strip().lower()
    colonne_settimane = [
        col for col in colonne_reali 
        if "settiman" in str(col).lower() or prefisso in str(col).lower()
    ]

    # Recupero o Inizializzazione registro pagamenti in session_state
    if "registro_pagamenti" not in st.session_state:
        st.session_state.registro_pagamenti = config.get("registro_pagamenti", {})

    # --- 2. ELABORAZIONE SCHEDE CONTABILI BANBINI ---
    dati_contabili = []

    for idx, row in df_iscritti.iterrows():
        cognome = str(row.get(col_cognome, "")).strip().upper()
        nome = str(row.get(col_nome, "")).strip().title()
        
        if not cognome or not nome or cognome == "NAN":
            continue

        chiave_bambino = f"{cognome}_{nome}".upper()

        # Conteggio settimane e calcolo lordo
        num_settimane = 0
        totale_lordo = 0.0

        for col_s in colonne_settimane:
            valore_scelta = str(row.get(col_s, "")).strip()
            # Se la colonna non è vuota e non è "Non Frequenta" / "No"
            if valore_scelta and valore_scelta.lower() not in ["nan", "", "no", "non frequenta", "none"]:
                num_settimane += 1
                
                # Cerchiamo il prezzo corrispondente alla scelta
                costo_sett = 0.0
                for opzione_tariffa, prezzo in tariffe.items():
                    if opzione_tariffa.lower() in valore_scelta.lower():
                        costo_sett = prezzo
                        break
                
                # Se non trova una corrispondenza esatta, usa la prima tariffa se disponibile o 0
                if costo_sett == 0.0 and tariffe:
                    costo_sett = list(tariffe.values())[0]

                totale_lordo += costo_sett

        # Calcolo Sconto Pacchetto Multi-Settimana (se applicabile)
        sconto_pacchetto_valore = 0.0
        nome_pacchetto_applicato = ""
        for pk in sorted(pacchetti, key=lambda x: x.get("min_settimane", 0), reverse=True):
            if num_settimane >= pk.get("min_settimane", 0):
                perc = pk.get("sconto_percentuale", 0.0)
                sconto_pacchetto_valore = (totale_lordo * perc) / 100.0
                nome_pacchetto_applicato = pk.get("nome", "Pacchetto Multi-settimana")
                break

        # Recupero dati di pagamento registrati manualmente
        dati_salvati = st.session_state.registro_pagamenti.get(chiave_bambino, {
            "acconto": 0.0,
            "saldo_versato": 0.0,
            "sconto_manuale": 0.0,
            "note_sconto": ""
        })

        acconto = float(dati_salvati.get("acconto", 0.0))
        saldo_versato = float(dati_salvati.get("saldo_versato", 0.0))
        sconto_manuale = float(dati_salvati.get("sconto_manuale", 0.0))
        note_sconto = dati_salvati.get("note_sconto", "")

        # Calcoli finali
        totale_sconti = sconto_pacchetto_valore + sconto_manuale
        netto_da_pagare = max(0.0, totale_lordo - totale_sconti)
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
            "Sconto Pacchetto (€)": sconto_pacchetto_valore,
            "Pacchetto": nome_pacchetto_applicato,
            "Sconto Manuale (€)": sconto_manuale,
            "Note Sconto": note_sconto,
            "Netto Dovuto (€)": netto_da_pagare,
            "Acconto (€)": acconto,
            "Saldo Versato (€)": saldo_versato,
            "Totale Incassato (€)": totale_incassato,
            "Rimanente (€)": rimanente,
            "Stato": stato
        })

    df_pagamenti = pd.DataFrame(dati_contabili)

    if df_pagamenti.empty:
        st.info("Nessun iscritto trovato per la gestione dei pagamenti.")
        return

    # --- 3. METRICHE RIEPILOGATIVE (KPI CONTABILI) ---
    tot_lordo_camp = df_pagamenti["Lordo (€)"].sum()
    tot_sconti_camp = df_pagamenti["Sconto Pacchetto (€)"].sum() + df_pagamenti["Sconto Manuale (€)"].sum()
    tot_netto_camp = df_pagamenti["Netto Dovuto (€)"].sum()
    tot_incassato_camp = df_pagamenti["Totale Incassato (€)"].sum()
    tot_rimanente_camp = df_pagamenti["Rimanente (€)"].sum()

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("💶 Netto Atteso", f"{tot_netto_camp:.2f} €", delta=f"Lordo: {tot_lordo_camp:.2f} €")
    col_m2.metric("🏷️ Totale Sconti", f"{tot_sconti_camp:.2f} €")
    col_m3.metric("✅ Totale Incassato", f"{tot_incassato_camp:.2f} €", delta=f"{(tot_incassato_camp/tot_netto_camp*100 if tot_netto_camp>0 else 0):.1f}% del totale")
    col_m4.metric("⏳ Ancora Da Incassare", f"{tot_rimanente_camp:.2f} €", delta_color="inverse")

    st.markdown("---")

    # --- 4. FILTRI E RICERCA ---
    col_f1, col_f2 = st.columns([2, 2])
    with col_f1:
        cerca = st.text_input("🔍 Cerca Minore (Cognome o Nome):", "").strip().lower()
    with col_f2:
        filtro_stato = st.selectbox("📌 Filtra per Stato Pagamento:", ["Tutti", "🔴 Da Pagare / Acconto Versato", "🟢 Saldato"])

    # Applicazione filtri
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

    st.markdown(f"**Iscritti Trovati:** `{len(df_filtrato)}`")

    # --- 5. TABELLA INTERATTIVA / EDITABILE DELLE REGISTRAZIONI ---
    st.subheader("📝 Registro Incassi & Conguagli")
    st.caption("Modifica direttamente nella tabella le colonne dell'Acconto, Saldo e Sconto Manuale per aggiornare l'incasso.")

    # Prepariamo la vista per l'editor
    colonne_editabili = ["Acconto (€)", "Saldo Versato (€)", "Sconto Manuale (€)", "Note Sconto"]
    
    # Visualizzazione Data Editor
    df_editor = st.data_editor(
        df_filtrato[[
            "Cognome", "Nome", "Settimane", "Lordo (€)", "Pacchetto",
            "Sconto Pacchetto (€)", "Sconto Manuale (€)", "Note Sconto",
            "Netto Dovuto (€)", "Acconto (€)", "Saldo Versato (€)", 
            "Totale Incassato (€)", "Rimanente (€)", "Stato"
        ]],
        use_container_width=True,
        column_config={
            "Lordo (€)": st.column_config.NumberColumn(format="%.2f €"),
            "Sconto Pacchetto (€)": st.column_config.NumberColumn(format="%.2f €"),
            "Sconto Manuale (€)": st.column_config.NumberColumn("🏷️ Sconto Man. (€)", format="%.2f €", min_value=0.0),
            "Netto Dovuto (€)": st.column_config.NumberColumn(format="%.2f €"),
            "Acconto (€)": st.column_config.NumberColumn("💵 Acconto (€)", format="%.2f €", min_value=0.0),
            "Saldo Versato (€)": st.column_config.NumberColumn("💳 Saldo (€)", format="%.2f €", min_value=0.0),
            "Totale Incassato (€)": st.column_config.NumberColumn(format="%.2f €"),
            "Rimanente (€)": st.column_config.NumberColumn(format="%.2f €"),
            "Stato": st.column_config.TextColumn("Status", width="medium"),
        },
        disabled=[col for col in df_filtrato.columns if col not in colonne_editabili],
        key="editor_pagamenti_table"
    )

    # --- 6. SALVATAGGIO DEI CAMBIAMENTI ---
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Salva Modifiche Incassi", type="primary", use_container_width=True):
        # Aggiorniamo il registro in session_state e su config.json
        for idx_ed, row_ed in df_editor.iterrows():
            chiave = f"{row_ed['Cognome']}_{row_ed['Nome']}".upper()
            
            st.session_state.registro_pagamenti[chiave] = {
                "acconto": float(row_ed["Acconto (€)"]),
                "saldo_versato": float(row_ed["Saldo Versato (€)"]),
                "sconto_manuale": float(row_ed["Sconto Manuale (€)"]),
                "note_sconto": str(row_ed["Note Sconto"])
            }

        config["registro_pagamenti"] = st.session_state.registro_pagamenti
        if salva_configurazione(config):
            st.success("🎉 Registro Pagamenti salvato con successo!")
            st.rerun()
        else:
            st.error("❌ Errore durante il salvataggio dei pagamenti.")