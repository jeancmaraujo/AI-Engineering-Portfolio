import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('CartolaAPI')

class CartolaAPI:
    def __init__(self):
        self.url = "https://api.cartola.globo.com/atletas/mercado"
        self.headers = {"User-Agent": "Mozilla/5.0"}
        
    def get_provaveis(self):
        try:
            logger.info("Buscando lista de prováveis atualizada da Globo...")
            r = requests.get(self.url, headers=self.headers, timeout=10)
            r.raise_for_status()
            data = r.json()
            
            atletas = data.get("atletas", [])
            posicoes = data.get("posicoes", {})
            clubes = data.get("clubes", {})
            
            provaveis = []
            for a in atletas:
                if a.get('status_id') == 7: # PROVAVEL
                    pos_id = str(a.get('posicao_id'))
                    clube_id = str(a.get('clube_id'))
                    
                    provaveis.append({
                        "atleta_id": a['atleta_id'],
                        "nome": a['apelido'],
                        "clube": clubes.get(clube_id, {}).get('nome', 'N/A'),
                        "posicao": posicoes.get(pos_id, {}).get('abreviacao', 'N/A'),
                        "preco": a['preco_num'],
                        "media": a.get('media_num', 0.0)
                    })
                    
            logger.info(f"API Base Retornou {len(provaveis)} jogadores aptos.")
            return provaveis, data.get('status', {}).get('rodada_atual', 0)
        except Exception as e:
            logger.error(f"Falha de conexão: {e}")
            return [], 0

if __name__ == "__main__":
    api = CartolaAPI()
    prov, rod = api.get_provaveis()
    print(f"Total Prováveis: {len(prov)} | Rodada: {rod}")
