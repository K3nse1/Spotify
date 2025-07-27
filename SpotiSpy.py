import os
import csv
import requests
import base64
import re
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()

class SpotiSpy:

    '''Necesitamos el user_id para obtener nuestras playlists. Con los IDs de estas podemos sacar los ítems que contienen'''

    def __init__(self):
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.redirect_uri = os.getenv('REDIRECT_URI')
        self.access_token = 'BQBjzEppudoFJvhZmwuSUtS7XQwMs48lTP6VyVY6ayVGU0_vQjm9eww7Jnwk1H70bWLRtGQjax3gO0eRv-yqS5eE6feHb5ZvT-it7UOpNdyzycdMimLEXeIzVKhk9e0JoUoie762wFooHXq_hzonvcJvnlxAC0uC2YSTZkHgCTT3Yo0p9JT1_L_PXYWPna-Vp9Gollju1GMZAfE6lPmO54Opq8Re6K6S3rICppUr'
    
    def get_auth_url(self):
        """Genera la URL para que el usuario autorice la aplicación"""
        scope = 'playlist-read-private playlist-read-collaborative'
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': scope
        }
        auth_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
        return auth_url

    def get_auth_code(self, auth_url):
        '''TODO: Que el programa busque en el navegador en la auth_url y extraiga la URL que devuelve para sacar el code'''
        
        '''El auth code que necesitamos está dentro de la auth_url. En este método extraemos sólo la parte que nos interesa
        mediante una expresión regular'''

        pattern = r'code=([^&]+)'

        auth_code = re.search(pattern=pattern, string=auth_url)
        return auth_code


    def get_access_token(self, auth_code):
        """Intercambia el código de autorización por un access token"""
        token_url = "https://accounts.spotify.com/api/token"
        
        # Codificar client_id y client_secret en base64
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_base64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_base64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(token_url, headers=headers, data=data)

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            return token_data
        else:
            print(f"Error obteniendo token: {response.status_code}")
            print(response.text)
            return None

    def get_user_id (self):
        endpoint = "https://api.spotify.com/v1/me"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        r = requests.get(endpoint, headers=headers)
        return r.json()['id']
    
    def get_user_playlists(self, user_id):
        endpoint = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        r = requests.get(endpoint, headers=headers)
        return [playlist['id'] for playlist in r.json()['items']], [playlist['name'] for playlist in r.json()['items']]

    def get_tracks_from_playlist (self, playlist_id:list):
        endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        r = requests.get(endpoint, headers=headers)
        # tracks_name = [item['track']['name'] for item in r.json()['items']]
        # tracks_artist = [item['track']['artists'][0]['name'] for item in r.json()['items']]
        tracks_name = []
        tracks_artist = []
        for item in r.json()['items']:
            try:
                if item['track'] is not None:
                    tracks_name.append(item['track']['name'])
                    tracks_artist.append(item['track']['artists'][0]['name'])
            except (KeyError, TypeError):
                print(f"Canción problemática encontrada: {item}")
                continue
        
        playlist = {}
        for item in range(len(tracks_name)):
            playlist[tracks_name[item]] = tracks_artist[item]
        return playlist

    def write_csv(self, user_playlists_id, user_playlists_name):
        with open('playlists.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Playlist', 'Clave', 'Valor'])  # Header del fichero
        
        for idx, id in enumerate(user_playlists_id):
            playlist = self.get_tracks_from_playlist(playlist_id=id)
            playlist_name = user_playlists_name[idx]
            with open('playlists.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for key, value in playlist.items():
                    writer.writerow([playlist_name, key, value])
        


    def run(self):
        # auth_url = self.get_auth_url()
        # # auth_code = self.get_auth_code(auth_url)
        # self.get_access_token(auth_code='AQBXCSJcDNM1D4qOu9zeydg_jCUVbLMcz7um1kVaK_JKEfgNEuUOhnaeJwo0AubZ9KDS4ELXsRDs6Oip1UwazgIuJgU618jj-EEU1b3ngR_s2a7MHLFPpzNi8vf3an5NYHgyYScNHZTKnWarlYI9J02l8ulSVz_SOCsXtqXv5LxZM-VnzqeFqYVR0UH6RVMRLTNV2JIsDU-NsZTXVy-IT7mNOWgAQgsjAwXlCaxrXzgPhqIZhb8')
        
        user_id = self.get_user_id()
        user_playlists_id, user_playlists_name = self.get_user_playlists(user_id=user_id)
        self.write_csv(user_playlists_id, user_playlists_name)      
    
if __name__ == "__main__":
    app = SpotiSpy()
    app.run()