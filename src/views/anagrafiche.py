import streamlit as st
import pandas as pd

# Stile compatto
st.markdown("""
    <style>
        .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
        .stVerticalBlock { gap: 0.5rem !important; }
        hr { margin: 0.8rem 0 !important; }
        h1, h2, h3, h4 { margin-bottom: 0.2rem !important; padding-bottom: 0 !important; }
    </style>
""", unsafe_allow_html=True)

def mostra_anagrafiche(df_iscritti):
    st.title("👤 Ricerca e Gestione Anagrafiche")
    
    # Inizializzazione stato
    if "id_bambino_corrente" not in st.session_state: st.session_state.id_bambino_corrente = None
    if "scheda_attiva" not in st.session_state: st.session_state.scheda_attiva = "bambino"
    if "modalita_modifica" not in st.session_state: st.session_state.modalita_modifica = False

    # Mappatura colonne
    colonne_reali = list(df_iscritti.columns)
    col_g_email, col_g_cognome, col_g_nome, col_g_tel, col_g_nascita, col_g_cf = colonne_reali[1:7]
    col_cognome, col_nome, col_nascita, col_luogo, col_via, col_civico, col_cap, col_citta, col_cf, col_allergie, col_quali = colonne_reali[7:18]
    colonne_settimane = [col for col in colonne_reali if "settiman" in str(col).lower()]

    # Ricerca
    df_iscritti_ordinato = df_iscritti.sort_values(by=[col_cognome, col_nome])
    opzioni_ricerca = df_iscritti_ordinato[col_cognome].astype(str).str.upper() + " " + df_iscritti_ordinato[col_nome].astype(str).str.title() + " (" + df_iscritti_ordinato[col_cf].astype(str).str.upper() + ")"
    mappa_opzioni = dict(zip(opzioni_ricerca, df_iscritti_ordinato.index))
    
    indice_corrente = None
    if st.session_state.id_bambino_corrente is not None:
        for i, (opt_str, idx_val) in enumerate(mappa_opzioni.items()):
            if idx_val == st.session_state.id_bambino_corrente:
                indice_corrente = i
                break

    scelta_utente = st.selectbox("Cerca un iscritto:", list(mappa_opzioni.keys()), index=indice_corrente, key="ricerca_dinamica_selectbox")
    
    if scelta_utente is not None:
        id_selezionato = mappa_opzioni.get(scelta_utente)
        if st.session_state.id_bambino_corrente != id_selezionato:
            st.session_state.id_bambino_corrente = id_selezionato
            st.session_state.scheda_attiva = "bambino"
            st.session_state.modalita_modifica = False
            st.rerun()

    if st.session_state.id_bambino_corrente is not None:
        riga_bambino = df_iscritti.loc[st.session_state.id_bambino_corrente]
        riga_index = st.session_state.id_bambino_corrente
        
        # Header
        st.markdown(f'<div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 20px; border-radius: 10px; margin-bottom: 25px;"><h2 style="color: white; margin: 0;">👦 {riga_bambino[col_cognome].upper()} {riga_bambino[col_nome].title()}</h2></div>', unsafe_allow_html=True)

        # Tab Navigation
        c1, c2, c3 = st.columns(3)
        if c1.button("👦 Dati Bambino", type="primary" if st.session_state.scheda_attiva=="bambino" else "secondary", use_container_width=True): 
            st.session_state.scheda_attiva="bambino"; st.session_state.modalita_modifica=False; st.rerun()
        if c2.button("👨‍👩‍👧 Contatti Genitore", type="primary" if st.session_state.scheda_attiva=="genitore" else "secondary", use_container_width=True): 
            st.session_state.scheda_attiva="genitore"; st.session_state.modalita_modifica=False; st.rerun()
        if c3.button("📅 Settimane", type="primary" if st.session_state.scheda_attiva=="settimane" else "secondary", use_container_width=True): 
            st.session_state.scheda_attiva="settimane"; st.session_state.modalita_modifica=False; st.rerun()

        # TAB BAMBINO
        if st.session_state.scheda_attiva == "bambino":
            if st.session_state.modalita_modifica:
                with st.form("form_unificato"):
                    st.subheader("📝 Modifica Dati (Bambino + Genitore)")
                    col1, col2 = st.columns(2)
                    e_cog = col1.text_input("Cognome Bambino", value=str(riga_bambino[col_cognome]))
                    e_nom = col2.text_input("Nome Bambino", value=str(riga_bambino[col_nome]))
                    e_g_tel = st.text_input("Telefono Genitore", value=str(riga_bambino[col_g_tel]))
                    e_g_email = st.text_input("Email Genitore", value=str(riga_bambino[col_g_email]))
                    if st.form_submit_button("💾 Salva Modifiche"):
                        df_iscritti.at[riga_index, col_cognome] = e_cog.upper()
                        df_iscritti.at[riga_index, col_g_tel] = e_g_tel
                        df_iscritti.at[riga_index, col_g_email] = e_g_email
                        df_iscritti.to_excel("iscritti.xlsx", index=False)
                        st.session_state.modalita_modifica = False
                        st.rerun()
            else:
                # BOX VISTA STATICA
                box1, box2, box3 = st.columns(3)
                box1.markdown(f"**Cognome:** {riga_bambino[col_cognome]}")
                box2.markdown(f"**Città:** {riga_bambino[col_citta]}")
                box3.markdown(f"**Allergie:** {riga_bambino[col_allergie]}")
                if st.button("✏️ Modifica Anagrafica"): st.session_state.modalita_modifica = True; st.rerun()

        # TAB GENITORE
        elif st.session_state.scheda_attiva == "genitore":
            st.write(f"### 📞 Contatti Genitore: {riga_bambino[col_g_cognome]} {riga_bambino[col_g_nome]}")
            st.info(f"Telefono: {riga_bambino[col_g_tel]} | Email: {riga_bambino[col_g_email]}")
            
            # Fratelli
            fratelli = df_iscritti[((df_iscritti[col_g_cf] == riga_bambino[col_g_cf]) & (pd.notnull(df_iscritti[col_g_cf]))) | ((df_iscritti[col_g_email] == riga_bambino[col_g_email]) & (pd.notnull(df_iscritti[col_g_email])))]
            fratelli = fratelli.drop(riga_index, errors='ignore')
            if not fratelli.empty:
                st.write("---")
                st.write("### 👦 Fratelli:")
                for idx_f, r_f in fratelli.iterrows():
                    if st.button(f"Vedi scheda di {r_f[col_nome]} 📂", key=f"btn_{idx_f}"):
                        st.session_state.id_bambino_corrente = idx_f
                        st.session_state.scheda_attiva = "bambino"
                        st.rerun()