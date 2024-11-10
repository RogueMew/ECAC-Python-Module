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

def scrape_current_rank(jsonData: dict, fileName: str)  -> None:
  def removeUneeded(rankList: list) -> list:
    temp = [] 
    for word in rankList:
      if "%" not in word and "Ranked" not in word:
        temp.append(word)
    return temp

  def randomSleep() -> None:
    time.sleep(random.randint(15, 20))
  
  df = pandas.DataFrame(columns=["Username", "Ranked BR", "Ranked ZB", "Ranked Reload BR", "Ranked Reload ZB"])
  for school in tqdm(list(jsonData.keys()),desc="Scraping Ranks             ", bar_format="{l_bar}{bar:30}{r_bar}" ,total=len(list(jsonData.keys()))):
  #for school in list(jsonData.keys()):
      for user in jsonData[school]:
        if user["game_network_username"] is None:
            continue
          
        driver = webdriver.Edge(options)
        driver.get(f"https://fortnitetracker.com/profile/search?q={user["game_network_username"].replace(" ", "%20")}")    
        
          
        try:
          error_card = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".trn-card--error")))
          df.loc[len(df.index)] = [user["game_network_username"], None,None,None,None]
          driver.close()
          continue
        except:
          pass
          
        try:
          rankText = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".profile-current-ranks__content")))
          rankText = removeUneeded(rankText.text.split("\n"))
          rankText.insert(0, user["game_network_username"])
          df.loc[len(df.index)] = rankText
          driver.close()
          #print(df.loc[len(df.index) - 1])
          randomSleep()
        except:
          driver.close()
          df.loc[len(df.index)] = [user["game_network_username"], None,None,None,None]
          continue
            
  df.to_csv(f"{fileName}.csv",encoding="utf-8", index=False, header=True)

def scrape_peak_rank(jsonData: dict, fileName: str) -> None:
  def removeUneeded(rankList: list) -> list:
    tempList = []
    for word in rankList:
      if "%"not in word and "Ranked" not in word and not word.startswith("CH"):
        tempList.append(word)
    return tempList
  
  def randomSleep() -> None:
    time.sleep(random.randint(15, 20))

  df = pandas.DataFrame(columns=["Username", "Ranked BR", "Ranked ZB"])
  for school in tqdm(list(jsonData.keys()), desc="Scraping Ranks             ", bar_format="{l_bar}{bar:30}{r_bar}", total=len(list(jsonData.keys()))):
  #for school in list(jsonData.keys()):
    for user in jsonData[school]:
      
      if user["game_network_username"] is None:
        continue
      
      driver = webdriver.Edge(options)
      driver.get(f"https://fortnitetracker.com/profile/search?q={user["game_network_username"].replace(" ", "%20")}")

      try:
        error_card = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".trn-card--error")))
        df.loc[len(df.index)] = [user["game_network_username"], "Username Not Found", "Username Not Found"]
        driver.close()
        continue
      except:
        pass

      try:
        rankText = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".profile-peak-ranks__grid")))
        rankText = removeUneeded(rankText.text.split("\n"))
        rankText.insert(0, user["game_network_username"])
        df.loc[len(df.index)] = rankText
        #print(df.loc[len(df.index) - 1])
        driver.close()
        randomSleep()
      
      except:
        driver.close()
        df.loc[len(df.index)] = [user["game_network_username"], "No Peak Rank", "No Peak Rank"]
        continue
  df.to_csv(f"{fileName}.csv", sep="," ,encoding="utf-8", index=False, header=True)

def scrape_current_team_average(data:dict, mode: str="ZB") -> None:
  parameters = ["BR", "ZB", "RBR", "RZB"]
  
  
  if mode not in parameters:
    raise CustomError(f"{mode} not a permitted parameter: {["BR", "ZB", "RBR", "RZB"]}")
  default_rank = "Gold 2"
  ranks = ["Unrated", "Bronze 1", "Bronze 2", "Bronze 3", "Silver 1", "Silver 2", "Silver 3", "Gold 1", "Gold 2", "Gold 3", "Platinum 1", "Platinum 2", "Platinum 3", "Diamond 1", "Diamond 2", "Diamond 3", "Elite", "Champion", "Unreal"]
  
  def rank_to_int(rankValue:str) -> int:
    if rankValue not in ranks:
      raise CustomError(f"Rank not in ranks list: {rankValue}")
   
    return (len(ranks) - ranks.index(rankValue))
  
  def removeUneeded(rankList: list) -> list:
    temp = [] 
    for word in rankList:
      if "%" not in word and "Ranked" not in word:
        temp.append(word)
    return temp

  def randomSleep() -> None:
    time.sleep(random.randint(10, 15))
  df = pandas.DataFrame(columns=["School Name", "Average Rank"])
  for school in list(data.keys()):
    
    team_average = 0
    temp = []
    for player in tqdm(data[school], desc=f"Scraping {school} Average", bar_format="{l_bar}{bar:30}{r_bar}", total=len(data[school])):
    #for player in data[school]:
      
      if player["game_network_username"] is None:
        continue

      driver = webdriver.Edge(options)
      driver.get(f"https://fortnitetracker.com/profile/search?q={player["game_network_username"].replace(" ", "%20")}")

      try:
        error_card = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".trn-card--error")))
        driver.close()
        team_average += rank_to_int(default_rank)
        continue
      except:
        pass

      try:
        rank_text = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".profile-current-ranks__content")))
        rank_text = removeUneeded(rank_text.text.split("\n"))
        team_average += rank_to_int(rank_text[parameters.index(mode)])
        driver.close()
        randomSleep()
      except:
        driver.close()
        continue    
    
    df.loc[len(df.index)] = [school, ranks[int(team_average / len(school))]]
  df.to_csv("test.csv", header=True, index=False)