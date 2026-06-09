import asyncio
from playwright.async_api import async_playwright
import json
import os

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "history.json")


def load_history():
    """Carrega o histórico de empresas já vistas."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_history(history: set):
    """Salva o histórico de empresas já vistas."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(history), f, ensure_ascii=False)


async def scrape_google_maps(search_term: str, max_results: int = 30, status_callback=None):
    """
    Realiza uma busca no Google Maps via Playwright e capta os dados básicos
    de empresas que NÃO possuem website listado.

    - Empresas COM site sao ignoradas e NAO contabilizadas.
    - Empresas ja vistas em buscas anteriores sao puladas automaticamente.
    """
    leads = []
    history = load_history()
    skipped_has_site = 0
    skipped_already_seen = 0

    def report(msg):
        if status_callback:
            status_callback(msg)
        try:
            print(msg)
        except UnicodeEncodeError:
            print(msg.encode("ascii", errors="replace").decode("ascii"))

    report(f"[BUSCA] Iniciando busca por: {search_term}")
    report(f"[HISTORICO] {len(history)} empresas ja vistas anteriormente.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="pt-BR",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Acessar o Google Maps
        search_url = f"https://www.google.com/maps/search/{search_term.replace(' ', '+')}"
        report(f"[NAV] Acessando Google Maps...")
        await page.goto(search_url)

        try:
            await page.wait_for_selector('div[role="feed"]', timeout=15000)
            report("[OK] Pagina carregada. Procurando resultados...")
        except Exception:
            report(f"[ERRO] Nao foi possivel encontrar resultados para '{search_term}'.")
            await browser.close()
            return leads

        # Scroll no feed lateral para carregar mais resultados
        feed = await page.query_selector('div[role="feed"]')
        if feed:
            report("[SCROLL] Carregando mais resultados...")
            for i in range(5):
                await feed.evaluate("el => el.scrollTop = el.scrollHeight")
                await page.wait_for_timeout(1500)

        # Extrair links de locais
        place_links = await page.query_selector_all('a[href*="/maps/place/"]')

        # Deduplica e limita
        places_hrefs = []
        seen_hrefs = set()
        for link in place_links:
            href = await link.get_attribute('href')
            if href and href not in seen_hrefs:
                seen_hrefs.add(href)
                places_hrefs.append(href)

        places_hrefs = places_hrefs[:max_results]
        total = len(places_hrefs)
        report(f"[INFO] {total} locais encontrados no Maps. Filtrando...")

        for idx, href in enumerate(places_hrefs, 1):
            try:
                new_page = await context.new_page()
                await new_page.goto(href, wait_until="domcontentloaded")
                await new_page.wait_for_timeout(2000)

                # Extrair Nome
                name_el = await new_page.query_selector('h1')
                name = (await name_el.inner_text()).strip() if name_el else "Sem Nome"

                # Verificar se ja foi vista antes (historico)
                name_key = name.lower().strip()
                if name_key in history:
                    skipped_already_seen += 1
                    report(f"  [{idx}/{total}] {name} -> Ja vista antes. Pulando.")
                    await new_page.close()
                    continue

                # Verificar se tem Website
                has_website = False

                website_btn = await new_page.query_selector('a[data-item-id="authority"]')
                if website_btn:
                    has_website = True

                if not has_website:
                    buttons = await new_page.query_selector_all('button')
                    for btn in buttons:
                        try:
                            text = await btn.inner_text()
                            if "site" in text.lower() or "website" in text.lower():
                                has_website = True
                                break
                        except:
                            pass

                # Adicionar ao historico (independente de ter site ou nao)
                history.add(name_key)

                if has_website:
                    skipped_has_site += 1
                    report(f"  [{idx}/{total}] {name} -> TEM SITE. Descartada.")
                    await new_page.close()
                    continue

                # Empresa sem site! Captar dados.

                # Telefone
                phone = ""
                phone_btn = await new_page.query_selector('button[data-tooltip="Copiar número de telefone"]')
                if phone_btn:
                    phone = (await phone_btn.inner_text()).strip()
                else:
                    phone_items = await new_page.query_selector_all('button[data-item-id^="phone"]')
                    for item in phone_items:
                        try:
                            phone = (await item.inner_text()).strip()
                            break
                        except:
                            pass

                # Endereço
                address = ""
                addr_btn = await new_page.query_selector('button[data-item-id="address"]')
                if addr_btn:
                    address = (await addr_btn.inner_text()).strip()
                else:
                    addr_btn2 = await new_page.query_selector('button[data-tooltip="Copiar endereço"]')
                    if addr_btn2:
                        address = (await addr_btn2.inner_text()).strip()

                # Avaliação
                rating = ""
                try:
                    rating_el = await new_page.query_selector('div.F7nice span[aria-hidden="true"]')
                    if rating_el:
                        rating = (await rating_el.inner_text()).strip()
                except:
                    pass

                # Número de avaliações
                reviews = ""
                try:
                    reviews_el = await new_page.query_selector('div.F7nice span span')
                    if reviews_el:
                        reviews_text = (await reviews_el.inner_text()).strip()
                        reviews = reviews_text.replace("(", "").replace(")", "").strip()
                except:
                    pass

                # Categoria
                category = ""
                try:
                    cat_el = await new_page.query_selector('button[jsaction*="category"]')
                    if cat_el:
                        category = (await cat_el.inner_text()).strip()
                except:
                    pass
                if not category:
                    category = search_term

                leads.append({
                    "Name": name,
                    "Phone": phone,
                    "Address": address,
                    "Category": category,
                    "Rating": rating,
                    "Reviews": reviews,
                })
                report(f"  [{idx}/{total}] ++ LEAD: {name} | Tel: {phone}")

                await new_page.close()

            except Exception as e:
                report(f"  [{idx}/{total}] ERRO ao processar: {e}")

        await browser.close()

    # Salvar historico atualizado
    save_history(history)

    report("")
    report("=" * 50)
    report(f"[RESULTADO] {len(leads)} leads SEM SITE encontrados")
    report(f"[DESCARTADAS] {skipped_has_site} empresas com site")
    report(f"[JA VISTAS] {skipped_already_seen} empresas ja prospectadas antes")
    report("=" * 50)

    return leads


def run_scraper(search_term: str, max_results: int = 30, status_callback=None):
    """Wrapper sincrono para o scraper assincrono."""
    return asyncio.run(scrape_google_maps(search_term, max_results, status_callback))
