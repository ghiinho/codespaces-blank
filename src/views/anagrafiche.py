import streamlit as st

def inizializza_stato():
    if "id_selezionato" not in st.session_state:
        st.session_state.id_selezionato = None
    if "scheda_attiva" not in st.session_state:
        st.session_state.scheda_attiva = "bambino"

def mostra_anagrafiche(df):
    inizializza_stato()
    
    st.title("Gestione Anagrafiche")
    
    # Logica di ricerca (come definita prima)
    df_ordinato = df.sort_values(by=["Cognome", "Nome"])
    lista_opzioni = (
        df_ordinato["Cognome"].astype(str).str.upper() + " " + 
        df_ordinato["Nome"].astype(str).str.title() + " (" + 
        df_ordinato["Codice Fiscale"].astype(str).str.upper() + ")"
    ).tolist()
    mappa = dict(zip(lista_opzioni, df_ordinato.index))
    
    indice_default = None
    if st.session_state.id_selezionato in mappa.values():
        valore = [k for k, v in mappa.items() if v == st.session_state.id_selezionato][0]
        indice_default = lista_opzioni.index(valore)

    scelta = st.selectbox("Cerca un iscritto:", options=lista_opzioni, index=indice_default, key="input_ricerca")
    
    if scelta and mappa[scelta] != st.session_state.id_selezionato:
        st.session_state.id_selezionato = mappa[scelta]
        st.session_state.scheda_attiva = "bambino"
        st.rerun()

    # Visualizzazione scheda se un iscritto è selezionato
    if st.session_state.id_selezionato is not None:
        dati_bambino = df.loc[st.session_state.id_selezionato]
        st.write(f"### Dati di {dati_bambino['Nome']}")
        # Qui continueresti con i tuoi tab...