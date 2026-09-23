"""Компоненты отображения результата рекомендации."""

import streamlit as st


def render_result(result):
    """Показывает сообщение и карточки в формате backend.recommend()."""
    status = result.get("status")
    message = result.get("message") or "Подбор завершён."

    if status == "matched":
        st.success(message)
        for card in result.get("cards", []):
            render_contractor_card(card)
    elif status == "category_absent":
        st.info("В выбранном городе такой категории нет. " + message)
    elif status == "no_match":
        st.warning("Категория в городе есть, но кандидаты не соответствуют условиям. " + message)
        diagnostics = result.get("diagnostics", {})
        reasons = diagnostics.get("reason_counts", {})
        if reasons:
            st.caption("Причины отклонения: " + "; ".join(
                f"{reason}: {count}" for reason, count in reasons.items()
            ))
    else:
        st.error(f"Backend вернул неизвестный статус: {status!r}")


def render_contractor_card(card):
    with st.container(border=True):
        st.subheader(card.get("anon_name") or "Подрядчик")
        st.caption(f"{card.get('category', 'Категория')} · {card.get('city', 'Город не указан')}")
        price = card.get("price_from_kzt")
        if price is not None:
            st.markdown(f"**Цена от:** {price:,.0f} ₸".replace(",", " "))
        explanation = card.get("explanation")
        if explanation:
            st.write(explanation)
        if card.get("synthetic"):
            st.warning("Синтетический профиль")
        elif card.get("city_imputed") or card.get("price_imputed"):
            st.caption("В профиле есть восстановленные данные: " + ", ".join(
                label for field, label in (
                    ("city_imputed", "город"),
                    ("price_imputed", "цена"),
                ) if card.get(field)
            ))


def render_error(error):
    st.error(f"Не удалось выполнить подбор: {error}")
