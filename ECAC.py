import requests as web
import json

class header:
    def __init__(self, headerTitle: any) -> None:
        self.headerTitle = headerTitle
        self.headerValue = None
        pass
    
    def as_dict(self) -> dict:
        if self.headerValue == None:
            raise customError("Header Not Set")
        
        return {self.headerTitle : self.headerValue}
        
class Competition:
    """Class used to hold Competition Data
    """
    def __init__(self, compId: int, bracketId: int = None) -> None:
        """Creates an Instance of the Competition Class

        Args:
            compId (int): The competitions ID in the form of an integer
            bracketId (int, optional): The bracket Id in the form of an integer. Defaults to None.
        """
        self.bracketId = bracketId
        self.compId = compId
  
    @property
    def teamIds(self) -> list:
        """Returns teamIds as a list. If the parameter bracketId is filled it will return data based off BracketId 

        Raises:
            ConnectionError: Error Connecting with API
            KeyError: Data Returned missing Vital Key "Content"

        Returns:
            list: Team Ids in a list
        """
        
        competitionURL = f"https://api.ecac.gg/competition/entry/document?competitionId={self.compId}&page=0&size=1000&sort=seed"
        bracketURL = f"https://api.ecac.gg/competition/entry/document?competitionId={self.compId}&brackets={self.bracketId}&page=0&size=2000"
                
        request = web.get(bracketURL if self.bracketId != None else competitionURL)
            
        if request.status_code != 200:
            raise ConnectionError(f"Unable to Connect to API or API sent a Non-200 Web Code: Error {request.status_code}") 
            
        data = json.loads(request.text)
            
        teamIds = []
            
        if "content" not in list(data.keys()):
            raise KeyError("Missing Vital 'Content' Key in Data")
            
        for team in data["content"]:
            teamIds.append(team["id"])
            
        return teamIds
    
    @property
    def bracketIds(self) -> list:  
        """Returns all bracket Ids from a Competition

        Raises:
            ConnectionError: Error Connecting with API
            json.JSONDecodeError: Json data returned from site is not parsable by json module
            KeyError: Data is missing Key Value "content"

        Returns:
            list:Returns the bracket Ids as a list 
        """
        bracketIds = []
        request  = web.get(f"https://api.ecac.gg/competition/{self.compId}/brackets")
        
        if request .status_code != 200:
            raise ConnectionError("Error Connecting with API, Status Code Error {request.status_code}") 

        try:
            data = json.loads(request .text)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error Decoding Json:\n{e}")
            
        if "content" not in list(data.keys()):
            raise KeyError("Missing Vital Key for Data")
        
        for bracket in data["content"]:
            bracketIds.append(bracket.get("id"))
        
        return bracketIds

    @property
    def name(self) -> str:
        """Name of the competition

        Raises:
            json.JSONDecodeError: Error Decoding Json
            ConnectionError: Error Connecting to API

        Returns:
            str: Name of the Competition
        """
        try:
            name = json.loads(web.get(f"https://api.ecac.gg/competition/{self.compId}").text)["name"]
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Issue Parsing Json Data\nError: {e}")
        except web.ConnectionError as e:
            raise ConnectionError(f"Error Connecting to API\nError: {e}")

        return name

class Team:
    """Class to hold all info based on a Team format
    """
    def __init__(self, teamId: int, compId: int, ECACHeader: header) -> None:
        """Creates a new instance of Team

        Args:
            teamId (int): The Id of the Team
            compId (int): The Id of the Competition the team is in 
            ECACHeader (header): A header Based off the Header Class created in this File
        """
        self.compId = compId
        self.ECACHeader = ECACHeader.as_dict()
        self.teamId = teamId
    
    @property
    def teamContactsRAW(self) -> dict:        
        """Returns team COntact info as it is requested

        Raises:
            ConnectionError: Not Able to find team
            ConnectionError: Incorrect Credentials
            ConnectionError: Unable to access API data

        Returns:
            dict: the request data as a dictionary 
        """
        request = web.get(f"https://api.ecac.gg/competition/entry/{self.teamId}/_view/contact-accounts", headers=self.ECACHeader)
        
        if request.status_code != 200:
            match request.status_code:
                case 401:
                    raise ConnectionError("Request Auth Needs Updating")
                case 403:
                    raise ConnectionError("You dont have the proper credentials to access data")
                case _:
                    raise ConnectionError(f"Error in Communication with API, Web Error Code {request.status_code}")
                
        return request.text
        
    @property
    def teamContacts(self) -> dict:
        """teamContacts providing only necessary data 

        Raises:
            KeyError: Missing data
            ConnectionError: Request Auth needs updating
            ConnectionError: Dont contain the proper credentials
            ConnectionError: Error Connectig with API

        Returns:
            dict: _description_
        """
        participantId = []

        try:
            participants = json.loads(web.get(f"https://api.ecac.gg/competition/entry/{self.teamId}/members").text)
            
            if participants.get("content", None) == None:
                raise KeyError("Missing Data for Particapents")
            
            for participant in participants["content"]:
                participantId.append(participant["participant"]["id"])
        except KeyError:
            pass
        
        request = web.get(f"https://api.ecac.gg/competition/entry/{self.teamId}/_view/contact-accounts", headers=self.ECACHeader)
        
        if request.status_code != 200:
            match request.status_code:
                case 401:
                    raise ConnectionError("Request Auth Needs Updating")
                case 403:
                    raise ConnectionError("You dont have the proper credentials to access data")
                case _:
                    raise ConnectionError(f"Error in Communication with API, Web Error Code {request.status_code}")
            
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
        """returns the name of the team

        Returns:
            str: Name of the Team as a string
        """
        try:
            name = json.loads(web.get("https://api.ecac.gg/competition/entry/{}".format(self.teamId)).text).get("alternateName", f"{self.teamId}")
        except json.JSONDecodeError as e:
            json.JSONDecodeError(f"Error Decoding JSON Data with Json module\nError: {e}")
        except web.ConnectionError as e:
            ConnectionError(f"Error Connecting with API\nError: {e}")
        return name  