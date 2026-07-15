import streamlit as st

def disegna_sidebar():
    st.sidebar.title("🧭 Navigazione")
    st.sidebar.write("Seleziona la sezione del gestionale:")
    
    # Inizializziamo lo stato della pagina se non esiste
    if "pagina_corrente" not in st.session_state:
        st.session_state.pagina_corrente = "Home Page"
        
    # Pulsante 1: Home Page
    if st.sidebar.button("🏠 Torna alla Home Page", use_container_width=True):
        st.session_state.pagina_corrente = "Home Page"
        st.rerun()
        
    # Pulsante 2: Anagrafiche (con RESET integrato)
    if st.sidebar.button("👤 Vai alle anagrafiche", use_container_width=True):
        st.session_state.id_bambino_corrente = None
        st.session_state.risultato_ricerca = None
        st.session_state.scheda_attiva = "bambino"
        if "ricerca_cognome" in st.session_state:
            st.session_state.ricerca_cognome = ""
        st.session_state.pagina_corrente = "Anagrafiche Iscritti"
        st.rerun()
        
    # Pulsante 3: Elenchi Settimanali (Futuro)
    if st.sidebar.button("📅 Elenchi Settimanali", use_container_width=True):
        st.session_state.pagina_corrente = "Elenchi Settimanali"
        st.rerun()