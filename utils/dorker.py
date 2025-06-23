import httpx
from bs4 import BeautifulSoup
import asyncio
import re
from urllib.parse import quote_plus
from colorama import Fore, Style, init

init(autoreset=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}

SEARCH_ENGINES = {
    "duckduckgo": "https://html.duckduckgo.com/html/?q={query}",
    # "bing": "https://www.bing.com/search?q={query}",  # Optionnel
    # "google": "https://www.google.com/search?q={query}"  # risqué (captcha)
}

def clean_results(html):
    """Nettoie le HTML et extrait les liens valides"""
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if re.match(r"^https?://", href) and "duckduckgo.com" not in href:
            links.append(href)
    return links

async def search_dork(session, dork, engine="duckduckgo"):
    url = SEARCH_ENGINES[engine].format(query=quote_plus(dork))
    try:
        r = await session.post(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return clean_results(r.text)
        else:
            print(f"{Fore.YELLOW}⚠️ Erreur HTTP {r.status_code} pour le dork: {dork}")
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur {e} pour {dork}")
    return []

async def dorker(dork_list, engine="duckduckgo"):
    found = {}
    async with httpx.AsyncClient(follow_redirects=True) as session:
        tasks = [search_dork(session, dork, engine=engine) for dork in dork_list]
        results = await asyncio.gather(*tasks)
        for dork, links in zip(dork_list, results):
            found[dork] = links or []
            print(f"\n{Fore.CYAN}[DORK] {dork}{Style.RESET_ALL}")
            if links:
                for link in links:
                    print(f"  {Fore.GREEN}- {link}")
            else:
                print(f"  {Fore.RED}- Aucun résultat")
    return found
