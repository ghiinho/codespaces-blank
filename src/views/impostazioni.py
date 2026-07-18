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
        config["moduli"] = nuovi_moduli
        
        if salva_configurazione(config):
            st.success("🎉 Impostazioni e Moduli salvati con successo! L'applicazione si sta aggiornando...")
            # Forziamo il ricaricamento della configurazione nello stato di sessione
            st.session_state.config = config
            st.rerun()
        else:
            st.error("Si è verificato un errore durante il salvataggio.")

    # =====================================================================
    # GESTIONE GRUPPI (Aggiungere in fondo alla pagina delle Impostazioni)
    # =====================================================================
    st.markdown("---")
    st.markdown("### 👥 Configurazione Gruppi del Camp")
    st.markdown("Crea i gruppi in cui dividere i bambini (es. *Piccoli, Medi, Grandi* oppure *Squadra Rossa, Squadra Blu*).")

    config = carica_configurazione()

    # Se nel config.json non esiste la chiave dei gruppi, la creiamo con i default
    if "gruppi_camp" not in config:
        config["gruppi_camp"] = ["Nessun Gruppo"]

    # Allineiamo il session_state al file config
    st.session_state.lista_gruppi = config["gruppi_camp"]

    # Inizializziamo la lista dei gruppi in memoria se non esiste
    if "lista_gruppi" not in st.session_state:
        st.session_state.lista_gruppi = ["Nessun Gruppo"]

    # Layout a colonne: una per inserire, una per vedere
    col_nuovo, col_lista = st.columns([2, 2])

    with col_nuovo:
        # Creiamo un form per bloccare il testo ed evitare che si svuoti al click
        with st.form(key="form_aggiungi_gruppo", clear_on_submit=True):
            nuovo_gruppo = st.text_input("✍️ Nome nuovo gruppo:", placeholder="Es. Lupi, Grandi...").strip()
            premuto_aggiungi = st.form_submit_button("➕ Aggiungi Gruppo", use_container_width=True)
            
        # Gestiamo il click fuori dal form, usando la variabile 'premuto_aggiungi'
        if premuto_aggiungi:
            if nuovo_gruppo:
                # Carichiamo il config fresco per sicurezza
                config = carica_configurazione()
                if "gruppi_camp" not in config:
                    config["gruppi_camp"] = ["Nessun Gruppo"]
                    
                if nuovo_gruppo not in config["gruppi_camp"]:
                    # Aggiungiamo il gruppo sia al config che alla memoria di Streamlit
                    config["gruppi_camp"].append(nuovo_gruppo)
                    st.session_state.lista_gruppi = config["gruppi_camp"]
                    
                    # 💾 SALVA SU FILE JSON (Usa la tua funzione reale se ha un nome diverso!)
                    salva_configurazione(config)
                    
                    st.success(f"🎉 Gruppo '{nuovo_gruppo}' aggiunto con successo!")
                    st.rerun()
                else:
                    st.warning("⚠️ Questo gruppo esiste già nella lista!")
            else:
                st.error("❌ Digita un nome prima di cliccare aggiungi!")

    with col_lista:
        st.markdown("**Gruppi Attuali:**")
        if len(st.session_state.lista_gruppi) <= 1:
            st.info("Nessun gruppo personalizzato creato.")
        else:
            for grp in st.session_state.lista_gruppi:
                if grp == "Nessun Gruppo": 
                    continue
                # Creiamo un bottone piccolino di fianco a ogni gruppo per poterlo eliminare
                c_nome, c_canc = st.columns([3, 1])
                c_nome.write(f"• {grp}")
                if c_canc.button("🗑️", key=f"del_{grp}"):
                    st.session_state.lista_gruppi.remove(grp)
                    config["gruppi_camp"] = st.session_state.lista_gruppi
                    st.rerun()