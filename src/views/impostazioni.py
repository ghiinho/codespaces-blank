import streamlit as st
from src.utils.config_manager import carica_configurazione, salva_configurazione

def mostra_impostazioni():
    st.title("⚙️ Pannello di Controllo & Moduli")
    st.write("Personalizza la tua dashboard attivando o disattivando le funzionalità in base alle tue esigenze.")
    st.markdown("---")

    # Carica la configurazione corrente
    config = carica_configurazione()

    # --- SEZIONE 1: IMPOSTAZIONI GENERALI ---
    st.subheader("🏫 Impostazioni Generali")
    nuovo_nome = st.text_input("Nome del Campus / Associazione:", value=config["general"].get("nome_campus", "Campus Estivo"))
    
    st.markdown("---")

    # --- SEZIONE 2: ATTIVAZIONE MODULI ---
    st.subheader("🔌 Gestione Moduli Attivi")
    st.info("I moduli disattivati verranno nascosti sia dalla Home Page a riquadri che dalla barra laterale di navigazione.")

    nuovi_moduli = {}
    
    for chiave_modulo, info in config["moduli"].items():
        col_info, col_toggle = st.columns([3, 1])
        with col_info:
            st.markdown(f"**{info['nome']}**")
            st.caption(info['descrizione'])
        with col_toggle:
            st.write("") # Spazio per allineare il toggle
            stato_attivo = st.toggle(
                "Attivo", 
                value=info['attivo'], 
                key=f"toggle_{chiave_modulo}",
                label_visibility="collapsed"
            )
        
        # Salviamo lo stato temporaneo
        nuovi_moduli[chiave_modulo] = {
            "nome": info["nome"],
            "attivo": stato_attivo,
            "descrizione": info["descrizione"]
        }
        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    st.markdown("---")

    # --- SALVATAGGIO ---
    if st.button("💾 Salva Impostazioni", type="primary", use_container_width=True):
        config["general"]["nome_campus"] = nuovo_nome
        config["general"]["mostra_metriche_rapide"] = mostra_metriche
        config["moduli"] = nuovi_moduli
        
        if salva_configurazione(config):
            st.success("🎉 Impostazioni e Moduli salvati con successo! L'applicazione si sta aggiornando...")
            # Forziamo il ricaricamento della configurazione nello stato di sessione
            st.session_state.config = config
            st.rerun()
        else:
            st.error("Si è verificato un errore durante il salvataggio.")