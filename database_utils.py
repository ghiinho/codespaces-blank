import sqlite3
from datetime import datetime

def inizializza_db_completo():
    conn = sqlite3.connect('gestionale_centri.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Tabelle Anagrafiche (Colonne Modulo Google)
    cursor.execute('''CREATE TABLE IF NOT EXISTS Genitori (
        cf_genitore TEXT PRIMARY KEY, cognome TEXT, nome TEXT, email TEXT, telefono TEXT, data_nascita TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Iscritti (
        cf_bambino TEXT PRIMARY KEY, cognome TEXT, nome TEXT, data_nascita TEXT, luogo_nascita TEXT,
        indirizzo TEXT, civico TEXT, cap TEXT, citta TEXT, intolleranze TEXT, dettaglio_intolleranze TEXT,
        note_segnalazioni TEXT, flag_fratelli TEXT DEFAULT 'No', cf_genitore TEXT, id_gruppo INTEGER,
        FOREIGN KEY (cf_genitore) REFERENCES Genitori(cf_genitore)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Iscrizioni (
        id INTEGER PRIMARY KEY AUTOINCREMENT, cf_bambino TEXT, settimana_numero INTEGER, tipo_frequenza TEXT,
        prezzo_lordo REAL DEFAULT 0.0, sconto_applicato REAL DEFAULT 0.0, prezzo_netto REAL DEFAULT 0.0,
        caparra_versata TEXT DEFAULT 'NO', settimana_saldata TEXT DEFAULT 'NO', stato_iscrizione TEXT DEFAULT 'Iscritto',
        FOREIGN KEY (cf_bambino) REFERENCES Iscritti(cf_bambino), UNIQUE(cf_bambino, settimana_numero)
    )''')
    
    # Listini e Pacchetti impostabili dall'operatore
    cursor.execute('''CREATE TABLE IF NOT EXISTS Listini (
        tipo_frequenza TEXT PRIMARY KEY, prezzo_standard REAL, prezzo_fratello REAL
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Pacchetti (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome_pacchetto TEXT, settimane_richieste INTEGER, prezzo_pacchetto REAL
    )''')
    
    # Dati di partenza di esempio
    cursor.execute("INSERT OR IGNORE INTO Listini VALUES ('GIORNATA INTERA', 120.0, 90.0)")
    cursor.execute("INSERT OR IGNORE INTO Listini VALUES ('MATTINO + PRANZO', 100.0, 100.0)")
    cursor.execute("INSERT OR IGNORE INTO Listini VALUES ('SOLO MATTINO', 80.0, 80.0)")
    cursor.execute("INSERT OR IGNORE INTO Listini VALUES ('AIUTO ANIMATORE', 50.0, 50.0)")
    cursor.execute("INSERT OR IGNORE INTO Pacchetti (nome_pacchetto, settimane_richieste, prezzo_pacchetto) VALUES ('Pacchetto 4 Settimane GI', 4, 400.0)")
    
    conn.commit()
    conn.close()

def calcola_tariffe_bambino(cf_bambino):
    """Calcola i prezzi delle iscrizioni applicando la regola del maggior favore"""
    conn = sqlite3.connect('gestionale_centri.db')
    cursor = conn.cursor()
    
    # Recupera info bambino
    cursor.execute("SELECT flag_fratelli, data_nascita FROM Iscritti WHERE cf_bambino = ?", (cf_bambino,))
    bambino = cursor.fetchone()
    if not bambino: return
    ha_fratelli = (bambino[0].strip().lower() == 'si')
    
    # Calcola l'età indicativa
    try:
        anno_nascita = datetime.strptime(bambino[1], "%d/%m/%Y").year
        eta = datetime.now().year - anno_nascita
    except:
        eta = 8 # default se la data è scritta male
        
    is_aiuto_animatore = (12 <= eta <= 13)
    
    # Recupera i listini aggiornati
    cursor.execute("SELECT tipo_frequenza, prezzo_standard, prezzo_fratello FROM Listini")
    listini = {row[0]: {'standard': row[1], 'fratello': row[2]} for row in cursor.fetchall()}
    
    # Recupera il prezzo del pacchetto da 4 settimane per Giornata Intera
    cursor.execute("SELECT settimane_richieste, prezzo_pacchetto FROM Pacchetti WHERE nome_pacchetto LIKE '%4%'")
    pacchetto_info = cursor.fetchone()
    sett_pacchetto, prezzo_pacchetto = pacchetto_info if pacchetto_info else (4, 400.0)

    # Prende tutte le iscrizioni attive del bambino
    cursor.execute("SELECT id, settimana_numero, tipo_frequenza FROM Iscrizioni WHERE cf_bambino = ?", (cf_bambino,))
    iscrizioni = cursor.fetchall()
    
    # Conteggio settimane a Giornata Intera per applicare i pacchetti chiusi
    isc_giornata_intera = [row for row in iscrizioni if row[2] == 'GIORNATA INTERA']
    num_gi = len(isc_giornata_intera)
    
    # Calcoliamo quanti pacchetti da 4 e quante settimane singole avanzano
    quanti_pacchetti = num_gi // sett_pacchetto
    settimane_sfuse = num_gi % sett_pacchetto
    
    # --- IPOTESI A: Applichiamo la logica a Pacchetti ---
    costo_totale_gi_pacchetto = (quanti_pacchetti * prezzo_pacchetto) + (settimane_sfuse * (listini['GIORNATA INTERA']['fratello'] if ha_fratelli else listini['GIORNATA INTERA']['standard']))
    
    # --- IPOTESI B: Applichiamo solo la tariffa Fratello (se ha fratelli) ---
    costo_totale_gi_singole = num_gi * (listini['GIORNATA INTERA']['fratello'] if ha_fratelli else listini['GIORNATA INTERA']['standard'])
    
    # REGOLA DEL MAGGIOR FAVORE: Scegliamo la strategia più conveniente per la Giornata Intera
    usa_prezzo_pacchetto = True
    if ha_fratelli and (costo_totale_gi_singole < costo_totale_gi_pacchetto):
        usa_prezzo_pacchetto = False # Vince lo sconto fratello sulle singole!

    # Adesso aggiorniamo ogni singola iscrizione nel database
    contatore_gi = 0
    for isc_id, sett_num, freq in iscrizioni:
        # Se è aiuto animatore la tariffa è flat indistintamente dalla frequenza
        if is_aiuto_animatore:
            lordo = listini['AIUTO ANIMATORE']['standard']
            netto = lordo
            sconto = 0.0
        else:
            lordo = listini[freq]['standard']
            if freq == 'GIORNATA INTERA':
                contatore_gi += 1
                if usa_prezzo_pacchetto:
                    # Se rientra nei blocchi di pacchetti interi da 4
                    if contatore_gi <= (quanti_pacchetti * sett_pacchetto):
                        netto = prezzo_pacchetto / sett_pacchetto # Prezzo spalmato del pacchetto
                    else:
                        netto = listini['GIORNATA INTERA']['fratello'] if ha_fratelli else lordo
                else:
                    netto = listini['GIORNATA INTERA']['fratello']
            else:
                # Per Mattino+Pranzo o Solo Mattino il prezzo fratello è uguale allo standard (come da tue specifiche)
                netto = listini[freq]['fratello'] if ha_fratelli else lordo
            
            sconto = lordo - netto
            
        cursor.execute("""
            UPDATE Iscrizioni 
            SET prezzo_lordo = ?, sconto_applicato = ?, prezzo_netto = ? 
            WHERE id = ?
        """, (lordo, sconto, netto, isc_id))
        
    conn.commit()
    conn.close()