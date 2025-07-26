import os
import requests
import base64
import re
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()

class APICall:

    '''Necesitamos el user_id para obtener nuestras playlists. Con los IDs de estas podemos sacar los ítems que contienen'''

    def __init__(self):
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.redirect_uri = os.getenv('REDIRECT_URI')
        self.access_token = None
    
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
        print(r.status_code)

    def run(self):
        # auth_url = self.get_auth_url()
        # auth_code = self.get_auth_code(auth_url)
        self.get_access_token(auth_code='AQC1LxcLl2Phb69k-cajwJJYn2zWtLEPPaD4cEJq4Q9ZRunSF_LhkX9gY0tVPu9Vfna3llxLKwcMaRIQTdBeEWaEICnRCzWcjggT_gLrxTDVHtVw5pAKARU6ROpZz1ENmi5S6EjfBdDk8bbjj3-SL4oQtnlRINBqh9ELtTVeVr0FxRFXHfDpIOEXwZ4COS2Ez8HHSVMj_3v8VJWeXMrnZqTupFSbT5p5KtrvARq3q10WiJtscQ0')
        self.get_user_id()  
        print('SIUUU') 
        
    

app = APICall()

print(app.run())
print('SIUUUU')