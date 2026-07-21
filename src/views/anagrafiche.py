import streamlit as st
import pandas as pd

from src.utils.config_manager import carica_configurazione
import database_utils as db_utils

# Riduzione spazi verticali nativi di Streamlit
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
        }
        .stVerticalBlock {
            gap: 0.5rem !important;
        }
        hr {
            margin: 0.8rem 0 !important;
        }
        h1, h2, h3, h4 {
            margin-bottom: 0.2rem !important;
            padding-bottom: 0 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

def mostra_anagrafiche(df_iscritti):
    st.title("👤 Ricerca e Gestione Anagrafiche")
    st.write("Visualizza, modifica o aggiorna i dati personali, sanitari e i contatti di ciascun iscritto.")
    
    if df_iscritti.empty:
        st.info("Nessun iscritto presente nel database. Carica un file per abilitare la gestione.")
        return

    df_iscritti = df_iscritti.astype(object)
    df_iscritti.fillna("", inplace=True)

    # --- INIZIALIZZAZIONE STATO ---
    if "id_bambino_corrente" not in st.session_state:
        st.session_state.id_bambino_corrente = None
    if "risultato_ricerca" not in st.session_state:
        st.session_state.risultato_ricerca = None
    if "scheda_attiva" not in st.session_state:
        st.session_state.scheda_attiva = "bambino"
    if "modalita_modifica" not in st.session_state:
        st.session_state.modalita_modifica = False

    # --- MAPPATURA COLONNE ---
    config = carica_configurazione()
    mapping = config.get("mappatura_colonne", {})
    colonne_reali = list(df_iscritti.columns)
    
    id_colonna = colonne_reali[0]

    # Helper recupero sicuro colonne
    def recupera_colonna_valida(nome_cercato, indice_fallback):
        if nome_cercato in colonne_reali:
            return nome_cercato
        if len(colonne_reali) > indice_fallback:
            return colonne_reali[indice_fallback]
        return nome_cercato

    # Mappatura Dati Genitore
    col_g_email = recupera_colonna_valida(mapping.get("email_genitore", "INDIRIZZO EMAIL"), 1)
    col_g_cognome = recupera_colonna_valida(mapping.get("cognome_genitore", "COGNOME GENITORE"), 2)
    col_g_nome = recupera_colonna_valida(mapping.get("nome_genitore", "NOME GENITORE"), 3)
    col_g_tel = recupera_colonna_valida(mapping.get("recapito", "TELEFONO GENITORE"), 4)
    col_g_nascita = recupera_colonna_valida(mapping.get("data_nascita_genitore", "DATA DI NASCITA GENITORE"), 5)
    col_g_cf = recupera_colonna_valida(mapping.get("cf_genitore", "CODICE FISCALE GENITORE"), 6)

    # Mappatura Dati Bambino
    col_cognome = recupera_colonna_valida(mapping.get("cognome", "COGNOME MINORE"), 7)
    col_nome = recupera_colonna_valida(mapping.get("nome", "NOME MINORE"), 8)
    col_nascita = recupera_colonna_valida(mapping.get("data_nascita", "DATA DI NASCITA MINORE"), 9)
    col_luogo = recupera_colonna_valida(mapping.get("luogo_nascita", "LUOGO DI NASCITA MINORE"), 10)
    col_via = recupera_colonna_valida(mapping.get("indirizzo", "INDIRIZZO DI RESIDENZA"), 11)
    col_civico = recupera_colonna_valida(mapping.get("civico", "N. CIVICO"), 12)
    col_cap = recupera_colonna_valida(mapping.get("cap", "CAP"), 13)
    col_citta = recupera_colonna_valida(mapping.get("citta", "CITTA'"), 14)
    col_cf = recupera_colonna_valida(mapping.get("codice_fiscale", "CODICE FISCALE MINORE"), 15)
    col_allergie = recupera_colonna_valida(mapping.get("allergie", "ALLERGIE O INTOLLERANZE?"), 16)
    col_quali = recupera_colonna_valida(mapping.get("note_allergie", "SE SI, INDICA QUALI"), 17)

    # Rilevamento Settimane
    prefisso = str(config.get("prefisso_settimane", "PERIODI DISPONIBILI")).strip().lower()
    colonne_settimane = [
        col for col in colonne_reali 
        if "settiman" in str(col).lower() or prefisso in str(col).lower() or "periodi" in str(col).lower()
    ]

    # ==========================================
    # CREAZIONE TABS PRINCIPALI
    # ==========================================
    tab_ricerca, tab_nuovo = st.tabs(["🔍 Cerca / Modifica Iscritto", "➕ Nuovo Iscritto"])

    # -------------------------------------------------------------------------
    # TAB 1: RICERCA E SCHEDA ISCRITTO
    # -------------------------------------------------------------------------
    with tab_ricerca:
        df_iscritti_ordinato = df_iscritti.sort_values(by=[col_cognome, col_nome])

        opzioni_ricerca = (
            df_iscritti_ordinato[col_cognome].astype(str).str.upper() + " " +
            df_iscritti_ordinato[col_nome].astype(str).str.title() + " (" +
            df_iscritti_ordinato[col_cf].astype(str).str.upper() + ")"
        )

        mappa_opzioni = dict(zip(opzioni_ricerca, df_iscritti_ordinato.index))
        lista_selectbox = list(opzioni_ricerca)
        mappa_indice_a_opzione = {v: k for k, v in mappa_opzioni.items()}

        col_ricerca, _ = st.columns([3, 2])

        def _on_selectbox_change():
            sel = st.session_state.get("ricerca_dinamica_selectbox")
            if sel in mappa_opzioni:
                id_sel = mappa_opzioni.get(sel)
                st.session_state.id_bambino_corrente = id_sel
                st.session_state.risultato_ricerca = df_iscritti.loc[[id_sel]]
                st.session_state.scheda_attiva = "bambino"

        index_corrente = None
        if st.session_state.id_bambino_corrente in mappa_indice_a_opzione:
            stringa_opzione = mappa_indice_a_opzione[st.session_state.id_bambino_corrente]
            if stringa_opzione in lista_selectbox:
                index_corrente = lista_selectbox.index(stringa_opzione)

        with col_ricerca:
            st.selectbox(
                "Cerca un iscritto:",
                options=lista_selectbox,
                index=index_corrente,
                placeholder="🔍 Digita il cognome o nome...",
                key="ricerca_dinamica_selectbox",
                on_change=_on_selectbox_change
            )

        st.markdown("---")

    # -------------------------------------------------------------------------
    # TAB 2: FORM DI CREAZIONE NUOVO ISCRITTO
    # -------------------------------------------------------------------------
    with tab_nuovo:
        st.subheader("➕ Inserimento Rapido Nuovo Iscritto")
        st.caption("Usa questo modulo per registrare un bambino iscritto in loco o fuori dal modulo online.")

        with st.form(key="form_nuovo_iscritto", clear_on_submit=True):
            st.markdown("#### 👶 Dati del Minore")
            col_b1, col_b2, col_b3 = st.columns(3)

            with col_b1:
                nuovo_cognome = st.text_input("Cognome Minore *").strip().upper()
            with col_b2:
                nuovo_nome = st.text_input("Nome Minore *").strip().title()
            with col_b3:
                nuova_data_nascita = st.date_input("Data di Nascita", value=None)

            col_cf_in, _ = st.columns([1, 2])
            with col_cf_in:
                nuovo_cf = st.text_input("Codice Fiscale Minore").strip().upper()

            st.markdown("---")
            st.markdown("#### 👨‍👩‍👧 Dati Genitore / Contatti")
            col_g1, col_g2, col_g3 = st.columns(3)

            with col_g1:
                nuovo_g_cognome = st.text_input("Cognome Genitore").strip().title()
                nuovo_g_nome = st.text_input("Nome Genitore").strip().title()
            with col_g2:
                nuovo_tel = st.text_input("Telefono Genitore").strip()
            with col_g3:
                nuova_email = st.text_input("Email").strip()

            st.markdown("---")
            st.markdown("#### 🩺 Allergie e Note Mediche")
            col_a1, col_a2 = st.columns([1, 2])
            with col_a1:
                ha_allergie = st.selectbox("Ha Allergie / Intolleranze?", ["NO", "SI"])
            with col_a2:
                dettaglio_allergie = st.text_input("Se SI, specifica quali:").strip()

            st.markdown("---")
            st.markdown("#### 🗓️ Iscrizione Settimane")
            settimane_selezionate = {}

            if colonne_settimane:
                cols_sett = st.columns(3)
                for i, col_s in enumerate(colonne_settimane):
                    nome_sett_pulito = str(col_s).replace(prefisso, "").strip(" -[]:")
                    with cols_sett[i % 3]:
                        settimane_selezionate[col_s] = st.checkbox(nome_sett_pulito, key=f"chk_new_{i}")
            else:
                st.info("Nessuna colonna per le settimane trovata nelle impostazioni.")

            btn_salva = st.form_submit_button("💾 Salva e Registra Iscritto", use_container_width=True)

        if btn_salva:
            if not nuovo_cognome or not nuovo_nome:
                st.error("❌ Nome e Cognome del minore sono obbligatori!")
            else:
                nuova_riga = {col: "" for col in df_iscritti.columns}
                nuova_riga[col_cognome] = nuovo_cognome
                nuova_riga[col_nome] = nuovo_nome
                if col_nascita in nuova_riga:
                    nuova_riga[col_nascita] = nuova_data_nascita.strftime("%d/%m/%Y") if nuova_data_nascita else ""
                if col_cf in nuova_riga:
                    nuova_riga[col_cf] = nuovo_cf
                if col_g_cognome in nuova_riga:
                    nuova_riga[col_g_cognome] = nuovo_g_cognome
                if col_g_nome in nuova_riga:
                    nuova_riga[col_g_nome] = nuovo_g_nome
                if col_g_tel in nuova_riga:
                    nuova_riga[col_g_tel] = nuovo_tel
                if col_g_email in nuova_riga:
                    nuova_riga[col_g_email] = nuova_email
                if col_allergie in nuova_riga:
                    nuova_riga[col_allergie] = ha_allergie
                if col_quali in nuova_riga:
                    nuova_riga[col_quali] = dettaglio_allergie if ha_allergie == "SI" else ""

                frequenza_default = list(config.get("tariffe", {}).keys())[0] if config.get("tariffe") else "GIORNATA INTERA"
                for col_s, selezionata in settimane_selezionate.items():
                    if selezionata:
                        nuova_riga[col_s] = frequenza_default

                db_utils.aggiungi_nuovo_iscritto(nuova_riga)
                st.session_state.id_bambino_corrente = len(df_iscritti)
                st.session_state.scheda_attiva = "bambino"
                st.success(f"🎉 **{nuovo_cognome} {nuovo_nome}** aggiunto con successo!")
                st.rerun()

    # ==========================================
    # VISUALIZZAZIONE E GESTIONE DELLA SCHEDA
    # ==========================================
    if st.session_state.id_bambino_corrente is not None and st.session_state.id_bambino_corrente in df_iscritti.index:
        riga_index = st.session_state.id_bambino_corrente
        riga_bambino = df_iscritti.loc[riga_index]

        nome_completo_bambino = f"{riga_bambino[col_cognome]} {riga_bambino[col_nome]}".upper()
        nome_completo_genitore = f"{riga_bambino[col_g_cognome]} {riga_bambino[col_g_nome]}".upper()

        cf_genitore_corrente = riga_bambino[col_g_cf]
        email_genitore_corrente = riga_bambino[col_g_email]
        
        fratelli = df_iscritti[
            ((df_iscritti[col_g_cf] == cf_genitore_corrente) & (pd.notnull(df_iscritti[col_g_cf]) & (df_iscritti[col_g_cf] != ""))) |
            ((df_iscritti[col_g_email] == email_genitore_corrente) & (pd.notnull(df_iscritti[col_g_email]) & (df_iscritti[col_g_email] != "")))
        ].drop(riga_index, errors='ignore')

        # Header Fisso
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 20px 25px; border-radius: 10px; margin-bottom: 25px;">
                <span style="color: #38bdf8; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; display: block; margin-bottom: 4px;">
                    Scheda Anagrafica Iscritto
                </span>
                <h2 style="color: #ffffff; margin: 0; font-size: 26px; font-weight: 700; border: none; padding: 0;">
                    👦 {nome_completo_bambino}
                </h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Menu Navigazione
        col_tab1, col_tab2, col_tab3 = st.columns(3)
        with col_tab1:
            if st.button("👦 Dati Bambino", type="primary" if st.session_state.scheda_attiva == "bambino" else "secondary", use_container_width=True):
                st.session_state.scheda_attiva = "bambino"
                st.session_state.modalita_modifica = False
                st.rerun()
        with col_tab2:
            if st.button("👨‍👩‍👧 Contatti Genitore", type="primary" if st.session_state.scheda_attiva == "genitore" else "secondary", use_container_width=True):
                st.session_state.scheda_attiva = "genitore"
                st.session_state.modalita_modifica = False
                st.rerun()
        with col_tab3:
            if st.button("📅 Settimane Iscrizione", type="primary" if st.session_state.scheda_attiva == "settimane" else "secondary", use_container_width=True):
                st.session_state.scheda_attiva = "settimane"
                st.session_state.modalita_modifica = False
                st.rerun()

        # -------------------------------------------------------------------------
        # SCHEDA 1: BAMBINO
        # -------------------------------------------------------------------------
        if st.session_state.scheda_attiva == "bambino":
            if st.session_state.modalita_modifica:
                with st.form("form_modifica_bambino"):
                    st.markdown("#### 📝 Modifica Scheda Anagrafica")
                    col_sinistra_bambino, col_destra_genitore = st.columns(2)

                    with col_sinistra_bambino:
                        st.markdown("##### 👦 Dati Bambino")
                        e_cognome = st.text_input("Cognome", value=str(riga_bambino[col_cognome]))
                        e_nome = st.text_input("Nome", value=str(riga_bambino[col_nome]))
                        e_cf = st.text_input("Codice Fiscale", value=str(riga_bambino[col_cf]).upper())

                        c_nasc1, c_nasc2 = st.columns(2)
                        with c_nasc1:
                            e_luogo = st.text_input("Luogo di Nascita", value=str(riga_bambino[col_luogo]))
                        with c_nasc2:
                            e_nascita = st.text_input("Data di Nascita (GG/MM/AAAA)", value=str(riga_bambino[col_nascita]))

                        c_res1, c_res2 = st.columns([3, 1])
                        with c_res1:
                            e_via = st.text_input("Via/Strada/Piazza", value=str(riga_bambino[col_via]))
                        with c_res2:
                            e_civico = st.text_input("Civico", value=str(riga_bambino[col_civico]))

                        c_res3, c_res4 = st.columns([1, 2])
                        with c_res3:
                            e_cap = st.text_input("CAP", value=str(riga_bambino[col_cap]))
                        with c_res4:
                            e_citta = st.text_input("Città", value=str(riga_bambino[col_citta]))

                        st.markdown("---")
                        st.markdown("##### 🩺 Informazioni Sanitarie")
                        e_allergie = st.selectbox("Allergie/Intolleranze?", ["SÌ", "NO"], index=0 if str(riga_bambino[col_allergie]).strip().upper() in ["SÌ", "SI", "YES", "TRUE"] else 1)
                        e_quali = st.text_area("Specificare allergie o farmaci salvavita:", value=str(riga_bambino[col_quali]), height=68)

                    with col_destra_genitore:
                        st.markdown("##### 👨‍👩‍👧 Dati Genitore")
                        e_g_cognome = st.text_input("Cognome Genitore", value=str(riga_bambino[col_g_cognome]))
                        e_g_nome = st.text_input("Nome Genitore", value=str(riga_bambino[col_g_nome]))
                        e_g_cf = st.text_input("Codice Fiscale Genitore", value=str(riga_bambino[col_g_cf]).upper())
                        e_g_nascita = st.text_input("Data di Nascita Genitore", value=str(riga_bambino[col_g_nascita]))

                        c_gen1, c_gen2 = st.columns(2)
                        with c_gen1:
                            e_g_tel = st.text_input("Telefono Genitore", value=str(riga_bambino[col_g_tel]))
                        with c_gen2:
                            e_g_email = st.text_input("Email Genitore", value=str(riga_bambino[col_g_email]))

                    salva_bambino = st.form_submit_button("💾 Salva Modifiche Anagrafica", use_container_width=True, type="primary")

                    if salva_bambino:
                        if not e_cognome.strip() or not e_nome.strip():
                            st.error("⚠️ Cognome e Nome del bambino sono obbligatori!")
                        else:
                            df_iscritti.at[riga_index, col_cognome] = e_cognome.strip().upper()
                            df_iscritti.at[riga_index, col_nome] = e_nome.strip().title()
                            df_iscritti.at[riga_index, col_cf] = e_cf.strip().upper()
                            df_iscritti.at[riga_index, col_luogo] = e_luogo.strip().upper()
                            df_iscritti.at[riga_index, col_nascita] = e_nascita.strip()
                            df_iscritti.at[riga_index, col_via] = e_via.strip().title()
                            df_iscritti.at[riga_index, col_civico] = e_civico.strip().upper()
                            df_iscritti.at[riga_index, col_cap] = e_cap.strip()
                            df_iscritti.at[riga_index, col_citta] = e_citta.strip().upper()
                            df_iscritti.at[riga_index, col_allergie] = e_allergie
                            df_iscritti.at[riga_index, col_quali] = e_quali.strip().upper() if e_allergie == "SÌ" else ""

                            df_iscritti.at[riga_index, col_g_cognome] = e_g_cognome.strip()
                            df_iscritti.at[riga_index, col_g_nome] = e_g_nome.strip()
                            df_iscritti.at[riga_index, col_g_cf] = e_g_cf.strip().upper()
                            df_iscritti.at[riga_index, col_g_tel] = e_g_tel.strip()
                            df_iscritti.at[riga_index, col_g_email] = e_g_email.strip()
                            df_iscritti.at[riga_index, col_g_nascita] = e_g_nascita.strip()

                            try:
                                df_iscritti.to_excel("gestionale.xlsx", index=False)
                                st.success("✅ Dati aggiornati con successo!")
                                st.session_state.modalita_modifica = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Errore durante il salvataggio: {e}")
            else:
                box_anagrafica, box_residenza, box_sanitario = st.columns(3)
                stile_box = "display: flex; flex-direction: column; justify-content: flex-start; padding: 18px; border-radius: 8px; height: 230px; box-sizing: border-box;"

                with box_anagrafica:
                    st.markdown("#### 👤 Dati anagrafici")
                    st.markdown(
                        f"""
                        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; {stile_box}">
                            <p style="margin: 0 0 8px 0; font-size: 16px;">Cognome e nome: <b>{nome_completo_bambino}</b></p>
                            <p style="margin: 0 0 8px 0; font-size: 16px;">Data di nascita: <b>{riga_bambino[col_nascita]}</b></p>
                            <p style="margin: 0 0 8px 0; font-size: 16px;">Luogo di nascita: <b>{riga_bambino[col_luogo]}</b></p>
                            <p style="margin: 0; font-size: 16px;">Codice Fiscale: <b>{riga_bambino[col_cf]}</b></p>
                        </div>
                        """, unsafe_allow_html=True
                    )

                with box_residenza:
                    st.markdown("#### 📍 Residenza")
                    st.markdown(
                        f"""
                        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; {stile_box}">
                            <p style="margin: 0 0 8px 0; font-size: 16px;">Indirizzo: <b>{riga_bambino[col_via]}, {riga_bambino[col_civico]}</b></p>
                            <p style="margin: 0 0 8px 0; font-size: 16px;">Città: <b>{riga_bambino[col_citta]} ({riga_bambino[col_cap]})</b></p>
                            <p style="margin: 0; font-size: 16px;">Genitore: <b>{nome_completo_genitore}</b></p>
                        </div>
                        """, unsafe_allow_html=True
                    )

                with box_sanitario:
                    st.markdown("#### ⚠️ Sanitario")
                    ha_allergie = str(riga_bambino[col_allergie]).strip().upper()
                    is_allergico = ha_allergie in ["SÌ", "SI", "YES", "TRUE"]
                    colore_sfondo = "#fef2f2" if is_allergico else "#f0fdf4"
                    colore_bordo = "#fee2e2" if is_allergico else "#dcfce7"
                    icona = "🚨" if is_allergico else "✅"

                    st.markdown(
                        f"""
                        <div style="background-color: {colore_sfondo}; border: 1px solid {colore_bordo}; {stile_box}">
                            <p style="margin: 0 0 4px 0; font-size: 15px; font-weight: 600;">ALLERGIE / INTOLLERANZE</p>
                            <p style="margin: 0 0 10px 0; font-size: 18px; font-weight: 700;">{icona} {ha_allergie}</p>
                            <p style="margin: 0; font-size: 14px;">{riga_bambino[col_quali] if is_allergico else 'Nessuna allergia indicata.'}</p>
                        </div>
                        """, unsafe_allow_html=True
                    )

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✏️ Modifica Anagrafica", key="btn_attiva_modifica"):
                    st.session_state.modalita_modifica = True
                    st.rerun()

        # -------------------------------------------------------------------------
        # SCHEDA 2: GENITORE
        # -------------------------------------------------------------------------
        elif st.session_state.scheda_attiva == "genitore":
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                st.markdown("#### 👤 Dati genitore")
                st.markdown(
                    f"""
                    <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0;">
                        <p><b>Nome Completo:</b> {nome_completo_genitore}</p>
                        <p><b>Data Nascita:</b> {riga_bambino[col_g_nascita]}</p>
                        <p><b>Codice Fiscale:</b> {riga_bambino[col_g_cf]}</p>
                    </div>
                    """, unsafe_allow_html=True
                )

            with g_col2:
                st.markdown("#### 📞 Recapiti")
                st.markdown(
                    f"""
                    <div style="background-color: #f0fdfa; padding: 20px; border-radius: 8px; border: 1px solid #99f6e4;">
                        <p><b>📞 Telefono:</b> <a href="tel:{riga_bambino[col_g_tel]}">{riga_bambino[col_g_tel]}</a></p>
                        <p><b>✉️ Email:</b> <a href="mailto:{riga_bambino[col_g_email]}">{riga_bambino[col_g_email]}</a></p>
                    </div>
                    """, unsafe_allow_html=True
                )

            if not fratelli.empty:
                st.markdown("---")
                st.markdown("### 👦 Altri figli iscritti:")
                for idx_fratello, riga_fratello in fratelli.iterrows():
                    nome_f = f"{riga_fratello[col_cognome]} {riga_fratello[col_nome]}".upper()
                    btn_col1, btn_col2 = st.columns([3, 1])
                    with btn_col1:
                        st.write(f"🧑‍🤝‍🧑 **{nome_f}** (`{riga_fratello[col_cf]}`)")
                    with btn_col2:
                        if st.button(f"Scheda 📂", key=f"btn_fratello_{idx_fratello}"):
                            st.session_state.id_bambino_corrente = idx_fratello
                            st.session_state.scheda_attiva = "bambino"
                            st.rerun()

        # -------------------------------------------------------------------------
        # SCHEDA 3: SETTIMANE
        # -------------------------------------------------------------------------
        elif st.session_state.scheda_attiva == "settimane":
            st.markdown("### 📅 Gestione Iscrizioni Settimanali")

            if not colonne_settimane:
                st.error("⚠️ Nessuna colonna relativa alle settimane/periodi trovata.")
            else:
                opzioni_frequenza = ["NON ISCRITTO ❌", "GIORNATA INTERA", "MATTINO + PRANZO", "SOLO MATTINO"]
                nuovi_valori = {}

                cols = st.columns(4)
                for i, col_sett in enumerate(colonne_settimane):
                    val_str = str(riga_bambino[col_sett]).strip()
                    idx_def = opzioni_frequenza.index(val_str) if val_str in opzioni_frequenza else 0

                    is_iscritto = idx_def > 0
                    colore_bordo = "#10b981" if is_iscritto else "#cbd5e1"
                    colore_sfondo = "#f0fdf4" if is_iscritto else "#f8fafc"

                    with cols[i % 4]:
                        st.markdown(
                            f"""
                            <div style="background-color: {colore_sfondo}; border-top: 4px solid {colore_bordo}; 
                                        padding: 8px; border-radius: 6px 6px 0 0; text-align: center; margin-bottom: 5px;">
                                <div style="font-weight: bold; font-size: 12px;">{col_sett}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        scelta = st.selectbox(
                            label=f"Sel_{col_sett}",
                            options=opzioni_frequenza,
                            index=idx_def,
                            key=f"sb_sett_{riga_index}_{i}",
                            label_visibility="collapsed"
                        )
                        nuovi_valori[col_sett] = scelta

                st.markdown("---")

                col_btn_salva, col_btn_pagamenti = st.columns([1, 1])

                with col_btn_salva:
                    if st.button("💾 Salva Settimane", type="primary", use_container_width=True):
                        try:
                            for col_sett, val_scelto in nuovi_valori.items():
                                val_finale = "" if val_scelto == "NON ISCRITTO ❌" else str(val_scelto)
                                df_iscritti.at[riga_index, col_sett] = val_finale

                            df_iscritti.to_excel("gestionale.xlsx", index=False)
                            st.success("🎉 Settimane salvate con successo!")
                            st.rerun()
                        except Exception as err:
                            st.error(f"❌ Errore durante il salvataggio: {err}")

                with col_btn_pagamenti:
                    if st.button(f"💳 Vai ai Pagamenti", key="btn_vai_a_pagamenti"):
                        st.session_state["seleziona_iscritto_pagamenti"] = nome_completo_bambino
                        st.session_state["pagina_corrente"] = "Gestione Pagamenti"
                        st.rerun()