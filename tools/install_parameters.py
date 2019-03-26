import os
import json 

class Install_Parameters():
    with open(os.getenv('INSTALL_PATH')+'/datos.json') as jsonData:
        install_data = json.loads(jsonData.read())
    
    def __init__(self):
        pass

    @staticmethod
    def get_traffic_light_pixels(self):
        pass