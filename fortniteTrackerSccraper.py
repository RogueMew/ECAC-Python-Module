import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas
from tqdm import tqdm

options = webdriver.EdgeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

def scrapeRank(jsonData: dict, fileName: str)  -> None:
  def removeUneeded(rankList: list) -> list:
    temp = [] 
    for word in rankList:
      if '%' not in word and 'Ranked' not in word:
        temp.append(word)
    return temp

  def randomSleep() -> None:
    time.sleep(random.randint(15, 20))
  
  df = pandas.DataFrame(columns=["Username", "Ranked BR", "Ranked ZB", "Ranked Reload BR", "Ranked Reload ZB"])
  for school in tqdm(list(jsonData.keys()),desc="Scraping Ranks             ", bar_format="{l_bar}{bar:30}{r_bar}" ,total=len(list(jsonData.keys()))):
      for user in jsonData[school]:
          if user['game_network_username'] is None:
              break
          
          driver = webdriver.Edge(options)
          driver.get(f"https://fortnitetracker.com/profile/search?q={user['game_network_username'].replace(' ', '%20')}")    
          
          try:
            driver.find_element(By.CSS_SELECTOR, '.trn-card--error')
            driver.close()
            break        
          except:
            text = removeUneeded(driver.find_element(By.CLASS_NAME, 'profile-current-ranks__content').text.split("\n"))
            text.insert(0, user['game_network_username'])
            df.loc[len(df.index)] = text
            #print(df.loc[len(df.index)-1])
            randomSleep()
            driver.close()
  df.to_csv(f'{fileName}.csv', sep="," ,encoding='utf-8', index=False, header=True)