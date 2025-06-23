import os
import httpx
import asyncio
from urllib.parse import urlparse

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Liste de mots-clés pour évaluer le risque potentiel d'une URL trouvée
RISK_KEYWORDS = {
    "high": ["phpmyadmin", ".env", "admin", "config", "passwd", "wp-login"],
    "medium": ["login", "signin", "dashboard", "panel"],
}


def detect_risk(url: str) -> str:
    url = url.lower()
    for keyword in RISK_KEYWORDS["high"]:
        if keyword in url:
            return "élevé"
    for keyword in RISK_KEYWORDS["medium"]:
        if keyword in url:
            return "modéré"
    return "faible"


def clean_url(url: str) -> str:
    try:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    except Exception:
        return url.strip()


async def search_google(dork: str) -> list:
    if not SERPAPI_KEY:
        raise ValueError("Clé SERPAPI manquante dans les variables d’environnement.")

    url = "https://serpapi.com/search"
    params = {
        "q": dork,
        "engine": "google",
        "api_key": SERPAPI_KEY,
        "num": 10,  # Nombre de résultats par dork
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            results = data.get("organic_results", [])
            links = [clean_url(r.get("link", "")) for r in results if r.get("link")]
            return list(set(links))  # Uniques
        except Exception as e:
            print(f"❌ Erreur SERPAPI: {e}")
            return []


async def scan_single_dork(dork: str) -> dict:
    links = await search_google(dork)
    risk_level = "aucun"
    if links:
        combined = " ".join(links).lower()
        risk_level = detect_risk(combined)
    return {
        "dork": dork,
        "results": links,
        "risk": risk_level,
    }


async def scan_dork(dorks: list[str]) -> list[dict]:
    tasks = [scan_single_dork(d) for d in dorks]
    return await asyncio.gather(*tasks)
