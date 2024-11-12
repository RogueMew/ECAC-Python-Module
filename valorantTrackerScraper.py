import time
import random
import pandas


from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CustomError(Exception):
    """
    Custom Error Message Class Allowing for Custom Errors
    """
    
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}"

options = webdriver.EdgeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
#options.add_argument("--headless")

def scrape_current_rank(json_data:dict, file_name: str="Output") -> None:
    df = pandas.DataFrame(columns=["Username", "Team", "Current Rank"])
    for team in tqdm(list(json_data.keys()), desc="Scraping Current Ranks", bar_format="{l_bar}{bar:30}{r_bar}" , total=len(list(json_data.keys()))):
    #for team in list(json_data.keys()):
        for player in json_data[team]:
            
            driver = webdriver.Edge(options)
            driver.get(f"https://tracker.gg/valorant/profile/riot/{player['game_network_username'].replace(" ", "%20").replace("#", "%23")}/overview")
            
            try:
                error_card = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".content--error")))
                driver.close()
                df.loc[len(df.index)] = [player['game_network_username'], "User Not Found or Data Private"]
                continue
            except:
                pass
            
            try:
                rank_text = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".rating-entry__rank")))
                df.loc[len(df.index)] = [player['game_network_username'], team ,rank_text.text.split("\n")[1]]
                driver.close()
            except:
                df.loc[len(df.index)] = [player["game_network_username"],team, "No Rank Found"]
                pass
                
    df.to_csv(f"{file_name}.csv", header=True, index=False, encoding="utf-8")
    
def scrape_peak_rank(json_data: dict, file_name:str = "Output") -> None:
    df = pandas.DataFrame(columns=["Username", "Team", "Peak Rank", "Peak Act/Episode"])
    for team in tqdm(list(json_data.keys()), desc="Scraping Peak Ranks", bar_format="{l_bar}{bar:30}{r_bar}" , total=len(list(json_data.keys()))):
    #for team in list(json_data.keys()):
        for player in json_data[team]:
            driver = webdriver.Edge(options)
            driver.get(f"https://tracker.gg/valorant/profile/riot/{player['game_network_username'].replace(" ", "%20").replace("#", "%23")}/overview")
            
            try:
                error_card = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".content--error")))
                driver.close()
                
                df.loc[len(df.index)] = [player['game_network_username'], team, "Private or Not Real", "Unkown"]
                continue
            except:
                pass
            
            try:
                rank_text = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".rating-summary__content--secondary")))
                rank_text = rank_text.text.split("\n")
                rank_text.pop(rank_text.index("Peak Rating"))
                if len(rank_text) > 2:
                    for word in rank_text:
                        if word.endswith("RR"):
                            rank_text.pop(rank_text.index(word))         
                rank_text.insert(0, team)
                rank_text.insert(0, player["game_network_username"])
                df.loc[len(df.index)] = rank_text
            except:
                df.loc[len(df.index)] = [player["game_network_username"], team, "No Peak Found", "Unknown"]
                pass
    
    df.to_csv(f"{file_name}.csv", header=True, index=False, encoding="utf-8")

def scrape_current_team_average(json_data: dict, file_name:str = "Output") -> None:
    df = pandas.DataFrame(columns=["School Name",  "Team Average"])
    rank_list = [
    "Unrated", "Iron 1", "Iron 2", "Iron 3",
    "Bronze 1", "Bronze 2", "Bronze 3",
    "Silver 1", "Silver 2", "Silver 3",
    "Gold 1", "Gold 2", "Gold 3",
    "Platinum 1", "Platinum 2", "Platinum 3",
    "Diamond 1", "Diamond 2", "Diamond 3",
    "Ascendant 1", "Ascendant 2", "Ascendant 3",
    "Immortal 1", "Immortal 2", "Immortal 3",
    "Radiant"
]
    def rank_to_int(rank:str) -> int:
        if rank not in rank_list:
            raise CustomError(f"Rank not in Rank List: {rank}")
        return len(rank_list) - rank_list.index(rank)
    
    
    for team in tqdm(list(json_data.keys()), desc="Scraping Team Current Average", bar_format="{l_bar}{bar:30}{r_bar}", total=len(list(json_data.keys()))):    
    #for team in list(json_data.keys()):
        team_average = 0
        for  player in json_data[team]:
            
            driver = webdriver.Edge(options)
            driver.get(f"https://tracker.gg/valorant/profile/riot/{player['game_network_username'].replace(" ", "%20").replace("#", "%23")}/overview")
            
            try:
                error_card = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".content--error")))
                driver.close()
                team_average += rank_to_int("Gold 1")
                continue
            except:
                pass
            
            try:
                rank_text = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".rating-entry__rank")))
                team_average += rank_to_int(rank_text.text.split("\n")[1])
                driver.close()
            except:
                team_average += rank_to_int("Gold 1")
                driver.close()
                continue 
                
        df.loc[len(df.index)] = [team, rank_list[int(team_average/len(json_data[team]))]]
        
    df.to_csv(f"{file_name}.csv", header=True, index=False, encoding="utf-8")