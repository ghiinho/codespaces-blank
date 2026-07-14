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
    st.write("Qui inseriremo la ricerca del singolo bambino e la visualizzazione ordinata della sua scheda.")
    
    # Spazio di lavoro temporaneo per farti vedere che i dati ci sono
    st.dataframe(df_iscritti.head(5), use_container_width=True)


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