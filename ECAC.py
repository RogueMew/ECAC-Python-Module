import requests as web
from tqdm import tqdm
import json


class authHeader:
    def __init__(self, headerTitle) -> None:
        self.header = {headerTitle : None}
        self.headerTitle = headerTitle 
        pass
    
    def set(self, authToken) -> None:
        self.header = {self.headerTitle : authToken}
        pass
    
    def read(self) -> dict:
        return self.header

    def is_empty(self) -> bool:
        return self.header[self.headerTitle] == None

class CustomError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}"

class compDetails:
    def __init__(self) -> None:
        pass
    def set(self, id) -> None:
        self.id = id
        pass
    
    def read_id(self) -> None:
        return self.id
    
    def scrape_details(self) -> None:
        request = web.get(comp_url.format(self.id))
        print(request.text)
#Header
ECAC_header = authHeader('Authorization')
fortnite_header = authHeader('Authorization')
comp_id = compDetails()

#URLs
contacts_url = "https://api.ecac.gg/competition/entry/{}/_view/contact-accounts"
comp_url = "https://api.ecac.gg/competition/entry/document?competitionId={}&page=0&size=1000&sort=seed" 
team_info_url = "https://api.ecac.gg/competition/entry/{}" 
fortnite_api_url = "https://fortnite-api.com/v2/stats/br/v2/"

comp_id= None
network = None
#Util
def is_empty(var: any) -> bool:
    return var == None

#Set Vars
def set_comp_id(id: int) -> None:
    global comp_id ; comp_id =  id

def set_game_network(networkIn: str) -> None:
    global network; network = networkIn


#Funcs for Data
def get_team_name(team_id: int) -> str:
    return json.loads(web.get(team_info_url.format(team_id)).text).get('alternateName', f'{team_id}')      
    
def grab_comp_json() -> dict:
    if is_empty(comp_id):
        raise CustomError('Competition ID is Empty')

    request = web.get(comp_url.format(comp_id))

    if request.status_code != 200:
        raise CustomError(f'Request Error: {request.status_code}')

    if json.dumps(request.text) == {}:
        raise CustomError('Empty Comp Site')

    return json.loads(request.text)

def scrape_team_ids(comp_contents:dict) -> list:
    team_id_list = []
    for team in comp_contents:
        team_id_list.append(team['id'])
    return team_id_list

def get_team_contacts(teamIDS: list) -> list:
    if ECAC_header.is_empty():
        raise CustomError('ECAC Header is not Set')

    team_contacts = []
    for id in tqdm(teamIDS, total=len(teamIDS), desc='Scraping Team Contacts Page'):
        request = web.get(contacts_url.format(id), headers=ECAC_header.read())
        if request.status_code != 200:
            if request.status_code == 401:
                raise CustomError('Request Header Needs Updating')
            else:
                raise CustomError(f'Error in Cimmunication with Server, Web Error Code {request.status_code}')
        team_contacts.append(request.text)
    return team_contacts

def process_contact_info_func(team_json: list, team_list_pos: int, team_id_list: list) -> list:
    temp_dict = json.loads(team_json)
    user_id_list = []
    user_contacts = []
    team_dict = {}
    if temp_dict != {}:
        for contacts in temp_dict['content']:
            user_id_list.append(contacts['user']['id'])

        user_id_list = list(set(user_id_list))

        for id in user_id_list:
            user_dict = {
                'id' : None,
                'game_network_username': None,
                'discord' : None
            }
            for contacts in temp_dict['content']:
                if contacts['user']['id'] == id:
                    user_dict['id'] = id
                    if contacts['network'] == network:
                        
                        user_dict['game_network_username'] = contacts['handle']

                    elif contacts['network'] == 'DISCORD':
                        user_dict['discord'] = contacts['handle']
            user_contacts.append(user_dict)
        #team_dict[get_team_name(team_id_list[team_list_pos])] = user_contacts
        #return team_dict
        return user_contacts
    else:
        user_dict = {'game_network_username' : 'Empty Team', 'discord' : 'Empty Team'}
        user_contacts.append(user_dict)
        return user_contacts

def process_contact_info(teams_contacts: list, team_id_list: list) -> list:
    temp_dict = {}
    for x in tqdm(teams_contacts, total= len(teams_contacts), desc= 'Processing Teams'):
        temp_dict[get_team_name(team_id_list[teams_contacts.index(x)])] = process_contact_info_func(x, teams_contacts.index(x), team_id_list)
    return temp_dict

#Fixes
def get_encoding_type(encoded_str: str) -> str:
    # UTF-8
    try:
        encoded_str.decode('utf-8')
        return 'utf-8'
    except:
        pass
    
    # UTF-16
    try:
        encoded_str.decode('utf-16')
        return 'utf-16'
    except:
        return None
    