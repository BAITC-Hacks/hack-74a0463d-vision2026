import html

import streamlit as st


def inject_styles():
    st.markdown(
        """
        <style>
        :root {
            --ink: #282345;
            --muted: #76728e;
            --violet: #6e55df;
            --coral: #ff806d;
            --mint: #57c7ae;
            --paper: #fffdfa;
        }
        .stApp {
            background:
                radial-gradient(ellipse at 8% 8%, rgba(255, 202, 168, .23), transparent 28%),
                radial-gradient(ellipse at 95% 16%, rgba(175, 156, 255, .2), transparent 30%),
                linear-gradient(145deg, #fbf9ff 0%, #fffaf6 54%, #f5fcfa 100%);
            color: var(--ink);
        }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stAppViewContainer"] > .main .block-container {
            max-width: 1180px;
            padding-top: 2.2rem;
            padding-bottom: 4rem;
        }
        h1, h2, h3, p, label { color: var(--ink); }
        .hero {
            position: relative;
            overflow: hidden;
            padding: 2.1rem 2.25rem;
            border-radius: 28px;
            color: white;
            background: linear-gradient(115deg, #5141ad 0%, #755ce3 52%, #dd7caa 100%);
            box-shadow: 0 18px 48px rgba(85, 65, 166, .2);
            margin-bottom: 1.65rem;
        }
        .hero:after {
            content: "";
            position: absolute;
            width: 260px;
            height: 260px;
            right: -58px;
            top: -100px;
            border: 1px solid rgba(255,255,255,.28);
            border-radius: 50%;
            box-shadow: 0 0 0 28px rgba(255,255,255,.06), 0 0 0 58px rgba(255,255,255,.045);
        }
        .hero-kicker {
            color: #e8e2ff;
            font-size: .75rem;
            font-weight: 800;
            letter-spacing: .16em;
            text-transform: uppercase;
            margin-bottom: .8rem;
        }
        .hero h1 {
            color: white !important;
            font-size: clamp(2rem, 4vw, 3.3rem);
            line-height: 1.08;
            letter-spacing: -.04em;
            margin: 0 0 .65rem;
        }
        .hero p { color: #f4f0ff !important; font-size: 1.05rem; margin: 0; max-width: 700px; }
        .hero-foot {
            display: flex;
            flex-wrap: wrap;
            gap: .55rem;
            margin-top: 1.35rem;
        }
        .hero-pill {
            border: 1px solid rgba(255,255,255,.27);
            background: rgba(255,255,255,.12);
            border-radius: 999px;
            padding: .38rem .75rem;
            color: white;
            font-size: .82rem;
        }
        .section-title { margin: .3rem 0 .25rem; font-weight: 750; letter-spacing: -.02em; }
        .section-note { color: var(--muted); margin: 0 0 .8rem; font-size: .92rem; }
        div[data-testid="stForm"] {
            background: rgba(255,255,255,.9);
            border: 1px solid #e9e4f3;
            border-radius: 24px;
            padding: 1.15rem 1.4rem 1.35rem;
            box-shadow: 0 12px 34px rgba(59, 49, 107, .07);
        }
        div[data-testid="stForm"] label { font-weight: 650; }
        div[data-testid="stSelectbox"] > div > div,
        div[data-testid="stNumberInput"] > div > div,
        div[data-testid="stDateInput"] > div > div {
            border-radius: 13px;
            border-color: #e5e0ef;
            background: #fff;
        }
        .stButton > button, .stFormSubmitButton > button {
            border-radius: 13px;
            font-weight: 700;
            min-height: 2.8rem;
            transition: transform .15s ease, box-shadow .15s ease;
        }
        .stButton > button {
            color: #5141ad;
            border: 1px solid #e2dcf6;
            background: rgba(255,255,255,.84);
        }
        .stButton > button:hover {
            color: #45349f;
            border-color: #a999ec;
            background: #f6f2ff;
            transform: translateY(-1px);
            box-shadow: 0 7px 18px rgba(90, 71, 174, .12);
        }
         div[data-testid="stFormSubmitButton"] button {
            color: #ffffff !important;
            background: #6e55df !important;
            border: 0 !important;
            border-radius: 13px;
            font-weight: 700;
            box-shadow: 0 9px 20px rgba(103, 78, 203, 0.22);
        }
        div[data-testid="stFormSubmitButton"] button:hover {
            color: #ffffff !important;
            background: #5943c4 !important;
            border: 0 !important;
            transform: translateY(-1px);
            box-shadow: 0 12px 24px rgba(103, 78, 203, 0.3);
        }
        .demo-wrap { margin: .4rem 0 1.15rem; }
        .result-heading {
            display: flex;
            align-items: center;
            gap: .65rem;
            margin: 1.65rem 0 .9rem;
        }
        .result-heading h2 { margin: 0; font-size: 1.55rem; }
        .result-count {
            border-radius: 999px;
            padding: .24rem .65rem;
            background: #eee9ff;
            color: #5a46c3;
            font-size: .82rem;
            font-weight: 800;
        }
        .status-box {
            padding: 1rem 1.2rem;
            border-radius: 17px;
            margin: .3rem 0 1.15rem;
            border: 1px solid transparent;
        }
        .status-title { font-size: 1.05rem; font-weight: 800; margin-bottom: .2rem; }
        .status-copy { margin: 0; line-height: 1.5; }
        .status-matched { background: #eaf8f2; border-color: #c8eddd; color: #176c55; }
        .status-empty { background: #fff3e6; border-color: #ffe1c3; color: #94561d; }
        .status-absent { background: #f0edff; border-color: #ddd6ff; color: #5141ad; }
        .contractor-card {
            height: 100%;
            padding: 1.15rem;
            border: 1px solid #e9e4f3;
            border-radius: 21px;
            background: rgba(255,255,255,.95);
            box-shadow: 0 12px 32px rgba(59,49,107,.08);
        }
        .card-top { display: flex; justify-content: space-between; gap: .5rem; align-items: center; }
        .category-chip, .synthetic-chip, .data-chip {
            display: inline-block;
            border-radius: 999px;
            padding: .28rem .62rem;
            font-size: .74rem;
            font-weight: 750;
        }
        .category-chip { background: #f0edff; color: #5b48bd; }
        .profile-id { color: #9691a7; font-size: .72rem; }
        .contractor-card h3 { font-size: 1.22rem; margin: .9rem 0 .25rem; line-height: 1.25; }
        .card-city { color: var(--muted); font-size: .88rem; }
        .price-block {
            margin: .9rem 0;
            padding: .75rem .85rem;
            border-radius: 14px;
            background: linear-gradient(105deg, #fff4eb, #fff0f5);
        }
        .price-label { color: #9a6a67; font-size: .76rem; font-weight: 700; }
        .price-value { color: #4f3d9f; font-size: 1.45rem; font-weight: 850; letter-spacing: -.03em; }
        .reason-box { border-top: 1px solid #eeeaf4; padding-top: .8rem; }
        .reason-label {
            color: #4c4282;
            font-size: .75rem;
            text-transform: uppercase;
            letter-spacing: .08em;
            font-weight: 850;
            margin-bottom: .35rem;
        }
        .reason-copy { color: #514e63; font-size: .88rem; line-height: 1.55; margin: 0; }
        .card-tags { display: flex; gap: .4rem; flex-wrap: wrap; margin-top: .85rem; }
        .synthetic-chip { color: #7b4e11; background: #fff0ca; }
        .data-chip { color: #456978; background: #e7f5f7; }
        .diagnostics-note { color: var(--muted); font-size: .84rem; }
        @media (max-width: 760px) {
            [data-testid="stAppViewContainer"] > .main .block-container { padding: 1rem .75rem 2.5rem; }
            .hero { padding: 1.5rem; border-radius: 21px; }
            div[data-testid="stForm"] { padding: .9rem; border-radius: 18px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(profile_count=None, category_count=None):
    details = []
    if profile_count is not None:
        details.append(f"{profile_count} профилей в каталоге")
    if category_count is not None:
        details.append(f"{category_count} категорий")
    pills = "".join(
        f'<span class="hero-pill">{html.escape(item)}</span>' for item in details
    )
    st.markdown(
        f"""
        <section class="hero">
            <div class="hero-kicker">Ваше событие · наши рекомендации</div>
            <h1>Найдите команду<br>для своего праздника</h1>
            <p>Подберём подрядчиков по дате, формату и бюджету — с понятным объяснением каждого выбора.</p>
            <div class="hero-foot">{pills}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_contractor_card(card):
    name = html.escape(str(card.get("anon_name") or "Подрядчик"))
    category = html.escape(str(card.get("category") or "Категория не указана"))
    city = html.escape(str(card.get("city") or "Город не указан"))
    contractor_id = html.escape(str(card.get("id") or ""))
    explanation = html.escape(str(card.get("explanation") or "Объяснение не предоставлено."))
    price = card.get("price_from_kzt")
    price_html = ""
    if price is not None:
        formatted_price = f"{float(price):,.0f}".replace(",", " ")
        price_html = (
            '<div class="price-block"><div class="price-label">Цена от</div>'
            f'<div class="price-value">{formatted_price} ₸</div></div>'
        )

    tags = []
    if card.get("synthetic"):
        tags.append('<span class="synthetic-chip">Синтетический профиль</span>')
    restored = []
    if card.get("city_imputed"):
        restored.append("город")
    if card.get("price_imputed"):
        restored.append("цена")
    if restored:
        tags.append(
            '<span class="data-chip">Восстановлены: '
            + html.escape(", ".join(restored))
            + "</span>"
        )
    tags_html = f'<div class="card-tags">{"".join(tags)}</div>' if tags else ""
    id_html = f'<span class="profile-id">{contractor_id}</span>' if contractor_id else ""

    st.markdown(
        f"""
        <article class="contractor-card">
            <div class="card-top"><span class="category-chip">{category}</span>{id_html}</div>
            <h3>{name}</h3>
            <div class="card-city">⌖ &nbsp;{city}</div>
            {price_html}
            <div class="reason-box">
                <div class="reason-label">Почему подходит</div>
                <p class="reason-copy">{explanation}</p>
            </div>
            {tags_html}
        </article>
        """,
        unsafe_allow_html=True,
    )


def render_diagnostics(diagnostics):
    with st.expander("Как прошёл подбор"):
        st.write(f"Подходящих профилей: {diagnostics.get('eligible_count', 0)}")
        st.write(f"Профилей исключено: {diagnostics.get('rejected_count', 0)}")
        for reason, count in diagnostics.get("reason_counts", {}).items():
            st.markdown(f'<div class="diagnostics-note">{html.escape(str(reason))}: {count}</div>', unsafe_allow_html=True)


def render_result(result):
    status = result.get("status")
    message = html.escape(str(result.get("message") or "Подбор завершён."))
    cards = result.get("cards", [])[:3]

    if status == "matched":
        st.markdown(
            f'<div class="status-box status-matched"><div class="status-title">Подходящие варианты найдены</div><p class="status-copy">{message}</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="result-heading"><h2>Ваши рекомендации</h2><span class="result-count">{len(cards)}</span></div>',
            unsafe_allow_html=True,
        )
        if cards:
            columns = st.columns(len(cards), gap="medium")
            for column, card in zip(columns, cards):
                with column:
                    render_contractor_card(card)
        else:
            st.info("Подходящих профилей пока нет.")
    elif status == "category_absent":
        st.markdown(
            f'<div class="status-box status-absent"><div class="status-title">В городе нет такой категории</div><p class="status-copy">{message}</p></div>',
            unsafe_allow_html=True,
        )
    elif status == "no_match":
        st.markdown(
            f'<div class="status-box status-empty"><div class="status-title">Пока не нашли подходящих</div><p class="status-copy">{message}</p></div>',
            unsafe_allow_html=True,
        )
        reasons = result.get("diagnostics", {}).get("reason_counts", {})
        if reasons:
            st.caption("Причины, которые чаще всего мешали подбору:")
            reason_columns = st.columns(min(3, len(reasons)))
            for index, (reason, count) in enumerate(reasons.items()):
                with reason_columns[index % len(reason_columns)]:
                    st.metric(str(reason), count)
    else:
        st.error(f"Backend вернул неизвестный статус: {status!r}")

    diagnostics = result.get("diagnostics", {})
    if diagnostics and status == "matched":
        render_diagnostics(diagnostics)


def render_error(error):
    detail = html.escape(str(error))
    st.markdown(
        f'<div class="status-box status-empty"><div class="status-title">Не удалось выполнить подбор</div><p class="status-copy">{detail}</p></div>',
        unsafe_allow_html=True,
    )
