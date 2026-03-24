import logging
import json
import os
import sys
import unicodedata

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapers.sofascore_scraper import SofascoreScraper
from scrapers.escala10_scraper import Escala10Scraper
from scrapers.twitter_scraper import TwitterScraper
from core.cartola_api import CartolaAPI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ConsensusEngine')

def normalizar(texto):
    """Remove acentos e deixa minúsculo para match exato (Evitar 'Pedro' vazar pra 'Pedro Rocha')."""
    if not texto: return ""
    n = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return n.lower().strip()

class ConsensusEngine:
    def __init__(self):
        self.output_file = os.path.join(os.path.dirname(__file__), "time_consenso.json")
        
    def run_aggregator(self):
        logger.info("Iniciando a Matrix de Consenso...")
        
        cartola = CartolaAPI()
        provaveis, rodada = cartola.get_provaveis()
        
        if not provaveis:
            logger.error("Sem lista de prováveis atualizada.")
            return
            
        dict_provaveis = {normalizar(p['nome']): p for p in provaveis}
        
        sofascore = SofascoreScraper().fetch_player_ratings()
        escala10 = Escala10Scraper().fetch_recommended_players()
        twitter = TwitterScraper().fetch_trending_names()
        
        consenso_final = []
        
        for norm_p_name, obj in dict_provaveis.items():
            score_confianca = 0.0
            origins = ["Cartola Oficial"]
            
            # Escala10 
            for esc_name in escala10:
                if normalizar(esc_name) == norm_p_name:
                    score_confianca += 50.0
                    origins.append("🔥 Dica do Escala 10")
                    break
                    
            # Twitter Hype
            for tw_name, votos in twitter.items():
                if normalizar(tw_name) == norm_p_name:
                    score_confianca += (votos * 10.0)
                    origins.append(f"🐦 Indicado no Twitter ({votos} votos)")
                    break
                    
            # Sofascore
            for sf_name, rating in sofascore.items():
                if normalizar(sf_name) == norm_p_name:
                    if rating >= 7.0:
                        score_confianca += (rating * 3.0) 
                        origins.append(f"📊 Tática Sofascore: {rating}")
                    break

            obj['score_consenso'] = round(score_confianca, 2)
            obj['tracking_fontes'] = " | ".join(origins)
            consenso_final.append(obj)
                
        # Ordenamos por score de consenso e usamos a media_num oficial como desempate!
        consenso_final.sort(key=lambda x: (x.get('score_consenso', 0.0), x.get('media', 0.0)), reverse=True)
        
        # Enforcing rigoroso do 4-3-3
        formacao = {"GOL": 1, "ZAG": 2, "LAT": 2, "MEI": 3, "ATA": 3, "TEC": 1}
        grouped = {"GOL": [], "ZAG": [], "LAT": [], "MEI": [], "ATA": [], "TEC": []}
        
        for p in consenso_final:
            pos = str(p.get("posicao", "")).upper()
            if pos in grouped:
                grouped[pos].append(p)
                
        titulares = []
        banco = []
        
        for pos, qtd in formacao.items():
            disp = grouped[pos]
            titulares.extend(disp[:qtd])
            if pos != "TEC" and len(disp) > qtd:
                banco.append(disp[qtd])

        linha = [t for t in titulares if t.get("posicao", "").upper() not in ["TEC", "GOL"]]
        capitao = max(linha, key=lambda x: x.get("score_consenso", 0.0)) if linha else titulares[0]
        
        final_payload = {
            "estrategia": f"Multi-Source Consensus Filtering (Rodada {rodada})",
            "titulares": titulares,
            "banco": banco,
            "capitao": capitao
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(final_payload, f, ensure_ascii=False, indent=4)
            
        print("\n" + "="*80)
        print("🎯 ESCALAÇÃO 4-3-3 COMPLETA (CONSENSO RIGOROSO)")
        print("="*80)
        for atleta in titulares:
            is_cap = "👑" if capitao and capitao["atleta_id"] == atleta["atleta_id"] else ""
            print(f"{atleta['posicao']} {atleta['nome']} ({atleta['clube']}) {is_cap}")
            print(f"   ► Score: {atleta['score_consenso']} | Fontes: {atleta['tracking_fontes']}")
            
        return final_payload

if __name__ == "__main__":
    engine = ConsensusEngine()
    engine.run_aggregator()
