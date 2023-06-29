import os
import json
import requests
import pandas as pd
from io import StringIO

class Spectr:
    def __init__(self, api_key):
        self.api_key = api_key
        self.repo_id = None
        self.base_url = "https://backend.getspectr.com/api"  # replace with your server's URL

    def repo(self, title, description=None):
        # Connect to the repo using the provided API key and repo_title
        response = requests.post(
            f"{self.base_url}/client/repo",
            data={"api_key": self.api_key, "title": title, "context": description}
        )

        if response.status_code == 200 or response.status_code == 201:
            self.repo_id = response.json()['id']
        else:
            raise Exception(f"Could not connect to repo: {response.json()}")

    def add(self, data, context=None):
        if isinstance(data, str):
            if not os.path.exists(data):
                raise FileNotFoundError(f"The file at {data} does not exist")
            if not data.endswith('.pdf') and not data.endswith('.json') and not data.endswith('.csv'):
                raise ValueError("Spectr currently supports PDF, JSON and CSV files only.")
            
            with open(data, 'rb') as file:
                response = requests.post(
                    f"{self.base_url}/client/add",
                    data={"api_key": self.api_key, "repo_id": self.repo_id, "context": context},
                    files={"file": file}
                )

        # Add data to the repo
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data)
        
            response = requests.post(
                f"{self.base_url}/client/add",
                data={"api_key": self.api_key, "repo_id": self.repo_id, "data": data, "context": context}
            )

        if response.status_code != 200:
            raise Exception(f"Could not add data: {response}")

        print(f"Response from add: {response.json()['detail']}")

    def query(self, query):
        # Perform a query on the repo
        response = requests.post(
            f"{self.base_url}/client/query",
            data={"api_key": self.api_key, "repo_id": self.repo_id, "query": query}
        )

        if response.status_code != 200:
            raise Exception(f"Query failed: {response.json()}")

        return response.json()['detail']

    def get_df(self, query):
        # Perform a query on the repo
        response = requests.post(
            f"{self.base_url}/client/get_df",
            data={"api_key": self.api_key, "repo_id": self.repo_id, "query": query}
        )

        if response.status_code != 200:
            raise Exception(f"Query failed: {response.json()}")
        
        df = pd.read_csv(StringIO(response.json()['detail']), sep=",")

        return df
    
    def ask_df(self, df, query):
        df_json = df.to_json(orient='split')
        response = requests.post(
            f"{self.base_url}/client/ask_df",
            data={"api_key": self.api_key, "repo_id": self.repo_id, "query": query, "df_json": df_json}
        )

        if response.status_code != 200:
            raise Exception(f"Query failed: {str(response)}")
        
        if isinstance(response.json()['detail'], dict):
            try:
                df = pd.DataFrame(response.json()['detail'])
                return df
            except Exception as e:
                raise ValueError(f"Error coverting the server response into a dataframe: {str(e) + str(response.json())}")
        else:
            raise ValueError(f"Invalid response received: {str(response.json())}")