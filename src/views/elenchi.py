import streamlit as st
import pandas as pd
import io

def mostra_elenchi_settimanali(df_iscritti, col_cognome, col_nome, col_allergie, col_quali, col_g_tel):
    st.markdown("## 📅 Elenchi Settimanali e Appello")
    st.markdown("Seleziona una settimana per visualizzare i bambini frequentanti e scaricare il registro presenze.")

    # 1. Rilevazione automatica delle colonne settimane (dalla S alla AD -> indici 18:30)
    colonne_settimane = list(df_iscritti.columns[18:30])

    if len(colonne_settimane) == 0:
        st.error("⚠️ Non è stato possibile rilevare le colonne delle settimane nel file Excel.")
        return

    # Riga di controllo in alto (Filtro + Contatore)
    c_filtro1, c_filtro2 = st.columns([2, 2])
    
    with c_filtro1:
        settimana_scelta = st.selectbox(
            "📆 Seleziona la settimana da visualizzare:", 
            options=colonne_settimane,
            help="Scegli la colonna corrispondente alla settimana di interesse"
        )
    
    # 2. Filtraggio dei frequentanti
    condizione_frequenza = (
        df_iscritti[settimana_scelta].notna() & 
        (df_iscritti[settimana_scelta].astype(str).str.strip() != "")
    )
    df_settimana = df_iscritti[condizione_frequenza].copy()
    tot_bambini = len(df_settimana)
    
    with c_filtro2:
        st.metric(label=f"Totale iscritti in {settimana_scelta}", value=f"{tot_bambini} Bambini")

    st.markdown("---")

    if tot_bambini == 0:
        st.info(f"ℹ️ Nessun bambino iscritto o nessuna frequenza inserita per la colonna **{settimana_scelta}**.")
    else:
        # 3. Preparazione DataFrame di visualizzazione
        colonne_visualizzazione = {
            col_cognome: "Cognome",
            col_nome: "Nome",
            settimana_scelta: "Tipo Frequenza",
            col_allergie: "Allergie",
            col_quali: "Dettaglio Allergie / Note",
            col_g_tel: "Telefono Genitore"
        }
        
        df_vista_settimanale = df_settimana[list(colonne_visualizzazione.keys())].rename(columns=colonne_visualizzazione)
        df_vista_settimanale = df_vista_settimanale.sort_values(by=["Cognome", "Nome"]).reset_index(drop=True)
        df_vista_settimanale.index += 1  # Numerazione elenco da 1
        
        st.markdown(f"#### 📋 Elenco Frequentanti — *{settimana_scelta}*")
        
        # 4. Funzione per evidenziare visivamente le allergie in rosso soft
        def evidenzia_allergie(row):
            if str(row["Allergie"]).strip().upper() in ["SÌ", "SI", "YES", "TRUE"]:
                return ['background-color: #fef2f2; color: #991b1b; font-weight: 500;'] * len(row)
            return [''] * len(row)
            
        styled_df = df_vista_settimanale.style.apply(evidenzia_allergie, axis=1)
        st.dataframe(styled_df, use_container_width=True)
        
        # 5. Generazione file Excel per l'appello cartaceo
        st.markdown("### 📥 Esporta Registro")
        
        df_appello = df_vista_settimanale[["Cognome", "Nome", "Tipo Frequenza", "Dettaglio Allergie / Note", "Telefono Genitore"]].copy()
        for giorno in ["LUN", "MAR", "MER", "GIO", "VEN"]:
            df_appello[giorno] = ""
            
        try:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_appello.to_excel(writer, index=True, index_label="N°", sheet_name="Appello")
            
            st.download_button(
                label="📄 Scarica Foglio Appello (Excel con giorni LUN-VEN)",
                data=buffer.getvalue(),
                file_name=f"Appello_{settimana_scelta.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Errore nella generazione dell'export: {e}")