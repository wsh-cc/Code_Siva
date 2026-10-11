from os import path 

from json import load ,dump

from logger import logger

file_name = path.join(path.dirname(path.abspath(__file__)),'storage.json')

def load_data():
    try:
        with open(file_name,'r',encoding='utf-8') as f:
            return load(f)
    except FileNotFoundError as e:
        logger.warning(f'not found: {e}')
        return []
    
def save_data(data):
    try:
        with open(file_name,'w',encoding='utf-8') as f:
            dump(data,f,indent=4,ensure_ascii=False)
    except PermissionError as E:
        #denf hui kan xia you guan ri zhi de
        logger.warning(f'permission denied: {E}')
        return