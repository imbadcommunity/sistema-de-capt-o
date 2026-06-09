import asyncio
from playwright.async_api import async_playwright
import time

async def scrape_google_maps(search_term: str, max_results: int = 20):
    """
    Realiza uma busca no Google Maps via Playwright e capta os dados básicos
    de empresas que NÃO possuem website listado.
    """
    leads = []
    
    print(f"[*] Iniciando busca por: {search_term}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Headless=False para evitar bloqueios do Google
        context = await browser.new_context(locale="pt-BR")
        page = await context.new_page()
        
        # Acessar o Google Maps
        await page.goto(f"https://www.google.com/maps/search/{search_term.replace(' ', '+')}")
        
        try:
            # Esperar carregar os resultados iniciais
            await page.wait_for_selector('a[href*="https://www.google.com/maps/place/"]', timeout=10000)
            print("[*] Resultados carregados. Extraindo dados...")
        except Exception as e:
            print(f"[!] Não foi possível encontrar resultados para '{search_term}'.")
            await browser.close()
            return leads

        # Lógica de scroll para carregar mais resultados (simplificada)
        # Em um cenário real, precisaríamos encontrar o painel lateral e scrollar
        
        # Extrair links de locais
        places = await page.query_selector_all('a[href*="https://www.google.com/maps/place/"]')
        
        # Limitar o número de lugares para não demorar demais no teste
        places_hrefs = []
        for place in places:
            href = await place.get_attribute('href')
            if href and href not in places_hrefs:
                places_hrefs.append(href)
                
        places_hrefs = places_hrefs[:max_results]
        print(f"[*] Encontrados {len(places_hrefs)} locais iniciais. Analisando...")

        for href in places_hrefs:
            try:
                # Abrir nova aba para cada local para não perder o feed principal
                new_page = await context.new_page()
                await new_page.goto(href)
                await new_page.wait_for_load_state('networkidle')
                
                # Extrair Nome
                name_element = await new_page.query_selector('h1')
                name = await name_element.inner_text() if name_element else "Sem Nome"
                
                # Verificar se tem Website
                # O Google Maps geralmente usa um ícone de "Mundo" para o website e texto do domínio.
                # Podemos procurar por botões/links que contenham "Website" ou que o href não seja do Google.
                website_elements = await new_page.query_selector_all('a[data-item-id="authority"]')
                
                has_website = False
                if website_elements:
                    has_website = True
                
                if has_website:
                    # Tem site, ignoramos!
                    await new_page.close()
                    continue
                    
                # Não tem site, vamos extrair o resto:
                
                # Telefone
                phone_element = await new_page.query_selector('button[data-tooltip="Copiar número de telefone"]')
                phone = await phone_element.inner_text() if phone_element else ""
                if phone:
                    phone = phone.strip()
                
                # Endereço
                address_element = await new_page.query_selector('button[data-tooltip="Copiar endereço"]')
                address = await address_element.inner_text() if address_element else ""
                if address:
                    address = address.strip()
                    
                # Avaliação e Categoria podem ser complexos de pegar devido a estrutura dinâmica.
                # Simplificando a extração:
                rating = ""
                reviews = ""
                category = search_term # Default fallback
                
                try:
                    rating_element = await new_page.query_selector('div.F7nice > span > span')
                    if rating_element:
                        rating = await rating_element.inner_text()
                except:
                    pass
                
                leads.append({
                    "Name": name,
                    "Phone": phone,
                    "Address": address,
                    "Category": category,
                    "Rating": rating,
                    "Reviews": reviews
                })
                print(f"[+] Lead Encontrado: {name} | Tel: {phone}")
                
                await new_page.close()
                
            except Exception as e:
                print(f"[-] Erro ao processar um local: {e}")
                
        await browser.close()
        
    return leads

def run_scraper(search_term: str):
    """Wrapper síncrono para o scraper assíncrono."""
    return asyncio.run(scrape_google_maps(search_term))
