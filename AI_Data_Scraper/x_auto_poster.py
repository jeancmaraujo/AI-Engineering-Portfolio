import asyncio
from playwright.async_api import async_playwright

# Aponta para o seu Chrome logado no X (evita bloqueios e necessidade de API Paga do Twitter)
USER_DATA_DIR = r"C:\Users\Jean\Automacoes_X\perfil_x_bot"

async def post_to_x(tweet_text):
    print("🚀 [AGENT] Iniciando Módulo de Automação Visual (Playwright)...")
    async with async_playwright() as p:
        # Abrimos o navegador usando a sua sessão real que já está logada
        print("🔓 [AGENT] Injetando Cookies de Sessão Segura...")
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False # Podemos deixar True depois para ele rodar "invisível"
        )
        page = await browser.new_page()
        
        try:
            print("🌐 [AGENT] Acessando Endpoint: x.com/home")
            await page.goto("https://x.com/home", timeout=60000)
            await page.wait_for_timeout(8000) # Espera o feed carregar na tela
            
            # Encontra a caixa de texto do Tweet
            print("✍️ [AGENT] Escrevendo a publicação...")
            tweet_box_selector = "div[data-testid='tweetTextarea_0']"
            await page.wait_for_selector(tweet_box_selector, state="visible", timeout=15000)
            await page.click(tweet_box_selector)
            
            # Digita o texto (como se fosse um humano teclado)
            await page.fill(tweet_box_selector, tweet_text)
            await page.wait_for_timeout(2000)
            
            # Clica no botão azul de Postar
            print("📨 [AGENT] Confirmando Envio via atalho (Ctrl+Enter)...")
            await page.keyboard.press("Control+Enter")
            
            # Aguarda a confirmação de que foi postado
            await page.wait_for_timeout(4000)
            print("✅ [AGENT] SUCESSO! Inteligência Artificial publicou seu Tweet.")
            
        except Exception as e:
            print(f"❌ [AGENT] Falha na matriz de automação: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    # TEXTO DE TESTE (AMANHÃ NÓS LIGAREMOS ISSO AO RELATÓRIO DO SEU DATA SCRAPER)
    meu_tweet = "🚀 Testando meu novo Agente Autônomo em Python... Esse Tweet foi escrito e publicado sozinho por uma IA local rodando no meu VSCode! A era do '#ClaudeCode' e automação Open-Source chegou. Quem quer o código? 👇"
    
    asyncio.run(post_to_x(meu_tweet))
