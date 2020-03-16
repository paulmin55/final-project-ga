import pandas as pd
import requests
import json

class Launch:
    def __init__(self):
        self.host = 'https://api.spacexdata.com/v3/launches'

    def get_data(self):
        response = requests.get(self.host).json()
        response_df = pd.DataFrame.from_dict(response)
        return response_df.dropna(subset=['launch_success'])