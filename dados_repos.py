import requests
import pandas as pd
import os
from dotenv import load_dotenv
from math import ceil

# Carrega as variáveis do arquivo .env
load_dotenv()

class DadosRepositorios:

    def __init__(self, owner):
        self.owner = owner
        self.api_base_url = 'https://api.github.com'
        self.access_token= os.getenv('GITHUB_TOKEN')

        if not self.access_token:
            raise ValueError("Token não encontrado no arquivo .env")
            
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-GitHub-Api-Version': '2022-11-28',
            'Accept': 'application/vnd.github.v3+json'
        }

    def lista_repositorios (self):
        repos_list = []
        try:
        # Primeira requisição para obter o número total de repositórios
            response = requests.get(
                f'{self.api_base_url}/users/{self.owner}',
                headers=self.headers    
            )
            response.raise_for_status()  # Lança exceção para status codes de erro
            num_pages = ceil(response.json()['public_repos']/30)

            for page_num in range(1, num_pages + 1):
                url = f'{self.api_base_url}/users/{self.owner}/repos?page={page_num}'
                response = requests.get(url, headers=self.headers)
                repos_list.append(response.json())
                
            return repos_list
        
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            return []


    def nomes_repos(self, repos_list):
        repo_names = []
        for page in repos_list:
            if isinstance(page, list):  # Verifica se page é uma lista
                for repo in page:
                    if isinstance(repo, dict) and 'name' in repo:  # Verifica se repo é um dicionário e tem 'name'
                        repo_names.append(repo['name'])
        
        return repo_names

    def nomes_linguagens(self, repos_list):
        repo_languages = []
        for page in repos_list:
            if isinstance(page, list):
                for repo in page:
                    if isinstance(repo, dict):
                        repo_languages.append(repo.get('language', None))  # Usa get() com valor padrão None

        return repo_languages

    def cria_df_linguagens (self):

        repositorios = self.lista_repositorios()
        if not repositorios:
            print(f"Nenhum repositório encontrado para {self.owner}")
            return pd.DataFrame(columns=['repository_name', 'language'])
        nomes = self.nomes_repos(repositorios)
        linguagens = self.nomes_linguagens(repositorios)

        dados = pd.DataFrame({
            'repository_name': nomes,
            'language': linguagens
        })

        return dados

# Certifique-se que o diretório 'dados' existe
os.makedirs('dados', exist_ok=True)

try:
    # Amazon
    print("Processando repositórios da Amazon...")
    amazon_rep = DadosRepositorios('amzn')
    ling_mais_usadas_amzn = amazon_rep.cria_df_linguagens()
    ling_mais_usadas_amzn.to_csv('dados/linguagens_amzn.csv', index=False)
    
    # Netflix
    print("Processando repositórios da Netflix...")
    netflix_rep = DadosRepositorios('netflix')
    ling_mais_usadas_netflix = netflix_rep.cria_df_linguagens()
    ling_mais_usadas_netflix.to_csv('dados/linguagens_netflix.csv', index=False)
    
    # Spotify
    print("Processando repositórios do Spotify...")
    spotify_rep = DadosRepositorios('spotify')
    ling_mais_usadas_spotify = spotify_rep.cria_df_linguagens()
    ling_mais_usadas_spotify.to_csv('dados/linguagens_spotify.csv', index=False)
    
    print("Processamento concluído com sucesso!")
    
except Exception as e:
    print(f"Ocorreu um erro durante o processamento: {e}")