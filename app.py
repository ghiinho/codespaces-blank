import streamlit as st
import database_utils as db_utils  # Le tue utility esistenti

# IMPORTIAMO I NUOVI MODULI CHE ABBIAMO CREATO
from src.sidebar import disegna_sidebar
from src.views.home import mostra_home
from src.views.anagrafiche import mostra_anagrafiche

# 1. Configurazione della pagina Streamlit
st.set_page_config(page_title="Gestionale Camp", layout="wide")

# 2. Inizializzazione e caricamento dati (usando il tuo metodo originale!)
db_utils.inizializza_database_in_memoria()
df_iscritti = db_utils.ottieni_iscritti()

# 3. Disegniamo la barra laterale di navigazione
disegna_sidebar()

# 4. Mostriamo la schermata corretta in base alla pagina selezionata
if st.session_state.pagina_corrente == "Home Page":
    mostra_home()

elif st.session_state.pagina_corrente == "Anagrafiche Iscritti":
    # Passiamo df_iscritti alla vista in modo che possa lavorarci direttamente
    mostra_anagrafiche(df_iscritti)

elif st.session_state.pagina_corrente == "Elenchi Settimanali":
    st.title("📅 Elenchi Settimanali")
    st.info("Questa sezione sarà implementata nei prossimi passaggi...")
    
# ==========================================
# 4. SEZIONE: GESTIONE PAGAMENTI (Futura)
# ==========================================
elif st.session_state.pagina_corrente == "Gestione Pagamenti":
    st.title("💳 Gestione Pagamenti")
    st.info("🚧 Questa sezione è in fase di sviluppo. Qui potrai monitorare le quote di iscrizione, i saldi e registrare i pagamenti ricevuti.")