import streamlit as st

# Carica la configurazione per sapere quali voci mostrare
config = carica_configurazione()

# La Home e le Impostazioni sono sempre visibili
pagine_disponibili = ["Home Page"]

# Mostra i moduli solo se sono impostati su True in config.json
if config["moduli"]["anagrafiche"]["attivo"]:
    pagine_disponibili.append("Anagrafiche Iscritti")
if config["moduli"]["presenze"]["attivo"]:
    pagine_disponibili.append("Registro Presenze")
if config["moduli"]["pagamenti"]["attivo"]:
    pagine_disponibili.append("Gestione Pagamenti")
if config["moduli"]["statistiche"]["attivo"]:
    pagine_disponibili.append("Statistiche")

pagine_disponibili.append("Impostazioni")