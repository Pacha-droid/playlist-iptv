import requests
import re

# Dictionnaire de toutes les sources IPTV mondiales requises
sources = {
    "FR": "https://iptv-org.github.io/iptv/countries/fr.m3u", # France
    "DZ": "https://iptv-org.github.io/iptv/countries/dz.m3u", # Algérie
    "CH": "https://iptv-org.github.io/iptv/countries/ch.m3u", # Suisse
    "BE": "https://iptv-org.github.io/iptv/countries/be.m3u", # Belgique
    "CA": "https://iptv-org.github.io/iptv/countries/ca.m3u", # Canada
    "DE": "https://iptv-org.github.io/iptv/countries/de.m3u", # Allemagne
    "SPORTS": "https://iptv-org.github.io/iptv/categories/sports.m3u" # Catégorie Sports mondiale
}

# Liste des pays européens (et Canada) autorisés pour le bouquet Sport complet
PAYS_SPORT_AUTORISES = ["FR", "DZ", "BE", "CH", "DE", "ES", "IT", "PT", "GB", "UK", "NL", "AT", "CA"]

lignes_finales = ["#EXTM3U\n"]
urls_uniques = set()

for cle, url in sources.items():
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            continue
        
        lignes = r.text.splitlines()
        inf_actuelle = None
        
        for ligne in lignes:
            if ligne.startswith("#EXTINF"):
                inf_actuelle = ligne
            elif ligne.startswith("http") and inf_actuelle:
                lien = ligne.strip()
                
                if lien not in urls_uniques:
                    garder = False
                    inf_lower = inf_actuelle.lower()
                    
                    # Extraction automatique du pays et de la langue
                    match_pays = re.search(r'tvg-country="([^"]+)"', inf_actuelle, re.IGNORECASE)
                    match_lang = re.search(r'tvg-language="([^"]+)"', inf_actuelle, re.IGNORECASE)
                    
                    pays = match_pays.group(1).upper() if match_pays else ""
                    langue = match_lang.group(1).lower() if match_lang else ""
                    
                    # --- LOGIQUE DES FILTRES ---
                    # 1. France et Algérie : On prend tout
                    if cle in ["FR", "DZ"]:
                        garder = True
                    
                    # 2. Suisse, Belgique, Canada : Uniquement si c'est en Français OU si c'est du Sport
                    elif cle in ["CH", "BE", "CA"]:
                        if "fra" in langue or "french" in langue or "sport" in inf_lower:
                            garder = True
                            
                    # 3. Allemagne (DE) : Uniquement les chaînes de Sport
                    elif cle == "DE":
                        if "sport" in inf_lower:
                            garder = True
                            
                    # 4. Source Sport Globale : On filtre uniquement l'Europe, l'Algérie et le Canada
                    elif cle == "SPORTS":
                        if pays in PAYS_SPORT_AUTORISES:
                            garder = True
                    
                    if garder:
                        lignes_finales.append(f"{inf_actuelle}\n{lien}\n")
                        urls_uniques.add(lien)
                        
                inf_actuelle = None
    except Exception as e:
        print(f"Erreur de connexion avec la source {cle}: {e}")

# Écriture du fichier final nettoyé
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.writelines(lignes_finales)

print(f"Génération réussie ! {len(urls_uniques)} chaînes ont été triées.")
