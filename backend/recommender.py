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


if __name__ == "__main__":
    from loader import load_contractors

    result = filter_candidates(
        load_contractors(),
        {
            "city": "Алматы",
            "date": "2026-10-15",
            "event_format": "корпоратив",
            "category": "Ведущий",
            "budget_kzt": 700000,
            "duration_hours": 5,
            "language": "русский",
        },
    )

    print("Статус:", result["status"])
    print(result["message"])

    for contractor in result["candidates"]:
        print(contractor["id"], contractor["anon_name"]) 