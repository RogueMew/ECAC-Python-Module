import requests as web
import json

class customError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        
    def __str__(self) -> str:
        return self.message
    
class header:
    def __init__(self, headerTitle: any) -> None:
        self.headerTitle = headerTitle
        self.headerValue = None
        pass
    
    @property
    def as_dict(self) -> dict:
        if self.headerValue == None:
            raise customError("Header Not Set")
        
        return {self.headerTitle : self.headerValue}
        
class Competition:
    def __init__(self, compId: int, bracketId: int = None) -> None:
        self.bracketId = bracketId
        self.compId = compId
  
    @property
    def teamIds(self) -> list:
        
        competitionURL = f"https://api.ecac.gg/competition/entry/document?competitionId={self.compId}&page=0&size=1000&sort=seed"
        bracketURL = f"https://api.ecac.gg/competition/entry/document?competitionId={self.compId}&brackets={self.bracketId}&page=0&size=2000"
                
        request = web.get(bracketURL if self.bracketId != None else competitionURL)
            
        if request.status_code != 200:
            raise customError(f"Request Error: {request.status_code}")
            
        data = json.loads(request.text)
            
        teamIds = []
            
        if "content" not in list(data.keys()):
            raise customError("Missing Data")
            
        for team in data["content"]:
            teamIds.append(team["id"])
            
        return teamIds
    
    @property
    def bracketIds(self) -> list:    
        bracketIds = []
        
        request  = web.get(f"https://api.ecac.gg/competition/{self.compId}/brackets")
        
        if request .status_code != 200:
            raise customError("Error Connecting with API, Status Code Error {request.status_code}") 

        try:
            data = json.loads(request .text)
        except json.JSONDecodeError as e:
            raise customError(f"Error Decoding Json:\n{e}")
            
        if "content" not in list(data.keys()):
            raise customError("Missing Vital Key for Data")
        
        for bracket in data["content"]:
            bracketIds.append(bracket.get("id"))
        
        return bracketIds

    @property
    def name(self):
       return json.loads(web.get(f"https://api.ecac.gg/competition/{self.compId}").text)["name"]

class Team:
    def __init__(self, teamId: int, compId: int, ECACHeader: header) -> None:
        self.compId = compId
        self.ECACHeader = ECACHeader.as_dict
        self.teamId = teamId
    
    @property
    def teamContactsRAW(self) -> dict:        
        request = web.get(f"https://api.ecac.gg/competition/entry/{self.teamId}/_view/contact-accounts", headers=self.ECACHeader)
        
        if request.status_code != 200:
            match request.status_code:
                case 401:
                    raise customError("Request Auth Needs Updating")
                case 403:
                    raise customError("You dont have the proper credentials to access data")
                case _:
                    raise customError(f"Error in Communication with API, Web Error Code {request.status_code}")
                
        return request.text
        
    @property
    def teamContacts(self) -> dict:
        participantId = []

        try:
            participants = json.loads(web.get(f"https://api.ecac.gg/competition/entry/{self.teamId}/members").text)
            
            if participants.get("content", None) == None:
                raise customError("Missing Data for Particapents")
            
            for participant in participants["content"]:
                participantId.append(participant["participant"]["id"])
        except:
            pass
        
        request = web.get(f"https://api.ecac.gg/competition/entry/{self.teamId}/_view/contact-accounts", headers=self.ECACHeader)
        
        if request.status_code != 200:
            match request.status_code:
                case 401:
                    raise customError("Request Auth Needs Updating")
                case 403:
                    raise customError("You dont have the proper credentials to access data")
                case _:
                    raise customError(f"Error in Communication with API, Web Error Code {request.status_code}")
            
        data = json.loads(request.text)
        userIdList = []
        userContacts = []
        
        if data == {}:
            userDict = {"game_network_username" : "Empty Team", "discord" : "Empty Team"}
            userContacts.append(userDict)
            return userContacts
        
        for contacts in data["content"]:
            userIdList.append(contacts["user"]["id"])
        
        userIdList = list(set(userIdList))
        
        for id in userIdList:
            
            if len(participantId) > 0 and id not in participantId :
                continue
            
            userDict = {}
            
            for contacts in data["content"]:
                if contacts["user"]["id"] != id:
                    continue
                
                if contacts["network"] == "DISCORD":
                    userDict["discord"] = contacts["handle"]
                else:
                    userDict[contacts["network"].lower()] = contacts["handle"]
            
            userContacts.append(userDict)
        return userContacts    
    
    @property
    def name(self) -> str:
        return json.loads(web.get("https://api.ecac.gg/competition/entry/{}".format(self.teamId)).text).get("alternateName", f"{self.teamId}") 