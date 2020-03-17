import pandas as pd
import requests
import json
import os

class Launch:
    def __init__(self):
        self.host = 'https://api.spacexdata.com/v3/launches'
        self.current_directory = os.getcwd()
        self.local_backup_file = self.current_directory + '/spacex_launch_data.json'

    def get_data(self):
        """ Get's SpaceX Data from API or
        fails over to example launch data json
        file if Internet is not present. """
        try:
            response = requests.get(self.host).json()
            response_df = pd.DataFrame.from_dict(response)
        except requests.exceptions.ConnectionError as err:
            print(f"Requests timeout, failing over to backup file: {err}")
            with open(self.local_backup_file) as file_obj:
                data = json.load(file_obj)
            data_df = pd.DataFrame.from_dict(data)
            return data_df.dropna(subset=['launch_success'])
        return response_df.dropna(subset=['launch_success'])