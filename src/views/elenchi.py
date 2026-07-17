import streamlit as st
import pandas as pd
import io

def mostra_elenchi_settimanali(df_iscritti, col_cognome, col_nome, col_allergie, col_quali, col_g_tel, prefisso_settimane):
    st.markdown("## 📅 Elenchi Settimanali e Appello")
    st.markdown("Seleziona una settimana per visualizzare i bambini frequentanti e scaricare il registro presenze.")

    # 1. RILEVAZIONE AUTOMATICA DELLE SETTIMANE
    prefisso_ricerca = str(prefisso_settimane).strip()
    colonne_settimane_reali = [
        str(col).strip() for col in df_iscritti.columns 
        if pd.notna(col) and str(col).strip().startswith(prefisso_ricerca)
    ]

    if not colonne_settimane_reali:
        st.error(f"⚠️ Non è stato possibile rilevare le colonne delle settimane con il prefisso '{prefisso_ricerca}' nel file Excel.")
        return

    # Mappatura nomi puliti per l'interfaccia
    mappa_nomi_settimane = {col.replace(f"{prefisso_ricerca} ", ""): col for col in colonne_settimane_reali}
    lista_settimane_pulite = sorted(list(mappa_nomi_settimane.keys()))

    # --- SBLOCCO LOGICO: DEFINIAMO LE VARIABILI IN MODO LINEARE ---
    # Creiamo il selettore e assegniamo IMMEDIATAMENTE il valore fuori dai blocchi "with"
    settimana_scelta_pulita = st.selectbox(
        "📆 Seleziona la settimana da visualizzare:", 
        options=lista_settimane_pulite,
        help="Il sistema mostra solo le settimane configurate nel modulo d'iscrizione."
    )
    
    # Questa è la colonna reale dell'Excel che useremo ovunque da qui in poi
    col_settimana_scelta = mappa_nomi_settimane[settimana_scelta_pulita]

    # 2. FILTRAGGIO DEI FREQUENTANTI
    condizione_frequenza = (
        df_iscritti[col_settimana_scelta].notna() & 
        (df_iscritti[col_settimana_scelta].astype(str).str.strip() != "") &
        (df_iscritti[col_settimana_scelta].astype(str).str.strip().str.lower() != "non frequenta")
    )
    df_settimana = df_iscritti[condizione_frequenza].copy()
    tot_bambini = len(df_settimana)
    
    # Mostriamo il contatore di fianco (usiamo le colonne di Streamlit solo per la grafica)
    c1, c2 = st.columns([2, 2])
    with c2:
        st.metric(label=f"Totale iscritti in questa settimana", value=f"{tot_bambini} Bambini")

    st.markdown("---")

    if tot_bambini == 0:
        st.info(f"ℹ️ Nessun bambino iscritto o nessuna frequenza inserita per la settimana selezionata.")
        return

    # 3. COSTRUZIONE DELLA TABELLA A SCHERMO
    mappa_colonne_finali = [
        (col_cognome, "Cognome"),
        (col_nome, "Nome"),
        (col_settimana_scelta, "Tipo Frequenza"),
        (col_allergie, "Allergie"),
        (col_quali, "Dettaglio Allergie / Note"),
        (col_g_tel, "Telefono Genitore")
    ]
    
    # ======= SUPER ISPEZIONE RADAR =======
    st.warning("🕵️‍♂️ Diagnosi Radar delle Variabili Ricevute:")
    for valore, nome_vista in mappa_colonne_finali:
        st.write(f"- **{nome_vista}**: Valore: `{valore}` | Tipo: `{type(valore).__name__}`")
    # ======================================
    
    # Controllo di sicurezza preventivo
    errori_mappatura = []
    colonne_valide = []
    nomi_interfaccia = []
    
    for col_excel, nome_vista in mappa_colonne_finali:
        # Se la colonna non è una stringa o non esiste nell'Excel, la tracciamo
        if str(col_excel).strip() not in [str(c).strip() for c in df_settimana.columns]:
            errori_mappatura.append(f"'{col_excel}' ({nome_vista})")
        else:
            colonne_valide.append(col_excel)
            nomi_interfaccia.append(nome_vista)
            
    if errori_mappatura:
        st.error("🚨 Errore di allineamento colonne nel config.json!")
        st.write("**Colonne non trovate dal sistema:**")
        st.json(errori_mappatura)
        
        with st.expander("👀 Clicca qui per vedere l'elenco reale di TUTTE le colonne presenti nel tuo Excel"):
            st.write(list(df_iscritti.columns))
        return

    # Estrazione e rinomina sicura
    df_vista_settimanale = df_settimana[colonne_valide].copy()
    df_vista_settimanale.columns = nomi_interfaccia
    
    # Ordinamento alfabetico
    df_vista_settimanale = df_vista_settimanale.sort_values(by=["Cognome", "Nome"]).reset_index(drop=True)
    df_vista_settimanale.index += 1
    
    st.markdown(f"#### 📋 Elenco Frequentanti — *{settimana_scelta_pulita}*")
    
    # Evidenzia allergie
    def evidenzia_allergie(row):
        if str(row["Allergie"]).strip().upper() in ["SÌ", "SI", "YES", "TRUE"]:
            return ['background-color: #fef2f2; color: #991b1b; font-weight: 500;'] * len(row)
        return [''] * len(row)
        
    styled_df = df_vista_settimanale.style.apply(evidenzia_allergie, axis=1)
    st.dataframe(styled_df, use_container_width=True)
    
    # 4. ESPORTAZIONE EXCEL
    st.markdown("### 📥 Esporta Registro")
    df_appello = df_vista_settimanale[["Cognome", "Nome", "Tipo Frequenza", "Dettaglio Allergie / Note", "Telefono Genitore"]].copy()
    for giorno in ["LUN", "MAR", "MER", "GIO", "VEN"]:
        df_appello[giorno] = ""
        
    try:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_appello.to_excel(writer, index=True, index_label="N°", sheet_name="Appello")
        
        st.download_button(
            label=f"📄 Scarica Foglio Appello Excel - {settimana_scelta_pulita}",
            data=buffer.getvalue(),
            file_name=f"Appello_{settimana_scelta_pulita.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Errore nella generazione dell'export: {e}")