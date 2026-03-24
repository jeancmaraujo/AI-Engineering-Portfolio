import logging
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SofascoreScraper')

class SofascoreScraper:
    """
    Busca as notas táticas globais (0.0 a 10.0) de jogadores do Brasileirão escondidas nas APIs base do Sofascore.
    Funciona buscando diretamente do JSON de Season Stats e poupa uso do CPU.
    """
    def __init__(self):
        # Ex: endpoint padrão base para estatisticas da liga Brasileira no Sofascore
        self.base_url = "https://api.sofascore.com/api/v1/unique-tournament/325/season/58766/statistics"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
    def fetch_player_ratings(self):
        logger.info("Acessando endpoint interno de notas do Sofascore Brasil...")
        ratings = {}
        try:
            res = requests.get(self.base_url, headers=self.headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                results = data.get('results', [])
                
                for p in results:
                    name = p.get('player', {}).get('name', '')
                    rating = p.get('rating', 0.0)
                    if name:
                        ratings[name] = float(rating)
                        
                logger.info(f"Sofascore retornou a nota técnica de {len(ratings)} jogadores.")
            else:
                logger.warning(f"Sofascore API bloqueou acesso nativo (Status {res.status_code}).")
        except Exception as e:
            logger.error(f"Erro na extração profunda do Sofascore: {e}")
            
        # Fallback demonstrativo pro Consenso
        if not ratings:
            logger.info("Injetando notas mockadas do tier principal do campeonato de fallback.")
            ratings = {
                "Pedro": 7.8, "Arrascaeta": 7.6, "Estêvão": 7.4, 
                "Lucas Moura": 7.2, "Veiga": 7.1, "Everton Ribeiro": 7.0
            }
            
        return ratings

if __name__ == "__main__":
    s = SofascoreScraper()
    print(s.fetch_player_ratings())
