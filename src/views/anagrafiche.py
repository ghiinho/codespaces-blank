import streamlit as st
import pandas as pd

def mostra_anagrafiche(df_iscritti):
    st.title("👤 Ricerca e Gestione Anagrafiche")
    st.write("Visualizza, modifica o aggiorna i dati personali, sanitari e i contatti di ciascun iscritto.")
    st.markdown("---")
    
    if df_iscritti.empty:
        st.info("Carica il file Excel per abilitare la gestione anagrafica.")
        return

    # --- MAPPATURA COLONNE ---
    colonne_reali = list(df_iscritti.columns)
    id_colonna = colonne_reali[0] # ID/Timestamp o prima colonna univoca
    
    # Genitore (B - G)
    col_g_email = colonne_reali[1]
    col_g_cognome = colonne_reali[2]
    col_g_nome = colonne_reali[3]
    col_g_tel = colonne_reali[4]
    col_g_nascita = colonne_reali[5]
    col_g_cf = colonne_reali[6]

    # Bambino (H - R)
    col_cognome = colonne_reali[7]
    col_nome = colonne_reali[8]
    col_nascita = colonne_reali[9]
    col_luogo = colonne_reali[10]
    col_via = colonne_reali[11]
    col_civico = colonne_reali[12]
    col_cap = colonne_reali[13]
    col_citta = colonne_reali[14]
    col_cf = colonne_reali[15]
    col_allergie = colonne_reali[16]
    col_quali = colonne_reali[17]

    # Settimane (Dinamica)
    colonne_settimane = [col for col in colonne_reali if "settiman" in str(col).lower()]

    # --- STATO DELLA RICERCA ---
    if "id_bambino_corrente" not in st.session_state:
        st.session_state.id_bambino_corrente = None
    if "risultato_ricerca" not in st.session_state:
        st.session_state.risultato_ricerca = None
    if "scheda_attiva" not in st.session_state:
        st.session_state.scheda_attiva = "bambino"
    if "modalita_modifica" not in st.session_state:
        st.session_state.modalita_modifica = False

    # --- MOTORE DI RICERCA ---
    col_ricerca, col_bottone = st.columns([4, 1])
    with col_ricerca:
        cognome_input = st.text_input(
            "🔍 Cerca iscritto per Cognome:", 
            placeholder="Scrivi il cognome...",
            key="ricerca_cognome"
        )
    with col_bottone:
        st.write("##")
        avvia_ricerca = st.button("Cerca 🚀", use_container_width=True)

    if avvia_ricerca and cognome_input:
        risultati = df_iscritti[df_iscritti[col_cognome].astype(str).str.lower().str.contains(cognome_input.strip().lower())]
        st.session_state.risultato_ricerca = risultati
        st.session_state.modalita_modifica = False # Resetta lo stato di modifica
        if not risultati.empty:
            st.session_state.id_bambino_corrente = risultati.index[0]
            st.session_state.scheda_attiva = "bambino"

    # --- GESTIONE DEI RISULTATI ---
    if st.session_state.risultato_ricerca is not None:
        df_filtrato = st.session_state.risultato_ricerca
        
        if df_filtrato.empty:
            st.warning(f"❌ Nessun iscritto trovato con il cognome '{cognome_input}'.")
            return

        # Gestione omonimie
        if len(df_filtrato) > 1:
            st.success(f"📋 Trovati {len(df_filtrato)} iscritti corrispondenti.")
            scelte = df_filtrato[col_cognome].astype(str) + " " + df_filtrato[col_nome].astype(str) + " (" + df_filtrato[col_cf].astype(str) + ")"
            
            default_index = 0
            if st.session_state.id_bambino_corrente in df_filtrato.index:
                default_index = list(df_filtrato.index).index(st.session_state.id_bambino_corrente)
                
            bambino_scelto = st.radio("Seleziona l'iscritto corretto:", scelte, index=default_index)
            nuovo_id = scelte[scelte == bambino_scelto].index[0]
            if nuovo_id != st.session_state.id_bambino_corrente:
                st.session_state.id_bambino_corrente = nuovo_id
                st.session_state.modalita_modifica = False
                st.rerun()
        
        elif len(df_filtrato) == 1 and st.session_state.id_bambino_corrente not in df_filtrato.index:
            st.session_state.id_bambino_corrente = df_filtrato.index[0]

        # Estrazione della riga corrente
        riga_bambino = df_iscritti.loc[st.session_state.id_bambino_corrente]
        riga_index = st.session_state.id_bambino_corrente
        
        nome_completo_bambino = f"{riga_bambino[col_cognome]} {riga_bambino[col_nome]}".upper()
        nome_completo_genitore = f"{riga_bambino[col_g_cognome]} {riga_bambino[col_g_nome]}".upper()
        
        # Logica Fratelli
        cf_genitore_corrente = riga_bambino[col_g_cf]
        email_genitore_corrente = riga_bambino[col_g_email]
        fratelli = df_iscritti[
            ((df_iscritti[col_g_cf] == cf_genitore_corrente) & (pd.notnull(df_iscritti[col_g_cf]))) |
            ((df_iscritti[col_g_email] == email_genitore_corrente) & (pd.notnull(df_iscritti[col_g_email])))
        ]
        fratelli = fratelli.drop(st.session_state.id_bambino_corrente, errors='ignore')

        # --- MENU NAVIGAZIONE SCHEDE ---
        col_tab1, col_tab2, col_tab3 = st.columns(3)
        with col_tab1:
            tipo_b = "primary" if st.session_state.scheda_attiva == "bambino" else "secondary"
            if st.button("👦 Dati Bambino", type=tipo_b, use_container_width=True):
                st.session_state.scheda_attiva = "bambino"
                st.session_state.modalita_modifica = False
                st.rerun()
        with col_tab2:
            tipo_g = "primary" if st.session_state.scheda_attiva == "genitore" else "secondary"
            if st.button("👨‍👩‍👧 Contatti Genitore", type=tipo_g, use_container_width=True):
                st.session_state.scheda_attiva = "genitore"
                st.session_state.modalita_modifica = False
                st.rerun()
        with col_tab3:
            tipo_s = "primary" if st.session_state.scheda_attiva == "settimane" else "secondary"
            if st.button("📅 Settimane Iscrizione", type=tipo_s, use_container_width=True):
                st.session_state.scheda_attiva = "settimane"
                st.session_state.modalita_modifica = False
                st.rerun()

        st.markdown("---")

        # --- AZIONI RAPIDE ---
        col_st_nome, col_st_azioni = st.columns([3, 1])
        with col_st_nome:
            st.subheader(f"📍 {nome_completo_bambino}")
        with col_st_azioni:
            if st.session_state.scheda_attiva != "settimane":
                if not st.session_state.modalita_modifica:
                    if st.button("📝 Modifica Dati", use_container_width=True, type="secondary"):
                        st.session_state.modalita_modifica = True
                        st.rerun()
                else:
                    if st.button("❌ Annulla Modifica", use_container_width=True, type="primary"):
                        st.session_state.modalita_modifica = False
                        st.rerun()

        # ==========================================
        # 1. TAB: BAMBINO
        # ==========================================
        if st.session_state.scheda_attiva == "bambino":
            if st.session_state.modalita_modifica:
                # FORM DI MODIFICA
                with st.form("form_modifica_bambino"):
                    st.markdown("#### 📝 Modifica Anagrafica e Sanitari Bambino")
                    
                    e_cognome = st.text_input("Cognome", value=str(riga_bambino[col_cognome]))
                    e_nome = st.text_input("Nome", value=str(riga_bambino[col_nome]))
                    e_cf = st.text_input("Codice Fiscale", value=str(riga_bambino[col_cf]).upper())
                    
                    c_nasc1, c_nasc2 = st.columns(2)
                    with c_nasc1:
                        e_luogo = st.text_input("Luogo di Nascita", value=str(riga_bambino[col_luogo]))
                    with c_nasc2:
                        e_nascita = st.text_input("Data di Nascita (GG/MM/AAAA o AAAA-MM-DD)", value=str(riga_bambino[col_nascita]))
                    
                    c_res1, c_res2, c_res3, c_res4 = st.columns([3, 1, 1, 2])
                    with c_res1:
                        e_via = st.text_input("Via/Piazza", value=str(riga_bambino[col_via]))
                    with c_res2:
                        e_civico = st.text_input("Civico", value=str(riga_bambino[col_civico]))
                    with c_res3:
                        e_cap = st.text_input("CAP", value=str(riga_bambino[col_cap]))
                    with c_res4:
                        e_citta = st.text_input("Città", value=str(riga_bambino[col_citta]))
                    
                    st.markdown("---")
                    st.markdown("##### 🩺 Informazioni Sanitarie")
                    e_allergie = st.selectbox("Allergie/Intolleranze?", ["SÌ", "NO"], index=0 if str(riga_bambino[col_allergie]).strip().upper() in ["SÌ", "SI", "YES", "TRUE"] else 1)
                    e_quali = st.text_area("Se sì, specificare quali allergie o farmaci salvavita:", value=str(riga_bambino[col_quali]) if pd.notnull(riga_bambino[col_quali]) else "")
                    
                    salva_bambino = st.form_submit_button("💾 Salva Modifiche Anagrafica", use_container_width=True, type="primary")
                    
                    if salva_bambino:
                        df_iscritti.at[riga_index, col_cognome] = e_cognome
                        df_iscritti.at[riga_index, col_nome] = e_nome
                        df_iscritti.at[riga_index, col_cf] = e_cf
                        df_iscritti.at[riga_index, col_luogo] = e_luogo
                        df_iscritti.at[riga_index, col_nascita] = e_nascita
                        df_iscritti.at[riga_index, col_via] = e_via
                        df_iscritti.at[riga_index, col_civico] = e_civico
                        df_iscritti.at[riga_index, col_cap] = e_cap
                        df_iscritti.at[riga_index, col_citta] = e_citta
                        df_iscritti.at[riga_index, col_allergie] = e_allergie
                        df_iscritti.at[riga_index, col_quali] = e_quali if e_allergie == "SÌ" else ""
                        
                        try:
                            df_iscritti.to_excel("iscritti.xlsx", index=False)
                            st.success("✅ Dati del bambino aggiornati con successo!")
                            st.session_state.modalita_modifica = False
                            st.session_state.risultato_ricerca = df_iscritti.loc[[riga_index]]
                            st.rerun()
                        except Exception as e:
                            st.error(f"Errore durante il salvataggio: {e}")
            else:
                # VISTA STATICA
                box_anagrafica, box_residenza, box_sanitario = st.columns(3)
                with box_anagrafica:
                    st.markdown("#### 👤 Identità")
                    cf_pulito = str(riga_bambino[col_cf]).strip().upper() if pd.notnull(riga_bambino[col_cf]) else "Dato mancante"
                    st.markdown(
                        f"""
                        <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; min-height: 220px;">
                            <p style="margin-bottom: 8px; font-size: 15px;"><b>Cognome:</b><br>{riga_bambino[col_cognome]}</p>
                            <p style="margin-bottom: 8px; font-size: 15px;"><b>Nome:</b><br>{riga_bambino[col_nome]}</p>
                            <p style="margin-bottom: 0; font-size: 15px;"><b>Codice Fiscale:</b><br><span style="color: #0f172a; font-weight: 600;">{cf_pulito}</span></p>
                        </div>
                        """, unsafe_allow_html=True
                    )
                
                with box_residenza:
                    st.markdown("#### 📍 Nascita e Residenza")
                    data_nascita_val = riga_bambino[col_nascita]
                    data_nascita_str = pd.to_datetime(data_nascita_val).strftime('%d/%m/%Y') if pd.notnull(data_nascita_val) and not isinstance(data_nascita_val, str) else str(data_nascita_val)
                    indirizzo_completo = f"{riga_bambino[col_via]}, {riga_bambino[col_civico]}"
                    citta_completa = f"{riga_bambino[col_cap]} - {riga_bambino[col_citta]}"
                    st.markdown(
                        f"""
                        <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; min-height: 220px;">
                            <p style="margin-bottom: 8px;"><b>Nato/a il:</b> {data_nascita_str}<br><b>a:</b> {riga_bambino[col_luogo]}</p>
                            <p style="margin-bottom: 8px;"><b>Indirizzo:</b><br>{indirizzo_completo}</p>
                            <p style="margin-bottom: 0;"><b>Città:</b><br>{citta_completa}</p>
                        </div>
                        """, unsafe_allow_html=True
                    )
                
                with box_sanitario:
                    st.markdown("#### ⚠️ Informazioni Sanitarie")
                    ha_allergie = str(riga_bambino[col_allergie]).strip().upper()
                    if ha_allergie in ["SÌ", "SI", "YES", "Vero", "TRUE"]:
                        colore_sfondo, colore_bordo, icona = "#fef2f2", "#f87171", "🚨"
                        dettaglio = f"<b>Quali:</b><br><span style='color: #b91c1c; font-weight: bold;'>{riga_bambino[col_quali]}</span>"
                    else:
                        colore_sfondo, colore_bordo, icona = "#f0fdf4", "#4ade80", "✅"
                        dettaglio = "<i>Nessuna allergia o intolleranza segnalata.</i>"
                    st.markdown(
                        f"""
                        <div style="background-color: {colore_sfondo}; padding: 15px; border-radius: 8px; border: 1px solid {colore_bordo}; min-height: 220px;">
                            <p style="font-size: 16px; margin-bottom: 12px;"><b>Stato:</b> {icona} {ha_allergie}</p>
                            <p style="margin-bottom: 0; font-size: 14px;">{dettaglio}</p>
                        </div>
                        """, unsafe_allow_html=True
                    )

        # ==========================================
        # 2. TAB: GENITORE & FAMIGLIA
        # ==========================================
        elif st.session_state.scheda_attiva == "genitore":
            if st.session_state.modalita_modifica:
                # FORM DI MODIFICA GENITORE
                with st.form("form_modifica_genitore"):
                    st.markdown("#### 📝 Modifica Dati Contatto Genitore")
                    e_g_cognome = st.text_input("Cognome Genitore", value=str(riga_bambino[col_g_cognome]))
                    e_g_nome = st.text_input("Nome Genitore", value=str(riga_bambino[col_g_nome]))
                    e_g_cf = st.text_input("Codice Fiscale Genitore", value=str(riga_bambino[col_g_cf]).upper())
                    
                    c_gen1, c_gen2 = st.columns(2)
                    with c_gen1:
                        e_g_tel = st.text_input("Telefono", value=str(riga_bambino[col_g_tel]))
                    with c_gen2:
                        e_g_email = st.text_input("Email", value=str(riga_bambino[col_g_email]))
                    
                    e_g_nascita = st.text_input("Data di Nascita Genitore", value=str(riga_bambino[col_g_nascita]))
                    
                    salva_genitore = st.form_submit_button("💾 Salva Modifiche Genitore", use_container_width=True, type="primary")
                    
                    if salva_genitore:
                        # Aggiorniamo la riga singola
                        df_iscritti.at[riga_index, col_g_cognome] = e_g_cognome
                        df_iscritti.at[riga_index, col_g_nome] = e_g_nome
                        df_iscritti.at[riga_index, col_g_cf] = e_g_cf
                        df_iscritti.at[riga_index, col_g_tel] = e_g_tel
                        df_iscritti.at[riga_index, col_g_email] = e_g_email
                        df_iscritti.at[riga_index, col_g_nascita] = e_g_nascita
                        
                        # Se ha altri figli, opzione comoda di aggiornare i contatti per tutti i fratelli automaticamente!
                        se_fratelli = df_iscritti[df_iscritti[col_g_cf] == cf_genitore_corrente].index
                        if len(se_fratelli) > 1:
                            for idx_f in se_fratelli:
                                df_iscritti.at[idx_f, col_g_tel] = e_g_tel
                                df_iscritti.at[idx_f, col_g_email] = e_g_email
                        
                        try:
                            df_iscritti.to_excel("iscritti.xlsx", index=False)
                            st.success("✅ Contatti della famiglia aggiornati (e allineati per eventuali fratelli)!")
                            st.session_state.modalita_modifica = False
                            st.session_state.risultato_ricerca = df_iscritti.loc[[riga_index]]
                            st.rerun()
                        except Exception as e:
                            st.error(f"Errore durante il salvataggio: {e}")
            else:
                # VISTA STATICA GENITORE
                tel_g_grezzo = str(riga_bambino[col_g_tel])
                tel_g_pulito = tel_g_grezzo.replace(" ", "").replace("/", "").replace("-", "").strip()
                if tel_g_pulito.endswith(".0"): tel_g_pulito = tel_g_pulito[:-2]

                data_n_g_val = riga_bambino[col_g_nascita]
                data_n_g_str = pd.to_datetime(data_n_g_val).strftime('%d/%m/%Y') if pd.notnull(data_n_g_val) and not isinstance(data_n_g_val, str) else str(data_n_g_val)
                cf_g_pulito = str(riga_bambino[col_g_cf]).strip().upper() if pd.notnull(riga_bambino[col_g_cf]) else "Dato mancante"
                
                g_col1, g_col2 = st.columns(2)
                with g_col1:
                    st.markdown("#### 👤 Dati Personali Genitore")
                    st.markdown(
                        f"""
                        <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; min-height: 180px;">
                            <p style="margin-bottom: 10px; font-size: 15px;"><b>Nominativo:</b> {nome_completo_genitore}</p>
                            <p style="margin-bottom: 10px; font-size: 15px;"><b>Data di Nascita:</b> {data_n_g_str}</p>
                            <p style="margin-bottom: 0; font-size: 15px;"><b>Codice Fiscale:</b> <span style="font-weight: 600;">{cf_g_pulito}</span></p>
                        </div>
                        """, unsafe_allow_html=True
                    )
                    
                with g_col2:
                    st.markdown("#### 📞 Contatti Rapidi")
                    st.markdown(
                        f"""
                        <div style="background-color: #f0fdfa; padding: 20px; border-radius: 8px; border: 1px solid #99f6e4; min-height: 180px;">
                            <p style="margin-bottom: 12px; font-size: 16px; color: #0d9488;"><b>Riferimenti di Emergenza:</b></p>
                            <p style="margin-bottom: 10px; font-size: 15px;"><b>📞 Telefono:</b> <a href="tel:{tel_g_pulito}" style="font-weight: bold; color: #0f172a; text-decoration: none;">{tel_g_pulito}</a></p>
                            <p style="margin-bottom: 0; font-size: 15px;"><b>✉️ Email:</b> <a href="mailto:{riga_bambino[col_g_email]}" style="font-weight: bold; color: #0d9488;">{riga_bambino[col_g_email]}</a></p>
                        </div>
                        """, unsafe_allow_html=True
                    )
                
                # Visualizzazione Fratelli
                if not fratelli.empty:
                    st.markdown("---")
                    st.markdown("### 👦 Altri figli iscritti a carico di questo genitore:")
                    for idx_fratello, riga_fratello in fratelli.iterrows():
                        nome_fratello = f"{riga_fratello[col_cognome]} {riga_fratello[col_nome]}".upper()
                        btn_col1, btn_col2 = st.columns([3, 1])
                        with btn_col1:
                            st.write(f"🧑‍🤝‍🧑 **{nome_fratello}** (Codice Fiscale: `{riga_fratello[col_cf]}`)")
                        with btn_col2:
                            if st.button(f"Vedi scheda di {riga_fratello[col_nome]} 📂", key=f"btn_fratello_{idx_fratello}"):
                                st.session_state.id_bambino_corrente = idx_fratello
                                st.session_state.scheda_attiva = "bambino"
                                st.rerun()

        # ==========================================
        # 3. TAB: SETTIMANE
        # ==========================================
        elif st.session_state.scheda_attiva == "settimane":
            st.markdown(f"### 📅 Gestione Iscrizioni Settimanali")
            st.write("Seleziona il tipo di iscrizione per ciascuna settimana e salva.")

            if colonne_settimane:
                opzioni_frequenza = ["NON ISCRITTO ❌", "GIORNATA INTERA", "MATTINO + PRANZO", "SOLO MATTINO"]

                with st.form("form_modifica_settimane"):
                    col_cards = st.columns(4)
                    nuovi_valori = {}

                    for i, col_settimana in enumerate(colonne_settimane):
                        valore_grezzo = riga_bambino[col_settimana]
                        valore_cella = str(valore_grezzo).strip() if pd.notnull(valore_grezzo) else ""
                        
                        nome_pulito = col_settimana.replace("SETTIMANE DISPONIBILI", "").strip()
                        if not nome_pulito: nome_pulito = col_settimana

                        indice_default = opzioni_frequenza.index(valore_cella) if valore_cella in opzioni_frequenza else 0
                        col_index = i % 4
                        
                        with col_cards[col_index]:
                            colore_b_s, colore_f_s = ("#10b981", "#f0fdf4") if indice_default > 0 else ("#cbd5e1", "#f8fafc")
                            st.markdown(
                                f"""
                                <div style="background-color: {colore_f_s}; border-top: 4px solid {colore_b_s}; padding: 10px; border-radius: 6px 6px 0 0; text-align: center;">
                                    <span style="font-weight: bold; font-size: 13px; color: #1e293b;">{nome_pulito}</span>
                                </div>
                                """, unsafe_allow_html=True
                            )
                            scelta = st.selectbox(
                                label=f"Stato {nome_pulito}",
                                options=opzioni_frequenza,
                                index=indice_default,
                                key=f"sel_{col_settimana}",
                                label_visibility="collapsed"
                            )
                            nuovi_valori[col_settimana] = scelta

                    st.markdown("---")
                    salva_settimane = st.form_submit_button("💾 Salva Settimane", type="primary", use_container_width=True)
                    
                    if salva_settimane:
                        for col_settimana, valore in nuovi_valori.items():
                            val_salva = None if valore == "NON ISCRITTO ❌" else valore
                            df_iscritti.at[riga_index, col_settimana] = val_salva
                        
                        try:
                            df_iscritti.to_excel("gestionale.xlsx", index=False)
                            st.success("✅ Settimane di frequenza salvate correttamente!")
                            st.session_state.risultato_ricerca = df_iscritti.loc[[riga_index]]
                            st.rerun()
                        except Exception as e:
                            st.error(f"Errore durante il salvataggio: {e}")