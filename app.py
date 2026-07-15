import streamlit as st
import pandas as pd
import database_utils as db_utils

# Configurazione della pagina
st.set_page_config(page_title="Gestionale Centro Estivo", layout="wide")

# Inizializza i dati dal tuo Excel
db_utils.inizializza_database_in_memoria()
df_iscritti = db_utils.ottieni_iscritti()

# Gestione della navigazione (se non esiste, parte dalla Home)
if "pagina_corrente" not in st.session_state:
    st.session_state.pagina_corrente = "Home"

# Funzione rapida per cambiare pagina
def naviga_a(nome_pagina):
    st.session_state.pagina_corrente = nome_pagina
    st.rerun()

# ==========================================
# SIDEBAR: NAVIGAZIONE A PULSANTI
# ==========================================
st.sidebar.title("Navigation")
st.sidebar.write("Seleziona la sezione desiderata:")

# Inizializziamo la pagina corrente se non esiste nello stato
if "pagina_corrente" not in st.session_state:
    st.session_state.pagina_corrente = "Home Page"

# --- PULSANTE 1: TORNA ALLA HOME PAGE ---
if st.sidebar.button("🏠 Torna alla Home Page", use_container_width=True):
    st.session_state.pagina_corrente = "Home Page"
    st.rerun()

# --- PULSANTE 2: VAI ALLE ANAGRAFICHE ---
# Quando viene cliccato, oltre a cambiare pagina, azzera attivamente la ricerca
if st.sidebar.button("👤 Vai alle anagrafiche", use_container_width=True):
    # RESET STATO RICERCA ANAGRAFICA
    st.session_state.id_bambino_corrente = None
    st.session_state.risultato_ricerca = None
    st.session_state.scheda_attiva = "bambino"
    
    # Questo svuota fisicamente il testo digitato nel campo di ricerca!
    if "ricerca_cognome" in st.session_state:
        st.session_state.ricerca_cognome = ""
    
    st.session_state.pagina_corrente = "Anagrafiche Iscritti"
    st.rerun()

# --- PULSANTE 3: VAI AGLI ELENCHI SETTIMANALI ---
if st.sidebar.button("📅 Vai agli elenchi settimanali", use_container_width=True):
    st.session_state.pagina_corrente = "Elenchi Settimanali"
    st.rerun()

# --- PULSANTE 4: VAI AI PAGAMENTI ---
if st.sidebar.button("💳 Vai ai pagamenti", use_container_width=True):
    st.session_state.pagina_corrente = "Gestione Pagamenti"
    st.rerun()

# ==========================================
# 1. PAGINA PRINCIPALE: HOME PAGE A RIQUADRI
# ==========================================
if st.session_state.pagina_corrente == "Home Page":
    st.title("Gestionale Centro Estivo")
    st.write("Benvenuto nel gestionale. Clicca su uno dei riquadri qui sotto per accedere alle funzioni specifiche:")
    st.markdown("---")

    # Creiamo una griglia di riquadri (3 colonne)
    ric1, ric2, ric3 = st.columns(3)

    with ric1:
        st.markdown(
            """
            <div style="background-color: #e0f2fe; padding: 20px; border-radius: 10px; border-left: 5px solid #0284c7; min-height: 140px;">
                <h3 style="color: #0369a1; margin-top: 0;">👤 Anagrafiche Iscritti</h3>
                <p style="color: #0c4a6e; font-size: 14px;">Visualizza le schede personali di ogni bambino, modifica dati personali e settimane iscritte.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button("Apri Anagrafiche →", key="btn_anagrafica", use_container_width=True):
            naviga_a("Anagrafiche Iscritti")

    with ric2:
        st.markdown(
            """
            <div style="background-color: #fef3c7; padding: 20px; border-radius: 10px; border-left: 5px solid #d97706; min-height: 140px;">
                <h3 style="color: #b45309; margin-top: 0;">📅 Elenchi Settimanali</h3>
                <p style="color: #78350f; font-size: 14px;">Controlla chi è presente nella Settimana 1, 2, 3... Genera i registri di presenza e i totali per la mensa.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button("Apri Elenchi →", key="btn_elenchi", use_container_width=True):
            naviga_a("Elenchi Settimanali")

    with ric3:
        st.markdown(
            """
            <div style="background-color: #dcfce7; padding: 20px; border-radius: 10px; border-left: 5px solid #22c55e; min-height: 140px;">
                <h3 style="color: #15803d; margin-top: 0;">💰 Gestione Pagamenti</h3>
                <p style="color: #14532d; font-size: 14px;">Vedi la situazione economica complessiva, le quote da riscuotere, i saldi e gli acconti ricevuti.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button("Apri Pagamenti →", key="btn_pagamenti", use_container_width=True):
            naviga_a("Gestione Pagamenti")


# ==========================================
# 2. SEZIONE: ANAGRAFICHE ISCRITTI
# ==========================================
elif st.session_state.pagina_corrente == "Anagrafiche Iscritti":
    st.title("👤 Ricerca Schede Anagrafiche")
    st.write("Inserisci il cognome dell'iscritto per visualizzare i dati anagrafici, sanitari e i contatti dei genitori.")
    st.markdown("---")
    
    if not df_iscritti.empty:
        # Recuperiamo le colonne reali dal tuo file Excel
        colonne_reali = list(df_iscritti.columns)
        
        # --- MAPPATURA COLONNE GENITORE (B - G) ---
        col_g_email = colonne_reali[1]    # B
        col_g_cognome = colonne_reali[2]  # C
        col_g_nome = colonne_reali[3]     # D
        col_g_tel = colonne_reali[4]      # E
        col_g_nascita = colonne_reali[5]  # F
        col_g_cf = colonne_reali[6]       # G

        # --- MAPPATURA COLONNE BAMBINO (H - R) ---
        col_cognome = colonne_reali[7]   # H
        col_nome = colonne_reali[8]      # I
        col_nascita = colonne_reali[9]   # J
        col_luogo = colonne_reali[10]    # K
        col_via = colonne_reali[11]      # L
        col_civico = colonne_reali[12]   # M
        col_cap = colonne_reali[13]      # N
        col_citta = colonne_reali[14]    # O
        col_cf = colonne_reali[15]       # P
        col_allergie = colonne_reali[16] # Q
        col_quali = colonne_reali[17]    # R

        # --- MAPPATURA COLONNE SETTIMANE (Dinamica) ---
        # Cerchiamo tutte le colonne che contengono "settimana" nel nome (non importa se maiuscolo/minuscolo)
        colonne_settimane = [col for col in colonne_reali if "Settimane" in col.lower()]

        # --- STATO DELLA RICERCA ---
        if "id_bambino_corrente" not in st.session_state:
            st.session_state.id_bambino_corrente = None
        if "risultato_ricerca" not in st.session_state:
            st.session_state.risultato_ricerca = None
        # Gestione della scheda visibile (0 = Bambino, 1 = Genitore)
        if "scheda_attiva" not in st.session_state:
            st.session_state.scheda_attiva = "bambino"

        # --- MOTORE DI RICERCA ---
        col_ricerca, col_bottone = st.columns([4, 1])
        
        with col_ricerca:
            # Abbiamo aggiunto key="ricerca_cognome" alla fine!
            cognome_input = st.text_input(
                "🔍 Inserisci il Cognome del bambino da cercare:", 
                placeholder="Es. Rossi...",
                key="ricerca_cognome"
            )
            
        with col_bottone:
            st.write("##") # Allineamento verticale
            avvia_ricerca = st.button("Avvia Ricerca 🚀", use_container_width=True)

        if avvia_ricerca and cognome_input:
            risultati = df_iscritti[df_iscritti[col_cognome].astype(str).str.lower().str.contains(cognome_input.strip().lower())]
            st.session_state.risultato_ricerca = risultati
            if not risultati.empty:
                st.session_state.id_bambino_corrente = risultati.index[0]
                st.session_state.scheda_attiva = "bambino" # Reset all'avvio di una nuova ricerca
        
        # --- MOSTRA I RISULTATI TROVATI ---
        if st.session_state.risultato_ricerca is not None:
            df_filtrato = st.session_state.risultato_ricerca
            
            if df_filtrato.empty:
                st.warning(f"❌ Nessun iscritto trovato con il cognome '{cognome_input}'. Riprova.")
            else:
                # Selezione manuale in caso di omonimia
                if len(df_filtrato) > 1:
                    st.success(f"📋 Trovati {len(df_filtrato)} iscritti corrispondenti.")
                    scelte = df_filtrato[col_cognome].astype(str) + " " + df_filtrato[col_nome].astype(str)
                    
                    default_index = 0
                    if st.session_state.id_bambino_corrente in df_filtrato.index:
                        default_index = list(df_filtrato.index).index(st.session_state.id_bambino_corrente)
                        
                    bambino_scelto = st.radio("Seleziona l'iscritto specifico da visualizzare:", scelte, index=default_index)
                    nuovo_id = scelte[scelte == bambino_scelto].index[0]
                    if nuovo_id != st.session_state.id_bambino_corrente:
                        st.session_state.id_bambino_corrente = nuovo_id
                        st.session_state.scheda_attiva = "bambino" # Reset quando si cambia selezione radio
                
                elif len(df_filtrato) == 1 and st.session_state.id_bambino_corrente not in df_filtrato.index:
                    st.session_state.id_bambino_corrente = df_filtrato.index[0]

                # Estraiamo la riga corrente
                riga_bambino = df_iscritti.loc[st.session_state.id_bambino_corrente]
                
                st.markdown("##")
                nome_completo_bambino = f"{riga_bambino[col_cognome]} {riga_bambino[col_nome]}".upper()
                nome_completo_genitore = f"{riga_bambino[col_g_cognome]} {riga_bambino[col_g_nome]}".upper()
                
                # --- LOGICA COLLEGAMENTO FRATELLI/SORELLE ---
                cf_genitore_corrente = riga_bambino[col_g_cf]
                email_genitore_corrente = riga_bambino[col_g_email]
                
                fratelli = df_iscritti[
                    ((df_iscritti[col_g_cf] == cf_genitore_corrente) & (pd.notnull(df_iscritti[col_g_cf]))) |
                    ((df_iscritti[col_g_email] == email_genitore_corrente) & (pd.notnull(df_iscritti[col_g_email])))
                ]
                fratelli = fratelli.drop(st.session_state.id_bambino_corrente, errors='ignore')
                
                # --- SISTEMA DI NAVIGAZIONE A PULSANTI (3 OPZIONI) ---
                col_tab1, col_tab2, col_tab3 = st.columns(3)
                with col_tab1:
                    tipo_pulsante_b = "primary" if st.session_state.scheda_attiva == "bambino" else "secondary"
                    if st.button("👦 Dati Bambino", type=tipo_pulsante_b, use_container_width=True):
                        st.session_state.scheda_attiva = "bambino"
                        st.rerun()
                with col_tab2:
                    tipo_pulsante_g = "primary" if st.session_state.scheda_attiva == "genitore" else "secondary"
                    if st.button("👨‍👩‍👧 Contatti Genitore", type=tipo_pulsante_g, use_container_width=True):
                        st.session_state.scheda_attiva = "genitore"
                        st.rerun()
                with col_tab3:
                    tipo_pulsante_s = "primary" if st.session_state.scheda_attiva == "settimane" else "secondary"
                    if st.button("📅 Settimane Iscrizione", type=tipo_pulsante_s, use_container_width=True):
                        st.session_state.scheda_attiva = "settimane"
                        st.rerun()
                
                st.markdown("---")

                # --- CONTENUTO DINAMICO IN BASE ALLO STATO ---
                if st.session_state.scheda_attiva == "bambino":
                    # --- VISTA DATI BAMBINO ---
                    st.markdown(f"### Scheda Personale: {nome_completo_bambino}")
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
                            """, 
                            unsafe_allow_html=True
                        )
                    
                    with box_residenza:
                        st.markdown("#### 📍 Nascita e Residenza")
                        data_nascita_val = riga_bambino[col_nascita]
                        if pd.notnull(data_nascita_val):
                            try:
                                data_nascita_str = pd.to_datetime(data_nascita_val).strftime('%d/%m/%Y')
                            except:
                                data_nascita_str = str(data_nascita_val)
                        else:
                            data_nascita_str = "Dato mancante"
                            
                        indirizzo_completo = f"{riga_bambino[col_via]}, {riga_bambino[col_civico]}"
                        citta_completa = f"{riga_bambino[col_cap]} - {riga_bambino[col_citta]}"
                        
                        st.markdown(
                            f"""
                            <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; min-height: 220px;">
                                <p style="margin-bottom: 8px;"><b>Nato/a il:</b> {data_nascita_str}<br><b>a:</b> {riga_bambino[col_luogo]}</p>
                                <p style="margin-bottom: 8px;"><b>Indirizzo:</b><br>{indirizzo_completo}</p>
                                <p style="margin-bottom: 0;"><b>Città:</b><br>{citta_completa}</p>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                    
                    with box_sanitario:
                        st.markdown("#### ⚠️ Informazioni Sanitarie")
                        ha_allergie = str(riga_bambino[col_allergie]).strip().upper()
                        
                        if ha_allergie in ["SÌ", "SI", "YES", "Vero", "TRUE"]:
                            colore_sfondo = "#fef2f2"
                            colore_bordo = "#f87171"
                            icona_stato = "🚨"
                            dettaglio_allergie = f"<b>Quali:</b><br><span style='color: #b91c1c; font-weight: bold;'>{riga_bambino[col_quali]}</span>"
                        else:
                            colore_sfondo = "#f0fdf4"
                            colore_bordo = "#4ade80"
                            icona_stato = "✅"
                            dettaglio_allergie = "<i>Nessuna allergia o intolleranza segnalata.</i>"
                        
                        st.markdown(
                            f"""
                            <div style="background-color: {colore_sfondo}; padding: 15px; border-radius: 8px; border: 1px solid {colore_bordo}; min-height: 220px;">
                                <p style="font-size: 16px; margin-bottom: 12px;"><b>Stato:</b> {icona_stato} {ha_allergie}</p>
                                <p style="margin-bottom: 0; font-size: 14px;">{dettaglio_allergie}</p>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )

                elif st.session_state.scheda_attiva == "genitore":
                    # --- VISTA DATI GENITORE & FRATELLI ---
                    st.markdown(f"### Riferimenti Familiari: {nome_completo_genitore}")
                    
                    tel_g_grezzo = str(riga_bambino[col_g_tel])
                    tel_g_pulito = tel_g_grezzo.replace(" ", "").replace("/", "").replace("-", "").strip()
                    if tel_g_pulito.endswith(".0"):
                        tel_g_pulito = tel_g_pulito[:-2]

                    data_n_g_val = riga_bambino[col_g_nascita]
                    data_n_g_str = pd.to_datetime(data_n_g_val).strftime('%d/%m/%Y') if pd.notnull(data_n_g_val) else "Dato mancante"
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
                            """, 
                            unsafe_allow_html=True
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
                            """, 
                            unsafe_allow_html=True
                        )
                    
                    # Se ci sono fratelli, mostriamo la sezione dedicata
                    if not fratelli.empty:
                        st.markdown("---")
                        st.markdown("### 👦 Altri figli iscritti a carico di questo genitore:")
                        st.info("Abbiamo rilevato altri iscritti registrati con gli stessi contatti familiari. Clicca per saltare direttamente alla loro scheda:")
                        
                        for idx_fratello, riga_fratello in fratelli.iterrows():
                            nome_fratello = f"{riga_fratello[col_cognome]} {riga_fratello[col_nome]}".upper()
                            
                            btn_col1, btn_col2 = st.columns([3, 1])
                            with btn_col1:
                                st.write(f"🧑‍🤝‍🧑 **{nome_fratello}** (Codice Fiscale: `{riga_fratello[col_cf]}`)")
                            with btn_col2:
                                # Premendo il pulsante del fratello:
                                # 1. Selezioniamo il nuovo id
                                # 2. Impostiamo programmaticamente la scheda attiva su "bambino"
                                # 3. Ricarichiamo la pagina per applicare il cambio
                                if st.button(f"Vedi scheda di {riga_fratello[col_nome]} 📂", key=f"btn_fratello_{idx_fratello}"):
                                    st.session_state.id_bambino_corrente = idx_fratello
                                    st.session_state.scheda_attiva = "bambino" # <--- SPOSTAMENTO FORZATO E SICURO
                                    st.rerun()
                
                elif st.session_state.scheda_attiva == "settimane":
                    # --- VISTA SETTIMANE DI ISCRIZIONE ---
                    st.markdown(f"### 📅 Calendario Settimanale: {nome_completo_bambino}")
                    st.write("Verifica in quali settimane l'iscritto risulta registrato ed ha confermato la frequenza:")
                    
                    if colonne_settimane:
                        # Creiamo una griglia responsive di card (es. 4 colonne per riga)
                        col_cards = st.columns(4)
                        
                        for i, col_settimana in enumerate(colonne_settimane):
                            valore_iscrizione = str(riga_bambino[col_settimana]).strip().upper()
                            
                            # Definiamo se è iscritto o meno
                            # Copriamo valori come "SI", "SÌ", "YES", "ISCRITTO", o valori booleani True
                            is_iscritto = valore_iscrizione in ["SÌ", "SI", "YES", "TRUE", "VERO", "ISCRITTO", "1", "1.0"]
                            
                            # Calcolo della colonna in cui inserire la card
                            col_index = i % 4
                            
                            with col_cards[col_index]:
                                if is_iscritto:
                                    colore_card = "#ecfdf5"  # Verde chiarissimo
                                    colore_bordo = "#10b981" # Verde smeraldo
                                    badge_html = "<span style='background-color: #10b981; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;'>ISCRITTO ✅</span>"
                                else:
                                    colore_card = "#f8fafc"  # Grigio chiaro
                                    colore_bordo = "#cbd5e1" # Grigio scuro
                                    badge_html = "<span style='background-color: #94a3b8; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;'>NON ATTIVO ❌</span>"
                                
                                # Visualizzazione della Card HTML elegante
                                st.markdown(
                                    f"""
                                    <div style="background-color: {colore_card}; border: 1px solid {colore_bordo}; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px; min-height: 120px;">
                                        <h5 style="margin-top: 0; margin-bottom: 12px; color: #1e293b; font-size: 15px;">{col_settimana}</h5>
                                        <div style="margin-top: 8px;">{badge_html}</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                
                        # Piccolo riepilogo testuale rapido
                        settimane_attive = []
                        for col_settimana in colonne_settimane:
                            valore = str(riga_bambino[col_settimana]).strip().upper()
                            if valore in ["SÌ", "SI", "YES", "TRUE", "VERO", "ISCRITTO", "1", "1.0"]:
                                settimane_attive.append(col_settimana)
                                
                        st.markdown("###")
                        if settimane_attive:
                            st.success(f"📌 **Riepilogo:** {riga_bambino[col_nome]} frequenta un totale di **{len(settimane_attive)} settimane** su {len(colonne_settimane)} disponibili.")
                        else:
                            st.warning(f"⚠️ **Attenzione:** Questo iscritto non risulta registrato in nessuna delle settimane disponibili.")
                    else:
                        st.error("⚠️ Non ho trovato colonne che contengono la parola 'Settimana' nel tuo foglio Excel. Verifica che i nomi delle colonne nel file corrispondano!")

    else:
        st.info("Carica il file Excel per abilitare la ricerca anagrafica.")


# ==========================================
# 3. SEZIONE: ELENCHI SETTIMANALI (Futura)
# ==========================================
elif st.session_state.pagina_corrente == "Elenchi Settimanali":
    st.title("📅 Elenchi Settimanali")
    st.info("🚧 Questa sezione è in fase di sviluppo. Qui potrai visualizzare e gestire le presenze e i gruppi settimana per settimana.")


# ==========================================
# 4. SEZIONE: GESTIONE PAGAMENTI (Futura)
# ==========================================
elif st.session_state.pagina_corrente == "Gestione Pagamenti":
    st.title("💳 Gestione Pagamenti")
    st.info("🚧 Questa sezione è in fase di sviluppo. Qui potrai monitorare le quote di iscrizione, i saldi e registrare i pagamenti ricevuti.")