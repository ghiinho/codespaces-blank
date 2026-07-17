import streamlit as st
import pandas as pd
import io

def mostra_elenchi_settimanali(df_iscritti, col_cf, col_cognome, col_nome, col_allergie, col_quali, col_g_tel, prefisso_settimane):
    st.markdown("## 📅 Elenchi Settimanali e Appello")
    st.markdown("Seleziona una settimana per visualizzare i bambini frequentanti e scaricare il registro presenze.")

    # 1. RILEVAZIONE AUTOMATICA E BLINDATA DELLE SETTIMANE
    # Filtriamo le colonne assicurandoci di ignorare i valori nulli (NaN) e convertendo tutto in testo in sicurezza
    prefisso_ricerca = str(prefisso_settimane).strip()
    colonne_settimane_reali = [
        str(col).strip() for col in df_iscritti.columns 
        if pd.notna(col) and str(col).strip().startswith(prefisso_ricerca)
    ]

    if not colonne_settimane_reali:
        st.error(f"⚠️ Non è stato possibile rilevare le colonne delle settimane nel file Excel.")
        return

    # CREAZIONE DELLE ETICHETTE PULITE PER IL MENU A TENDINA
    # Puliamo il nome eliminando il prefisso noioso: "Iscrizione - Settimana 1 (15-19 Giu)" -> "Settimana 1 (15-19 Giu)"
    mappa_nomi_settimane = {col.replace(f"{prefisso_settimane} ", ""): col for col in colonne_settimane_reali}
    
    # Ordiniamo le settimane per mostrarle in ordine cronologico nel menu
    lista_settimane_pulite = sorted(list(mappa_nomi_settimane.keys()))

    # Riga di controllo in alto (Filtro + Contatore)
    c_filtro1, c_filtro2 = st.columns([2, 2])
    
    with c_filtro1:
        settimana_scelta_pulita = st.selectbox(
            "📆 Seleziona la settimana da visualizzare:", 
            options=lista_settimane_pulite,
            help="Il sistema mostra solo le settimane configurate nel modulo d'iscrizione."
        )
    
    # Recuperiamo il nome reale della colonna nell'Excel (quello lungo di Google Moduli)
    colonna_excel_effettiva = mappa_nomi_settimane[settimana_scelta_pulita]
    
    # 2. FILTRAGGIO INTELLIGENTE DEI FREQUENTANTI
    # Escludiamo i vuoti e chi ha esplicitamente risposto "Non frequenta"
    condizione_frequenza = (
        df_iscritti[colonna_excel_effettiva].notna() & 
        (df_iscritti[colonna_excel_effettiva].astype(str).str.strip() != "")
    )
    df_settimana = df_iscritti[condizione_frequenza].copy()
    tot_bambini = len(df_settimana)
    
    with c_filtro2:
        st.metric(label=f"Totale iscritti in {settimana_scelta_pulita}", value=f"{tot_bambini} Bambini")

    st.markdown("---")

    if tot_bambini == 0:
        st.info(f"ℹ️ Nessun bambino iscritto o nessuna frequenza inserita per la **{settimana_scelta_pulita}**.")
    else:
        # 3. PREPARAZIONE DATAFRAME DI VISUALIZZAZIONE (Incluso Codice Fiscale)
        colonne_visualizzazione = {
            col_cf: "Codice Fiscale",
            col_cognome: "Cognome",
            col_nome: "Nome",
            colonna_excel_effettiva: "Tipo Frequenza",
            col_allergie: "Allergie",
            col_quali: "Dettaglio Allergie / Note",
            col_g_tel: "Telefono Genitore"
        }

        # Estraiamo solo le colonne che ci servono davvero per lo schermo
        df_vista_settimanale = df_settimana[list(colonne_visualizzazione.keys())].rename(columns=colonne_visualizzazione)
        df_vista_settimanale = df_vista_settimanale.sort_values(by=["Cognome", "Nome"]).reset_index(drop=True)
        df_vista_settimanale.index += 1  # Numerazione elenco da 1
        
        st.markdown(f"#### 📋 Elenco Frequentanti — *{settimana_scelta_pulita}*")
        
        # 4. FUNZIONE PER EVIDENZIARE LE ALLERGIE
        def evidenzia_allergie(row):
            if str(row["Allergie"]).strip().upper() in ["SÌ", "SI", "YES", "TRUE"]:
                return ['background-color: #fef2f2; color: #991b1b; font-weight: 500;'] * len(row)
            return [''] * len(row)
            
        styled_df = df_vista_settimanale.style.apply(evidenzia_allergie, axis=1)
        st.dataframe(styled_df, use_container_width=True)
        
        # 5. GENERAZIONE FILE EXCEL PER L'APPELLO CARTACEO (Senza codice fiscale per la privacy dei ragazzi sul campo)
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