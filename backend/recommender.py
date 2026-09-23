from collections import Counter
from datetime import date
from math import isfinite


CALENDAR_START = date(2026, 9, 23)
CALENDAR_END = date(2026, 12, 31)


def normalize(value):
    return str(value).strip().casefold()


def positive_number(value, name):
    if isinstance(value, bool):
        raise ValueError(f"{name}: укажи положительное число")

    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name}: укажи положительное число") from None

    if not isfinite(number) or number <= 0:
        raise ValueError(f"{name}: укажи положительное число")

    return number


def filter_candidates(contractors, request):
    required = ("city", "date", "event_format", "category", "budget_kzt")

    for field in required:
        if request.get(field) is None or not str(request[field]).strip():
            raise ValueError(f"Не заполнено поле: {field}")

    try:
        event_date = date.fromisoformat(str(request["date"]))
    except ValueError:
        raise ValueError("Укажи дату в формате ГГГГ-ММ-ДД") from None

    if not CALENDAR_START <= event_date <= CALENDAR_END:
        raise ValueError("Доступны даты с 23.09.2026 по 31.12.2026")

    budget = positive_number(request["budget_kzt"], "Бюджет")
    duration = request.get("duration_hours")

    if duration is not None:
        duration = positive_number(duration, "Длительность")

    city = normalize(request["city"])
    category = normalize(request["category"])
    event_format = normalize(request["event_format"])
    language = normalize(request.get("language") or "")

    local_candidates = [
        contractor
        for contractor in contractors
        if normalize(contractor["city"]) == city
        and category in {
            normalize(value) for value in contractor["categories"]
        }
    ]

    if not local_candidates:
        return {
            "status": "category_absent",
            "candidates": [],
            "message": "В каталоге нет такой категории в выбранном городе.",
            "rejected": [],
            "reason_counts": {},
        }

    accepted = []
    rejected = []
    reason_counts = Counter()

    for contractor in local_candidates:
        reasons = []

        if event_date in contractor["busy_dates"]:
            reasons.append("заняты на дату")

        if contractor["price_from_kzt"] > budget:
            reasons.append("цена «от» превышает бюджет")

        formats = {
            normalize(value) for value in contractor["event_formats"]
        }
        if event_format not in formats:
            reasons.append("не работают с выбранным форматом")

        languages = {
            normalize(value) for value in contractor["languages"]
        }
        if language and language not in languages:
            reasons.append("не указан нужный язык")

        max_hours = contractor["max_hours"]
        if (
            duration is not None
            and max_hours is not None
            and duration > max_hours
        ):
            reasons.append("недостаточная длительность работы")

        if reasons:
            rejected.append({
                "id": contractor["id"],
                "reasons": reasons,
            })
            reason_counts.update(reasons)
        else:
            accepted.append(contractor)

    if accepted:
        message = f"Под условия подходят: {len(accepted)}."
    else:
        message = "Категория в городе есть, но никто не подходит по условиям."

    if rejected:
        details = "; ".join(
            f"{reason}: {count}"
            for reason, count in reason_counts.items()
        )
        message += f" Причины исключения: {details}."
        message += " Один профиль может иметь несколько причин."

    return {
        "status": "matched" if accepted else "no_match",
        "candidates": accepted,
        "message": message,
        "rejected": rejected,
        "reason_counts": dict(reason_counts),
    }


def description_excerpt(contractor, event_format):
    import re

    text = " ".join(contractor["description"].split())
    sentences = re.split(r"(?<=[.!?])\s+", text)

    relevant = [
        sentence
        for sentence in sentences
        if normalize(event_format) in normalize(sentence)
    ]

    excerpt = next(iter(relevant), sentences[0] if sentences else "")

    if len(excerpt) > 220:
        excerpt = excerpt[:220].rsplit(" ", 1)[0] + "…"

    return excerpt


def build_explanation(contractor, request):
    price = f"{contractor['price_from_kzt']:,}".replace(",", " ")
    budget = f"{float(request['budget_kzt']):,.0f}".replace(",", " ")

    facts = [
        f"работает с форматом «{request['event_format']}»",
        f"на {request['date']} нет отметки о занятости",
        f"цена от {price} ₸ при бюджете {budget} ₸",
    ]

    if request.get("language"):
        facts.append(f"язык — {request['language']}")

    duration = request.get("duration_hours")
    if duration is not None and contractor["max_hours"] is not None:
        facts.append(
            f"длительность {float(duration):g} ч "
            f"укладывается в максимум {contractor['max_hours']:g} ч"
        )

    explanation = "; ".join(facts)
    explanation = explanation[0].upper() + explanation[1:] + "."

    excerpt = description_excerpt(contractor, request["event_format"])
    if excerpt:
        explanation += f" Из описания профиля: «{excerpt}»"

    return explanation


def recommend(contractors, request):
    result = filter_candidates(contractors, request)

    # Сначала прямое упоминание формата в описании,
    # затем цена, затем уникальный id.
    ranked = sorted(
        result["candidates"],
        key=lambda contractor: (
            -int(
                normalize(request["event_format"])
                in normalize(contractor["description"])
            ),
            contractor["price_from_kzt"],
            contractor["id"],
        ),
    )

    cards = [
        {
            "id": contractor["id"],
            "anon_name": contractor["anon_name"],
            "category": request["category"],
            "city": contractor["city"],
            "price_from_kzt": contractor["price_from_kzt"],
            "explanation": build_explanation(contractor, request),
            "synthetic": contractor["synthetic"],
            "city_imputed": contractor["city_imputed"],
            "price_imputed": contractor["price_imputed"],
        }
        for contractor in ranked[:3]
    ]

    message = result["message"]

    if 0 < len(ranked) < 3:
        total = len(ranked) + len(result["rejected"])

        if total < 3:
            message += (
                f" В этой категории в выбранном городе "
                f"всего профилей: {total}."
            )
        else:
            message += " Остальные профили исключены по указанным причинам."

    return {
        "status": result["status"],
        "cards": cards,
        "message": message,
        "diagnostics": {
            "eligible_count": len(ranked),
            "rejected_count": len(result["rejected"]),
            "reason_counts": result["reason_counts"],
        },
    }


if __name__ == "__main__":
    import json
    from loader import load_contractors

    contractors = load_contractors()

    request = {
        "city": "Алматы",
        "date": "2026-10-15",
        "event_format": "корпоратив",
        "category": "Ведущий",
        "budget_kzt": 700000,
        "duration_hours": 5,
        "language": "русский",
    }

    result = recommend(contractors, request)
    repeated = recommend(contractors, request)

    assert len(result["cards"]) <= 3
    assert result == repeated, "Повторный запрос изменил результат"

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("Проверки количества карточек и повторяемости пройдены.")
