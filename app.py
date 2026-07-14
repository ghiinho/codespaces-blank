import streamlit as st
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
# ==========================================
# 2. SEZIONE: ANAGRAFICHE ISCRITTI
# ==========================================
elif st.session_state.pagina_corrente == "Anagrafiche Iscritti":
    st.title("👤 Ricerca Schede Anagrafiche")
    st.write("Inserisci il cognome dell'iscritto per visualizzare i dati dedicati (Colonne H-R).")
    st.markdown("---")
    
    if not df_iscritti.empty:
        # Recuperiamo la colonna del cognome (ipotizzando sia la seconda colonna, indice 1, se non si chiama "Cognome")
        colonne_reali = list(df_iscritti.columns)
        colonne_pulite = [c.strip().lower() for c in colonne_reali]
        col_cognome = colonne_reali[colonne_pulite.index('cognome')] if 'cognome' in colonne_pulite else colonne_reali[1]
        
        # --- MOTORE DI RICERCA CON BOTTONE ---
        # Creiamo una riga con due colonne: una larga per il testo e una stretta per il bottone
        col_ricerca, col_bottone = st.columns([4, 1])
        
        with col_ricerca:
            cognome_input = st.text_input("🔍 Inserisci il Cognome da cercare:", placeholder="Es. Rossi...")
            
        with col_bottone:
            st.write("##") # Spazio per allineare il bottone alla casella di testo
            avvia_ricerca = st.button("Avvia Ricerca 🚀", use_container_width=True)
            
        # Stato della ricerca (mantiene i risultati a schermo anche dopo l'interazione)
        if "risultato_ricerca" not in st.session_state:
            st.session_state.risultato_ricerca = None

        if avvia_ricerca and cognome_input:
            # Filtro parziale: trova tutti i bambini il cui cognome contiene il testo cercato (ignorando maiuscole/minuscole)
            risultati = df_iscritti[df_iscritti[col_cognome].astype(str).str.lower().str.contains(cognome_input.strip().lower())]
            st.session_state.risultato_ricerca = risultati
        
        # --- MOSTRA I RISULTATI TROVATI ---
        if st.session_state.risultato_ricerca is not None:
            df_filtrato = st.session_state.risultato_ricerca
            
            if df_filtrato.empty:
                st.warning(f"❌ Nessun iscritto trovato con il cognome '{cognome_input}'. Riprova.")
            else:
                st.success(f"📋 Trovati {len(df_filtrato)} iscritti corrispondenti.")
                
                # Se ci sono più iscritti con lo stesso cognome, permettiamo di selezionare quello corretto
                if len(df_filtrato) > 1:
                    col_nome_fallback = colonne_reali[colonne_pulite.index('nome')] if 'nome' in colonne_pulite else colonne_reali[2]
                    scelte = df_filtrato[col_cognome].astype(str) + " " + df_filtrato[col_nome_fallback].astype(str)
                    bambino_scelto = st.radio("Seleziona l'iscritto specifico da visualizzare:", scelte)
                    # Estraiamo la riga specifica
                    indice_scelto = scelte[scelte == bambino_scelto].index[0]
                    riga_bambino = df_filtrato.loc[indice_scelto]
                else:
                    # Se è solo uno, lo prendiamo direttamente
                    riga_bambino = df_filtrato.iloc[0]
                
                st.markdown("##")
                st.markdown(f"### 📋 Dati Estratti (Colonne H - R)")
                
                # --- VISUALIZZAZIONE DELLE COLONNE DA H A R ---
                # In Python gli indici partono da 0. La colonna H corrisponde all'indice 7, la colonna R all'indice 17.
                # Prendiamo in sicurezza le colonne in quel range presenti nel tuo file Excel
                colonne_da_mostrare = colonne_reali[7:18] # Prende gli indici da 7 a 17 inclusi
                
                # Layout pulito a riquadri per incolonnare le informazioni da H a R
                st.markdown("<div style='background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #cbd5e1;'>", unsafe_allow_html=True)
                
                # Dividiamo le informazioni in due colonne visive all'interno del riquadro per dare ordine
                sub_col1, sub_col2 = st.columns(2)
                
                for i, colonna in enumerate(colonne_da_mostrare):
                    # Distribuiamo i campi un po' a sinistra e un po' a destra
                    if i % 2 == 0:
                        with sub_col1:
                            st.write(f"📌 **{colonna}:** {riga_bambino[colonna]}")
                    else:
                        with sub_col2:
                            st.write(f"📌 **{colonna}:** {riga_bambino[colonna]}")
                            
                st.markdown("</div>", unsafe_allow_html=True)

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