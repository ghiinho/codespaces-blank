import streamlit as st
import database_utils as db_utils  # Le tue utility esistenti

# IMPORTIAMO I NUOVI MODULI CHE ABBIAMO CREATO
from src.sidebar import disegna_sidebar
from src.views.home import mostra_home
from src.views.anagrafiche import mostra_anagrafiche
from src.utils.config_manager import carica_configurazione
from src.views.impostazioni import mostra_impostazioni
from src.views.elenchi import mostra_elenchi_settimanali

# --- INIZIALIZZAZIONE STATO ---
if "pagina_corrente" not in st.session_state:
    st.session_state.pagina_corrente = "Home Page"

# Inizializzazione globale dei gruppi
if "lista_gruppi" not in st.session_state:
    st.session_state.lista_gruppi = ["Nessun Gruppo"]

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

# Rileviamo cambi di pagina per eseguire azioni una-tantum al cambio di vista
pagina_precedente = st.session_state.get("pagina_precedente")
if st.session_state.pagina_corrente == "Anagrafiche Iscritti" and pagina_precedente != "Anagrafiche Iscritti":
    # Forziamo l'apertura sui Dati Bambino quando si accede alla pagina Anagrafiche
    st.session_state.scheda_attiva = "bambino"
    st.session_state.modalita_modifica = False

# Aggiorniamo la pagina precedente
st.session_state.pagina_precedente = st.session_state.pagina_corrente

# Ora mostriamo la pagina corretta in totale sicurezza
if st.session_state.pagina_corrente == "Home Page":
    mostra_home()
elif st.session_state.pagina_corrente == "Anagrafiche Iscritti":
    mostra_anagrafiche(df_iscritti)
elif st.session_state.pagina_corrente == "Registro Presenze":
    config = carica_configurazione()    
    mapping = config.get("mappatura_colonne", {})
    prefisso = str(config.get("prefisso_settimane", "PERIODI DISPONIBILI")).strip()
    
    col_cognome = mapping.get("cognome", "COGNOME MINORE")
    col_nome = mapping.get("nome", "NOME MINORE")
    col_allergie = mapping.get("allergie", "ALLERGIE O INTOLLERANZE?")
    col_quali = mapping.get("note_allergie", "SE SI, INDICA QUALI")
    col_g_tel = mapping.get("recapito", "TELEFONO GENITORE")
    
    col_cf = "CODICE FISCALE"

    mostra_elenchi_settimanali(
        df_iscritti=df_iscritti,
        col_cognome=str(col_cognome).strip(),
        col_nome=str(col_nome).strip(),
        col_allergie=str(col_allergie).strip(),
        col_quali=str(col_quali).strip(),
        col_g_tel=str(col_g_tel).strip(),
        prefisso_settimane=prefisso
    )
elif st.session_state.pagina_corrente == "Impostazioni":
    mostra_impostazioni()
    
# ==========================================
# 4. SEZIONE: GESTIONE PAGAMENTI (Futura)
# ==========================================
elif st.session_state.pagina_corrente == "Gestione Pagamenti":
    st.title("💳 Gestione Pagamenti")
    st.info("🚧 Questa sezione è in fase di sviluppo. Qui potrai monitorare le quote di iscrizione, i saldi e registrare i pagamenti ricevuti.")