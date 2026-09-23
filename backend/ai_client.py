import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, APIError


load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def ask_ai(prompt):
    key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "").strip()

    if not key or not model:
        raise ValueError(
            "В .env нужны OPENAI_API_KEY и OPENAI_MODEL"
        )

    with OpenAI(
        api_key=key,
        timeout=8.0,
        max_retries=0,
    ) as client:
        response = client.responses.create(
            model=model,
            input=prompt,
            max_output_tokens=150,
            store=False,
        )

    text = response.output_text.strip()
    if not text:
        raise ValueError("Модель вернула пустой ответ")

    return text


if __name__ == "__main__":
    try:
        print(ask_ai("Ответь по-русски: Подключение работает."))
    except APIError as error:
        print("Ошибка API:", type(error).__name__)
        print("Статус:", getattr(error, "status_code", None))
        raise SystemExit(1)
    except ValueError as error:
        print(error)
        raise SystemExit(1)