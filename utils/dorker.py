import httpx
import asyncio

async def fetch_url(client, url):
    try:
        r = await client.get(url, timeout=5)
        return r.status_code, len(r.text)
    except Exception:
        return None, None

async def scan_dork(dorks):
    results = []
    async with httpx.AsyncClient() as client:
        for dork in dorks:
            url = f"https://google.com/search?q={dork.replace(' ', '+')}"
            status, length = await fetch_url(client, url)
            result = {
                "dork": dork,
                "url": url,
                "status": status or "timeout",
                "content_length": length or 0,
                "risk": "High" if "admin" in dork else "Medium",
                "country": "FR"
            }
            results.append(result)
    return results
