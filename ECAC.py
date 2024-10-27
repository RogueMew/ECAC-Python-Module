import requests as web
from tqdm import tqdm
import json

#Classes
class header:
    def __init__(self, headerTitle) -> None:
        self.header = {headerTitle : None}
        self.headerTitle = headerTitle 
        pass
    
    def set(self, headerValue) -> None:
        self.header = {self.headerTitle : headerValue}
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
        self.url = 'https://api.ecac.gg/competition/{}'
        pass

    def set_id(self, id) -> None:
        self.data['id'] = id
        pass
    
    def scrape_details(self) -> None:
        request = web.get(self.url.format(self.data['id'], 1))
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

class matchData:
    
    def __init__(self, team_id) -> None:
        self.header = header('expand')
        self.header.set('_links,activeChannel,bracket{settings,competition},assignments{entry{leader,_links,representing{additionalOrganizations,profile}}},event,games,channel')
        self.url = 'https://api.ecac.gg/competition/bracket/match/{}'
        self.team_id = team_id
        pass

    def set_match_id(self, id: int) -> None:
        self.match_id = id
        pass

    def scrape(self) -> str:
        request = web.get(self.url.format(self.match_id), headers=self.header.read())
        
        if request.status_code != 200:
            raise CustomError(f'Web Error Code: {request.status_code}')
        
        return request.text
    
    def id_finder(self) -> str:
        request_json = json.loads(self.scrape())
        bracketIDS =[]
        
        for bracketAssign in request_json['_expanded']['bracketAssignment']:
            temp = {bracketAssign['id'] : bracketAssign['entry']['id']}
            bracketIDS.append(temp)

        for id in bracketIDS:
                if list(id.values())[0] == self.team_id:
                    self.team_match_id = list(id.keys())[0]
        
        return self.team_match_id
    
    def print_match_results(self) -> None:
        self.id_finder()
        data = json.loads(self.scrape())
        if data['_expanded'].get('matchGame', None) == None:
            print('Game Not Played Yet')
            return
        if data['winner']['id'] != self.team_match_id:
            print('Lost Overall')
        else:
            print('Won Overall')
        
        for game in data['_expanded']['matchGame']:
            if game['winner']['id'] == self.team_match_id:
                print(f"Won Game: {max(game['scores'])} - {min(game['scores'])}")
            else:
                print(f"Lost Game: {min(game['scores'])} - {max(game['scores'])}")


#Header
ECAC_API_header = header('Authorization')

#Classed Variables
comp_details = compDetails()

#URLs
contacts_url = "https://api.ecac.gg/competition/entry/{}/_view/contact-accounts"
comp_url = "https://api.ecac.gg/competition/entry/document?competitionId={}&page=0&size=1000&sort=seed"
bracket_url = 'https://api.ecac.gg/competition/entry/document?competitionId={}&brackets={}&page=0&size=2000'
team_info_url = "https://api.ecac.gg/competition/entry/{}" 
match_data_url = 'https://api.ecac.gg/competition/{}/_view/matches?entry={}&page=0'

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

    request = web.get(comp_url.format(comp_details.read(name=False, size=False)['id']))

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
    if ECAC_API_header.is_empty():
        raise CustomError('ECAC Header is not Set')

    team_contacts = []
    for id in tqdm(teamIDS, total=len(teamIDS), desc='Scraping Team Contacts Page'):
        request = web.get(contacts_url.format(id), headers=ECAC_API_header.read())
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
    for x in tqdm(teams_contacts, total= len(teams_contacts), desc= 'Processing Teams'):
        temp_dict[get_team_name(team_id_list[teams_contacts.index(x)])] = process_contact_info_func(x, teams_contacts.index(x), team_id_list)
    return temp_dict

# Grab Match Ids
def team_match_ids(team_id: int) -> list:
    
    returned_list = []

    expandHeader = header('expand')
    expandHeader.set('_links,totalElements,content{bracket{settings},event,games,assignments{entry{leader,representing{additionalOrganizations}}}}')
    request = web.get(match_data_url.format(comp_details.read(name=False,size=False)['id'], team_id), headers=expandHeader.read())
    
    if request.status_code != 200:
        raise CustomError(f'Web Status Code: {request.status_code}')
    
    
    for item in request.json()['content']:
        returned_list.append(item['id'])
    return returned_list