import ECAC
import typer
import os
import json

class CustomError(Exception):
    def __init__(self, message:str) -> None:
        self.message = message
    
    def __str__(self) -> str:
        return self.message
    
app = typer.Typer()

def read_file(api_key_path: str) -> str:
    try:
        file = open(f"{api_key_path}", "r")
        output = file.readline()
        return output
    
    except Exception as e:
        print(f"Error:\n{e}")

def get_key(api_key_path:str) -> str:
    key = read_file(api_key_path)
    
    if not key.startswith("Bearer"):
        raise CustomError("Incorrect API Key, Must start with Bearer")
    return key
    
@app.command()
def scrape_users(api_key_path: str, comp_id: int, network: str, bracket_id: int = None, ouput_folder: str = "Ouput"):
    #Check Vars
    if not os.path.isfile(api_key_path):
        raise CustomError(f"File Doesnt Exist: {api_key_path}")
    
    if not api_key_path.endswith(".txt"):
        raise CustomError("Api key file must be a .txt file")
    
    if ouput_folder == "Output":
        if not os.path.isdir(ouput_folder):
                os.mkdir("./Ouput")
        else:
            pass
    else:
        if not os.path.isdir(ouput_folder):
            os.mkdir(f"./{ouput_folder}")
    
    #Set ECAC Vars
    ECAC.ECAC_API_header.set(get_key(api_key_path))
    ECAC.comp_details.set_id(comp_id)
    ECAC.network = network
    
    #Run ECAC Comp Details Scrape
    ECAC.comp_details.scrape_details()
    
    #Actual Processor
    file = open(f"./{ouput_folder}/{ECAC.comp_details.read()['name'].replace(" ", "-")}-users.json", "w", encoding="utf-8")
    
    if bracket_id is None:
        file.write(json.dumps(ECAC.process_contact_info(ECAC.scrape_team_ids()), ensure_ascii=False))
        file.close()
    else:
        file.write(json.dumps(ECAC.process_contact_info(ECAC.scrape_team_ids_bracket(bracket_id)), ensure_ascii=False))
        file.close()
        
@app.command()
def temp():
    print("Temp")
    
    
    
if __name__ == "__main__":
    app()