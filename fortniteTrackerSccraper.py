import time
import random
import pandas


from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.EdgeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

def scrape_rank_individuals(jsonData: dict, fileName: str)  -> None:
  def removeUneeded(rankList: list) -> list:
    temp = [] 
    for word in rankList:
      if '%' not in word and 'Ranked' not in word:
        temp.append(word)
    return temp

  def randomSleep() -> None:
    time.sleep(random.randint(15, 20))
  
  df = pandas.DataFrame(columns=["Username", "Ranked BR", "Ranked ZB", "Ranked Reload BR", "Ranked Reload ZB"])
  #for school in tqdm(list(jsonData.keys()),desc="Scraping Ranks             ", bar_format="{l_bar}{bar:30}{r_bar}" ,total=len(list(jsonData.keys()))):
  for school in list(jsonData.keys()):
      for user in jsonData[school]:
        if user['game_network_username'] is None:
            break
          
        driver = webdriver.Edge(options)
        driver.get(f"https://fortnitetracker.com/profile/search?q={user['game_network_username'].replace(' ', '%20')}")    
        
          
        try:
          error_card = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.trn-card--error')))
          df.loc[len(df.index)] = [user['game_network_username'], "Username404","Username404","Username404","Username404"]
          driver.close()
          break
        except:
          pass
          
        try:
          rankText = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.profile-current-ranks__content')))
          rankText = removeUneeded(rankText.text.split('\n'))
          rankText.insert(0, user['game_network_username'])
          df.loc[len(df.index)] = rankText
          driver.close()
          print(df.loc[len(df.index) - 1])
          randomSleep()
        except:
          driver.close()
          df.loc[len(df.index)] = [user['game_network_username'], "data404","data404","data404","data404"]
          break
            
  df.to_csv(f'{fileName}.csv', sep="," ,encoding='utf-8', index=False, header=True)