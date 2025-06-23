# utils/ai_gen.py
import os
import openai
import asyncio

openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_dorks_openai(prompt):
    if not prompt:
        raise ValueError("Un prompt est requis.")

    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Tu es un expert en sécurité informatique. Génère une liste de dorks Google efficaces pour le hacking éthique. Réponds uniquement par une liste sans explication."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.8,
        n=1
    )
    text = response.choices[0].message.content
    dorks = [line.strip("-* \n\t") for line in text.split("\n") if line.strip()]
    return dorks
