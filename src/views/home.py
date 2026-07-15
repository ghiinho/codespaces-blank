import streamlit as st

def mostra_home():
    st.title("☀️ Campus Estivo - Dashboard Gestionale")
    st.write("Benvenuto nel pannello di controllo. Seleziona una delle funzionalità rapide qui sotto o usa la barra laterale per navigare.")
    st.markdown("---")

    # Creiamo una griglia di card usando le colonne di Streamlit
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; min-height: 180px; margin-bottom: 20px;">
                <h3 style="margin-top: 0; color: #0f172a;">👤 Anagrafiche Iscritti</h3>
                <p style="color: #64748b; font-size: 14px;">Cerca le schede dei bambini, visualizza i contatti di emergenza dei genitori e gestisci le settimane di iscrizione.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button("Vai ad Anagrafiche ➡️", use_container_width=True, key="card_anagrafiche"):
            st.session_state.pagina_corrente = "Anagrafiche Iscritti"
            st.rerun()

    with col2:
        st.markdown(
            """
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; min-height: 180px; margin-bottom: 20px;">
                <h3 style="margin-top: 0; color: #0f172a;">📊 Statistiche e Report</h3>
                <p style="color: #64748b; font-size: 14px;">Visualizza l'andamento delle iscrizioni, i grafici delle presenze settimanali e i dati di riepilogo del campus.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        # Se hai una pagina statistiche, punta a quella. Altrimenti puoi lasciarla come segnaposto o puntare a un'altra sezione
        if st.button("Vai a Statistiche ➡️", use_container_width=True, key="card_statistiche"):
            st.session_state.pagina_corrente = "Statistiche"
            st.rerun()

    # Puoi aggiungere altre righe (col3, col4) in futuro se hai altre funzionalità (es. Presenze, Pagamenti, ecc.)