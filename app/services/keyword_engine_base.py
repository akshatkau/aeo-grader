# app/services/keyword.py
from typing import List
from app.schemas.outputs import KeywordInsights
import re

def extract_keywords(text: str) -> List[str]:
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    return list(set(words))[:50]

def simple_keywords(text: str):
    return extract_keywords(text)
