import os
import re
from huggingface_hub import InferenceClient

MODEL = "google/gemma-3-12b-it"
HF_TOKEN = os.getenv("HF_TOKEN", "")

client = InferenceClient(model=MODEL, token=HF_TOKEN)

def rate_text_quality(text: str) -> float:
    """
    Использует Gemma 3 (через chat_completion API Hugging Face)
    для оценки качества текста по шкале 0–100.
    """
    system_prompt = (
        "Ты эксперт по анализу и оценке текстов кандидатов в сфере IT-рекрутинга. "
        "Твоя задача — оценить ценность текста кандидата по шкале от 0 до 100.\n\n"
        "Критерии оценки:\n"
        "— 100 — текст высокого качества: кандидат упоминает конкретные проекты, победы в олимпиадах, участие в хакатонах, опыт в разработке или аналитике, владение технологиями.\n"
        "— 50 — текст среднего качества: есть интерес к IT, базовые знания или намерение развиваться, но без конкретных достижений.\n"
        "— 0 — текст низкого качества: общие или пустые фразы, отсутствие упоминания опыта, навыков или проектов.\n\n"
        "Дополнительно:\n"
        "— Игнорируй орфографию и стиль — оценивай только содержательность.\n"
        "— Не объясняй ответ, не добавляй текст — выведи только одно число в диапазоне от 0 до 100."
    )

    user_prompt = f'Текст кандидата:\n"{text}"'

    try:
        response = client.chat_completion(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            max_tokens=128
        )

        content = response.choices[0].message["content"]
        match = re.search(r"\d+(\.\d+)?", content)
        return float(match.group()) if match else 0.0

    except Exception as e:
        print(f"⚠️ Ошибка API оценки качества: {e}")
        return 0.0


def calculate_points(quality_score: float) -> float:
    """
    Конвертирует оценку качества (0-100) в поинты.
    Формула: поинты = качество / 10 (т.е. 100 баллов = 10 поинтов)
    """
    return round(quality_score / 10.0, 2)