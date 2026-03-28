api_key="" #tutaj wpisujesz aktualny klucz wygenerowany na stronie riotu
current_puuid = ""
user_stats_text ="Wpisz nick i kliknij szukaj"
game_name="Bartix117"
game_tag="EUNE"
user_data = []

import requests
import threading

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

#import BeautifulSoup

selected_region="EUNE"

REGION_MAP = {
    "EUNE": {"platform":"eun1", "region": "europe"},
    "EUW": {"platform":"euw1", "region": "europe"},
    "NA": {"platform":"na1", "region": "americas"},
    "KR": {"platform":"kr", "region":"asia"},
    "BR": {"platform":"br1", "region": "americas"},
    "LAN": {"platform":"la1", "region": "americas"},
    "LAS": {"platform":"la2", "region": "americas"},
    "OCE": {"platform":"oc1", "region": "sea"},
    "TR": {"platform":"tr1", "region": "europe"},
    "RU": {"platform":"ru", "region": "europe"},
    "JP": {"platform":"jp1", "region": "asia"}
}

def get_stats_by_queue(target_queue):
    """
    Zwraca tekst dla konkretnego trybu (Solo lub Double Up).
    """
    if not user_data:
        return "Brak danych. Najpierw wyszukaj gracza."

    found_entry = None
    for entry in user_data:
        if entry.get('queueType') == target_queue:
            found_entry = entry
            break
    
    display_names = {
        'RANKED_TFT': 'RANKED SOLO',
        'RANKED_TFT_DOUBLE_UP': 'DOUBLE UP'
    }

    if found_entry:
        tier = found_entry.get('tier', 'Unknown')
        rank = found_entry.get('rank', '')
        lp = found_entry.get('leaguePoints', 0)
        wins = found_entry.get('wins', 0)
        losses = found_entry.get('losses', 0)
        
        total = wins + losses
        wr = round((wins / total) * 100, 1) if total > 0 else 0

        return (f"Tryb: {display_names.get(target_queue)}\n"
                f"Ranga: {tier} {rank}\n"
                f"Punkty LP: {lp}\n"
                f"Statystyki: {wins}W / {losses}L)\n"
                f"Winrate: {wr}%\n"
                f"Ilość gier:{total}")
    else:
        return f"Gracz nie ma rangi w trybie:\n{display_names.get(target_queue, target_queue)}"
    
def fetch_match_data():
    global match_data
    if not current_puuid:
        print("Błąd: Brak PUUID")
        return "NO_PUUID"
    platform= REGION_MAP[selected_region]["platform"]
    match_url=f"https://{platform}.api.riotgames.com/lol/spectator/tft/v5/active-games/by-puuid/{current_puuid}?"
    try:
        response = requests.get(match_url,params={"api_key": api_key,},timeout=15)
        if response.status_code == 200:
            match_data= response.json()
            print (f"{match_data}")
            return "W_grze"
        elif response.status_code == 404:
            match_data = None
            return "Nie_w_grze"
        else:
            print(f"Błąd API: {response.status_code}")
            return "ERROR"
    except Exception as e:
        print(f"Błąd połączenia: {e}")
        return "ERROR"
  

def get_live_game_text():
    """Formatuje dane meczu do wyświetlenia"""
    if not match_data:
        return "Brak danych o aktywnej grze."
    
    queue_id = match_data.get('gameQueueConfigId', 0)
    mode = "TFT (Nieznany)"
    if queue_id == 1100: mode = "RANKED SOLO"
    elif queue_id == 1090: mode = "NORMAL"
    elif queue_id == 1160: mode = "DOUBLE UP"

    participants = match_data.get('participants', [])
    players_list = ""
    
    for p in participants:
        name = p.get('riotId', p.get('summonerName', 'Gracz'))
        if name == "": name = "Ukryty Nick"
        players_list += f"- {name}\n"

    return (f"--- GRA NA ŻYWO ---\n"
            f"Tryb: {mode}\n"
            f"Gracze w lobby:\n{players_list}")

def get_game_seconds():
    if match_data and 'gameLength' in match_data:
        return match_data['gameLength']
    return 0

def fetch_data():
    """Pobiera dane z API i zapisuje je w globalnej zmiennej"""
    global user_data
    platform= REGION_MAP[selected_region]["platform"]
    user_rank_url=f"https://{platform}.api.riotgames.com/tft/league/v1/by-puuid/{current_puuid}?"
    try:
        response = requests.get(user_rank_url, params={"api_key": api_key})
        if response.status_code == 200:
            user_data = response.json()
            print (f"{user_data}")
            return True
        else:
            print(f"Błąd API: {response.status_code}")
            return False
    except Exception as e:
        print(f"Błąd połączenia: {e}")
        return False

def fetch_data_comps():
    temp_comps = []
    global global_comps_data
    driver = None
    try:
   
        chrome_options = Options()
        chrome_options.add_argument("--headless=new") 
        chrome_options.add_argument("--window-size=1920,6000")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--log-level=3")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get("https://tftactics.gg/tierlist/team-comps")

        driver.implicitly_wait(1)
        team_elements = driver.find_elements(By.CLASS_NAME, "team-portrait")
        strategy_keywords = ["Roll", "Fast", "Level", "Economy", "Default"]
   
        for i, team in enumerate(team_elements[:40]):
            raw_text = team.text
            lines = raw_text.split('\n')
            print(raw_text)
            comp_tier = "?"
            comp_name = "Nieznana"
            comp_strategy = ""
            champs = []
            for line in lines:
                if len(line) == 1 and line in ["S", "A", "B", "C", "D"]:
                    comp_tier=line
                    continue
                if any(word in line for word in strategy_keywords):
                    comp_strategy = line
                    continue
                if comp_name == "Nieznana" and len(line) > 1:
                    comp_name = line
                    continue
                if len(line) > 2 and "Fast" not in line and "Reroll" not in line and "Level" not in line and "Slow" not in line and comp_name not in line:
                    champs.append(line)
            comp_obj = {
            "id": i+1,
            "tier": comp_tier,
            "name": comp_name,
            "strategy": comp_strategy,
            "champs": champs,
            }
            temp_comps.append(comp_obj)
        global_comps_data = temp_comps
        print(f"--- SUKCES: Przeanalizowano {len(temp_comps)} kompozycji ---")    
        print("--- SUKCES: Pobrano dane z Selenium ---")
    except Exception as e:
        print(f"Błąd Selenium: {e}")
    finally:
        if driver:
            driver.quit()




