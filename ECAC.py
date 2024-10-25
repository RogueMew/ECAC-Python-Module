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
        self.data = {
            'name' : None,
            'id' : None,
            'size' : None
        }
        pass

    def set_id(self, id) -> None:
        self.data['id'] = id
        pass
    
    def scrape_details(self) -> None:
        request = web.get(comp_url.format(self.data['id'], 1))
        if request.status_code != 200:
            raise CustomError(f'Error Communicating with Server, Error Code: {request.status_code} ')
       
        if 'content' in list(json.loads(request.text).keys()):
            self.data = {
                'name' : json.loads(request.text)['content'][0]['competition'].get('name', None),
                'size' : json.loads(request.text).get('totalElements', None),
                'id' : self.data['id']
            }
    
    def read(self, name=True, id=True, size=True) -> dict:
        result ={}
        if name:
            result['name'] = self.data.get('name', None)
        if id:
            result['id'] = self.data.get('id', None)
        
        if size:
            result['size'] = self.data.get('size', None)
        
        return result
    
    def is_empty(self, param='id') -> bool:
        if param not in list(self.data.keys()):
            raise CustomError(f'{param} is Not in List of Acceptable Parameters: {list(self.data.keys())}')
        return self.data.get(param) is None


#Header
ECAC_header = authHeader('Authorization')
fortnite_header = authHeader('Authorization')
ECAC_cookie = authHeader('GAESA')

#Classed Variables
comp_details = compDetails()

#URLs
contacts_url = "https://api.ecac.gg/competition/entry/{}/_view/contact-accounts"
comp_url = "https://api.ecac.gg/competition/entry/document?competitionId={}&page=0&size={}&sort=seed"
bracket_url = 'https://api.ecac.gg/competition/entry/document?competitionId={}&brackets={}&page=0&size=2000'
team_info_url = "https://api.ecac.gg/competition/entry/{}" 
fortnite_api_url = "https://fortnite-api.com/v2/stats/br/v2/"

network = None

#Util
def is_empty(var: any) -> bool:
    return var == None

#Set Vars
def set_game_network(networkIn: str) -> None:
    global network; network = networkIn

#Competition Functions
def get_team_name(team_id: int) -> str:
    return json.loads(web.get(team_info_url.format(team_id)).text).get('alternateName', f'{team_id}')      
    
def grab_comp_json() -> dict:
    if comp_details.is_empty():
        raise CustomError('Competition ID is Empty')

    request = web.get(comp_url.format(comp_details.read(name=False, size=False)['id'], 1000))

    if request.status_code != 200:
        raise CustomError(f'Request Error: {request.status_code}')

    if json.dumps(request.text) == {}:
        raise CustomError('Empty Comp Site')

    return json.loads(request.text)

#Bracket Functions
def grab_bracket_json(bracket_id: int) -> dict:
    if comp_details.is_empty():
        raise CustomError('Competition ID is not Set')
    request = web.get(bracket_url.format( comp_details.read(name=False, size=False)['id'], bracket_id))

    if request.status_code != 200:
        raise CustomError(f'Request Error: {request.status_code}')

    if json.dumps(request.text) == {}:
        raise CustomError('Empty Bracket Site')
    
    return json.loads(request.text)
    
def scrape_team_ids_bracket(bracket_contents: dict) -> list:
    team_id_list = []
    if 'content' not in list(bracket_contents.keys()):
        raise CustomError('Missing Data')
    for team in bracket_contents['content']:
        
        team_id_list.append(team['id'])
    return team_id_list

#Gather and Scrape Funcs   
def scrape_team_ids(comp_contents:dict) -> list:
    team_id_list = []
    if 'content' not in list(comp_contents.keys()):
        raise CustomError('Missing Data')
    for team in comp_contents['content']:
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

def process_contact_info_func(team_json: list) -> list:
    temp_dict = json.loads(team_json)
    user_id_list = []
    user_contacts = []
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
        return user_contacts
    else:
        user_dict = {'game_network_username' : 'Empty Team', 'discord' : 'Empty Team'}
        user_contacts.append(user_dict)
        return user_contacts

def process_contact_info(teams_contacts: list, team_id_list: list)-> list:
    temp_dict = {}
    for team_list in tqdm(teams_contacts, total= len(teams_contacts), desc= 'Processing Teams'):
        temp_dict[get_team_name(team_id_list[teams_contacts.index(team_list)])] = process_contact_info_func(team_list)
    return temp_dict
