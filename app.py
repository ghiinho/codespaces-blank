import streamlit as st
import database_utils as db_utils  # Le tue utility esistenti

# IMPORTIAMO I NUOVI MODULI CHE ABBIAMO CREATO
from src.sidebar import disegna_sidebar
from src.views.home import mostra_home
from src.views.anagrafiche import mostra_anagrafiche
from src.utils.config_manager import carica_configurazione
from src.views.impostazioni import mostra_impostazioni

# --- INIZIALIZZAZIONE STATO ---
if "pagina_corrente" not in st.session_state:
    st.session_state.pagina_corrente = "Home Page"

# 1. Configurazione della pagina Streamlit
st.set_page_config(page_title="Gestionale Camp", layout="wide")

# 2. Inizializzazione e caricamento dati (usando il tuo metodo originale!)
db_utils.inizializza_database_in_memoria()
df_iscritti = db_utils.ottieni_iscritti()

# 3. Disegniamo la barra laterale di navigazione
disegna_sidebar()

# 💡 IL SEGRETO: Se la pagina corrente NON è le Anagrafiche, 
# svuotiamo completamente i dati di ricerca in modo che non rimangano in memoria!
if st.session_state.pagina_corrente != "Anagrafiche Iscritti":
    st.session_state.risultato_ricerca = None
    st.session_state.id_bambino_corrente = None
    # Svuotiamo anche il testo scritto nel box di ricerca
    if "ricerca_cognome" in st.session_state:
        st.session_state["ricerca_cognome"] = ""

# Ora mostriamo la pagina corretta in totale sicurezza
if st.session_state.pagina_corrente == "Home Page":
    mostra_home()
elif st.session_state.pagina_corrente == "Anagrafiche Iscritti":
    mostra_anagrafiche(df_iscritti)
elif st.session_state.pagina_corrente == "Impostazioni":
    mostra_impostazioni()
    
# ==========================================
# 4. SEZIONE: GESTIONE PAGAMENTI (Futura)
# ==========================================
elif st.session_state.pagina_corrente == "Gestione Pagamenti":
    st.title("💳 Gestione Pagamenti")
    st.info("🚧 Questa sezione è in fase di sviluppo. Qui potrai monitorare le quote di iscrizione, i saldi e registrare i pagamenti ricevuti.")