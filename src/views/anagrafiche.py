import streamlit as st
import pandas as pd

from src.utils.config_manager import carica_configurazione

# Riduciamo gli spazi verticali nativi di Streamlit per compattare la pagina
st.markdown(
    """
    <style>
        /* Riduce il margine superiore dell'intera pagina */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
        }
        /* Riduce lo spazio tra i singoli blocchi/elementi di Streamlit */
        .stVerticalBlock {
            gap: 0.5rem !important;
        }
        /* Riduce la distanza sopra e sotto i divisori (---) */
        hr {
            margin: 0.8rem 0 !important;
        }
        /* Riduce il margine sotto i titoli */
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
    df_iscritti = df_iscritti.astype(object)
    # Sostituiamo eventuali valori NaN/None con stringhe vuote per pulizia
    df_iscritti.fillna("", inplace=True)

    if df_iscritti.empty:
        st.info("Carica il file Excel per abilitare la gestione anagrafica.")
        return

    # --- INIZIALIZZAZIONE STATO (Super semplice) ---
    if "id_bambino_corrente" not in st.session_state:
        st.session_state.id_bambino_corrente = None
    if "risultato_ricerca" not in st.session_state:
        st.session_state.risultato_ricerca = None
    if "scheda_attiva" not in st.session_state:
        st.session_state.scheda_attiva = "bambino"
    if "modalita_modifica" not in st.session_state:
        st.session_state.modalita_modifica = False

    # --- MAPPATURA COLONNE (DINAMICA DA CONFIG E FALLBACK SICURO) ---
    config = carica_configurazione()
    mapping = config.get("mappatura_colonne", {})
    colonne_reali = list(df_iscritti.columns)
    
    # 1. ID / Timestamp univoco (usiamo la prima colonna se non specificata)
    id_colonna = colonne_reali[0]

    # 2. Dati Genitore
    col_g_email = mapping.get("email_genitore", "INDIRIZZO EMAIL")
    col_g_cognome = mapping.get("cognome_genitore", "COGNOME GENITORE")
    col_g_nome = mapping.get("nome_genitore", "NOME GENITORE")
    col_g_tel = mapping.get("recapito", "TELEFONO GENITORE")
    col_g_nascita = mapping.get("data_nascita_genitore", "DATA DI NASCITA GENITORE")
    col_g_cf = mapping.get("cf_genitore", "CODICE FISCALE GENITORE")

    # 3. Dati Bambino / Minore
    col_cognome = mapping.get("cognome", "COGNOME MINORE")
    col_nome = mapping.get("nome", "NOME MINORE")
    col_nascita = mapping.get("data_nascita", "DATA DI NASCITA MINORE")
    col_luogo = mapping.get("luogo_nascita", "LUOGO DI NASCITA MINORE")
    col_via = mapping.get("indirizzo", "INDIRIZZO DI RESIDENZA")
    col_civico = mapping.get("civico", "N. CIVICO")
    col_cap = mapping.get("cap", "CAP")
    col_citta = mapping.get("citta", "CITTA'")
    col_cf = mapping.get("codice_fiscale", "CODICE FISCALE MINORE")
    col_allergie = mapping.get("allergie", "ALLERGIE O INTOLLERANZE?")
    col_quali = mapping.get("note_allergie", "SE SI, INDICA QUALI")

    # Funzione di aiuto per verificare se la colonna esiste realmente nel file caricato
    def recupera_colonna_valida(nome_cercato, indice_fallback):
        # Se la colonna mappata esiste nel file Excel, usiamo quella
        if nome_cercato in colonne_reali:
            return nome_cercato
        # Altrimenti, usiamo la posizione d'emergenza
        if len(colonne_reali) > indice_fallback:
            return colonne_reali[indice_fallback]
        return nome_cercato

    # Assegnazione blindata
    col_g_email = recupera_colonna_valida(col_g_email, 1)
    col_g_cognome = recupera_colonna_valida(col_g_cognome, 2)
    col_g_nome = recupera_colonna_valida(col_g_nome, 3)
    col_g_tel = recupera_colonna_valida(col_g_tel, 4)
    col_g_nascita = recupera_colonna_valida(col_g_nascita, 5)
    col_g_cf = recupera_colonna_valida(col_g_cf, 6)

    col_cognome = recupera_colonna_valida(col_cognome, 7)
    col_nome = recupera_colonna_valida(col_nome, 8)
    col_nascita = recupera_colonna_valida(col_nascita, 9)
    col_luogo = recupera_colonna_valida(col_luogo, 10)
    col_via = recupera_colonna_valida(col_via, 11)
    col_civico = recupera_colonna_valida(col_civico, 12)
    col_cap = recupera_colonna_valida(col_cap, 13)
    col_citta = recupera_colonna_valida(col_citta, 14)
    col_cf = recupera_colonna_valida(col_cf, 15)
    col_allergie = recupera_colonna_valida(col_allergie, 16)
    col_quali = recupera_colonna_valida(col_quali, 17)

    # 4. Settimane (Rilevamento automatico e flessibile)
    prefisso = str(config.get("prefisso_settimane", "PERIODI DISPONIBILI")).strip().lower()
    colonne_settimane = [
        col for col in colonne_reali 
        if "settiman" in str(col).lower() or prefisso in str(col).lower()
    ]

    # ==========================================
    # 1. PREPARAZIONE DELLA LISTA DI RICERCA
    # ==========================================
    df_iscritti_ordinato = df_iscritti.sort_values(by=[col_cognome, col_nome])
    
    opzioni_ricerca = (
        df_iscritti_ordinato[col_cognome].astype(str).str.upper() + " " + 
        df_iscritti_ordinato[col_nome].astype(str).str.title() + " (" + 
        df_iscritti_ordinato[col_cf].astype(str).str.upper() + ")"
    )
    
    mappa_opzioni = dict(zip(opzioni_ricerca, df_iscritti_ordinato.index))
    lista_selectbox = list(opzioni_ricerca)
    # Mappa inversa: indice -> stringa opzione (utile per sincronizzare la selectbox)
    mappa_indice_a_opzione = {v: k for k, v in mappa_opzioni.items()}

    # ==========================================
    # 2. INTERFACCIA GRAFICA COMPATTA & CSS
    # ==========================================
   
    # CSS per lo stile visivo
    st.markdown(
        """
        <style>
        div[data-testid="stSelectbox"] p {
            font-size: 18px !important;
        }
        div[data-testid="stSelectbox"] div[role="button"] {
            font-size: 18px !important;
            padding: 8px 12px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    col_ricerca, col_vuota = st.columns([3, 2])

    # Callback quando l'utente cambia la selectbox: sincronizza lo stato corrente
    def _on_selectbox_change():
        sel = st.session_state.get("ricerca_dinamica_selectbox")
        if sel in mappa_opzioni:
            id_sel = mappa_opzioni.get(sel)
            st.session_state.id_bambino_corrente = id_sel
            st.session_state.risultato_ricerca = df_iscritti.loc[[id_sel]]
            # Assicurarsi di posizionarsi sempre sui Dati Bambino quando si apre una scheda
            st.session_state.scheda_attiva = "bambino"

    with col_ricerca:
        scelta_utente = st.selectbox(
            "Cerca un iscritto:",
            options=lista_selectbox,
            index=None,
            placeholder="🔍 Digita il cognome o nome...",
            key="ricerca_dinamica_selectbox",
            on_change=_on_selectbox_change
        )

    # ==========================================
    # 💡 L'ASSO NELLA MANICA: JAVASCRIPT INJECTION
    # ==========================================
    # Questo script trova l'input di ricerca della selectbox di Streamlit nel DOM del browser
    # e forza la selezione totale del testo al click, permettendo la sovrascrittura istantanea.
    st.components.v1.html(
        """
        <script>
        // Funzione che aggancia l'evento di focus all'input di Streamlit
        function attenuaInput() {
            // Cerchiamo l'elemento input generato da Streamlit per la selectbox
            const inputs = window.parent.document.querySelectorAll('div[data-testid="stSelectbox"] input');
            inputs.forEach(input => {
                if (!input.dataset.hasAutoSelectListener) {
                    input.dataset.hasAutoSelectListener = "true";
                    
                    // Al click o al focus, selezioniamo tutto il testo contenuto
                    const selectText = () => {
                        setTimeout(() => {
                            input.select();
                        }, 50); // Piccolo delay per attendere il rendering di Streamlit
                    };
                    
                    input.addEventListener('focus', selectText);
                    input.addEventListener('click', selectText);
                }
            });
        }

        // Monitoriamo continuamente la pagina (necessario perché Streamlit ridisegna spesso i componenti)
        setInterval(attenuaInput, 500);
        </script>
        """,
        height=0, # Invisibile all'utente, non occupa spazio a schermo
    )

    # ==========================================
    # 3. GESTIONE DELLA PERSISTENZA DELLA SCHEDA
    # ==========================================
    # Nota: la sincronizzazione dalla selectbox è gestita tramite callback `_on_selectbox_change`

    # ==========================================
    # 4. CARICAMENTO E VISUALIZZAZIONE DELLA SCHEDA
    # ==========================================
    if st.session_state.id_bambino_corrente is not None:
        bambino_selezionato = df_iscritti.loc[st.session_state.id_bambino_corrente]

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

        # ==========================================
        # 🌟 HEADER FISSO: BANNER BLU IN CIMA A TUTTO
        # ==========================================
        nome_completo = f"{str(riga_bambino[col_cognome]).upper()} {str(riga_bambino[col_nome]).title()}"

        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                padding: 20px 25px;
                border-radius: 10px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                margin-bottom: 25px;
            ">
                <span style="color: #38bdf8; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; display: block; margin-bottom: 4px;">
                    Scheda Anagrafica Iscritto
                </span>
                <h2 style="color: #ffffff; margin: 0; font-size: 26px; font-weight: 700; border: none; padding: 0; line-height: 1.2;">
                    👦 {nome_completo}
                </h2>
            </div>
            """,
            unsafe_allow_html=True
        )

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
                # Sincronizziamo la selectbox con l'iscritto corrente per evitare sovrascritture
                try:
                    current_id = st.session_state.get('id_bambino_corrente')
                    if current_id is not None:
                        opt = mappa_indice_a_opzione.get(current_id)
                        if opt is not None:
                            st.session_state.ricerca_dinamica_selectbox = opt
                except Exception:
                    pass
                st.session_state.scheda_attiva = "genitore"
                st.session_state.modalita_modifica = False
                st.rerun()
        with col_tab3:
            tipo_s = "primary" if st.session_state.scheda_attiva == "settimane" else "secondary"
            if st.button("📅 Settimane Iscrizione", type=tipo_s, use_container_width=True):
                st.session_state.scheda_attiva = "settimane"
                st.session_state.modalita_modifica = False
                st.rerun()

        # ==========================================
        # 1. TAB: BAMBINO
        # ==========================================
        if st.session_state.scheda_attiva == "bambino":
            
            # --- CORPO DELLA SCHEDA ---
            if st.session_state.modalita_modifica:
                # FORM DI MODIFICA COMPATTO (Dati Affiancati)
                with st.form("form_modifica_bambino"):
                    st.markdown("#### 📝 Modifica Scheda Anagrafica")
                    
                    # Creiamo le due macro-colonne principali per affiancare Bambino e Genitore
                    col_sinistra_bambino, col_destra_genitore = st.columns(2)
                    
                    # ==========================================
                    # COLONNA SINISTRA: BAMBINO E SANITARI
                    # ==========================================
                    with col_sinistra_bambino:
                        st.markdown("##### 👦 Dati Bambino")
                        e_cognome = st.text_input("Cognome", value=str(riga_bambino[col_cognome]))
                        e_nome = st.text_input("Nome", value=str(riga_bambino[col_nome]))
                        e_cf = st.text_input("Codice Fiscale", value=str(riga_bambino[col_cf]).upper())
                        
                        c_nasc1, c_nasc2 = st.columns(2)
                        with c_nasc1:
                            e_luogo = st.text_input("Luogo di Nascita", value=str(riga_bambino[col_luogo]))
                        with c_nasc2:
                            data_grezza = riga_bambino[col_nascita]
                            try:
                                data_pulita = pd.to_datetime(data_grezza).strftime('%d/%m/%Y')
                            except Exception:
                                data_pulita = str(data_grezza) if pd.notna(data_grezza) else ""
                            e_nascita = st.text_input("Data di Nascita (GG/MM/AAAA)", value=data_pulita)
                        
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
                        e_quali = st.text_area("Specificare allergie o farmaci salvavita:", value=str(riga_bambino[col_quali]) if pd.notnull(riga_bambino[col_quali]) else "", height=68)

                    # ==========================================
                    # COLONNA DESTRA: DATI GENITORE
                    # ==========================================
                    with col_destra_genitore:
                        st.markdown("##### 👨‍👩‍👧 Dati Genitore")
                        e_g_cognome = st.text_input("Cognome Genitore", value=str(riga_bambino[col_g_cognome]))
                        e_g_nome = st.text_input("Nome Genitore", value=str(riga_bambino[col_g_nome]))
                        e_g_cf = st.text_input("Codice Fiscale Genitore", value=str(riga_bambino[col_g_cf]).upper())
                        data_grezza_genitore = riga_bambino[col_g_nascita]
                        try:
                            data_pulita_genitore = pd.to_datetime(data_grezza_genitore).strftime('%d/%m/%Y')
                        except Exception:
                            data_pulita_genitore = str(data_grezza_genitore) if pd.notna(data_grezza_genitore) else ""
                        e_g_nascita = st.text_input("Data di Nascita Genitore (GG/MM/AAAA)", value=data_pulita_genitore)

                        c_gen1, c_gen2 = st.columns(2)
                        with c_gen1:
                            e_g_tel = st.text_input("Telefono Genitore", value=str(riga_bambino[col_g_tel]))
                        with c_gen2:
                            e_g_email = st.text_input("Email Genitore", value=str(riga_bambino[col_g_email]))
                        
                        st.markdown("<div style='margin-top: 45px;'></div>", unsafe_allow_html=True)
                        st.info("ℹ️ Se ci sono fratelli iscritti, i dati del genitore verranno allineati automaticamente a tutte le schede.")

                    st.markdown("---")
                    salva_bambino = st.form_submit_button("💾 Salva Modifiche Anagrafica", use_container_width=True, type="primary")
                    
                    if salva_bambino:
                        campi_da_validare = {
                            "Cognome": e_cognome,
                            "Nome": e_nome,
                            "Codice Fiscale": e_cf,
                            "Luogo di Nascita": e_luogo,
                            "Data di Nascita": e_nascita,
                            "Via/Piazza": e_via,
                            "Civico": e_civico,
                            "CAP": e_cap,
                            "Città": e_citta,
                            "Allergie (SÌ/NO)": e_allergie
                        }

                        campi_da_validare_genitore = {
                            "Cognome Genitore": e_g_cognome,
                            "Nome Genitore": e_g_nome,
                            "Codice Fiscale Genitore": e_g_cf,
                            "Telefono Genitore": e_g_tel,
                            "Email Genitore": e_g_email,
                            "Data di Nascita Genitore": e_g_nascita
                        }

                        campi_da_validare.update(campi_da_validare_genitore)

                        campi_mancanti = []
                        for nome_campo, valore in campi_da_validare.items():
                            valore_stringa = str(valore).strip() if valore is not None else ""
                            if not valore_stringa:
                                campi_mancanti.append(nome_campo)
                        
                        if e_allergie == "SÌ" and (not e_quali or not str(e_quali).strip()):
                            campi_mancanti.append("Specificare quali allergie")

                        if len(campi_mancanti) > 0:
                            st.error(f"⚠️ **Impossibile salvare!** Tutti i campi sono obbligatori. Ti sei dimenticato di compilare: **{', '.join(campi_mancanti)}**")
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

                            se_fratelli = df_iscritti[df_iscritti[col_g_cf] == cf_genitore_corrente].index
                            if len(se_fratelli) > 1:
                                for idx_f in se_fratelli:
                                    df_iscritti.at[idx_f, col_g_cognome] = e_g_cognome.strip()
                                    df_iscritti.at[idx_f, col_g_nome] = e_g_nome.strip()
                                    df_iscritti.at[idx_f, col_g_cf] = e_g_cf.strip().upper()
                                    df_iscritti.at[idx_f, col_g_tel] = e_g_tel.strip()
                                    df_iscritti.at[idx_f, col_g_email] = e_g_email.strip()
                                    df_iscritti.at[idx_f, col_g_nascita] = e_g_nascita.strip()
                            
                            try:
                                df_iscritti.to_excel("gestionale.xlsx", index=False)
                                st.success("✅ Dati del bambino aggiornati con successo!")
                                st.session_state.modalita_modifica = False
                                st.session_state.risultato_ricerca = df_iscritti.loc[[riga_index]]
                                st.rerun()
                            except Exception as e:
                                st.error(f"Errore durante il salvataggio: {e}")
            else:
                # VISTA STATICA (I 3 Box Dati rimessi in riga)
                box_anagrafica, box_residenza, box_sanitario = st.columns(3)
                
                data_nascita_val = riga_bambino[col_nascita]
                data_nascita_str = pd.to_datetime(data_nascita_val).strftime('%d/%m/%Y') if pd.notnull(data_nascita_val) and not isinstance(data_nascita_val, str) else str(data_nascita_val)
                contatto_genitore = riga_bambino.get(col_g_tel, "Non specificato") if 'col_g_tel' in locals() else "Dato mancante"
                
                # Stile standardizzato per altezza fissa identica e nessuna linea di separazione
                stile_box = "display: flex; flex-direction: column; justify-content: flex-start; padding: 18px; border-radius: 8px; height: 230px; box-sizing: border-box;"

                # ==========================================
                # 1. BOX IDENTITÀ
                # ==========================================
                with box_anagrafica:
                    st.markdown("#### 👤 Dati anagrafici")
                    cf_pulito = str(riga_bambino[col_cf]).strip().upper() if pd.notnull(riga_bambino[col_cf]) else "Dato mancante"
                    st.markdown(
                        f"""
                        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; {stile_box}">
                            <div style="margin-bottom: 12px;">
                                <p style="margin: 0 0 12px 0; font-size: 17px; color: #0f172a;">Cognome e nome: <span style="font-weight: 600;">{nome_completo}</span></p>
                                <p style="margin: 0 0 12px 0; font-size: 17px; color: #0f172a;">Data di nascita: <span style="font-weight: 600;">{data_nascita_str}</span></p>
                                <p style="margin: 0 0 12px 0; font-size: 17px; color: #0f172a;">Luogo di nascita: <span style="font-weight: 600;">{riga_bambino[col_luogo]}</span></p>
                                <p style="margin: 0; font-size: 17px; color: #0f172a;">Codice Fiscale: <span style="font-weight: 600;">{cf_pulito}</span></p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True
                    )
                
                # ==========================================
                # 2. BOX RESIDENZA E CONTATTI
                # ==========================================
                with box_residenza:
                    st.markdown("#### 📍 Residenza e Contatti")
                    indirizzo_completo = f"{riga_bambino[col_via]}, {riga_bambino[col_civico]}"
                    citta_completa = f"{riga_bambino[col_citta]} - {riga_bambino[col_cap]}"
                    st.markdown(
                        f"""
                        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; {stile_box}">
                            <div style="margin-bottom: 12px;">
                                <p style="margin: 0 0 12px 0; font-size: 17px; color: #0f172a;">Indirizzo: <span style="font-weight: 600;">{indirizzo_completo}</span></p>
                                <p style="margin: 0 0 12px 0; font-size: 17px; color: #0f172a;">Città e CAP: <span style="font-weight: 600;">{citta_completa}</span></p>
                                <p style="margin: 0 0 12px 0; font-size: 17px; color: #0f172a;">Numero di contatto: <span style="font-weight: 600;">{contatto_genitore}</span></p>
                                <p style="margin: 0; font-size: 17px; color: #0f172a;">Nome genitore: <span style="font-weight: 600;">{nome_completo_genitore}</span></p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True
                    )
                
                # ==========================================
                # 3. BOX SANITARIO
                # ==========================================
                with box_sanitario:
                    st.markdown("#### ⚠️ Informazioni Sanitarie")
                    ha_allergie = str(riga_bambino[col_allergie]).strip().upper()
                    if ha_allergie in ["SÌ", "SI", "YES", "Vero", "TRUE"]:
                        colore_sfondo, colore_bordo, icona, colore_testo = "#fef2f2", "#fee2e2", "🚨", "#991b1b"
                        dettaglio = f"<span style='color: {colore_testo}; font-weight: 500;'>{riga_bambino[col_quali]}</span>"
                    else:
                        colore_sfondo, colore_bordo, icona, colore_testo = "#f0fdf4", "#dcfce7", "✅", "#166534"
                        dettaglio = "<span style='color: #64748b; font-style: italic;'>Nessuna allergia o intolleranza segnalata.</span>"
                    st.markdown(
                        f"""
                        <div style="background-color: {colore_sfondo}; border: 1px solid {colore_bordo}; {stile_box}">
                            <div style="margin-bottom: 12px;">
                                <p style="margin: 0 0 4px 0; font-size: 17px; color: #64748b; font-weight: 600;">PRESENZA ALLERGIE</p>
                                <p style="margin: 0 0 16px 0; font-size: 18px; font-weight: 700; color: {colore_testo};">{icona} {ha_allergie}</p>
                                <p style="margin: 0 0 4px 0; font-size: 17px; color: #64748b; font-weight: 600;">DETTAGLIO ALLERGIE / FARMACI</p>
                                <p style="margin: 0; font-size: 15px; line-height: 1.4;">{dettaglio}</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True
                    )

                # --- PULSANTE DI MODIFICA IN FONDO AL TAB BAMBINO ---
                st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

                # Nessuna colonna: inserito direttamente nel container/tab principale
                # use_container_width=False impedisce al pulsante di espandersi fino a destra
                if st.button("✏️ Modifica Anagrafica", key="btn_attiva_modifica", use_container_width=False, type="secondary"):
                    st.session_state.modalita_modifica = True
                    st.rerun()

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
                    st.info("Se ci sono altri fratelli iscritti, i dati del genitore verranno aggiornati nelle schede di tutti gli iscritti.")
                    
                    # Se ci sono altri figli, chiediamo conferma prima di applicare le modifiche a tutti
                    se_fratelli = df_iscritti[df_iscritti[col_g_cf] == cf_genitore_corrente].index
                    if len(se_fratelli) > 1:
                        applica_a_tutti = st.checkbox(f"Applica le modifiche anche agli altri {len(se_fratelli)} figli dello stesso genitore", value=False, key=f"chk_applica_gen_{riga_index}")
                    else:
                        applica_a_tutti = False

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
                        if applica_a_tutti:
                            se_fratelli = df_iscritti[df_iscritti[col_g_cf] == cf_genitore_corrente].index
                            if len(se_fratelli) > 1:
                                for idx_f in se_fratelli:
                                    df_iscritti.at[idx_f, col_g_cognome] = e_g_cognome
                                    df_iscritti.at[idx_f, col_g_nome] = e_g_nome
                                    df_iscritti.at[idx_f, col_g_cf] = e_g_cf
                                    df_iscritti.at[idx_f, col_g_tel] = e_g_tel
                                    df_iscritti.at[idx_f, col_g_email] = e_g_email
                                    df_iscritti.at[idx_f, col_g_nascita] = e_g_nascita
                        
                        try:
                            df_iscritti.to_excel("gestionale.xlsx", index=False)
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
                    st.markdown("#### 👤 Dati genitore")
                    st.markdown(
                        f"""
                        <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; min-height: 180px;">
                            <p style="margin-bottom: 10px; font-size: 17px;"><b>Cognome e nome:</b> {nome_completo_genitore}</p>
                            <p style="margin-bottom: 10px; font-size: 17px;"><b>Data di nascita:</b> {data_n_g_str}</p>
                            <p style="margin-bottom: 0; font-size: 17px;"><b>Codice Fiscale:</b> {cf_g_pulito}</p>
                        </div>
                        """, unsafe_allow_html=True
                    )
                    
                with g_col2:
                    st.markdown("#### 📞 Recapiti")
                    st.markdown(
                        f"""
                        <div style="background-color: #f0fdfa; padding: 20px; border-radius: 8px; border: 1px solid #99f6e4; min-height: 180px;">
                            <p style="margin-bottom: 10px; font-size: 17px;"><b>📞 Telefono:</b> <a href="tel:{tel_g_pulito}" style="font-weight: bold; color: #0f172a; text-decoration: none;">{tel_g_pulito}</a></p>
                            <p style="margin-bottom: 0; font-size: 17px;"><b>✉️ Email:</b> <a href="mailto:{riga_bambino[col_g_email]}" style="font-weight: bold; color: #0d9488;">{riga_bambino[col_g_email]}</a></p>
                        </div>
                        """, unsafe_allow_html=True
                    )
                
                # Visualizzazione Fratelli
                if not fratelli.empty:
                    st.markdown("---")
                    st.markdown("### 👦 Altri figli iscritti da questo genitore:")
                    for idx_fratello, riga_fratello in fratelli.iterrows():
                        nome_fratello = f"{riga_fratello[col_cognome]} {riga_fratello[col_nome]}".upper()
                        btn_col1, btn_col2 = st.columns([3, 1])
                        with btn_col1:
                            st.write(f"🧑‍🤝‍🧑 **{nome_fratello}** (Codice Fiscale: `{riga_fratello[col_cf]}`)")
                        with btn_col2:
                            if st.button(f"Vedi scheda di {riga_fratello[col_nome]} 📂", key=f"btn_fratello_{idx_fratello}"):
                                # Impostiamo anche la selectbox di ricerca con l'opzione corrispondente
                                # Impostiamo anche la selectbox se riusciamo a trovare l'opzione
                                try:
                                    opt = mappa_indice_a_opzione.get(idx_fratello, None)
                                    if opt is not None:
                                        st.session_state.ricerca_dinamica_selectbox = opt
                                except Exception:
                                    pass
                                st.session_state.id_bambino_corrente = idx_fratello
                                st.session_state.scheda_attiva = "bambino"
                                st.rerun()

# ==========================================
        # 3. TAB: SETTIMANE (RICOSTRUITO DA CAPO)
        # ==========================================
        elif st.session_state.scheda_attiva == "settimane":
            st.markdown("### 📅 Gestione Iscrizioni Settimanali")
            st.caption("Modifica le frequenze e clicca sul pulsante in basso per salvare su file.")

            # 1. RILEVAMENTO DINAMICO COLONNE DAL NUOVO MASTER
            colonne_settimane = [
                c for c in df_iscritti.columns 
                if any(k in str(c).upper() for k in ["PERIODI", "SETTIMAN", "SETT."])
            ]

            if not colonne_settimane:
                st.error("⚠️ Nessuna colonna relativa alle settimane/periodi trovata nel file Excel Master.")
            else:
                opzioni_frequenza = ["NON ISCRITTO ❌", "GIORNATA INTERA", "MATTINO + PRANZO", "SOLO MATTINO"]
                riga_idx = st.session_state.id_bambino_corrente

                # Verify index correctness
                if riga_idx not in df_iscritti.index:
                    st.error(f"⚠️ Impossibile trovare l'indice del bambino (#{riga_idx}) nel DataFrame.")
                else:
                    # 2. PREPARAZIONE DATI E VALORI CORRENTI
                    # Rileggiamo la riga direttamente dal DataFrame originale
                    riga_dati = df_iscritti.loc[riga_idx]

                    # Mappa per memorizzare i nuovi valori selezionati
                    nuovi_valori = {}

                    # Layout a 4 colonne per le schede
                    cols = st.columns(4)

                    for i, col_sett in enumerate(colonne_settimane):
                        # Pulizia del valore estratto dal file Excel
                        val_grezzo = riga_dati[col_sett]
                        val_str = str(val_grezzo).strip() if pd.notnull(val_grezzo) and str(val_grezzo).strip().lower() not in ["nan", "none", "<na>", ""] else ""

                        # Determinazione indice predefinito per la selectbox
                        idx_def = opzioni_frequenza.index(val_str) if val_str in opzioni_frequenza else 0

                        # Pulizia del nome della settimana da mostrare
                        etichetta_pulita = str(col_sett).replace("PERIODI DISPONIBILI", "").replace("SETTIMANE DISPONIBILI", "").strip()
                        if not etichetta_pulita or etichetta_pulita.startswith("["):
                            etichetta_mostrata = f"Settimana {i+1}"
                        else:
                            etichetta_mostrata = f"Sett {i+1}: {etichetta_pulita}"

                        # Gestione visuale delle Card (Verde = Iscritto, Grigio = Non iscritto)
                        is_iscritto = idx_def > 0
                        colore_bordo = "#10b981" if is_iscritto else "#cbd5e1"
                        colore_sfondo = "#f0fdf4" if is_iscritto else "#f8fafc"
                        testo_stato = "✅ ISCRITTO" if is_iscritto else "⚪ NON ISCRITTO"

                        with cols[i % 4]:
                            # Card con Intestazione
                            st.markdown(
                                f"""
                                <div style="background-color: {colore_sfondo}; border-top: 4px solid {colore_bordo}; 
                                            padding: 8px; border-radius: 6px 6px 0 0; text-align: center; margin-bottom: 5px;">
                                    <div style="font-weight: bold; font-size: 13px; color: #0f172a;">{etichetta_mostrata}</div>
                                    <div style="font-size: 10px; color: {colore_bordo}; font-weight: bold; margin-top: 2px;">{testo_stato}</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            # Selectbox per la scelta
                            scelta = st.selectbox(
                                label=f"Sel_{col_sett}",
                                options=opzioni_frequenza,
                                index=idx_def,
                                key=f"sb_sett_{riga_idx}_{i}",
                                label_visibility="collapsed"
                            )

                            nuovi_valori[col_sett] = scelta

                    st.markdown("---")

                    # =========================================================
                    # 🔗 NAVEGAZIONE RAPIDA AI PAGAMENTI + SALVATAGGIO
                    # =========================================================
                    # Recuperiamo Cognome e Nome del bambino per la selezione
                    cognome_bambino = str(riga_dati.get("COGNOME MINORE", riga_dati.get("COGNOME", ""))).strip()
                    nome_bambino = str(riga_dati.get("NOME MINORE", riga_dati.get("NOME", ""))).strip()
                    nome_completo = f"{cognome_bambino} {nome_bambino}".strip().upper()

                    col_btn_salva, col_btn_pagamenti = st.columns([1, 1])

                    with col_btn_salva:
                        # 3. PULSANTE DI SALVATAGGIO UNICO E RIGIDO
                        if st.button("💾 Salva Modifiche Settimane", type="primary", use_container_width=True):
                            try:
                                # a. Convertiamo preventivamente tutte le colonne settimane in object per sbloccare i dtypes
                                for c in colonne_settimane:
                                    df_iscritti[c] = df_iscritti[c].astype(object)

                                # b. Scrittura diretta dei dati nel DataFrame
                                for col_sett, val_scelto in nuovi_valori.items():
                                    val_finale = "" if val_scelto == "NON ISCRITTO ❌" else str(val_scelto)
                                    df_iscritti.at[riga_idx, col_sett] = val_finale

                                # c. Scrittura fisica su disco
                                df_iscritti.to_excel("iscrizioni.xlsx", index=False)

                                # d. Aggiornamento degli Stati di Sessione
                                if "df_iscritti" in st.session_state:
                                    st.session_state.df_iscritti = df_iscritti
                                
                                st.session_state.risultato_ricerca = df_iscritti.loc[[riga_idx]]

                                # e. Pulizia cache lettura Streamlit
                                st.cache_data.clear()

                                st.success("🎉 Settimane salvate con successo nel file Excel!")
                                st.rerun()

                            except Exception as err:
                                st.error(f"❌ Errore durante il salvataggio: {err}")

                    with col_btn_pagamenti:
                        # 🔗 PULSANTE PER PASSARE AI PAGAMENTI
                        if st.button(f"💳 Vai ai Pagamenti di {nome_bambino}", use_container_width=True):
                            st.session_state["seleziona_iscritto_pagamenti"] = nome_completo
                            st.session_state["pagina_attiva"] = "pagamenti"
                            st.rerun()