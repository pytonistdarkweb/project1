from typing import Optional
import httpx
from fastapi import HTTPException
import os

class TranslationClient:
    def __init__(self):
        self.api_key = os.getenv("TRANSLATION_API_KEY")
        self.base_url = "https://translation.googleapis.com/language/translate/v2"

    async def translate_text(self, text: str, target_lang: str = "en", source_lang: str = "ru") -> Optional[str]:
        if not text:
            return None
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    params={
                        "key": self.api_key,
                    },
                    json={
                        "q": text,
                        "target": target_lang,
                        "source": source_lang,
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result["data"]["translations"][0]["translatedText"]
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Translation service error: {str(e)}") 