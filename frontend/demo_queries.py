"""Демонстрационные запросы для локального подбора."""

DEMO_QUERIES = {
    "Популярная категория — ведущий": {
        "city": "Алматы",
        "date": "2026-09-24",
        "event_format": "корпоратив",
        "category": "Ведущий",
        "budget_kzt": 2_000_000,
        "duration_hours": 4,
        "language": "русский",
    },
    "Редкая категория — декоратор": {
        "city": "Алматы",
        "date": "2026-09-24",
        "event_format": "корпоратив",
        "category": "Декоратор",
        "budget_kzt": 2_000_000,
        "duration_hours": 4,
        "language": "",
    },
    "Нет подходящих вариантов — бюджет ниже цены": {
        "city": "Алматы",
        "date": "2026-09-24",
        "event_format": "корпоратив",
        "category": "Ведущий",
        "budget_kzt": 1,
        "duration_hours": None,
        "language": "",
    },
}
