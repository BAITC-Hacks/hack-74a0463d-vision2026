import csv
from datetime import date
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "contactors.csv"


def split_values(value):
    return [
        item.strip()
        for item in value.split("|")
        if item.strip()
    ]


def parse_bool(value):
    value = value.strip().lower()

    if value not in {"true", "false"}:
        raise ValueError(f"Некорректный флаг: {value!r}")

    return value == "true"


def load_contractors(path=DATA_PATH):
    contractors = []
    seen_ids = set()

    with Path(path).open(encoding="utf-8-sig", newline="") as file:
        for line, row in enumerate(csv.DictReader(file), start=2):
            try:
                contractor_id = row["id"].strip()

                if not contractor_id or contractor_id in seen_ids:
                    raise ValueError("Пустой или повторяющийся id")

                price = int(row["price_from_kzt"])
                hours_text = row["max_hours"].strip()
                hours = float(hours_text) if hours_text else None

                if price < 0:
                    raise ValueError("Цена не может быть отрицательной")

                if hours is not None and not 0 < hours < float("inf"):
                    raise ValueError("Некорректная длительность")

                contractor = {
                    "id": contractor_id,
                    "anon_name": row["anon_name"].strip(),
                    "city": row["city"].strip(),
                    "categories": split_values(row["categories"]),
                    "event_formats": split_values(row["event_formats"]),
                    "languages": split_values(row["languages"]),
                    "price_from_kzt": price,
                    "max_hours": hours,
                    "busy_dates": {
                        date.fromisoformat(value)
                        for value in split_values(row["busy_dates"])
                    },
                    "description": row["description"].strip(),
                    "synthetic": parse_bool(row["synthetic"]),
                    "city_imputed": parse_bool(row["city_imputed"]),
                    "price_imputed": parse_bool(row["price_imputed"]),
                }

                contractors.append(contractor)
                seen_ids.add(contractor_id)

            except (KeyError, TypeError, ValueError, AttributeError) as error:
                raise ValueError(
                    f"Ошибка в строке CSV {line}: {error}"
                ) from error

    if not contractors:
        raise ValueError("CSV не содержит подрядчиков")

    return contractors


if __name__ == "__main__":
    contractors = load_contractors()

    print(f"Загружено профилей: {len(contractors)}")
    print(f"Синтетических: {sum(c['synthetic'] for c in contractors)}")