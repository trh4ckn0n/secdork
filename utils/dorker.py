import os
from serpapi import GoogleSearch
import asyncio

def scan_dork_google(dork: str, api_key: str):
    try:
        search = GoogleSearch({
            "q": dork,
            "api_key": api_key,
            "num": 10,  # nombre max de résultats (jusqu'à 100)
            "hl": "fr",  # langue française
            "google_domain": "google.com",
        })
        results = search.get_dict()
        links = []
        for r in results.get("organic_results", []):
            link = r.get("link")
            if link:
                links.append(link)
        return {
            "dork": dork,
            "status": 200 if links else "no_results",
            "results": links,
            "risk": "High" if any(x in dork.lower() for x in ["admin", "login", "root"]) else "Medium",
            "source": "serpapi",
            "country": "FR"
        }
    except Exception as e:
        return {
            "dork": dork,
            "status": "error",
            "error": str(e)
        }

async def scan_dork(dorks):
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise ValueError("❌ La variable d'environnement SERPAPI_KEY est manquante.")

    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(None, scan_dork_google, dork, api_key) for dork in dorks]
    return await asyncio.gather(*tasks)
