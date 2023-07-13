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

    def repo(self, title, context=None):
        # Connect to the repo using the provided API key and repo_title
        try:
            response = requests.post(
                f"{self.base_url}/client/repo",
                data={"api_key": self.api_key, "title": title, "context": context}
            )
        except Exception as e:
            raise Exception(
                "Error: Failed to get a response from Spectr server. Please try again."
                "If the problem persists, please contact Hussain at hussain@getspectr.com"
            ) from None

        if response.status_code == 200 or response.status_code == 201:
            self.repo_id = response.json()['id']
        else:
            raise Exception(f"Could not connect to repo: {str(response.json())}")


    def add(self, data, context):
        if isinstance(data, str):
            if not os.path.exists(data):
                raise FileNotFoundError(f"The file at {data} does not exist")
            if not data.endswith('.pdf') and not data.endswith('.json') and not data.endswith('.csv'):
                raise ValueError("Spectr currently supports PDF, JSON and CSV files only.")
            
            with open(data, 'rb') as file:
                try:
                    response = requests.post(
                        f"{self.base_url}/client/add",
                        data={"api_key": self.api_key, "repo_id": self.repo_id, "context": context},
                        files={"file": file}
                    )
                except Exception as e:
                    raise Exception(
                        "Error: Failed to get a response from Spectr server. Please try again."
                        "If the problem persists, please contact Hussain at hussain@getspectr.com"
                    ) from None

        # Add data to the repo
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data)
        
            try:
                response = requests.post(
                    f"{self.base_url}/client/add",
                    data={"api_key": self.api_key, "repo_id": self.repo_id, "data": data, "context": context}
                )
            except Exception as e:
                raise Exception(
                    "Error: Failed to get a response from Spectr server. Please try again."
                    "If the problem persists, please contact Hussain at hussain@getspectr.com"
                ) from None

        if response.status_code != 200:
            raise Exception(f"Could not add data: {str(response.json())}")

        print(f"{response.json()['detail']}")

    def query(self, query, verify=False):
        # Perform a query on the repo
        try:
            response = requests.post(
                f"{self.base_url}/client/query",
                data={"api_key": self.api_key, "repo_id": self.repo_id, "query": query, "eval": verify}
            )
        except Exception as e:
            raise Exception(
                "Error: Failed to get a response from Spectr server. Please try again."
                "If the problem persists, please contact Hussain at hussain@getspectr.com"
            ) from None

        if response.status_code != 200:
            raise Exception(f"Query failed: {str(response.json())}")
        if not verify:
            print(response.json()['response'])
            return
        print("Response:")
        print(response.json()['response'])
        print("Evaluation:")
        eval_df = pd.DataFrame(response.json()['evaluation'])
        eval_df.style.set_properties(
        **{
            'inline-size': '600px',
            'overflow-wrap': 'break-word',
        }, 
        subset=["Response", "Source"]
    )
        print(eval_df)
        return

    def get_df(self, query, verify=False):
        # Perform a query on the repo
        try:
            response = requests.post(
                f"{self.base_url}/client/get_df",
                data={"api_key": self.api_key, "repo_id": self.repo_id, "query": query, "eval": verify}
            )
        except Exception as e:
            raise Exception(
                "Error: Failed to get a response from Spectr server. Please try again."
                "If the problem persists, please contact Hussain at hussain@getspectr.com"
            ) from None

        if response.status_code != 200:
            raise Exception(f"Query failed: {response.json()}")
        
        if not verify:
            response_df = pd.read_csv(StringIO(response.json()['response']), sep=",")
            return response_df

        response_df = pd.read_csv(StringIO(response.json()['response']), sep=",")
        eval_df = pd.DataFrame(response.json()['evaluation'])

        eval_df.style.set_properties(
            **{
                'inline-size': '600px',
                'overflow-wrap': 'break-word',
            }, 
            subset=["Response", "Source"]
        )

        return response_df, eval_df
    
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