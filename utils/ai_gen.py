# utils/ai_gen.py
import os
import openai
import asyncio

openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_dorks_openai(prompt: str) -> list[str]:
    """
    Génère une liste de dorks Google ciblés pour un usage en hacking éthique et pentesting.
    
    Args:
        prompt (str): Description précise du type de dorks recherchés (ex: "WordPress vulnerable admin", "exposure de fichiers config", etc.)

    Returns:
        list[str]: Liste de dorks Google prêts à être utilisés pour la recherche.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Le prompt est requis et ne peut pas être vide.")

    system_prompt = (
        "Tu es un expert confirmé en sécurité informatique offensive et pentesting. "
        "Génère une liste claire et concise de dorks Google très efficaces et précis pour la recherche de vulnérabilités, "
        "fuites d'information, failles connues. Répond uniquement par une liste simple, "
        "sans explications ni numérotation, en format texte brut."
    )

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.6,
            n=1,
            stop=None,
        )
        text = response.choices[0].message.content

        # Nettoyer et extraire les dorks : retirer puces, tirets, espaces inutiles
        dorks = []
        for line in text.splitlines():
            clean_line = line.strip(" -–*•\t\n\r")
            if clean_line:
                dorks.append(clean_line)
        return dorks

    except Exception as e:
        # En cas d'erreur, on la remonte
        raise RuntimeError(f"Erreur lors de la génération des dorks OpenAI : {e}")
