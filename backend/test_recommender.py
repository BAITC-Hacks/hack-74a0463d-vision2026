import json
import unittest
from datetime import date
from unittest.mock import patch

from backend import ai_explanations
from backend.recommender import recommend


class RecommenderTests(unittest.TestCase):
    def setUp(self):
        self.request = {
            "city": "Алматы",
            "date": "2026-10-15",
            "event_format": "корпоратив",
            "category": "Ведущий",
            "budget_kzt": 200000,
            "duration_hours": 5,
            "language": "русский",
        }

        self.profile = {
            "id": "TEST-1",
            "anon_name": "Тестовый подрядчик",
            "city": "Алматы",
            "categories": ["Ведущий"],
            "event_formats": ["корпоратив"],
            "languages": ["русский"],
            "price_from_kzt": 200000,
            "max_hours": 5,
            "busy_dates": set(),
            "description": "Провожу корпоративы с живой музыкой.",
            "synthetic": True,
            "city_imputed": False,
            "price_imputed": False,
        }

        ai_explanations.select_facts.cache_clear()
        self.addCleanup(ai_explanations.select_facts.cache_clear)

        mocker = patch.object(
            ai_explanations,
            "ask_ai",
            side_effect=self.fake_ai,
        )
        self.ai = mocker.start()
        self.addCleanup(mocker.stop)

    @staticmethod
    def fake_ai(prompt):
        payload = json.loads(prompt.rsplit("\n", 1)[-1])
        return json.dumps({
            profile["id"]: 1 if profile["fragments"] else 0
            for profile in payload["profiles"]
        })

    def pick(self, profiles=None, **changes):
        if profiles is None:
            profiles = [self.profile]

        return recommend(
            profiles,
            {**self.request, **changes},
        )

    def test_exact_budget_and_duration(self):
        result = self.pick()

        self.assertEqual(result["status"], "matched")
        self.assertEqual(len(result["cards"]), 1)
        self.assertTrue(result["cards"][0]["synthetic"])
        self.assertIn("всего профилей: 1", result["message"])

    def test_busy_people_and_venues(self):
        for category in ("Ведущий", "Банкетный зал"):
            with self.subTest(category=category):
                profile = {
                    **self.profile,
                    "categories": [category],
                    "busy_dates": {date(2026, 10, 15)},
                }

                result = self.pick([profile], category=category)

                self.assertEqual(result["status"], "no_match")
                self.assertEqual(result["cards"], [])
                self.assertIn("заняты на дату", result["message"])

        self.ai.assert_not_called()

    def test_each_condition_excludes_candidate(self):
        cases = [
            ({"price_from_kzt": 200001}, "превышает бюджет"),
            ({"event_formats": ["свадьба"]}, "форматом"),
            ({"languages": ["казахский"]}, "язык"),
            ({"max_hours": 4}, "длительность"),
        ]

        for changes, reason in cases:
            with self.subTest(changes=changes):
                result = self.pick([
                    {**self.profile, **changes}
                ])

                self.assertEqual(result["status"], "no_match")
                self.assertEqual(result["cards"], [])
                self.assertIn(reason, result["message"])

    def test_missing_city_category(self):
        for changes in (
            {"category": "Фотограф"},
            {"city": "Астана"},
        ):
            with self.subTest(changes=changes):
                result = self.pick(**changes)

                self.assertEqual(
                    result["status"],
                    "category_absent",
                )
                self.assertEqual(result["cards"], [])
                self.assertTrue(result["message"])

        self.ai.assert_not_called()

    def test_limit_and_stable_order(self):
        profiles = [
            {**self.profile, "id": f"TEST-{number}"}
            for number in (4, 2, 1, 3)
        ]

        first = self.pick(profiles)
        repeated = self.pick(profiles)
        shuffled = self.pick(list(reversed(profiles)))

        expected = ["TEST-1", "TEST-2", "TEST-3"]

        for result in (first, repeated, shuffled):
            ids = [card["id"] for card in result["cards"]]
            self.assertEqual(ids, expected)

        # Повторные запросы используют сохранённый ответ AI.
        self.assertEqual(self.ai.call_count, 1)

    def test_date_changes_availability(self):
        self.profile["busy_dates"] = {date(2026, 10, 15)}

        self.assertEqual(self.pick()["status"], "no_match")

        result = self.pick(date="2026-10-16")

        self.assertEqual(result["status"], "matched")
        self.assertIn(
            "2026-10-16",
            result["cards"][0]["explanation"],
        )

    def test_null_hours_and_optional_fields(self):
        self.profile["max_hours"] = None

        result = self.pick(duration_hours=12)
        self.assertEqual(result["status"], "matched")

        self.request.pop("duration_hours")
        self.request.pop("language")

        self.assertEqual(self.pick()["status"], "matched")

    def test_invalid_input(self):
        for changes in (
            {"budget_kzt": -1},
            {"budget_kzt": True},
            {"budget_kzt": float("inf")},
            {"duration_hours": 0},
            {"date": "2027-01-01"},
            {"date": "не дата"},
            {"city": " "},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.pick(**changes)

    def test_ai_uses_original_fact(self):
        card = self.pick()["cards"][0]

        self.assertEqual(card["explanation_source"], "ai")
        self.assertIn(
            self.profile["description"],
            card["explanation"],
        )

    def test_ai_error_keeps_recommendation(self):
        self.ai.side_effect = ValueError("Ошибка ответа AI")

        with self.assertLogs(level="WARNING"):
            result = self.pick()

        self.assertEqual(result["status"], "matched")
        self.assertEqual(
            result["cards"][0]["explanation_source"],
            "rules",
        )

    def test_invalid_ai_fact_uses_fallback(self):
        self.ai.side_effect = None
        self.ai.return_value = '{"TEST-1": 999}'

        with self.assertLogs(level="WARNING"):
            result = self.pick()

        self.assertEqual(result["status"], "matched")
        self.assertEqual(
            result["cards"][0]["explanation_source"],
            "rules",
        )


if __name__ == "__main__":
    unittest.main()
    