import os
import json

CONFIG_FILE = "config.json"

# Impostazioni di fabbrica (Default)
DEFAULT_CONFIG = {
    "moduli": {
        "anagrafiche": {
            "nome": "👤 Anagrafiche Iscritti",
            "attivo": True,
            "descrizione": "Visualizza, modifica e gestisci le schede personali dei bambini iscritti."
        },
        "presenze": {
            "nome": "📝 Registro Presenze",
            "attivo": True,
            "descrizione": "Visualizza gli elenchi settimanali degli iscritti e gestisci i gruppi."
        },
        "pagamenti": {
            "nome": "💰 Gestione Pagamenti",
            "attivo": True,
            "descrizione": "Monitora le quote pagate, gli acconti e genera le ricevute per le famiglie."
        },
        "statistiche": {
            "nome": "📊 Statistiche e Report",
            "attivo": True,
            "descrizione": "Grafici sull'andamento delle iscrizioni, fasce d'età e saturazione delle settimane."
        }
    },
    "general": {
        "nome_campus": "Campus Estivo 2026",
        "mostra_metriche_rapide": True
    }
}

def carica_configurazione():
    """Carica la configurazione da file JSON. Se non esiste, crea quello di default."""
    if not os.path.exists(CONFIG_FILE):
        salva_configurazione(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Riempiamo eventuali chiavi mancanti in caso di futuri aggiornamenti
            for key, val in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = val
            return config
    except Exception:
        return DEFAULT_CONFIG

def salva_configurazione(config):
    """Salva la configurazione corrente su file JSON."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Errore nel salvataggio config: {e}")
        return False