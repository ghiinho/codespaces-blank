import os
import json

CONFIG_FILE = "config.json"

# Impostazioni di fabbrica (Default) incluse Tariffe, Pacchetti e Mappatura
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
    },
    "tariffe": {
        "GIORNATA INTERA": 135.0,
        "MATTINO + PRANZO": 110.0,
        "SOLO MATTINO": 95.0
    },
    "pacchetti": [
        {
            "nome": "Sconto 4 Settimane Intere",
            "frequenza_target": "GIORNATA INTERA",
            "num_settimane": 4,
            "prezzo_pacchetto": 500.0
        }
    ],
    "mappatura_colonne": {
        "cognome": "COGNOME MINORE",
        "nome": "NOME MINORE"
    },
    "prefisso_settimane": "PERIODI DISPONIBILI",
    "registro_pagamenti": {}
}

def carica_configurazione():
    """Carica la configurazione da file JSON. Se non esiste o è incompleta, integra i valori di default."""
    if not os.path.exists(CONFIG_FILE):
        salva_configurazione(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            
            # Riempiamo eventuali chiavi principali mancanti
            for key, val in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = val
            
            # Ripristino paracadute: se tariffe o pacchetti sono vuoti o None, ripopolali
            if not config.get("tariffe"):
                config["tariffe"] = DEFAULT_CONFIG["tariffe"]
            if not config.get("pacchetti"):
                config["pacchetti"] = DEFAULT_CONFIG["pacchetti"]
                
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