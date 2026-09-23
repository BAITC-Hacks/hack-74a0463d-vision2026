from datetime import date

import streamlit as st

from backend.loader import load_contractors
from backend.recommender import CALENDAR_END, CALENDAR_START, recommend
from frontend.demo_queries import DEMO_QUERIES
from frontend.ui_components import inject_styles, render_error, render_hero, render_result


@st.cache_data
def get_contractors():
    return load_contractors()


def apply_demo(name):
    demo = DEMO_QUERIES[name]
    st.session_state["selected_demo"] = name
    st.session_state["city"] = demo["city"]
    st.session_state["category"] = demo["category"]
    st.session_state["event_format"] = demo["event_format"]
    st.session_state["event_date"] = date.fromisoformat(demo["date"])
    st.session_state["budget_kzt"] = int(demo["budget_kzt"])
    st.session_state["duration_hours"] = float(demo.get("duration_hours") or 0)
    st.session_state["language"] = demo.get("language") or "Не важно"


def option_index(options, value):
    try:
        return options.index(value)
    except (ValueError, AttributeError):
        return 0


def initial_date():
    today = date.today()
    return min(max(today, CALENDAR_START), CALENDAR_END)


def main():
    st.set_page_config(page_title="Праздник рядом", layout="wide")
    inject_styles()

    try:
        contractors = get_contractors()
    except Exception as error:
        render_error(error)
        st.stop()

    cities = sorted({contractor["city"] for contractor in contractors})
    categories = sorted({value for contractor in contractors for value in contractor["categories"]})
    formats = sorted({value for contractor in contractors for value in contractor["event_formats"]})
    languages = sorted({value for contractor in contractors for value in contractor["languages"]})

    render_hero(len(contractors), len(categories))

    st.markdown('<div class="section-title">Начните с готового запроса</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-note">Нажмите пример — форма заполнится автоматически.</p>',
        unsafe_allow_html=True,
    )
    demo_columns = st.columns(len(DEMO_QUERIES), gap="small")
    for column, (name, demo) in zip(demo_columns, DEMO_QUERIES.items()):
        with column:
            label = name
            st.button(
                label,
                key=f"demo_{name}",
                type="secondary",
                on_click=apply_demo,
                args=(name,),
                use_container_width=True,
            )

    with st.form("recommendation_request"):
        st.markdown('<div class="section-title">Расскажите о мероприятии</div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="section-note">Подберём подрядчиков с учётом даты, формата и бюджета.</p>',
            unsafe_allow_html=True,
        )

        first_row, second_row = st.columns(2, gap="large")
        with first_row:
            city = st.selectbox(
                "Город",
                cities,
                index=option_index(cities, "Алматы"),
                key="city",
            )
            event_format = st.selectbox(
                "Формат мероприятия",
                formats,
                index=option_index(formats, "свадьба"),
                key="event_format",
            )
            budget = st.number_input(
                "Бюджет подрядчика, ₸",
                min_value=1,
                value=500_000,
                step=50_000,
                key="budget_kzt",
                help="Укажите максимальную цену «от», которая вам подходит.",
            )

        with second_row:
            category = st.selectbox(
                "Кого ищем",
                categories,
                index=option_index(categories, "Ведущий"),
                key="category",
            )
            event_date = st.date_input(
                "Дата мероприятия",
                value=initial_date(),
                min_value=CALENDAR_START,
                max_value=CALENDAR_END,
                key="event_date",
            )
            duration = st.number_input(
                "Длительность, часов · необязательно",
                min_value=0.0,
                value=0.0,
                step=0.5,
                key="duration_hours",
                help="Оставьте 0, если длительность не важна.",
            )

        language_options = ["Не важно"] + languages
        language = st.selectbox(
            "Язык общения · необязательно",
            language_options,
            index=option_index(language_options, "Не важно"),
            key="language",
        )
        submitted = st.form_submit_button(
            "Подобрать подрядчиков",
            type="primary",
            use_container_width=True,
        )

    st.markdown(
        '<div class="trust-note"><span class="trust-dot"></span>'
        'До 3 рекомендаций · понятные причины · условия можно менять сколько угодно раз</div>',
        unsafe_allow_html=True,
    )

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
        with st.spinner("Подбираем свободных подрядчиков…"):
            try:
                st.session_state["recommendation_result"] = recommend(contractors, request)
                st.session_state.pop("recommendation_error", None)
            except Exception as error:
                st.session_state["recommendation_error"] = str(error)
                st.session_state.pop("recommendation_result", None)

    if st.session_state.get("recommendation_error"):
        render_error(st.session_state["recommendation_error"])
    elif st.session_state.get("recommendation_result"):
        render_result(st.session_state["recommendation_result"])


if __name__ == "__main__":
    main()
