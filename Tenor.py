import requests
import json

class Tenor():
    def __init__(self, token: str):
        self.token = token

    def search_gifs(self, search_query: str):
        res = requests.get(f"https://g.tenor.com/v1/search?q={search_query}&key={self.token}&limit=1")

        if res.status_code == 200:
            return json.loads(res.content)
    
    def get_random_gif_with_query(self, search_query: str):
        res = requests.get(f"https://g.tenor.com/v1/random?key={self.token}&q={search_query}&limit=1&locale=en_EN&contentfilter=off&media_filter=minimal")

        if res.status_code == 200:
            content = json.loads(res.content)
            return content["results"][0]["itemurl"]
