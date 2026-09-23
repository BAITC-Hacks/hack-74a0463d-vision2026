"""Streamlit интерфейс над существующим backend.recommender."""

from datetime import date

import streamlit as st

from backend.loader import load_contractors
from backend.recommender import CALENDAR_END, CALENDAR_START, recommend
from frontend.demo_queries import DEMO_QUERIES
from frontend.ui_components import render_error, render_result


@st.cache_data
def get_contractors():
    return load_contractors()


def main():
    st.set_page_config(page_title="Подбор подрядчиков", page_icon="🎉", layout="wide")
    st.title("Подбор подрядчиков для мероприятия")
    st.write("Укажите условия — покажем подходящие профили из каталога.")

    try:
        contractors = get_contractors()
    except Exception as error:
        render_error(error)
        st.stop()

    cities = sorted({contractor["city"] for contractor in contractors})
    categories = sorted({value for contractor in contractors for value in contractor["categories"]})
    formats = sorted({value for contractor in contractors for value in contractor["event_formats"]})
    languages = sorted({value for contractor in contractors for value in contractor["languages"]})

    demo_name = st.selectbox("Демо-запрос (необязательно)", ["—"] + list(DEMO_QUERIES))
    demo = DEMO_QUERIES.get(demo_name, {})
    with st.form("recommendation_request"):
        left, right = st.columns(2)
        city = left.selectbox("Город", cities, index=_index(cities, demo.get("city")))
        category = right.selectbox("Категория", categories, index=_index(categories, demo.get("category")))
        event_format = left.selectbox("Формат мероприятия", formats, index=_index(formats, demo.get("event_format")))
        event_date = right.date_input(
            "Дата мероприятия",
            value=_date_value(demo.get("date")),
            min_value=CALENDAR_START,
            max_value=CALENDAR_END,
        )
        budget = left.number_input(
            "Бюджет, ₸", min_value=1, value=int(demo.get("budget_kzt", 500_000)), step=50_000
        )
        duration = right.number_input(
            "Длительность, часов (необязательно)", min_value=0.0,
            value=float(demo.get("duration_hours") or 0), step=0.5,
        )
        language_options = ["Не важно"] + languages
        language_index = _index(languages, demo.get("language")) + 1 if demo.get("language") else 0
        language = st.selectbox("Язык (необязательно)", language_options, index=language_index)
        submitted = st.form_submit_button("Подобрать")

    if submitted:
        request = {
            "city": city,
            "date": event_date.isoformat(),
            "event_format": event_format,
            "category": category,
            "budget_kzt": float(budget),
            "duration_hours": float(duration) if duration > 0 else None,
            "language": language if language != "Не важно" else None,
        }
        try:
            render_result(recommend(contractors, request))
        except Exception as error:
            render_error(error)


def _index(options, value):
    try:
        return options.index(value)
    except (ValueError, AttributeError):
        return 0


def _date_value(value):
    return date.fromisoformat(value) if value else max(CALENDAR_START, date.today())


if __name__ == "__main__":
    main()
