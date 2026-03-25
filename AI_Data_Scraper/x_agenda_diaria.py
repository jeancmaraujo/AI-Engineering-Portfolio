import asyncio
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# Importamos as Funções do script de Automação
from x_viral_agent import main as postar_noticia_matinal, postar_relatorio_da_noite

async def run_noticia_da_manha():
    print(f"\n🌞 [08:00 AM] ACORDANDO A MÁQUINA: Lendo Jornal do Cripto e Postando no X...")
    await postar_noticia_matinal()

async def run_codigo_da_tarde():
    print(f"\n☕ [14:00 PM] TARDE: Carregando banco de dados de Dicas Python para enviar... (Lógica a ser programada)")
    # await_sua_logica_de_postar_codigo()

async def run_relatorio_da_noite():
    print(f"\n🌙 [20:00 PM] NOITE: Carregando e escrevendo o Relatório do Trading Bot...")
    await postar_relatorio_da_noite()

async def iniciar_agenda_eterna():
    print("="*60)
    print("⏰ [SISTEMA] INICIANDO AGENDAMENTO GLOBAL DE POSTAGENS - 24/7")
    print("="*60)
    
    # Criamos o relógio do sistema
    scheduler = AsyncIOScheduler()
    
    # Configuração Exata dos Horários (Pode alterar para testar = hour=*, minute=*)
    scheduler.add_job(run_noticia_da_manha, 'cron', hour=8, minute=0)
    scheduler.add_job(run_codigo_da_tarde, 'cron', hour=14, minute=0)
    scheduler.add_job(run_relatorio_da_noite, 'cron', hour=20, minute=0)
    
    scheduler.start()
    print("🤖 O Bot Centralizador está vivo. Os canhões estão apontados para as 08:00, 14:00 e 20:00.")
    print("Pressione 'Ctrl + C' se quiser desligar o motor de agendamento.")
    
    # Prende o script num loop infinito para não fechar a tela preta
    while True:
        await asyncio.sleep(3600) # Dorme 1 hora para economizar memória (ele acorda pelo Scheduler nas horas certas)

if __name__ == "__main__":
    try:
        asyncio.run(iniciar_agenda_eterna())
    except (KeyboardInterrupt, SystemExit):
        print("\nDesligando a IA com segurança...")
