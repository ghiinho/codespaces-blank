import streamlit as st
import pandas as pd

# Riduciamo gli spazi verticali nativi di Streamlit per compattare la pagina
st.markdown(
    """
    <style>
        .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
        .stVerticalBlock { gap: 0.5rem !important; }
        hr { margin: 0.8rem 0 !important; }
        h1, h2, h3, h4 { margin-bottom: 0.2rem !important; padding-bottom: 0 !important; }
    </style>
    """,
    unsafe_allow_html=True
)

def mostra_anagrafiche(df_iscritti):
    st.title("👤 Ricerca e Gestione Anagrafiche")
    st.write("Visualizza, modifica o aggiorna i dati personali, sanitari e i contatti di ciascun iscritto.")
    
    if df_iscritti.empty:
        st.info("Carica il file Excel per abilitare la gestione anagrafica.")
        return

    # --- INIZIALIZZAZIONE STATO ---
    if "id_bambino_corrente" not in st.session_state: st.session_state.id_bambino_corrente = None
    if "scheda_attiva" not in st.session_state: st.session_state.scheda_attiva = "bambino"
    if "modalita_modifica" not in st.session_state: st.session_state.modalita_modifica = False

    # --- MAPPATURA COLONNE ---
    colonne_reali = list(df_iscritti.columns)
    col_g_email, col_g_cognome, col_g_nome, col_g_tel, col_g_nascita, col_g_cf = colonne_reali[1:7]
    col_cognome, col_nome, col_nascita, col_luogo, col_via, col_civico, col_cap, col_citta, col_cf, col_allergie, col_quali = colonne_reali[7:18]
    colonne_settimane = [col for col in colonne_reali if "settiman" in str(col).lower()]

    # --- PREPARAZIONE LISTA DI RICERCA ---
    df_iscritti_ordinato = df_iscritti.sort_values(by=[col_cognome, col_nome])
    opzioni_ricerca = (df_iscritti_ordinato[col_cognome].astype(str).str.upper() + " " + 
                       df_iscritti_ordinato[col_nome].astype(str).str.title() + " (" + 
                       df_iscritti_ordinato[col_cf].astype(str).str.upper() + ")")
    
    mappa_opzioni = dict(zip(opzioni_ricerca, df_iscritti_ordinato.index))
    lista_selectbox = list(opzioni_ricerca)

    # --- RICERCA DINAMICA ---
    col_ricerca, _ = st.columns([3, 2])
    
    # Indice dinamico: si aggiorna da solo se id_bambino_corrente cambia
    indice_corrente = None
    if st.session_state.id_bambino_corrente is not None:
        for i, (opt_str, idx_val) in enumerate(mappa_opzioni.items()):
            if idx_val == st.session_state.id_bambino_corrente:
                indice_corrente = i
                break

    with col_ricerca:
        scelta_utente = st.selectbox(
            "Cerca un iscritto:",
            options=lista_selectbox,
            index=indice_corrente,
            placeholder="🔍 Digita il cognome o nome...",
            key="ricerca_dinamica_selectbox"
        )

    # Logica cambio bambino: RESETTA SCHEDA SU BAMBINO
    if scelta_utente is not None:
        id_selezionato = mappa_opzioni.get(scelta_utente)
        if st.session_state.id_bambino_corrente != id_selezionato:
            st.session_state.id_bambino_corrente = id_selezionato
            st.session_state.scheda_attiva = "bambino" # <-- RESETTA SCHEDA
            st.session_state.modalita_modifica = False
            st.rerun()

    # --- VISUALIZZAZIONE DATI ---
    if st.session_state.id_bambino_corrente is not None:
        riga_bambino = df_iscritti.loc[st.session_state.id_bambino_corrente]
        riga_index = st.session_state.id_bambino_corrente
        nome_completo = f"{str(riga_bambino[col_cognome]).upper()} {str(riga_bambino[col_nome]).title()}"
        nome_completo_genitore = f"{riga_bambino[col_g_cognome]} {riga_bambino[col_g_nome]}".upper()
        
        fratelli = df_iscritti[((df_iscritti[col_g_cf] == riga_bambino[col_g_cf]) & (pd.notnull(df_iscritti[col_g_cf]))) |
                               ((df_iscritti[col_g_email] == riga_bambino[col_g_email]) & (pd.notnull(df_iscritti[col_g_email])))]
        fratelli = fratelli.drop(riga_index, errors='ignore')

        # Header
        st.markdown(f'<div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 20px; border-radius: 10px; margin-bottom: 25px;"><h2 style="color: white; margin: 0;">👦 {nome_completo}</h2></div>', unsafe_allow_html=True)

        # Tab Navigation
        c1, c2, c3 = st.columns(3)
        if c1.button("👦 Dati Bambino", type="primary" if st.session_state.scheda_attiva=="bambino" else "secondary", use_container_width=True):
            st.session_state.scheda_attiva = "bambino"; st.session_state.modalita_modifica = False; st.rerun()
        if c2.button("👨‍👩‍👧 Contatti Genitore", type="primary" if st.session_state.scheda_attiva=="genitore" else "secondary", use_container_width=True):
            st.session_state.scheda_attiva = "genitore"; st.session_state.modalita_modifica = False; st.rerun()
        if c3.button("📅 Settimane Iscrizione", type="primary" if st.session_state.scheda_attiva=="settimane" else "secondary", use_container_width=True):
            st.session_state.scheda_attiva = "settimane"; st.session_state.modalita_modifica = False; st.rerun()

        # LOGICA TAB BAMBINO
        if st.session_state.scheda_attiva == "bambino":
            if st.session_state.modalita_modifica:
                with st.form("form_unificato"):
                    st.subheader("Modifica Dati Completi")
                    e_cog = st.text_input("Cognome", value=riga_bambino[col_cognome])
                    e_nom = st.text_input("Nome", value=riga_bambino[col_nome])
                    e_cf = st.text_input("CF", value=riga_bambino[col_cf])
                    e_g_tel = st.text_input("Telefono Genitore", value=riga_bambino[col_g_tel])
                    e_g_email = st.text_input("Email Genitore", value=riga_bambino[col_g_email])
                    
                    if st.form_submit_button("💾 Salva"):
                        df_iscritti.at[riga_index, col_cognome] = e_cog.upper()
                        df_iscritti.at[riga_index, col_g_tel] = e_g_tel
                        # ... (aggiungi qui gli altri campi che vuoi salvare)
                        df_iscritti.to_excel("iscritti.xlsx", index=False)
                        st.session_state.modalita_modifica = False
                        st.rerun()
            else:
                st.write("Visualizzazione dati...") # Inserisci qui i tuoi box
                if st.button("✏️ Modifica Anagrafica"):
                    st.session_state.modalita_modifica = True; st.rerun()

        # LOGICA TAB GENITORE
        elif st.session_state.scheda_attiva == "genitore":
            st.write(f"Contatti di {nome_completo_genitore}")
            if not fratelli.empty:
                for idx_f, r_f in fratelli.iterrows():
                    if st.button(f"Vedi fratello: {r_f[col_nome]}", key=f"f_{idx_f}"):
                        st.session_state.id_bambino_corrente = idx_f
                        st.session_state.scheda_attiva = "bambino"
                        st.rerun()