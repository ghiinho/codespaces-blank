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
elif st.session_state.pagina_corrente == "Anagrafiche Iscritti":
    st.title("👤 Sezione: Anagrafiche Iscritti")
    st.write("Seleziona un bambino per visualizzare, ordinare o modificare la sua scheda personale in tempo reale.")
    st.markdown("---")
    
    if not df_iscritti.empty:
        # --- 1. MOTORE DI RICERCA INTELLIGENTE ---
        # Tentiamo di creare il nominativo combinando Cognome e Nome (gestendo maiuscole/minuscole delle colonne)
        colonne_pulite = [c.strip().lower() for c in df_iscritti.columns]
        
        col_cognome = df_iscritti.columns[colonne_pulite.index('cognome')] if 'cognome' in colonne_pulite else df_iscritti.columns[1]
        col_nome = df_iscritti.columns[colonne_pulite.index('nome')] if 'nome' in colonne_pulite else df_iscritti.columns[2]
        
        # Creiamo la colonna virtuale per la ricerca
        df_iscritti['Nominativo_Cerca'] = df_iscritti[col_cognome].astype(str) + " " + df_iscritti[col_nome].astype(str)
        lista_bambini = sorted(df_iscritti['Nominativo_Cerca'].unique())
        
        # Barra di ricerca/selezione in alto
        bambino_selezionato = st.selectbox(
            "🔍 Digita o seleziona il cognome/nome del bambino:",
            lista_bambini
        )
        
        # Estraiamo i dati del bambino scelto
        riga_bambino = df_iscritti[df_iscritti['Nominativo_Cerca'] == bambino_selezionato].iloc[0]
        
        st.markdown("##")
        
        # --- 2. INTERFACCIA GRAFICA DELLA SCHEDA ANAGRAFICA ---
        # Dividiamo la scheda in 3 macro-aree visive (Colonne)
        scheda_col1, scheda_col2, scheda_col3 = st.columns(3)
        
        with scheda_col1:
            st.markdown("### 📝 Dati Anagrafici e Personali")
            # Mostriamo in modo pulito le prime informazioni fondamentali del file Excel
            # (Qui agganceremo i tuoi campi specifici come Telefono, intolleranze, classe...)
            st.markdown("<div style='background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
            
            # Recuperiamo e stampiamo le prime 6 colonne reali del tuo file in modo ordinato
            for colonna in df_iscritti.columns[:6]:
                if colonna != 'Nominativo_Cerca':
                    st.write(f"**{colonna}:** {riga_bambino[colonna]}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with scheda_col2:
            st.markdown("### 📅 Presenze e Settimane")
            st.markdown("<div style='background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
            st.write("Qui collegheremo i selettori per mettere o togliere i 'Sì/No' alle tue settimane reali.")
            
            # Esempio visivo: prende un blocco centrale di colonne (es. da colonna 7 a 15) dove di solito risiedono le settimane
            for colonna in df_iscritti.columns[6:14]:
                if colonna != 'Nominativo_Cerca':
                    st.write(f"🔹 **{colonna}:** {riga_bambino[colonna]}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with scheda_col3:
            st.markdown("### 💰 Riepilogo Contabile")
            st.markdown("<div style='background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
            st.write("Qui estrarremo la situazione dei pagamenti, acconti e il calcolo automatico.")
            
            # Esempio visivo: prende le colonne finali del tuo Excel
            for colonna in df_iscritti.columns[14:22]:
                if colonna != 'Nominativo_Cerca':
                    st.write(f"💵 **{colonna}:** {riga_bambino[colonna]}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        # --- 3. TABELLA COMPLETA DI SUPPORTO IN BASSO ---
        st.markdown("---")
        st.subheader("📋 Vista Tabella Completa (Solo per questo iscritto)")
        st.write("Se preferisci una visualizzazione tabellare vecchio stile di tutte le sue 34 colonne contemporaneamente:")
        # Mostriamo l'intera riga del bambino con tutte le sue colonne da A ad AH in formato orizzontale
        st.dataframe(df_iscritti[df_iscritti['Nominativo_Cerca'] == bambino_selezionato].drop(columns=['Nominativo_Cerca']), use_container_width=True)

    else:
        st.info("Carica il file Excel per visualizzare le anagrafiche.")


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