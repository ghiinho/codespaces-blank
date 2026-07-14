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

# --- BARRA LATERALE PER TORNARE SEMPRE ALLA HOME ---
with st.sidebar:
    st.markdown("### ☀️ Centro Estivo")
    if st.button("🏠 Torna alla Home Page", use_container_width=True):
        naviga_a("Home")
    st.markdown("---")
    st.caption("Fatto con ❤️ per la simulazione del gestionale")

# ==========================================
# 1. PAGINA PRINCIPALE: HOME PAGE A RIQUADRI
# ==========================================
if st.session_state.pagina_corrente == "Home":
    st.title("Plancia di Comando - Centro Estivo")
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
        
        # Mappatura colonne H-R (indici 7-17)
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

        # --- MOTORE DI RICERCA ---
        col_ricerca, col_bottone = st.columns([4, 1])
        
        with col_ricerca:
            cognome_input = st.text_input("🔍 Inserisci il Cognome da cercare:", placeholder="Es. Rossi...")
            
        with col_bottone:
            st.write("##") # Allineamento verticale del bottone
            avvia_ricerca = st.button("Avvia Ricerca 🚀", use_container_width=True)
            
        if "risultato_ricerca" not in st.session_state:
            st.session_state.risultato_ricerca = None

        if avvia_ricerca and cognome_input:
            risultati = df_iscritti[df_iscritti[col_cognome].astype(str).str.lower().str.contains(cognome_input.strip().lower())]
            st.session_state.risultato_ricerca = risultati
        
        # --- MOSTRA I RISULTATI TROVATI ---
        if st.session_state.risultato_ricerca is not None:
            df_filtrato = st.session_state.risultato_ricerca
            
            if df_filtrato.empty:
                st.warning(f"❌ Nessun iscritto trovato con il cognome '{cognome_input}'. Riprova.")
            else:
                st.success(f"📋 Trovati {len(df_filtrato)} iscritti corrispondenti.")
                
                # Selezione in caso di omonimia
                if len(df_filtrato) > 1:
                    scelte = df_filtrato[col_cognome].astype(str) + " " + df_filtrato[col_nome].astype(str)
                    bambino_scelto = st.radio("Seleziona l'iscritto specifico da visualizzare:", scelte)
                    indice_scelto = scelte[scelte == bambino_scelto].index[0]
                    riga_bambino = df_filtrato.loc[indice_scelto]
                else:
                    riga_bambino = df_filtrato.iloc[0]
                
                st.markdown("##")
                nome_completo = f"{riga_bambino[col_cognome]} {riga_bambino[col_nome]}".upper()
                
                # --- STRUTTURA A TAB PER BAMBINO / GENITORE ---
                tab_bambino, tab_genitore = st.tabs(["👦 Dati Bambino", "👨‍👩‍👧 Contatti Genitore"])
                
                # --- TAB 1: DATI BAMBINO ---
                with tab_bambino:
                    st.markdown(f"### Scheda Personale: {nome_completo}")
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

                # --- TAB 2: DATI GENITORE ---
                with tab_genitore:
                    st.markdown(f"### 👨‍👩‍👧 Riferimenti Familiari per: {nome_completo}")
                    
                    # Layout organizzato in due colonne per i dati di contatto
                    g_col1, g_col2 = st.columns(2)
                    
                    with g_col1:
                        st.markdown("#### 👤 Dati di Contatto")
                        # Qui andremo ad inserire i riferimenti reali del tuo file Excel.
                        # Per ora inserisco dei dati fittizi leggendo alcune colonne di esempio
                        # (es. colonne da A a G o le ultimissime del file)
                        st.markdown(
                            f"""
                            <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; min-height: 180px;">
                                <p style="font-size: 16px; margin-bottom: 8px;"><b>Genitore / Tutore di Riferimento:</b></p>
                                <p style="font-size: 15px; color: #0369a1; font-weight: bold; margin-bottom: 12px;">Da collegare alle tue colonne Excel</p>
                                <p style="margin-bottom: 6px;"><b>📞 Telefono Primario:</b> [Colonna da definire]</p>
                                <p style="margin-bottom: 0;"><b>✉️ Email:</b> [Colonna da definire]</p>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        
                    with g_col2:
                        st.markdown("#### 📝 Informazioni Aggiuntive")
                        st.info("Qui possiamo mostrare note sul ritiro (es. deleghe, chi è autorizzato a prendere il bambino) o contatti di emergenza secondari.")

    else:
        st.info("Carica il file Excel per abilitare la ricerca anagrafica.")


# ==========================================
# 3. SEZIONE: ELENCHI SETTIMANALI
# ==========================================
elif st.session_state.pagina_corrente == "Elenchi Settimanali":
    st.title("📅 Sezione: Elenchi Settimanali")
    st.write("Qui metteremo il filtro (es. 'Settimana 1') per vedere l'elenco dei soli bambini iscritti in quella settimana.")


# ==========================================
# 4. SEZIONE: GESTIONE PAGAMENTI
# ==========================================
elif st.session_state.pagina_corrente == "Gestione Pagamenti":
    st.title("💰 Sezione: Gestione Pagamenti")
    st.write("Qui metteremo i resoconti dei soldi incassati, da incassare e i calcoli delle tariffe.")