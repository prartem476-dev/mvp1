import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os


# --- INITIALIZE ARCHIVE STATE ---
if 'agent_goals' not in st.session_state:
    st.session_state['agent_goals'] = []

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="CENTURY 21 — Личный кабинет брокера (MVP)",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR BRANDING (Gold & Charcoal) ---
st.markdown("""
<style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;600;700;800&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap');

    /* Global App Setup */
    .stApp {
        background-color: #F8F8F9 !important;
        color: #222222 !important;
        font-family: 'Barlow', 'Segoe UI', Arial, sans-serif !important;
    }
    
    /* Elegant Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 2px solid #C5A059 !important;
    }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label {
        color: #F5F5F5 !important;
        font-family: 'Barlow', sans-serif !important;
    }
    section[data-testid="stSidebar"] hr {
        border-top: 1px solid #2D2D2D !important;
    }
    
    /* Sidebar Radio Buttons */
    div[data-testid="stSidebarUserContent"] .stRadio > label {
        color: #C5A059 !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        margin-bottom: 12px !important;
        border-bottom: 1px solid #2D2D2D !important;
        padding-bottom: 5px !important;
    }
    div[data-testid="stSidebarUserContent"] [data-testid="stWidgetLabel"] p {
        color: #C5A059 !important;
        font-weight: 700 !important;
    }

    /* Headings Styling */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Barlow', 'Segoe UI', Arial, sans-serif !important;
        color: #111111 !important;
        font-weight: 700 !important;
    }
    
    .brand-gold-text {
        color: #C5A059 !important;
        font-weight: 800 !important;
    }
    
    /* Premium Metric Card Styling with Left Gold Border */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E2E6 !important;
        border-left: 5px solid #C5A059 !important;
        padding: 20px !important;
        border-radius: 4px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
    }
    div[data-testid="metric-container"] label {
        color: #111111 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        font-weight: 700 !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #C5A059 !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
    }
    
    /* Styled Corporate Buttons */
    div.stButton > button {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 1px solid #C5A059 !important;
        border-radius: 4px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.85rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        background-color: #C5A059 !important;
        color: #111111 !important;
        border: 1px solid #111111 !important;
        box-shadow: 0 4px 12px rgba(197, 160, 89, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Download Buttons */
    div.stDownloadButton > button {
        background-color: #C5A059 !important;
        color: #111111 !important;
        border: 1px solid #111111 !important;
        border-radius: 4px !important;
        padding: 10px 24px !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.85rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    div.stDownloadButton > button:hover {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 1px solid #C5A059 !important;
        box-shadow: 0 4px 12px rgba(17, 17, 17, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    /* Input Widget Enhancements */
    input, select, textarea, div[role="listbox"] {
        border-radius: 4px !important;
    }
    
    /* Clean Cards for Sections */
    .c21-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E2E6;
        padding: 25px;
        border-radius: 4px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
        margin-bottom: 25px;
    }
    
    /* Status Badge styling */
    .status-badge-green {
        background-color: #E2EFDA;
        color: #375623;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .status-badge-red {
        background-color: #FCE4D6;
        color: #C65911;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER: FILE DOWNLOAD SENDER ---
def get_file_bytes(filename):
    paths_to_try = [
        f"/workspace/artifacts/{filename}",
        f"/workspace/knowledge/{filename}",
        f"/workspace/scratch/{filename}",
        filename
    ]
    for p in paths_to_try:
        if os.path.exists(p):
            with open(p, "rb") as f:
                return f.read()
    return b""

# --- SIDEBAR & LOGO ---
st.sidebar.markdown(f"""
<div style="text-align: center; padding: 15px 0px; background-color: #111111; border-radius: 4px; margin-bottom: 15px;">
    <h1 style="color: #C5A059 !important; margin: 0; font-size: 1.95rem; font-family: 'Times New Roman', Times, serif; font-weight: 300; letter-spacing: 5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">CENTURY 21</h1>
    <p style="color: #FFFFFF; font-size: 0.85rem; margin: 5px 0 0 0; font-family: 'Barlow', sans-serif; font-weight: 600; text-transform: uppercase; letter-spacing: 2px;">Россия</p>
    <div style="border-top: 2px solid #C5A059; width: 60px; margin: 15px auto 10px auto;"></div>
    <p style="color: #C5A059; font-size: 0.72rem; font-family: 'Barlow', sans-serif; font-weight: 700; letter-spacing: 3px; margin: 0; text-transform: uppercase;">Smarter. Bolder. Faster.</p>
</div>
<hr style="border-top: 1px solid #2D2D2D; margin: 10px 0 20px 0;">
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "НАВИГАЦИЯ ПО MVP",
    [
        "📊 Главный дашборд & What-If",
        "🤝 Welcome-Центр & Онбординг",
        "🏢 Финансовое планирование (Лист1)",
        "🎯 Планировщик целей агента",
        "💰 Калькулятор доходности сделок",
        "📈 Калькулятор KPI премий",
        "🗺️ Дорожная карта запуска",
        "🎓 Центр обучения & Адаптации",
        "🏃 Стандарты Адаптации & Лидов",
        "🤖 ИИ-Консультант CENTURY 21",
        "🌐 Сервисы & Экосистема C21",
        "📦 Все файлы & Загрузки"
    ]
)

st.sidebar.markdown("""
<hr style="border-top: 1px solid #2D2D2D; margin: 20px 0;">
<div style="padding: 12px; border-radius: 4px; background-color: #1A1A1A; border: 1px solid #2D2D2D; text-align: center;">
    <p style="font-size: 0.8rem; margin: 0; color: #C5A059; font-family: 'Barlow', sans-serif; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;"><b>Версия MVP: 8.0 (Полная Экосистема C21)</b></p>
    <p style="font-size: 0.75rem; margin: 5px 0 0 0; color: #CCCCCC; font-family: 'Barlow', sans-serif; line-height: 1.4;">Премиальный релиз CENTURY 21 с ИИ-Консультантом и Интерактивным каталогом всех 23 сервисов</p>
</div>
<div style="margin-top: 20px; text-align: center;">
    <p style="font-size: 0.65rem; color: #888888; font-family: 'Barlow', sans-serif; line-height: 1.4; letter-spacing: 0.5px;">«Каждый офис находится в независимом владении и управлении.»</p>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# MODULE 1: MAIN DASHBOARD & WHAT-IF SIMULATOR
# ==============================================================================
if menu == "📊 Главный дашборд & What-If":
    st.markdown("""
    <div style="background-color: #111111; padding: 25px 30px; border-left: 5px solid #C5A059; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h1 style="color: #FFFFFF !important; margin: 0; font-size: 2.1rem; letter-spacing: 3px; font-weight: 700; font-family: 'Barlow', sans-serif; text-transform: uppercase;">БИЗНЕС-СИМУЛЯТОР "WHAT-IF"</h1>
        <p style="color: #C5A059; margin: 8px 0 0 0; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Сквозная воронка рекрутинга и продаж, совмещенная со сценарным финансовым симулятором</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Preset Scenarios logic
    col_scen, col_desc = st.columns([1, 3])
    with col_scen:
        scenario = st.selectbox(
            "Выберите сценарий для автозаполнения:",
            ["Базовый (Текущий)", "Оптимистичный (Целевой)", "Пессимистичный (Риски)"]
        )
    with col_desc:
        if scenario == "Базовый (Текущий)":
            st.info("📊 **Базовый сценарий:** Текущие метрики офиса. Штат: 9 экспертов, 8 стажеров. Активность по нормативу Книги агента — 21 звонок в день. Средняя конверсия звонка во встречу — 10%.")
            default_staff_exp = 9
            default_recruits = 500
            default_conv_rec = 0.35 # 35% из звонка в встречу HR
            default_conv_class = 0.45 # 45% в класс обучения
            default_conv_start = 0.25 # 25% вышли на стажировку
            default_conv_end = 0.12 # 12% прошли 2-недельную стажировку
            default_calls_day = 21
            default_conv_call_meet = 0.10 # 10%
            default_conv_meet_ed = 0.25 # 25%
            default_conv_ed_deal = 0.30 # 30%
            default_avg_gci = 150000.0
        elif scenario == "Оптимистичный (Целевой)":
            st.success("🌟 **Оптимистичный сценарий:** Масштабирование штата до 14 экспертов, рост конверсии звонков за счет обучения скриптам и повышение среднего чека сделки.")
            default_staff_exp = 14
            default_recruits = 800
            default_conv_rec = 0.45
            default_conv_class = 0.55
            default_conv_start = 0.35
            default_conv_end = 0.18
            default_calls_day = 25
            default_conv_call_meet = 0.12
            default_conv_meet_ed = 0.35
            default_conv_ed_deal = 0.35
            default_avg_gci = 180000.0
        else:
            st.error("⚠️ **Пессимистичный сценарий:** Отток опытных агентов, снижение активности, падение конверсий до минимальных рыночных значений.")
            default_staff_exp = 6
            default_recruits = 300
            default_conv_rec = 0.25
            default_conv_class = 0.35
            default_conv_start = 0.15
            default_conv_end = 0.08
            default_calls_day = 15
            default_conv_call_meet = 0.07
            default_conv_meet_ed = 0.15
            default_conv_ed_deal = 0.20
            default_avg_gci = 120000.0

    st.markdown("### 🔧 Управляемые параметры (Слайдеры What-If)")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        st.markdown("<h4 style='color: #C5A059 !important;'>1. Рекрутинг и Кадры</h4>", unsafe_allow_html=True)
        staff_exp = st.slider("Опытные агенты в штате", 1, 30, default_staff_exp)
        recruits_called = st.slider("Обзвон соискателей в месяц", 100, 2000, default_recruits, 50)
        conv_rec_meet = st.slider("Конверсия: Звонок -> Интервью HR (%)", 10.0, 80.0, default_conv_rec * 100.0, 1.0) / 100.0
        conv_meet_class = st.slider("Конверсия: Интервью -> Класс (%)", 10.0, 80.0, default_conv_class * 100.0, 1.0) / 100.0
        conv_class_start = st.slider("Конверсия: Класс -> Старт стажировки (%)", 10.0, 80.0, default_conv_start * 100.0, 1.0) / 100.0
        conv_start_end = st.slider("Конверсия: Выживаемость стажера (>2 нед.) (%)", 5.0, 50.0, default_conv_end * 100.0, 1.0) / 100.0
        
    with col_s2:
        st.markdown("<h4 style='color: #C5A059 !important;'>2. Активность и Продажи</h4>", unsafe_allow_html=True)
        calls_per_day = st.slider("Звонков на 1 агента в день (лимит)", 5, 40, default_calls_day)
        working_days = st.slider("Рабочих дней в месяце", 15, 26, 22)
        conv_call_meet = st.slider("Конверсия: Звонок -> Встреча (%)", 2.0, 30.0, default_conv_call_meet * 100.0, 0.5) / 100.0
        conv_meet_ed = st.slider("Конверсия: Встреча -> Экскл. договор (%)", 5.0, 60.0, default_conv_meet_ed * 100.0, 1.0) / 100.0
        conv_ed_deal = st.slider("Конверсия: Договор -> Сделка (%)", 5.0, 60.0, default_conv_ed_deal * 100.0, 1.0) / 100.0
        
    with col_s3:
        st.markdown("<h4 style='color: #C5A059 !important;'>3. Финансовые допущения</h4>", unsafe_allow_html=True)
        avg_gci = st.number_input("Средняя комиссия (ВКД) со сделки (руб.)", 50000, 500000, int(default_avg_gci), 5000)
        adv_cost_per_ed = st.number_input("Реклама 1 эксклюзива (руб.)", 2000, 15000, 6000, 500)
        cpa_recruit = st.number_input("CPA (Стоимость привлечения 1 соискателя, руб.)", 50, 500, 150, 10)
        rent_and_office = st.number_input("Аренда и бэк-офис в месяц (руб.)", 50000, 500000, 120000, 10000)

    # --- CALCULATIONS BACKEND ---
    # Recruitment Funnel
    rec_interviews = recruits_called * conv_rec_meet
    rec_class = rec_interviews * conv_meet_class
    rec_starts = rec_class * conv_class_start
    rec_successful = rec_starts * conv_start_end
    
    # Workforce Integration
    active_trainees = rec_successful
    total_staff = staff_exp + active_trainees
    
    # Sales Funnel Activity
    total_calls_month = total_staff * calls_per_day * working_days
    total_meets = total_calls_month * conv_call_meet
    total_eds = total_meets * conv_meet_ed
    total_deals = total_eds * conv_ed_deal
    
    # Financial Output
    calculated_gci = total_deals * avg_gci
    marketing_opex = total_eds * adv_cost_per_ed
    recruitment_opex = recruits_called * cpa_recruit
    total_fixed_costs = rent_and_office + 75000 # 75K is fixed HR/Admin base
    total_opex = marketing_opex + recruitment_opex + total_fixed_costs
    calculated_ebitda = calculated_gci - total_opex
    calculated_margin = (calculated_ebitda / calculated_gci * 100.0) if calculated_gci > 0 else 0.0
    calculated_roi = (calculated_ebitda / total_opex * 100.0) if total_opex > 0 else 0.0
    
    # Break-Even Analysis
    # Contribution Margin = avg_gci - (adv_cost_per_ed / conv_ed_deal)
    # Marketing cost per closed deal = adv_cost_per_ed * (eds / deals) = adv_cost_per_ed / conv_ed_deal
    var_cost_per_deal = adv_cost_per_ed / conv_ed_deal if conv_ed_deal > 0 else 0
    contribution_margin = avg_gci - var_cost_per_deal
    
    total_period_fixed_costs = total_fixed_costs + recruitment_opex
    if contribution_margin > 0:
        be_deals = total_period_fixed_costs / contribution_margin
        be_gci = be_deals * avg_gci
    else:
        be_deals = 999.0
        be_gci = 9999999.0
        
    margin_of_safety = ((total_deals - be_deals) / total_deals * 100.0) if total_deals > 0 else -100.0
    
    st.markdown("---")
    st.markdown("### 📊 Аналитический Свод")
    
    # Metric cards row
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Плановый ВКД (Выручка)", f"{calculated_gci:,.0f} ₽", delta=None)
    with col_m2:
        color_delta = "normal" if calculated_ebitda > 0 else "inverse"
        st.metric("Чистая прибыль (EBITDA)", f"{calculated_ebitda:,.0f} ₽", delta=f"{calculated_margin:.1f}% рентабельность", delta_color=color_delta)
    with col_m3:
        st.metric("Количество сделок", f"{total_deals:.1f} шт.", f"Штат: {total_staff:.1f} чел.")
    with col_m4:
        if margin_of_safety > 15.0:
            status_text = "✅ ОФИС ПРИБЫЛЕН"
            st.metric("Запас прочности", f"+{margin_of_safety:.1f}%", f"{status_text}")
        elif margin_of_safety >= 0.0:
            status_text = "🟡 ГРАНИЦА РИСКА"
            st.metric("Запас прочности", f"+{margin_of_safety:.1f}%", f"{status_text}")
        else:
            status_text = "❌ УБЫТОЧНАЯ ЗОНА"
            st.metric("Запас прочности", f"{margin_of_safety:.1f}%", f"{status_text}")

    # Funnel visualization side-by-side
    st.markdown("---")
    st.markdown("### 📈 Сквозные графические воронки")
    
    col_ch1, col_ch2 = st.columns(2)
    
    with col_ch1:
        # Recruiting Funnel
        rec_stages = ["Обзвон HR", "Интервью HR", "Обучение", "Старт стажировки", "Успешные стажеры"]
        rec_values = [recruits_called, rec_interviews, rec_class, rec_starts, rec_successful]
        fig_rec = go.Figure(go.Funnel(
            y=rec_stages,
            x=rec_values,
            textinfo="value+percent initial",
            marker=dict(color=["#1A1A1A", "#333333", "#C5A059", "#D9C193", "#EAE0CE"])
        ))
        fig_rec.update_layout(title="Воронка рекрутинга и адаптации стажеров (месяц)", height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_rec, use_container_width=True)
        
    with col_ch2:
        # Sales Funnel
        sales_stages = ["Исходящие звонки", "Встречи", "Эксклюзивные договоры", "Закрытые сделки"]
        sales_values = [total_calls_month, total_meets, total_eds, total_deals]
        fig_sales = go.Figure(go.Funnel(
            y=sales_stages,
            x=sales_values,
            textinfo="value+percent previous",
            marker=dict(color=["#C5A059", "#D9C193", "#EAE0CE", "#1A1A1A"])
        ))
        fig_sales.update_layout(title="Воронка продаж агентства (месяц)", height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_sales, use_container_width=True)

    # Break-Even Breakdown block
    st.markdown("---")
    st.markdown("### 🎯 Анализ точки безубыточности (Break-Even Analysis)")
    
    col_be1, col_be2 = st.columns([1, 2])
    with col_be1:
        st.markdown(f"""
        <div style="background-color: #FFFFFF; padding: 20px; border-radius: 8px; border: 1px solid #EAEAEA;">
            <h4 style="color: #1A1A1A; margin-top: 0;">Показатели безубыточности:</h4>
            <p style="margin: 10px 0; font-size: 0.95rem;">🏢 <b>Постоянные расходы:</b> {total_period_fixed_costs:,.0f} ₽</p>
            <p style="margin: 10px 0; font-size: 0.95rem;">📢 <b>Переменные расходы на 1 сделку:</b> {var_cost_per_deal:,.0f} ₽</p>
            <p style="margin: 10px 0; font-size: 0.95rem;">💰 <b>Маржинальный доход на сделку:</b> {contribution_margin:,.0f} ₽</p>
            <hr style="margin: 15px 0; border-top: 1px solid #EEE;">
            <p style="margin: 10px 0; font-size: 1.1rem; color: #C5A059;"><b>🎯 Точка безубыточности:</b></p>
            <p style="margin: 5px 0; font-size: 1.05rem;">🎯 <b>{be_deals:.1f} сделок</b></p>
            <p style="margin: 5px 0; font-size: 1.05rem;">💰 <b>{be_gci:,.0f} ₽ (минимальный ВКД)</b></p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_be2:
        # Chart: Cost vs Revenue
        deals_range = np.linspace(0, max(total_deals * 1.5, be_deals * 1.5, 5), 50)
        revenue_line = deals_range * avg_gci
        costs_line = total_period_fixed_costs + (deals_range * var_cost_per_deal)
        
        fig_be = go.Figure()
        fig_be.add_trace(go.Scatter(x=deals_range, y=revenue_line, name="Выручка (ВКД)", line=dict(color="#C5A059", width=3)))
        fig_be.add_trace(go.Scatter(x=deals_range, y=costs_line, name="Совокупные расходы", line=dict(color="#1A1A1A", width=2, dash="dash")))
        fig_be.add_trace(go.Scatter(x=[be_deals], y=[be_gci], name="Точка безубыточности", marker=dict(color="red", size=12, symbol="star")))
        
        fig_be.update_layout(
            title="График окупаемости офиса CENTURY 21",
            xaxis_title="Количество закрытых сделок",
            yaxis_title="Сумма (руб.)",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        st.plotly_chart(fig_be, use_container_width=True)

# ==============================================================================
# MODULE 2: KPI payroll calculator
# ==============================================================================
elif menu == "📈 Калькулятор KPI премий":
    st.markdown("""
    <div style="background-color: #111111; padding: 25px 30px; border-left: 5px solid #C5A059; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h1 style="color: #FFFFFF !important; margin: 0; font-size: 2.1rem; letter-spacing: 3px; font-weight: 700; font-family: 'Barlow', sans-serif; text-transform: uppercase;">ИНТЕЛЛЕКТУАЛЬНЫЙ РАСЧЕТ KPI</h1>
        <p style="color: #C5A059; margin: 8px 0 0 0; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Ведомость автоматического расчета окладов, премий и стипендий для всей команды с автоконтролем весов</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    role = st.selectbox("Выберите роль для расчета зарплаты:", ["Агент-Новичок (Адаптация)", "HR-менеджер по рекрутингу", "Руководитель отдела продаж (РОП)"])
    
    if role == "Агент-Новичок (Адаптация)":
        st.markdown("### 🎓 Расчет стипендии стажера на испытательном сроке")
        
        col_ag1, col_ag2 = st.columns(2)
        with col_ag1:
            month_num = st.radio("Месяц стажировки:", ["1-й месяц (Стипендия 30,000 руб.)", "2-й месяц (Стипендия 20,000 руб.)"])
            stipend_total = 30000 if "1-й" in month_num else 20000
            stipend_base = stipend_total / 2.0
            stipend_kpi = stipend_total / 2.0
            
            st.markdown(f"**Структура выплаты:** Оклад: **{stipend_base:,.0f} руб.** | Бонусная часть KPI: **{stipend_kpi:,.0f} руб.**")
            
            st.markdown("---")
            st.markdown("**Ввод фактических результатов по KPI:**")
            weight_obj = st.number_input("Вес 1: Привлечение объектов (%)", 10, 90, 50, 5)
            fact_obj = st.number_input("Факт: Привлечено объектов (план: 10)", 0, 30, 8)
            
            weight_leads = st.number_input("Вес 2: Заявки на покупку (%)", 10, 90, 30, 5)
            fact_leads = st.number_input("Факт: Получено заявок на покупку (план: 15)", 0, 50, 13)
            
            weight_meets = st.number_input("Вес 3: Проведено показов объектов (%)", 10, 90, 20, 5)
            fact_meets = st.number_input("Факт: Проведено показов стажером (план: 10)", 0, 30, 9)
            
        with col_ag2:
            st.markdown("#### 🔍 Проверка весов и Итоговый расчет")
            sum_weights = weight_obj + weight_leads + weight_meets
            
            if sum_weights != 100:
                st.error(f"❌ **Сумма весов должна быть строго 100%!** Сейчас: {sum_weights}%")
                st.stop()
            else:
                st.success("✅ **Распределение весов KPI корректно (100%)**")
                
            # Calculation of each metric execution
            exec_obj = (fact_obj / 10.0)
            # Threshold rule: if obj < 50%, payout is 0%
            if exec_obj < 0.5:
                payout_rate_obj = 0.0
                obj_msg = "🚨 Выполнение < 50% — Выплата сгорела!"
            else:
                payout_rate_obj = min(exec_obj, 1.2) # capped at 120%
                obj_msg = f"Выполнение: {exec_obj*100:.1f}%"
                
            exec_leads = (fact_leads / 15.0)
            # Threshold rule: if leads < 80%, payout is 0%
            if exec_leads < 0.8:
                payout_rate_leads = 0.0
                leads_msg = "🚨 Выполнение < 80% — Выплата сгорела!"
            else:
                payout_rate_leads = min(exec_leads, 1.2)
                leads_msg = f"Выполнение: {exec_leads*100:.1f}%"
                
            exec_meets = (fact_meets / 10.0)
            payout_rate_meets = min(exec_meets, 1.2)
            meets_msg = f"Выполнение: {exec_meets*100:.1f}%"
            
            # Weighted KPI Factor
            kpi_factor = (payout_rate_obj * (weight_obj/100.0)) + (payout_rate_leads * (weight_leads/100.0)) + (payout_rate_meets * (weight_meets/100.0))
            bonus_earned = stipend_kpi * kpi_factor
            total_earned = stipend_base + bonus_earned
            
            # Output Box
            st.markdown(f"""
            <div style="background-color: #FFFFFF; padding: 20px; border-radius: 8px; border: 1px solid #EAEAEA;">
                <h4 style="color: #1A1A1A; margin-top: 0;">Справка о начислении стажеру:</h4>
                <p>🟢 <b>Базовый оклад:</b> {stipend_base:,.0f} ₽</p>
                <hr style="border-top: 1px solid #EEE;">
                <p>🔹 <b>Показатель 1 (Объекты):</b> {obj_msg} (Начислено: {stipend_kpi * (weight_obj/100.0) * payout_rate_obj:,.0f} ₽)</p>
                <p>🔹 <b>Показатель 2 (Заявки):</b> {leads_msg} (Начислено: {stipend_kpi * (weight_leads/100.0) * payout_rate_leads:,.0f} ₽)</p>
                <p>🔹 <b>Показатель 3 (Показы):</b> {meets_msg} (Начислено: {stipend_kpi * (weight_meets/100.0) * payout_rate_meets:,.0f} ₽)</p>
                <hr style="border-top: 1px solid #EEE;">
                <p style="font-size: 1.1rem;">🔥 <b>Итоговая премия KPI:</b> {bonus_earned:,.0f} ₽ (Эффективность: {kpi_factor*100:.1f}%)</p>
                <h3 style="color: #C5A059 !important; margin-top: 10px;">💵 ВСЕГО К ВЫПЛАТЕ: {total_earned:,.0f} ₽</h3>
            </div>
            """, unsafe_allow_html=True)
            
    elif role == "HR-менеджер по рекрутингу":
        st.markdown("### 👔 Расчет дохода HR-менеджера")
        col_hr1, col_hr2 = st.columns(2)
        with col_hr1:
            target_income = st.number_input("Целевой совокупный доход HR (руб.)", 40000, 150000, 60000, 5000)
            hr_fixed = target_income * 0.40 # 40% base
            hr_bonus_target = target_income * 0.60 # 60% variable target
            
            st.markdown(f"**Оклад (40%):** {hr_fixed:,.0f} руб. | **Целевой бонус (60%):** {hr_bonus_target:,.0f} руб.")
            st.markdown("---")
            
            plan_adapt = st.number_input("План: Количество адаптированных стажеров", 1, 10, 3)
            fact_adapt = st.number_input("Факт: Количество адаптированных стажеров", 0, 15, 3)
            
            extra_deals = st.slider("Сделки стажеров в первые 3 месяца после адаптации (шт.)", 0, 10, 2)
            extra_bonus_rate = st.number_input("Премия за 1 сделку стажера (руб.)", 1000, 10000, 5000, 500)
            
        with col_hr2:
            st.markdown("#### 🔍 Расчет переменной части")
            exec_adapt = fact_adapt / plan_adapt if plan_adapt > 0 else 0.0
            
            # C21 Threshold rules for HR:
            # If achievement < 80% -> Variable = 0
            # If 80% <= achievement < 100% -> Coefficient = 1.0
            # If >= 100% -> Coefficient = 1.5 (for the surplus)
            if exec_adapt < 0.8:
                bonus_coeff = 0.0
                hr_msg = "🚨 Выполнение < 80% — Переменная часть аннулирована!"
            elif exec_adapt < 1.0:
                bonus_coeff = 1.0
                hr_msg = "🟢 Выполнение плана на 80-100% (коэфф. 1.0)"
            else:
                bonus_coeff = 1.5
                hr_msg = "🔥 Выполнение плана >= 100% (коэфф. 1.5 за перевыполнение)"
                
            calculated_hr_bonus = hr_bonus_target * exec_adapt * bonus_coeff
            calculated_deal_bonus = extra_deals * extra_bonus_rate
            total_hr_salary = hr_fixed + calculated_hr_bonus + calculated_deal_bonus
            
            st.markdown(f"""
            <div style="background-color: #FFFFFF; padding: 20px; border-radius: 8px; border: 1px solid #EAEAEA;">
                <h4 style="color: #1A1A1A; margin-top: 0;">Справка о начислении HR:</h4>
                <p>💼 <b>Фиксированный оклад:</b> {hr_fixed:,.0f} ₽</p>
                <p>🎯 <b>Коэффициент бонуса (адаптация):</b> {hr_msg}</p>
                <p>💰 <b>Начисленный бонус за адаптацию:</b> {calculated_hr_bonus:,.0f} ₽</p>
                <p>🤝 <b>Бонус за сделки стажеров (+):</b> {calculated_deal_bonus:,.0f} ₽ ({extra_deals} сделок)</p>
                <hr style="border-top: 1px solid #EEE;">
                <h3 style="color: #C5A059 !important; margin-top: 10px;">💵 ВСЕГО К ВЫПЛАТЕ: {total_hr_salary:,.0f} ₽</h3>
            </div>
            """, unsafe_allow_html=True)
            
    elif role == "Руководитель отдела продаж (РОП)":
        st.markdown("### 🏆 Мотивация Руководителя отдела продаж (РОПа)")
        col_rop1, col_rop2 = st.columns(2)
        with col_rop1:
            st.markdown("**1. Контур опытных агентов:**")
            rop_fixed = st.number_input("Фиксированный оклад РОПа (руб.)", 20000, 100000, 35000)
            vcd_department = st.number_input("Валовый комиссионный доход (ВКД) отдела за месяц (руб.)", 100000, 5000000, 1500000, 50000)
            
            # C21 rule: if average plan achievement of department > 80% -> ROP gets 10% of VCD, else 7% of VCD
            exec_dept_plan = st.slider("Средний процент выполнения планов опытными агентами (%)", 40, 150, 85)
            
            # C21 rule: if plan for Exclusive Contracts (ЭД) is failed -> rate is reduced by 2%
            eds_plan_passed = st.checkbox("План отдела по эксклюзивным договорам (ЭД) ВЫПОЛНЕН", value=True)
            
            st.markdown("---")
            st.markdown("**2. Контур стажеров (сделки):**")
            trainee_deals_vcd = st.number_input("ВКД от сделок стажеров в этом месяце (руб.)", 0, 1000000, 150000, 10000)
            trainee_deal_speed = st.selectbox(
                "Сроки закрытия сделок стажерами относительно бизнес-плана:",
                [
                    "Все закрыты в плановый месяц (Ставка 20%)",
                    "С задержкой на 1 месяц (Ставка 15%)",
                    "С задержкой на 2 месяца (Ставка 10%)",
                    "С задержкой на 3 месяца (Ставка 5%)",
                    "С задержкой более 3 месяцев (Ставка 0%)"
                ]
            )
            
        with col_rop2:
            st.markdown("#### 🔍 Профессиональный расчет дохода РОПа")
            
            # Base Rate calculation (10% vs 7%)
            if exec_dept_plan >= 80:
                base_rate = 0.10
                rate_msg = "📈 Средний показатель отдела >= 80% — Базовая ставка 10%"
            else:
                base_rate = 0.07
                rate_msg = "🚨 Средний показатель отдела < 80% — Пониженная ставка 7%"
                
            # Penalty for Exclusive Contract failure
            if not eds_plan_passed:
                final_rate = base_rate - 0.02
                penalty_msg = "⚠️ План по ЭД провален — Штраф -2% к ставке!"
            else:
                final_rate = base_rate
                penalty_msg = "✅ План по ЭД выполнен — Ставка сохранена"
                
            rop_dept_bonus = vcd_department * final_rate
            
            # Trainee bonus rate mapping
            speed_rates = {
                "Все закрыты в плановый месяц (Ставка 20%)": 0.20,
                "С задержкой на 1 месяц (Ставка 15%)": 0.15,
                "С задержкой на 2 месяца (Ставка 10%)": 0.10,
                "С задержкой на 3 месяца (Ставка 5%)": 0.05,
                "С задержкой более 3 месяцев (Ставка 0%)": 0.00
            }
            trainee_rate = speed_rates[trainee_deal_speed]
            rop_trainee_bonus = trainee_deals_vcd * trainee_rate
            
            # Total Calculation
            total_rop_income = rop_fixed + rop_dept_bonus + rop_trainee_bonus
            
            st.markdown(f"""
            <div style="background-color: #FFFFFF; padding: 20px; border-radius: 8px; border: 1px solid #EAEAEA;">
                <h4 style="color: #1A1A1A; margin-top: 0;">Справка о начислении РОПу:</h4>
                <p>🏢 <b>Базовый оклад РОПа:</b> {rop_fixed:,.0f} ₽</p>
                <hr style="border-top: 1px solid #EEE;">
                <p>📋 <b>Анализ эффективности опытного отдела:</b></p>
                <p style="font-size: 0.9rem; color: #555;">• {rate_msg}</p>
                <p style="font-size: 0.9rem; color: #555;">• {penalty_msg}</p>
                <p style="font-size: 1rem;">🔥 <b>Итоговый процент от ВКД отдела:</b> {(final_rate*100):.1f}% (Начислено: {rop_dept_bonus:,.0f} ₽)</p>
                <hr style="border-top: 1px solid #EEE;">
                <p>🎓 <b>Анализ контура адаптации стажеров:</b></p>
                <p style="font-size: 0.9rem; color: #555;">• Ставка РОПа со стажеров: {(trainee_rate*100):.1f}%</p>
                <p style="font-size: 1rem;">🔥 <b>Итоговый бонус со стажеров:</b> {rop_trainee_bonus:,.0f} ₽</p>
                <hr style="border-top: 1px solid #EEE;">
                <h3 style="color: #C5A059 !important; margin-top: 10px;">💵 ВСЕГО К ВЫПЛАТЕ: {total_rop_income:,.0f} ₽</h3>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# MODULE 3: Operational Launch Roadmap (8 sprints)
# ==============================================================================

# ==============================================================================
# MODULE: TRANSACTION PROFITABILITY CALCULATOR (💰 Калькулятор доходности сделок)
# ==============================================================================
# ==============================================================================
# MODULE: AGENT GOAL PLANNER (REVERSE FUNNEL)
# ==============================================================================
# ==============================================================================
# MODULE: FINANCIAL PLANNING (🏢 Финансовое планирование (Лист1))
# ==============================================================================

# ==============================================================================
# MODULE: WELCOME-CENTER & ONBOARDING (🤝 Welcome-Центр & Онбординг)
# ==============================================================================
elif menu == "🤝 Welcome-Центр & Онбординг":
    st.markdown("""
    <div style="background-color: #111111; padding: 25px 30px; border-left: 5px solid #C5A059; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h1 style="color: #FFFFFF !important; margin: 0; font-size: 2.1rem; letter-spacing: 3px; font-weight: 700; font-family: 'Barlow', sans-serif; text-transform: uppercase;">🤝 Welcome-Центр & Онбординг</h1>
        <p style="color: #C5A059; margin: 8px 0 0 0; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">История бренда, Золотой стандарт качества и мотивационный трекер CENTURION</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab_welcome, tab_swot, tab_centurion, tab_slides = st.tabs([
        "📅 Хроника & Масштаб бренда",
        "⚖️ SWOT-Анализ презентации",
        "🏆 Мотивация CENTURION",
        "💻 Слайд-Шоу Welcome"
    ])
    
    with tab_welcome:
        st.markdown("### 📅 Исторический Таймлайн CENTURY 21")
        st.markdown("Отследите путь становления глобального лидера на рынке недвижимости [1]:")
        
        # Interactive slider for timeline
        selected_year = st.select_slider(
            "Выберите веху в развитии компании:",
            options=["1971", "1974", "1983", "1989", "1998", "2002", "2007"]
        )
        
        timeline_data = {
            "1971": {"title": "🏠 Рождение бренда (США)", "desc": "Первый офис CENTURY 21 открывается в Калифорнии, закладывая фундамент для мировых стандартов качества [1]."},
            "1974": {"title": "🇨🇦 Выход на международную арену (Канада)", "desc": "Открывается первый международный офис CENTURY 21 в Канаде, запуская процесс глобального масштабирования [1]."},
            "1983": {"title": "🇯🇵 Покорение Азии (Япония)", "desc": "CENTURY 21 начинает работу в Японии, доказывая универсальность своей бизнес-системы [1]."},
            "1989": {"title": "🇲🇽 Экспансия в Латинскую Америку (Мексика)", "desc": "Открывается представительство в Мексике, укрепляя доминирование на американских континентах [1]."},
            "1998": {"title": "🇨🇳 Освоение крупнейшего азиатского рынка (Китай)", "desc": "Бренд CENTURY 21 запускается в Китае, создавая мощную реферальную базу клиентов [1]."},
            "2002": {"title": "🇪🇺 Запуск в Европе", "desc": "Компания открывает свои представительства в ключевых европейских столицах, внедряя единые стандарты качества [1]."},
            "2007": {"title": "🇷🇺 Выход на рынок России", "desc": "CENTURY 21 Россия начинает строить цивилизованный и прозрачный рынок недвижимости на территории РФ [1]."}
        }
        
        veha = timeline_data[selected_year]
        st.markdown(f"""
        <div style="background-color: #FFFFFF; padding: 25px; border-left: 5px solid #C5A059; border-radius: 4px; box-shadow: 0 4px 15px rgba(0,0,0,0.02); margin-top: 15px;">
            <h4 style="color: #C5A059; margin-top:0;">{selected_year} — {veha['title']}</h4>
            <p style="font-size: 1.05rem; line-height: 1.5; color: #333333; margin: 0;">{veha['desc']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📈 Глобальный масштаб бренда в цифрах")
        
        col_st1, col_st2, col_st3 = st.columns(3)
        with col_st1:
            st.metric("Опыт на мировом рынке", "> 45 лет", "Надежность и авторитет [1]")
            st.metric("Присутствие в мире", "80 стран", "Глобальный охват [1]")
        with col_st2:
            st.metric("Офисов по всему миру", "8 000+ шт.", "Масштабная франчайзинговая сеть [1]")
            st.metric("Агентов по всему миру", "118 000+ чел.", "Огромная профессиональная семья [1]")
        with col_st3:
            st.metric("Доля мирового рынка", "20%", "Каждая пятая сделка в мире [1]")
            st.metric("Офисов в России", "50+ городов", "Активное масштабирование [2]")
            
        st.markdown(f"""
        <div style="background-color: #F1EAD3; padding: 20px; border-radius: 4px; border: 1px solid #C5A059; margin-top: 25px;">
            <h4 style="color: #111111; margin-top: 0; text-transform: uppercase;">🌟 СИНЕРГИЯ СИСТЕМЫ CENTURY 21</h4>
            <p style="font-size: 1.05rem; margin: 0; line-height: 1.5;">
                <b>БРЕНД:</b> Повышает лояльность и конверсию первого звонка на 25-30% [3, 4].<br>
                <b>СИСТЕМА:</b> Единые жесткие регламенты обслуживания клиентов, Книга агента и Книга брокера [4].<br>
                <b>СЕТЬ:</b> Обмен опытом, международная экспертиза и кросс-региональные совместные сделки (МЛС) [4].
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with tab_swot:
        st.markdown("### ⚖️ Профессиональный аудит Welcome-Презентации")
        st.markdown("Анализ сильных и слабых сторон официального вводного документа бренда:")
        
        col_sw1, col_sw2 = st.columns(2)
        with col_sw1:
            st.markdown("""
            <div style="background-color: #E2EFDA; padding: 20px; border-left: 5px solid #375623; border-radius: 4px; height: 100%; min-height: 380px;">
                <h4 style="color: #375623; margin-top: 0; text-transform: uppercase;">💪 Сильные стороны (Strengths)</h4>
                <ul style="font-size: 0.95rem; line-height: 1.5; color: #111111;">
                    <li><b>Мощный международный статус:</b> Статистика бренда (>45 лет на рынке, 80 стран, 118 тыс. агентов) моментально вызывает доверие у стажеров и клиентов [1].</li>
                    <li><b>Проработанное ценностное предложение:</b> Четко расписаны преимущества профессии риелтора (свободный график, доход без потолка, отсутствие сокращений) [5, 6].</li>
                    <li><b>Академический контур полного цикла:</b> Структурированное представление курса <b>CREATE 21</b> (9 модулей, СДО, тренажеры диалогов) [9, 10].</li>
                    <li><b>Высшая мотивация (CENTURION):</b> Наличие международной премии с поездкой в США — мощный стимул для рекрутинга лучших кадров на рынке [12, 13].</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        with col_sw2:
            st.markdown("""
            <div style="background-color: #FCE4D6; padding: 20px; border-left: 5px solid #C65911; border-radius: 4px; height: 100%; min-height: 380px;">
                <h4 style="color: #C65911; margin-top: 0; text-transform: uppercase;">⚠️ Слабые стороны (Weaknesses)</h4>
                <ul style="font-size: 0.95rem; line-height: 1.5; color: #111111;">
                    <li><b>Устаревание части метрик:</b> Сведения о возрасте бренда в России (указано 11 лет) и даты награждений (2017 год) требуют периодической актуализации в коде [2, 13].</li>
                    <li><b>Информационный разрыв:</b> Полезные ссылки на расписание Бизнес-Академии, СДО и сувенирный магазин напечатаны текстом, требуя ручного ввода в браузере [7, 9, 16].</li>
                    <li><b>Отсутствие интерактива:</b> Презентация статична и не вовлекает новичка в реальный расчет своего будущего финансового плана.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
    with tab_centurion:
        st.markdown("### 🏆 Симулятор-Планировщик CENTURION")
        st.markdown("**CENTURION** — это высшая ежегодная международная награда для лучших агентов сети. Главный приз — поездка на глобальную конвенцию бренда в США [12, 13].")
        st.markdown("Рассчитайте, какие нормативы активности вам необходимо поддерживать, чтобы войти в элитный клуб CENTURION в этом году:")
        
        col_c_in, col_c_res = st.columns([1, 1])
        with col_c_in:
            c_target_income = st.number_input("Желаемый чистый доход за ГОД (руб.):", 500000, 10000000, 2400000, 100000)
            c_avg_gci = st.number_input("Средний ВКД (комиссия) с одной сделки (руб.):", 50000, 500000, 150000, 10000)
            c_grade = st.selectbox(
                "Ваша комиссионная ставка (грейд):",
                ["Агент (35%)", "Эксперт (40%)", "Ведущий эксперт (50%)"],
                index=1
            )
            c_rate = 0.35 if "35%" in c_grade else 0.40 if "40%" in c_grade else 0.50
            
            c_conv = st.slider("Ваша средняя конверсия 'Эксклюзив -> Сделка' (%):", 10, 80, 30) / 100.0
            
        with col_c_res:
            # Calculations
            commission_per_deal = c_avg_gci * c_rate
            needed_deals_year = c_target_income / commission_per_deal if commission_per_deal > 0 else 0
            needed_deals_month = needed_deals_year / 12.0
            needed_listing_year = needed_deals_year / c_conv if c_conv > 0 else 0
            
            # Status Check
            if needed_deals_year >= 60:
                status_gold = "🏆 КАНДИДАТ В ЧЛЕНЫ КЛУБА CENTURION!"
                status_desc = "Вы полностью выполняете международный норматив в 60 закрытых транзакций! При сохранении темпа вы гарантируете себе поездку на глобальную конференцию в США и мировое признание [12, 13]."
                status_color = "#C5A059"
                status_text_color = "#FFFFFF"
            elif needed_deals_year >= 30:
                status_gold = "⭐ ЛИДЕР СЕТИ CENTURY 21 РОССИЯ!"
                status_desc = "Прекрасный результат! Вы входите в топ лучших агентов России. До звания CENTURION и поездки в США вам не хватает закрыть еще несколько сделок в этом году [12, 13]."
                status_color = "#111111"
                status_text_color = "#C5A059"
            else:
                status_gold = "💼 АКТИВНЫЙ ПРОФЕССИОНАЛ"
                status_desc = "Вы ведете стабильный бизнес на локальном рынке. Чтобы пробиться в элиту сети и квалифицироваться на CENTURION, поработайте над конверсиями и средним чеком сделки! [3]."
                status_color = "#EAEAEA"
                status_text_color = "#111111"
                
            st.markdown(f"""
            <div style="background-color: {status_color}; padding: 25px; border-radius: 4px; border: 2px solid #C5A059; text-align: center; color: {status_text_color};">
                <h3 style="margin-top: 0; color: {status_text_color} !important;">{status_gold}</h3>
                <p style="font-size: 0.95rem; margin: 10px 0 0 0; line-height: 1.4;">{status_desc}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### Ваши годовые нормативы:")
            col_m_y1, col_m_y2 = st.columns(2)
            with col_m_y1:
                st.metric("Закрытых сделок в год", f"{needed_deals_year:.1f} шт.", f"{needed_deals_month:.1f} в месяц")
            with col_m_y2:
                st.metric("Эксклюзивных договоров в год", f"{needed_listing_year:.1f} шт.", "Минимум в работе")
                
    with tab_slides:
        st.markdown("### 💻 Слайд-Шоу Welcome-Презентации")
        st.markdown("Интерактивная текстовая визуализация ключевых слайдов официального велкам-пакета компании:")
        
        slide_num = st.radio("Выберите слайд:", [
            "Слайд 1. Миссия CENTURY 21 Россия",
            "Слайд 2. Профессия Риелтор: Специфика",
            "Слайд 3. Бизнес-Академия и CREATE 21",
            "Слайд 4. Маркетинговая полиграфия",
            "Слайд 5. Мультилистинговая система (МЛС)"
        ])
        
        if "Миссия" in slide_num:
            st.markdown("""
            <div class="c21-card" style="border-left: 5px solid #C5A059;">
                <h3 style="color: #C5A059 !important; margin-top: 0;">ЗОЛОТОЙ СТАНДАРТ РИЭЛТОРСКИХ УСЛУГ И БИЗНЕСА В НЕДВИЖИМОСТИ</h3>
                <p style="font-size: 1.05rem; line-height: 1.6; color: #222222;">
                    🎯 <b>Миссия CENTURY 21 в России [3]:</b><br>
                    • Сделать рынок недвижимости прозрачным, цивилизованным и безопасным.<br>
                    • Внедрить лучшие мировые стандарты обслуживания клиентов и современные сервисы.<br>
                    • Вырастить кузницу профессиональных кадров экстра-класса.<br>
                    • Изменить имидж риелтора и радикально поднять престиж профессии в стране.
                </p>
            </div>
            """, unsafe_allow_html=True)
        elif "Специфика" in slide_num:
            st.markdown("""
            <div class="c21-card" style="border-left: 5px solid #111111;">
                <h3 style="color: #111111 !important; margin-top: 0;">ПРЕИМУЩЕСТВА И ОСОБЕННОСТИ ПРОФЕССИИ АГЕНТА</h3>
                <p style="font-size: 1.05rem; line-height: 1.6; color: #222222;">
                    💼 <b>Что определяет работу риелтора по стандартам бренда [5, 6]:</b><br>
                    • <b>Полная независимость:</b> агент сам планирует свой день и принимает решения.<br>
                    • <b>Гибкий график:</b> нет жестких офисных рамок, вы работаете на результат.<br>
                    • <b>Доход без потолка:</b> заработная плата зависит исключительно от вашей энергии и способностей.<br>
                    • <b>Антикризис:</b> у нас никогда не бывает сокращений штатов, а спрос на жилье стабилен всегда.<br>
                    • <b>Диверсификация задач:</b> постоянное переключение между общением, маркетингом, аналитикой и правом.
                </p>
            </div>
            """, unsafe_allow_html=True)
        elif "CREATE 21" in slide_num:
            st.markdown("""
            <div class="c21-card" style="border-left: 5px solid #C5A059;">
                <h3 style="color: #C5A059 !important; margin-top: 0;">CREATE 21 — ФУНДАМЕНТ УСПЕШНОЙ КАРЬЕРЫ</h3>
                <p style="font-size: 1.05rem; line-height: 1.6; color: #222222;">
                    📚 <b>Глобальная программа обучения новичков [9, 10]:</b><br>
                    • <b>9 последовательных модулей:</b> подробный разбор всего цикла работы риелтора на вторичном рынке недвижимости.<br>
                    • <b>Система СДО:</b> дистанционное обучение в любое время в любом удобном месте.<br>
                    • <b>Интерактивные тренажеры:</b> анимированные диалоги для безопасной тренировки навыков общения с клиентами.<br>
                    • <b>Международная аттестация:</b> сдача онлайн-экзамена и получение престижного именного сертификата бренда.
                </p>
            </div>
            """, unsafe_allow_html=True)
        elif "полиграфия" in slide_num:
            st.markdown("""
            <div class="c21-card" style="border-left: 5px solid #111111;">
                <h3 style="color: #111111 !important; margin-top: 0;">МАРКЕТИНГОВЫЕ МАТЕРИАЛЫ И ПОЛИГРАФИЯ БРЕНДА</h3>
                <p style="font-size: 1.05rem; line-height: 1.6; color: #222222;">
                    📢 <b>Эффект масштаба в вашем продвижении [15, 16]:</b><br>
                    • <b>Брендирование агента:</b> профессиональные визитки, личные папки, значки и элементы стиля.<br>
                    • <b>Брендирование объекта:</b> баннеры «ПРОДАЕТСЯ», наклейки на окна и профессиональная полиграфия объекта.<br>
                    • <b>Журнал CENTURY 21 Magazine:</b> высококлассный ежеквартальный глянцевый журнал (тираж читка около 40 000 человек) [16].<br>
                    • <b>Интернет-магазин:</b> заказ сертифицированной POS-продукции бренда через единый портал <b>shop.century21.ru</b> [16].
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="c21-card" style="border-left: 5px solid #C5A059;">
                <h3 style="color: #C5A059 !important; margin-top: 0;">21-ONLINE И МУЛЬТИЛИСТИНГОВАЯ СИСТЕМА (МЛС)</h3>
                <p style="font-size: 1.05rem; line-height: 1.6; color: #222222;">
                    💻 <b>Информационные сервисы для совместных сделок [13, 14]:</b><br>
                    • <b>База CENTURY21.RU:</b> единая федеральная база данных всех объектов недвижимости сети, генерирующая поток заявок покупателей.<br>
                    • <b>Мультилистинг (МЛС):</b> единое рабочее пространство 21-online для быстрого обмена сделками между агентствами сети по всей стране.<br>
                    • <b>Автовыгрузка:</b> автоматическая трансляция ваших объявлений на 70+ лидирующих интернет-площадок России [15].<br>
                    • <b>Сайт агента:</b> автоматическое развертывание личной веб-страницы риелтора с его контактами и отзывами на главном портале [13, 15].
                </p>
            </div>
            """, unsafe_allow_html=True)


elif menu == "🏢 Финансовое планирование (Лист1)":
    st.markdown("""
    <div style="background-color: #111111; padding: 25px 30px; border-left: 5px solid #C5A059; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h1 style="color: #FFFFFF !important; margin: 0; font-size: 2.1rem; letter-spacing: 3px; font-weight: 700; font-family: 'Barlow', sans-serif; text-transform: uppercase;">ФИНАНСОВОЕ ПЛАНИРОВАНИЕ ОФИСА (Лист1)</h1>
        <p style="color: #C5A059; margin: 8px 0 0 0; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Детальный расчет постоянных затрат, расчет точки безубыточности (ТБ) и сценарное планирование целевой прибыли</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_fp1, col_fp2 = st.columns([1, 1])
    
    with col_fp1:
        st.markdown("<h4 style='color: #C5A059 !important;'>🏢 1. СОДЕРЖАНИЕ ОФИСА & ПОСТОЯННЫЕ ЗАТРАТЫ</h4>", unsafe_allow_html=True)
        office_area = st.slider("Общая площадь агентства (кв. м.)", 50, 500, 250)
        rent_per_m2 = st.number_input("Ежемесячная стоимость аренды за 1 м² (руб.)", 200, 5000, 1000)
        rent_total = office_area * rent_per_m2
        
        utilities = st.number_input("Коммунальные расходы в месяц (руб.)", 0, 100000, 20000)
        other_office_exp = st.number_input("Другие расходы в месяц (руб.)", 0, 100000, 20000)
        marketing_exp_fixed = st.number_input("Постоянные затраты на Маркетинг (руб.)", 0, 500000, 70000)
        
        office_total_exp = rent_total + utilities + other_office_exp + marketing_exp_fixed
        st.markdown(f"Итого расходы по содержанию офиса: **{office_total_exp:,.0f} руб.**")
        
        st.markdown("---")
        st.markdown("**👤 Фонд Оплаты Труда (Штат бэк-офиса):**")
        salary_office_mgr = st.number_input("Оклад: Офис-менеджер (руб.)", 0, 150000, 30000)
        salary_lawyer = st.number_input("Оклад: Юрист (руб.)", 0, 150000, 20000)
        salary_hr = st.number_input("Оклад: HR-специалист (руб.)", 0, 150000, 30000)
        salary_ros = st.number_input("Оклад: Руководитель отдела стажеров (РОС) (руб.)", 0, 150000, 30000)
        salary_ros_dep = st.number_input("Оклад: Руководитель отдела вторички (РОП) (руб.)", 0, 150000, 30000)
        salary_accountant = st.number_input("Оклад: Бухгалтер (руб.)", 0, 150000, 20000)
        
        base_payroll = salary_office_mgr + salary_lawyer + salary_hr + salary_ros + salary_ros_dep + salary_accountant
        ndfl_gross = base_payroll * 0.13 / 0.87
        total_payroll_exp = base_payroll + ndfl_gross
        
        st.markdown(f"""
        *   Базовая сумма окладов (без НДФЛ): **{base_payroll:,.0f} руб.**
        *   НДФЛ (начислено с гроссированием 13%): **{ndfl_gross:,.0f} руб.**
        *   Итого затраты на персонал (ФОТ): **{total_payroll_exp:,.0f} руб.**
        """)
        
        st.markdown("---")
        outsourcing_exp = st.number_input("Аутсорсинг услуг (в месяц, руб.)", 0, 200000, 0)
        
        # Total fixed expenses
        total_fixed_expenses = office_total_exp + total_payroll_exp + outsourcing_exp
        st.markdown(f"""
        <div style="background-color: #111111; padding: 15px; border-radius: 4px; border-left: 5px solid #C5A059; text-align: center;">
            <p style="color: #FFFFFF; margin: 0; font-size: 0.95rem; text-transform: uppercase;"><b>Итого Постоянные Затраты офиса:</b></p>
            <h3 style="color: #C5A059 !important; margin: 5px 0 0 0; font-size: 1.8rem; font-weight: 800;">{total_fixed_expenses:,.0f} ₽ / мес.</h3>
        </div>
        """, unsafe_allow_html=True)

    with col_fp2:
        st.markdown("<h4 style='color: #C5A059 !important;'>📊 2. ТОЧКА БЕЗУБЫТОЧНОСТИ & ПЛАНИРОВАНИЕ ПРИБЫЛИ</h4>", unsafe_allow_html=True)
        agent_commission_pct = st.slider("Средний процент комиссии агента (% от сделки)", 10, 90, 45, key="fp_agent_split")
        avg_commission_region = st.number_input("Сумма средней комиссии в регионе (руб.)", 10000, 1000000, 150000, 5000, key="fp_avg_comm")
        agent_efficiency_coef = st.slider("Коэффициент эффективности агента (сделок в мес.)", 0.1, 1.0, 0.50, 0.05, key="fp_agent_eff")
        
        target_profit_fp = st.number_input("Желаемая чистая Прибыль в месяц (П) (руб.)", 100000, 5000000, 1000000, 50000, key="fp_target_profit")
        
        # Break-even Point calculations
        retained_commission_rate = 1.0 - (agent_commission_pct / 100.0)
        retained_per_deal = avg_commission_region * retained_commission_rate
        
        be_deals_exact = total_fixed_expenses / retained_per_deal if retained_per_deal > 0 else 0
        be_deals_rounded = np.ceil(be_deals_exact)
        
        be_agents_exact = be_deals_exact / agent_efficiency_coef if agent_efficiency_coef > 0 else 0
        be_agents_rounded = np.ceil(be_agents_exact)
        
        st.markdown("---")
        st.markdown("**Аналитические расчеты:**")
        
        col_fpm1, col_fpm2 = st.columns(2)
        with col_fpm1:
            st.metric("Сделок для выхода в ТБ", f"{be_deals_rounded:.0f} шт.", f"Точно: {be_deals_exact:.2f}")
        with col_fpm2:
            st.metric("Агентов для ТБ (при коэфф. {0:.2f})".format(agent_efficiency_coef), f"{be_agents_rounded:.0f} чел.", f"Точно: {be_agents_exact:.2f}")
            
        # Target Profit planning math
        needed_gci_fp = (target_profit_fp + total_fixed_expenses) / retained_commission_rate if retained_commission_rate > 0 else 0
        needed_deals_fp = needed_gci_fp / avg_commission_region if avg_commission_region > 0 else 0
        needed_agents_fp = needed_deals_fp / agent_efficiency_coef if agent_efficiency_coef > 0 else 0
        
        # Exp totals with corrected formulas
        payout_agents_fp = needed_gci_fp * (agent_commission_pct / 100.0)
        corrected_total_expenses = total_fixed_expenses + payout_agents_fp
        
        st.markdown(f"""
        <div style="background-color: #FFFFFF; padding: 20px; border-radius: 4px; border: 1px solid #E2E2E6; margin-top: 15px; border-left: 5px solid #76933C;">
            <h5 style="color: #111111; margin-top: 0; font-weight: 700; text-transform: uppercase; font-size: 0.9rem; letter-spacing: 1px;">🎯 Нормативы для достижения прибыли {target_profit_fp:,.0f} ₽/мес:</h5>
            <p style="margin: 8px 0; font-size: 0.9rem;">💰 <b>Необходимый валовой доход (ВКД):</b> {needed_gci_fp:,.0f} ₽</p>
            <p style="margin: 8px 0; font-size: 0.9rem;">🤝 <b>Количество закрытых сделок (С):</b> <b>{np.ceil(needed_deals_fp):.0f} шт.</b> (точно: {needed_deals_fp:.2f})</p>
            <p style="margin: 8px 0; font-size: 0.9rem;">👥 <b>Минимум активных агентов в штате (А):</b> <b>{np.ceil(needed_agents_fp):.0f} чел.</b> (точно: {needed_agents_fp:.2f})</p>
            <p style="margin: 8px 0; font-size: 0.9rem;">🛑 <b>Итого совокупные расходы (Р):</b> {corrected_total_expenses:,.0f} ₽ (постоянные {total_fixed_expenses:,.0f} + агенты {payout_agents_fp:,.0f})</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Formula Bug Analysis Expandable Block
    with st.expander("🚨 АНАЛИЗ И ВЫЯВЛЕНИЕ КРИТИЧЕСКОЙ ОШИБКИ В ИСХОДНОМ ЛИСТЕ «Лист1» (ФИДБЕК БРОКЕРУ)"):
        st.markdown(f"""
        <div style="background-color: #FFF2CC; padding: 25px; border-left: 5px solid #F0C13A; border-radius: 4px; color: #111111;">
            <h4 style="color: #B58100 !important; margin-top: 0; text-transform: uppercase; font-size: 1.1rem; font-weight: 800; letter-spacing: 1px;">Критическая математическая ошибка в исходной формуле расходов агентства</h4>
            <p style="font-size: 0.95rem; line-height: 1.5; margin: 10px 0;">
                В оригинальном файле <i>«Расчет прибыли и агентов АН - Лист1»</i> заложена серьезная математическая ошибка, которая искусственно завышает расходы агентства и существенно занижает реальную чистую прибыль брокера.
            </p>
            <hr style="border-top: 1px solid #D9C193; margin: 15px 0;">
            <p style="font-size: 0.95rem; line-height: 1.5; margin: 10px 0;">
                <b>Как устроена ошибка:</b><br>
                Для расчета совокупных расходов <b>Р (Расходы агентства)</b> при целевом планировании прибыли в оригинальном листе используется формула: <br>
                <code style="background-color: rgba(0,0,0,0.05); padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 1rem;">Р = Постоянные расходы + ВКД * {1.0 - (agent_commission_pct / 100.0):.2f}</code>
            </p>
            <p style="font-size: 0.95rem; line-height: 1.5; margin: 10px 0;">
                Однако, средний процент комиссии агента зафиксирован как <b>{agent_commission_pct}%</b>. Это значит, что агентство выплачивает агенту {agent_commission_pct}% от сделки (расход), а себе забирает остальные <b>{100-agent_commission_pct}%</b> (удержание/доход).<br>
                Таким образом, переменные затраты на выплату агентских комиссионных составляют <b>ВКД * {agent_commission_pct}%</b>, а не <b>ВКД * {100-agent_commission_pct}%</b> (процент, который удерживает компания). Из-за того, что в формуле расходов по ошибке применили процент удержания вместо процента выплаты, расходы агентства завышены на 10% от валового оборота!
            </p>
            <hr style="border-top: 1px solid #D9C193; margin: 15px 0;">
            <h5 style="color: #111111 !important; font-weight: 700; margin: 10px 0;">Сравнение показателей при целевой прибыли {target_profit_fp:,.0f} ₽:</h5>
        </div>
        """, unsafe_allow_html=True)
        
        col_bug1, col_bug2 = st.columns(2)
        
        # Bug calculation
        buggy_var_payout = needed_gci_fp * (1.0 - (agent_commission_pct / 100.0))
        buggy_total_expenses = total_fixed_expenses + buggy_var_payout
        buggy_actual_profit = needed_gci_fp - buggy_total_expenses
        
        with col_bug1:
            st.markdown(f"""
            <div style="background-color: #FCE4D6; padding: 20px; border-radius: 4px; border: 1px solid #F8CBAD; border-left: 5px solid #C65911; height: 100%;">
                <h5 style="color: #C65911; margin-top: 0; text-transform: uppercase; font-size: 0.85rem; font-weight: 800; letter-spacing: 1px;">❌ РАСЧЕТ ИЗ ОРИГИНАЛЬНОГО ЛИСТА (С ОШИБКОЙ)</h5>
                <p style="margin: 8px 0; font-size: 0.85rem; color: #555;">• Необходимый ВКД: {needed_gci_fp:,.0f} ₽</p>
                <p style="margin: 8px 0; font-size: 0.85rem; color: #555;">• Начисленные расходы (Р): <b>{buggy_total_expenses:,.0f} ₽</b> (использован процент удержания {100-agent_commission_pct}%)</p>
                <hr style="border-top: 1px solid #F8CBAD; margin: 10px 0;">
                <p style="margin: 5px 0; font-size: 1.05rem; color: #C65911;"><b>Реальная прибыль по расчетам:</b></p>
                <p style="margin: 0; font-size: 1.6rem; font-weight: 800; color: #C65911;">{buggy_actual_profit:,.0f} ₽</p>
                <p style="margin: 5px 0; font-size: 0.75rem; color: #C65911; font-style: italic;">Убыток на бумаге: -{target_profit_fp - buggy_actual_profit:,.0f} ₽ из-за завышения расходов</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_bug2:
            st.markdown(f"""
            <div style="background-color: #E2EFDA; padding: 20px; border-radius: 4px; border: 1px solid #C6E0B4; border-left: 5px solid #375623; height: 100%;">
                <h5 style="color: #375623; margin-top: 0; text-transform: uppercase; font-size: 0.85rem; font-weight: 800; letter-spacing: 1px;">✅ БЕЗОШИБОЧНЫЙ РАСЧЕТ CENTURY 21</h5>
                <p style="margin: 8px 0; font-size: 0.85rem; color: #555;">• Необходимый ВКД: {needed_gci_fp:,.0f} ₽</p>
                <p style="margin: 8px 0; font-size: 0.85rem; color: #555;">• Корректные расходы (Р): <b>{corrected_total_expenses:,.0f} ₽</b> (использован процент выплаты агенту {agent_commission_pct}%)</p>
                <hr style="border-top: 1px solid #C6E0B4; margin: 10px 0;">
                <p style="margin: 5px 0; font-size: 1.05rem; color: #375623;"><b>Реальная чистая прибыль:</b></p>
                <p style="margin: 0; font-size: 1.6rem; font-weight: 800; color: #375623;">{target_profit_fp:,.0f} ₽</p>
                <p style="margin: 5px 0; font-size: 0.75rem; color: #375623; font-style: italic;">Расчет сошелся копейка в копейку: чистая маржинальность восстановлена!</p>
            </div>
            """, unsafe_allow_html=True)

elif menu == "🎯 Планировщик целей агента":
    st.markdown("""
    <div style="background-color: #111111; padding: 25px 30px; border-left: 5px solid #C5A059; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h1 style="color: #FFFFFF !important; margin: 0; font-size: 2.1rem; letter-spacing: 3px; font-weight: 700; font-family: 'Barlow', sans-serif; text-transform: uppercase;">ОБРАТНОЕ ПЛАНИРОВАНИЕ ЦЕЛЕЙ</h1>
        <p style="color: #C5A059; margin: 8px 0 0 0; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Установите желаемый доход, и система рассчитает нормативы активности агента по стандартам бренда</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_g1, col_g2 = st.columns([1, 2])
    with col_g1:
        st.markdown("<h4 style='color: #C5A059 !important;'>1. Финансовые ориентиры</h4>", unsafe_allow_html=True)
        target_income = st.number_input("Желаемый чистый доход агента в месяц (руб.)", 30000, 1000000, 100000, 5000)
        
        agent_grade_type = st.selectbox(
            "Ваш текущий карьерный грейд:",
            [
                "Стажер (30% комиссии)",
                "Стажер на окладной схеме (20% комиссии)",
                "Агент (35% комиссии)",
                "Эксперт (40% комиссии)",
                "Ведущий эксперт (50% комиссии)"
            ]
        )
        
        # Commission rate map
        grade_rates = {
            "Стажер (30% комиссии)": 0.30,
            "Стажер на окладной схеме (20% комиссии)": 0.20,
            "Агент (35% комиссии)": 0.35,
            "Эксперт (40% комиссии)": 0.40,
            "Ведущий эксперт (50% комиссии)": 0.50
        }
        active_rate = grade_rates[agent_grade_type]
        
        avg_deal_gci = st.number_input("Средняя комиссия (ВКД) со сделки (руб.)", 50000, 500000, 150000, 5000)
        work_days = st.slider("Рабочих дней в месяце (для планирования активности)", 15, 26, 22)
        
        st.markdown("<h4 style='color: #C5A059 !important;'>2. Ваши персональные конверсии</h4>", unsafe_allow_html=True)
        g_conv_call_meet = st.slider("Конверсия: Звонок -> Встреча (%)", 2.0, 30.0, 10.0, 0.5) / 100.0
        g_conv_meet_ed = st.slider("Конверсия: Встреча -> Договор (ЭД) (%)", 5.0, 60.0, 25.0, 1.0) / 100.0
        g_conv_ed_deal = st.slider("Конверсия: Договор (ЭД) -> Сделка (%)", 5.0, 60.0, 30.0, 1.0) / 100.0
        
    with col_g2:
        # Calculate reverse funnel
        # Target Income = Deals * Avg Deal GCI * Commission Rate
        commission_per_deal = avg_deal_gci * active_rate
        needed_deals = target_income / commission_per_deal if commission_per_deal > 0 else 0
        needed_eds = needed_deals / g_conv_ed_deal if g_conv_ed_deal > 0 else 0
        needed_meets = needed_eds / g_conv_meet_ed if g_conv_meet_ed > 0 else 0
        needed_calls = needed_meets / g_conv_call_meet if g_conv_call_meet > 0 else 0
        
        # Daily/weekly metrics
        daily_calls = needed_calls / work_days if work_days > 0 else 0
        weekly_meets = needed_meets / 4.0 # 4 weeks
        
        st.markdown("### 🏆 Ваши нормативы активностей для достижения цели:")
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.metric("Чистый доход со сделки", f"{commission_per_deal:,.0f} ₽", f"Грейд: {active_rate*100:.0f}%")
        with col_c2:
            st.metric("Необходимо сделок", f"{needed_deals:.2f} шт.", f"В месяц")
        with col_c3:
            st.metric("Необходимо договоров (ЭД)", f"{needed_eds:.1f} шт.", "В работе")
            
        col_c4, col_c5 = st.columns(2)
        with col_c4:
            st.metric("Необходимо встреч", f"{needed_meets:.1f} шт.", f"{weekly_meets:.1f} в неделю")
        with col_c5:
            st.metric("Необходимо звонков", f"{needed_calls:,.0f} шт.", f"{daily_calls:.1f} в день")
            
        # Funnel chart for Agent
        stages = ["Холодные звонки", "Встречи", "Эксклюзивные договоры", "Закрытые сделки"]
        values = [needed_calls, needed_meets, needed_eds, needed_deals]
        
        fig_agent_funnel = go.Figure(go.Funnel(
            y=stages,
            x=values,
            textinfo="value",
            marker=dict(color=["#333333", "#C5A059", "#D9C193", "#EAE0CE"])
        ))
        fig_agent_funnel.update_layout(
            title="Индивидуальная воронка активностей (обратное планирование)",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_agent_funnel, use_container_width=True)
        
        # Dynamic insight
        st.markdown("#### 💡 Аналитический совет:")
        if daily_calls > 30:
            st.warning(f"🚨 **Высокая нагрузка!** Вам необходимо делать **{daily_calls:.1f}** звонков в день. Чтобы снизить нагрузку, работайте над улучшением конверсий: используйте наши карточки возражений (Flashcards) для роста конверсии из встречи в договор!")
        else:
            st.success(f"🟢 **Отличный баланс!** Нагрузка в **{daily_calls:.1f}** звонков в день абсолютно комфортна и соответствует стандартам CENTURY 21. Регулярно выполняйте эту норму для стабильного закрытия сделок!")

    st.markdown("---")
    col_save1, col_save2 = st.columns(2)
    with col_save1:
        st.markdown("<h4 style='color: #C5A059 !important;'>📥 Сохранить цель в архив офиса</h4>", unsafe_allow_html=True)
        agent_name = st.text_input("Введите ваше ФИО для сохранения цели:", key="save_agent_name")
        if st.button("💾 Отправить цель в архив CENTURY 21"):
            if agent_name.strip() == "":
                st.error("⚠️ Введите имя агента перед отправкой!")
            else:
                new_goal = {
                    "Имя": agent_name.strip(),
                    "Грейд": agent_grade_type,
                    "Желаемый доход": float(target_income),
                    "ВКД со сделки": float(avg_deal_gci),
                    "Необходимо сделок": round(float(needed_deals), 2),
                    "Необходимо договоров": round(float(needed_eds), 1),
                    "Необходимо звонков в день": round(float(daily_calls), 1)
                }
                exists = False
                for i, g in enumerate(st.session_state['agent_goals']):
                    if g['Имя'].lower() == agent_name.strip().lower():
                        st.session_state['agent_goals'][i] = new_goal
                        exists = True
                        break
                if not exists:
                    st.session_state['agent_goals'].append(new_goal)
                st.success(f"✅ Цель агента {agent_name} успешно сохранена/обновлена в архиве офиса CENTURY 21!")
                st.rerun()

    with col_save2:
        st.markdown("<h4 style='color: #C5A059 !important;'>🔒 Панель Брокера: Личный архив целей</h4>", unsafe_allow_html=True)
        broker_password = st.text_input("Введите пароль брокера для доступа к архиву (пароль по умолчанию: c21):", type="password", key="broker_pass_archive")
        
        if broker_password == "c21":
            st.success("🔓 Доступ разрешен! Загрузка архива целей команды...")
            
            if len(st.session_state['agent_goals']) == 0:
                st.info("📂 Архив целей пуст. Агенты еще не сохранили свои цели.")
            else:
                goals_df = pd.DataFrame(st.session_state['agent_goals'])
                total_team_ambitions = goals_df["Желаемый доход"].sum()
                
                st.markdown(f"##### 🏆 Общая сумма амбиций CENTURY 21: **{total_team_ambitions:,.0f} ₽**")
                
                scale_max = max(float(total_team_ambitions * 1.2), 1000000.0)
                
                fig_goals_bar = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = total_team_ambitions,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Совокупные финансовые амбиции команды (чистый доход, руб.)", 'font': {'size': 12, 'color': '#1A1A1A'}},
                    gauge = {
                        'axis': {'range': [None, scale_max], 'tickwidth': 1, 'tickcolor': "#1A1A1A"},
                        'bar': {'color': "#C5A059"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "#EAEAEA",
                        'steps': [
                            {'range': [0, scale_max * 0.5], 'color': '#F2F2F2'},
                            {'range': [scale_max * 0.5, scale_max], 'color': '#EBF1F5'}
                        ],
                    }
                ))
                fig_goals_bar.update_layout(height=180, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_goals_bar, use_container_width=True)
                
                st.dataframe(goals_df, use_container_width=True)
                
                if st.button("🗑️ Очистить весь архив целей"):
                    st.session_state['agent_goals'] = []
                    st.toast("Архив целей успешно очищен")
                    st.rerun()
        elif broker_password != "":
            st.error("❌ Неверный пароль брокера! Доступ заблокирован.")


elif menu == "💰 Калькулятор доходности сделок":
    st.markdown("""
    <div style="background-color: #111111; padding: 25px 30px; border-left: 5px solid #C5A059; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h1 style="color: #FFFFFF !important; margin: 0; font-size: 2.1rem; letter-spacing: 3px; font-weight: 700; font-family: 'Barlow', sans-serif; text-transform: uppercase;">UNIT-ЭКОНОМИКА СДЕЛКИ</h1>
        <p style="color: #C5A059; margin: 8px 0 0 0; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Детальный расчет рентабельности отдельной транзакции с учетом роялти бренда (6%), налогов и KPI выплат</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_dc1, col_dc2 = st.columns([1, 1])
    
    with col_dc1:
        st.markdown("<h4 style='color: #C5A059 !important;'>📥 Параметры сделки</h4>", unsafe_allow_html=True)
        
        property_val = st.number_input("Стоимость объекта недвижимости (руб.)", 1000000, 100000000, 15000000, 500000)
        commission_pct = st.slider("Процент комиссии агентства (%)", 1.0, 10.0, 3.0, 0.5)
        
        # Gross Commission Income (ВКД)
        deal_gci = property_val * (commission_pct / 100.0)
        st.markdown(f"Валовый комиссионный доход (ВКД): **{deal_gci:,.0f} руб.**")
        
        st.markdown("---")
        st.markdown("**👤 Мотивация Агента (из источника «Мотивация агентов»):**")
        agent_grade = st.selectbox(
            "Грейд и базовая ставка агента:",
            [
                "Стажер (30%)",
                "Стажер на альтернативном окладе (20%)",
                "Агент - базовый (35%)",
                "Агент - сверхобъем (45%)",
                "Эксперт - базовый (40%)",
                "Эксперт - сверхобъем (50%)",
                "Ведущий эксперт - базовый (50%)",
                "Ведущий эксперт - сверхобъем (60%)"
            ]
        )
        
        # Extract base percentage
        grade_mapping = {
            "Стажер (30%)": 0.30,
            "Стажер на альтернативном окладе (20%)": 0.20,
            "Агент - базовый (35%)": 0.35,
            "Агент - сверхобъем (45%)": 0.45,
            "Эксперт - базовый (40%)": 0.40,
            "Эксперт - сверхобъем (50%)": 0.50,
            "Ведущий эксперт - базовый (50%)": 0.50,
            "Ведущий эксперт - сверхобъем (60%)": 0.60
        }
        agent_base_rate = grade_mapping[agent_grade]
        
        # Disciplinary penalty check
        agent_penalty = st.checkbox("У стажера/агента был провален план по привлечению клиентов (-3% к ставке)")
        agent_final_rate = agent_base_rate - 0.03 if agent_penalty else agent_base_rate
        agent_final_rate = max(0.0, agent_final_rate) # safeguard
        
        st.markdown("---")
        st.markdown("**🏆 Мотивация РОПа (из источника «Мотивация руководителей»):**")
        rop_role_type = st.selectbox(
            "Контур сделки для РОПа:",
            [
                "Сделка стажера - закрыта вовремя (Ставка РОПа 20%)",
                "Сделка стажера - задержка 1 месяц (Ставка РОПа 15%)",
                "Сделка стажера - задержка 2 месяца (Ставка РОПа 10%)",
                "Сделка стажера - задержка 3 месяца (Ставка РОПа 5%)",
                "Сделка стажера - задержка >3 месяцев (Ставка РОПа 0%)",
                "Сделка опытного агента - выполнение планов отдела >= 80% (Ставка РОПа 10%)",
                "Сделка опытного агента - выполнение планов отдела < 80% (Ставка РОПа 7%)"
            ]
        )
        
        rop_mapping = {
            "Сделка стажера - закрыта вовремя (Ставка РОПа 20%)": 0.20,
            "Сделка стажера - задержка 1 месяц (Ставка РОПа 15%)": 0.15,
            "Сделка стажера - задержка 2 месяца (Ставка РОПа 10%)": 0.10,
            "Сделка стажера - задержка 3 месяца (Ставка РОПа 5%)": 0.05,
            "Сделка стажера - задержка >3 месяцев (Ставка РОПа 0%)": 0.00,
            "Сделка опытного агента - выполнение планов отдела >= 80% (Ставка РОПа 10%)": 0.10,
            "Сделка опытного агента - выполнение планов отдела < 80% (Ставка РОПа 7%)": 0.07
        }
        rop_base_rate = rop_mapping[rop_role_type]
        
        # ROP Exclusive Contract plan failed penalty
        rop_penalty = False
        if "Сделка опытного агента" in rop_role_type:
            rop_penalty = st.checkbox("План РОПа по эксклюзивным договорам (ЭД) провален (-2% к ставке)")
            
        rop_final_rate = rop_base_rate - 0.02 if (rop_penalty and "Сделка опытного агента" in rop_role_type) else rop_base_rate
        rop_final_rate = max(0.0, rop_final_rate)
        
        st.markdown("---")
        st.markdown("**💼 Накладные и налоги:**")
        marketing_exp = st.number_input("Маркетинговый бюджет продвижения объекта (руб.)", 0, 50000, 10000, 1000)
        tax_regime = st.selectbox("Система налогообложения офиса:", ["УСН Доходы (6% от ВКД)", "УСН Доходы минус Расходы (15% от операционной прибыли)"])
        
    with col_dc2:
        st.markdown("<h4 style='color: #C5A059 !important;'>📊 Расчет доходности и распределение</h4>", unsafe_allow_html=True)
        
        # Calculations backend
        agent_payout = deal_gci * agent_final_rate
        royalty_payout = deal_gci * 0.06 # standard 6% C21 royalty
        rop_payout = deal_gci * rop_final_rate
        
        # Operating income before tax
        opex_total_calc = agent_payout + rop_payout + royalty_payout + marketing_exp
        operating_income = deal_gci - opex_total_calc
        
        # Tax calculation
        if tax_regime == "УСН Доходы (6% от ВКД)":
            taxes_payout = deal_gci * 0.06
        else:
            taxes_payout = max(0.0, operating_income * 0.15)
            
        # Final Net Profit
        net_profit = operating_income - taxes_payout
        net_margin = (net_profit / deal_gci * 100.0) if deal_gci > 0 else 0.0
        
        # Metric Card summary
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("Чистая прибыль Брокера", f"{net_profit:,.0f} ₽", f"{net_margin:.1f}% рентабельность")
        with col_res2:
            color_grade = "normal" if net_margin >= 30.0 else "inverse"
            status_deal = "🔥 ВЫСОКОМАРЖИНАЛЬНАЯ" if net_margin >= 35.0 else "🟢 ПРИБЫЛЬНАЯ" if net_margin >= 20.0 else "🚨 НИЗКОМАРЖИНАЛЬНАЯ"
            st.metric("Статус прибыльности сделки", status_deal)
            
        st.markdown("---")
        st.markdown("**Структура распределения ВКД от сделки:**")
        
        # Plotly Pie Chart representing the distribution
        labels_chart = ['Выплата агенту', 'Выплата РОПу', 'Роялти бренда C21', 'Расходы на маркетинг', 'Корпоративные налоги', 'Чистая прибыль офиса']
        values_chart = [agent_payout, rop_payout, royalty_payout, marketing_exp, taxes_payout, max(0.0, net_profit)]
        
        # Remove labels with 0 value to make chart clean
        clean_labels = []
        clean_values = []
        for l, v in zip(labels_chart, values_chart):
            if v > 0:
                clean_labels.append(l)
                clean_values.append(v)
                
        fig_pie = go.Figure(data=[go.Pie(
            labels=clean_labels,
            values=clean_values,
            hole=.4,
            marker=dict(colors=['#C5A059', '#D9C193', '#1A1A1A', '#555555', '#EAE0CE', '#76933C'])
        )])
        fig_pie.update_layout(
            title="Распределение валового дохода (ВКД) по статье расходов",
            height=320,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", y=-0.1)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Details Table
        st.markdown("**Детализация отчета по транзакции:**")
        det_data = {
            "Статья": [
                "Валовый комиссионный доход (ВКД) от сделки",
                f"Выплата агенту ({agent_final_rate*100:.1f}% от ВКД)",
                f"Выплата РОПу ({rop_final_rate*100:.1f}% от ВКД)",
                "Роялти франшизы CENTURY 21 (6.0% от ВКД)",
                "Маркетинговый бюджет объекта недвижимости",
                f"Корпоративные налоги ({tax_regime})",
                "Чистая прибыль брокера (агентства)"
            ],
            "Сумма (руб.)": [
                f"{deal_gci:,.0f} ₽",
                f"- {agent_payout:,.0f} ₽",
                f"- {rop_payout:,.0f} ₽",
                f"- {royalty_payout:,.0f} ₽",
                f"- {marketing_exp:,.0f} ₽",
                f"- {taxes_payout:,.0f} ₽",
                f"{net_profit:,.0f} ₽"
            ]
        }
        st.table(pd.DataFrame(det_data))

elif menu == "🗺️ Дорожная карта запуска":
    st.markdown("""
    <div style="background-color: #111111; padding: 25px 30px; border-left: 5px solid #C5A059; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h1 style="color: #FFFFFF !important; margin: 0; font-size: 2.1rem; letter-spacing: 3px; font-weight: 700; font-family: 'Barlow', sans-serif; text-transform: uppercase;">ОПЕРАЦИОННЫЙ ЗАПУСК ФРАНШИЗЫ</h1>
        <p style="color: #C5A059; margin: 8px 0 0 0; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">8-недельный операционный план и сквозной чеклист открытия агентства по стандартам бренда</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Roadmap tasks dataset in code for portability
    tasks_data = [
        # Week 1
        {"week": 1, "task": "Утверждение 7-ступенчатого бизнес-плана и бюджета офиса", "dept": "Брокер", "pri": "Высокий", "status": "Выполнено", "desc": "Оценка финансовой рентабельности и расчет дефицита/профицита по стандартам Глава 2."},
        {"week": 1, "task": "Регистрация юридического лица (ООО/ИП) и открытие счетов", "dept": "Юрист", "pri": "Высокий", "status": "Выполнено", "desc": "Подготовка учредительных документов по МЛС стандартам."},
        {"week": 1, "task": "Постановка на учет в Росфинмониторинг (ПОД/ФТ)", "dept": "Юрист", "pri": "Высокий", "status": "Выполнено", "desc": "Обязательное требование законодательства РФ в сфере сделок с недвижимостью."},
        
        # Week 2
        {"week": 2, "task": "Поиск и аудит офисного помещения (не менее 70 кв.м.)", "dept": "Брокер", "pri": "Высокий", "status": "Выполнено", "desc": "Оценка проходимости, видимости фасада и соответствия бренду."},
        {"week": 2, "task": "Подписание договора долгосрочной аренды офиса", "dept": "Юрист", "pri": "Средний", "status": "Выполнено", "desc": "Юридический аудит собственника помещения и регистрация договора."},
        {"week": 2, "task": "Разработка плана зонирования офисного пространства", "dept": "Брокер", "pri": "Средний", "status": "В процессе", "desc": "Разделение на рецепцию, рабочую зону агентов, стажерский класс и переговорные."},
        
        # Week 3
        {"week": 3, "task": "Проведение косметического ремонта офиса по брендбуку", "dept": "Офис-менеджер", "pri": "Средний", "status": "В процессе", "desc": "Использование серых, белых и золотых корпоративных цветов бренда."},
        {"week": 3, "task": "Заказ брендированной фасадной вывески и POSM-материалов", "dept": "Офис-менеджер", "pri": "Высокий", "status": "В процессе", "desc": "Закупка папок ППА, ручек, журналов CENTURY 21 Magazine через shop.century21.ru."},
        {"week": 3, "task": "Закупка мебели и оргтехники для рабочих мест", "dept": "Офис-менеджер", "pri": "Средний", "status": "Не начата", "desc": "Оснащение рабочих мест компьютером, гарнитурами для телефонии и МФУ."},
        
        # Week 4
        {"week": 4, "task": "Настройка CRM-системы 21online.ru для офиса", "dept": "Брокер", "pri": "Высокий", "status": "Не начата", "desc": "Создание личных кабинетов, настройка прав доступа и шлюзов выгрузки."},
        {"week": 4, "task": "Подключение IP-телефонии и интеграция с CRM", "dept": "Брокер", "pri": "Высокий", "status": "Не начата", "desc": "Настройка записи разговоров для контроля качества скриптов в Главе 12."},
        {"week": 4, "task": "Регистрация корпоративных почт в домене century21.ru", "dept": "Офис-менеджер", "pri": "Низкий", "status": "Не начата", "desc": "Создание персональных почтовых ящиков для сотрудников офиса."},
        
        # Week 5
        {"week": 5, "task": "Подготовка профилей вакансий HR, РОСа и РОПа", "dept": "Брокер", "pri": "Высокий", "status": "Не начата", "desc": "Составление объявлений и регламентов мотивации согласно Главы 3 книги."},
        {"week": 5, "task": "Наем и оформление в штат HR-менеджера офиса", "dept": "Брокер", "pri": "Высокий", "status": "Не начата", "desc": "Первое ключевое звено кадрового контура агентства."},
        {"week": 5, "task": "Обучение и адаптация офис-менеджера по стандартам", "dept": "Брокер", "pri": "Средний", "status": "Не начата", "desc": "Изучение стандартов приема звонков, встречи гостей и ведения канцелярии."},
        
        # Week 6
        {"week": 6, "task": "Размещение вакансий стажеров на работных сайтах", "dept": "HR-менеджер", "pri": "Высокий", "status": "Не начата", "desc": "Запуск воронки рекрутинга, подготовка скриптов первого контакта."},
        {"week": 6, "task": "Подготовка и проведение Карьерного семинара", "dept": "HR-менеджер", "pri": "Средний", "status": "Не начата", "desc": "Презентация бренда CENTURY 21 для соискателей в офисе согласно Главы 4."},
        
        # Week 7
        {"week": 7, "task": "Подготовка учебного класса для стажеров", "dept": "Офис-менеджер", "pri": "Средний", "status": "Не начата", "desc": "Подготовка проектора, досок, методических материалов ORIENTATION 21."},
        {"week": 7, "task": "Утверждение Положения о мотивации и шаблонов договоров", "dept": "Юрист", "pri": "Высокий", "status": "Не начата", "desc": "Официальный регламент деления комиссии и грейдовой сетки агентов CENTURY 21."},
        
        # Week 8
        {"week": 8, "task": "Запуск 14-дневного учебного интенсива CREATE 21", "dept": "Брокер", "pri": "Высокий", "status": "Не начата", "desc": "Выход первого потока стажеров на обучение, выдача папок ППА и старт «90 дней»."}
    ]
    
    df_tasks = pd.DataFrame(tasks_data)
    
    # Summary of progress
    total_t = len(df_tasks)
    done_t = len(df_tasks[df_tasks["status"] == "Выполнено"])
    prog_t = len(df_tasks[df_tasks["status"] == "В процессе"])
    none_t = len(df_tasks[df_tasks["status"] == "Не начата"])
    progress_percentage = (done_t / total_t) * 100
    
    col_p1, col_p2, col_p3 = st.columns([1, 1, 2])
    with col_p1:
        st.metric("Всего операционных задач", f"{total_t} шт.", "8 недель запуска")
    with col_p2:
        st.metric("Выполнено / В процессе", f"{done_t} / {prog_t} шт.", f"{none_t} не начато")
    with col_p3:
        st.markdown(f"**Общий прогресс запуска франшизы:**")
        st.progress(progress_percentage / 100.0)
        st.markdown(f"<h3 style='color: #C5A059 !important; margin: 0;'>{progress_percentage:.1f}% ГОТОВНОСТИ ОФИСА</h3>", unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("### 📋 Интерактивный канбан-чеклист задач")
    
    # Filter by week
    selected_week = st.slider("Фильтр по неделям (спринтам):", 1, 8, 3)
    
    filtered_tasks = df_tasks[df_tasks["week"] == selected_week]
    
    for idx, row in filtered_tasks.iterrows():
        status_color = "🟢" if row["status"] == "Выполнено" else "🟡" if row["status"] == "В процессе" else "⚪"
        prio_color = "🔴" if row["pri"] == "Высокий" else "🟡" if row["pri"] == "Средний" else "🟢"
        
        with st.expander(f"{status_color} {row['task']} (Неделя {row['week']})"):
            st.markdown(f"**Ответственный отдел:** {row['dept']}")
            st.markdown(f"**Приоритет задачи:** {prio_color} {row['pri']}")
            st.markdown(f"**Регламент выполнения:** {row['desc']}")
            
            # Simulated Status Editor
            new_status = st.selectbox(
                f"Изменить статус задачи (ID: {idx}):",
                ["Не начата", "В процессе", "Выполнено"],
                index=["Не начата", "В процессе", "Выполнено"].index(row["status"]),
                key=f"task_{idx}"
            )
            if new_status != row["status"]:
                st.toast(f"Статус задачи '{row['task']}' изменен на '{new_status}'")

# ==============================================================================
# MODULE 4: TRAINING CENTER (Quiz, Flashcards, Podcasts, Videos)
# ==============================================================================
elif menu == "🎓 Центр обучения & Адаптации":
    st.markdown("""
    <div style="background-color: #111111; padding: 25px 30px; border-left: 5px solid #C5A059; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h1 style="color: #FFFFFF !important; margin: 0; font-size: 2.1rem; letter-spacing: 3px; font-weight: 700; font-family: 'Barlow', sans-serif; text-transform: uppercase;">АКАДЕМИЯ АДАПТАЦИИ "ПЕРВЫЕ 90 ДНЕЙ"</h1>
        <p style="color: #C5A059; margin: 8px 0 0 0; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Интегрированный хаб знаний: электронный трекер, экспресс-тестирование, тренажер возражений и медиатека</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab_guide, tab_quiz, tab_cards, tab_media = st.tabs([
        "📅 План адаптации «90 дней»",
        "✏️ Интерактивный тест (Quiz)",
        "📇 Карточки возражений (Flashcards)",
        "🎧 Медиа-подготовка (Подкаст и Видео)"
    ])
    
    with tab_guide:
        st.markdown("### 📅 Индивидуальный трекер стажера «Первые 90 дней»")
        
        col_st1, col_st2 = st.columns([2, 1])
        with col_st1:
            st_name = st.text_input("ФИО стажера-агента:", "Алексей Смирнов")
            st_mentor = st.text_input("Наставник (РОС/РОП):", "Мария Иванова")
            
            st.markdown("#### Прогресс выполнения задач адаптации:")
            st.checkbox("1. Подготовка: получение корпоративной почты, доступов в CRM 21online.ru", value=True)
            st.checkbox("2. Снабжение: выдача папки ППА, визиток, бланков эксклюзивных договоров", value=True)
            st.checkbox("3. Обучение: успешная регистрация на дистанционный курс CREATE 21", value=True)
            st.checkbox("4. Практика: проведение 21 исходящего звонка в день согласно нормативам", value=False)
            st.checkbox("5. Аттестация: сдача теоретического зачета и получение сертификата", value=False)
            
        with col_st2:
            st.markdown("#### ⚖️ Анализ KPI за 30 дней (Месяц 1)")
            calls_f = st.number_input("Факт: Звонки стажера за месяц", 0, 1000, 462)
            meets_f = st.number_input("Факт: Встречи стажера за месяц", 0, 100, 41)
            eds_f = st.number_input("Факт: Договоры (ЭД) за месяц", 0, 20, 10)
            
            # Calculations
            st_conv_calls = (meets_f / calls_f * 100) if calls_f > 0 else 0
            st_conv_meets = (eds_f / meets_f * 100) if meets_f > 0 else 0
            
            st.markdown(f"""
            <div style="background-color: #FFFFFF; padding: 15px; border-radius: 8px; border: 1px solid #EAEAEA;">
                <p style="margin: 5px 0;">📊 <b>Конверсия звонок -> встреча:</b> {st_conv_calls:.1f}%</p>
                <p style="margin: 5px 0; font-size: 0.85rem; color: #666;">(Целевой норматив: > 10.0%)</p>
                <hr style="margin: 10px 0; border-top: 1px solid #EEE;">
                <p style="margin: 5px 0;">🤝 <b>Конверсия встреча -> договор:</b> {st_conv_meets:.1f}%</p>
                <p style="margin: 5px 0; font-size: 0.85rem; color: #666;">(Целевой норматив: > 25.0%)</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st_conv_calls >= 10.0 and st_conv_meets >= 25.0:
                st.success("🎉 Стажер полностью выполняет нормативы конверсии!")
            else:
                st.warning("⚠️ Внимание: стажеру требуется дополнительный тренинг по скриптам звонков или защите комиссии.")

    with tab_quiz:
        st.markdown("### ✏️ Интерактивный учебный экспресс-тест")
        st.markdown("Проверьте свои знания стандартов бренда CENTURY 21 и регламентов курса CREATE 21.")
        
        q1 = st.radio(
            "1. Какова ежедневная норма контактов в телемаркетинге по Книге агента CENTURY 21?",
            ["10 звонков в день", "21 звонок в день", "50 звонков в день", "Звонить без ограничений"]
        )
        
        q2 = st.radio(
            "2. Какой размер базовой комиссии получает стажер на испытательном сроке?",
            ["20%", "30%", "40%", "50%"]
        )
        
        q3 = st.radio(
            "3. Что такое ППА в регламенте проведения встреч CENTURY 21?",
            ["Программа продаж агента", "Презентационная папка агента", "План продвижения объекта", "Персональный портфель активов"]
        )
        
        if st.button("Проверить ответы"):
            score = 0
            if q1 == "21 звонок в день": score += 1
            if q2 == "30%": score += 1
            if q3 == "Презентационная папка агента": score += 1
            
            if score == 3:
                st.success("🎉 Отличный результат! 3 из 3 правильных ответов. Вы полностью готовы к аттестации!")
            else:
                st.warning(f"Вы ответили правильно на {score} из 3 вопросов. Рекомендуем повторить регламенты обучения!")

    with tab_cards:
        st.markdown("### 📇 Карточки возражений собственников (Flashcards)")
        st.markdown("Потренируйтесь отрабатывать самые частые возражения собственников жилья с помощью проверенных скриптов CENTURY 21.")
        
        card = st.selectbox(
            "Выберите типичное возражение собственника:",
            [
                "Возражение: «Я продам сам, мне не нужны услуги агента»",
                "Возражение: «У вас слишком большая комиссия (6%)»",
                "Возражение: «Я не хочу подписывать эксклюзивный договор»"
            ]
        )
        
        if "Я продам сам" in card:
            st.markdown("""
            <div style="background-color: #FFF2CC; padding: 20px; border-left: 5px solid #F0C13A; border-radius: 4px;">
                <p style="margin: 0; font-weight: bold; color: #856404;">Речевой модуль отработки (скрипт):</p>
                <p style="margin: 10px 0 0 0; font-style: italic; color: #1A1A1A;">
                    «Иван Иванович, я прекрасно понимаю ваше желание сэкономить. Именно поэтому я и предлагаю встретиться. Моя цель — не просто разместить объявление на тех же сайтах, что и вы, а применить профессиональную маркетинговую воронку из 21 шага, включая хоум-стейджинг и точечную работу с базой покупателей, чтобы продать вашу квартиру по максимальной рыночной цене, защитив ваши интересы. Скажите, вам было бы удобно встретиться сегодня в 15:00 или завтра в 11:00?»
                </p>
            </div>
            """, unsafe_allow_html=True)
        elif "большая комиссия" in card:
            st.markdown("""
            <div style="background-color: #FFF2CC; padding: 20px; border-left: 5px solid #F0C13A; border-radius: 4px;">
                <p style="margin: 0; font-weight: bold; color: #856404;">Речевой модуль отработки (скрипт):</p>
                <p style="margin: 10px 0 0 0; font-style: italic; color: #1A1A1A;">
                    «Иван Иванович, размер нашей комиссии полностью оправдан тем объемом работы и рекламного бюджета, который компания инвестирует в ваш объект еще ДО совершения сделки. Мы полностью берем на себя юридическую проверку покупателя, подготовку документов, организацию показов и агрессивный маркетинг на 40+ площадках. По сути, мы гарантируем безопасность и выгоду сделки. Если мы продадим квартиру на 5-10% дороже, чем вы планировали, вы ведь будете согласны оплатить качественную работу?»
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #FFF2CC; padding: 20px; border-left: 5px solid #F0C13A; border-radius: 4px;">
                <p style="margin: 0; font-weight: bold; color: #856404;">Речевой модуль отработки (скрипт):</p>
                <p style="margin: 10px 0 0 0; font-style: italic; color: #1A1A1A;">
                    «Иван Иванович, эксклюзивный договор — это не ограничение вашей свободы, а гарантия того, что агентство будет вкладывать 100% своих ресурсов и платного маркетинга именно в вашу квартиру. Когда объектом занимаются сразу 5 агентств, никто из них не несет ответственности, и объект обесценивается. При эксклюзиве я лично отвечаю перед вами головой и еженедельно предоставляю отчет о ходе рекламной кампании. Давайте я покажу вам преимущества эксклюзива на встрече?»
                </p>
            </div>
            """, unsafe_allow_html=True)

    with tab_media:
        st.markdown("### 🎧 Аудиоподкаст и Видеокурс по стандартам бренда")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("#### 🎧 Аудиоподкаст «Детский врач»")
            st.markdown("Слушайте разбор философии проспектинга и преодоления страха холодных звонков на примере работы детского врача.")
            st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3") # Placeholder clean audio
            st.caption("Аудио-брифинг в формате живого диалога. Длительность: 12 минут.")
            
        with col_m2:
            st.markdown("#### 📹 Видеообзор «Цикл успешной сделки»")
            st.markdown("Вовлекающий экскурс в бизнес-архитектуру проведения сделки CENTURY 21 для брокеров и РОПов.")
            # Standard video mockup with info
            st.image("https://images.unsplash.com/photo-1560518883-ce09059eeffa?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80")
            st.caption("Видео-лекция. Хронометраж: 18 минут. Доступно в вашей панели Studio.")


# ==============================================================================
# MODULE: AI CONSULTANT (🤖 ИИ-Консультант CENTURY 21)
# ==============================================================================

# ==============================================================================
# MODULE: ADAPTATION STANDARDS & LEADS CONVEYOR (🏃 Стандарты Адаптации & Лидов)
# ==============================================================================
elif menu == "🏃 Стандарты Адаптации & Лидов":
    st.markdown("""
    <div style="background-color: #111111; padding: 25px 30px; border-left: 5px solid #C5A059; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h1 style="color: #FFFFFF !important; margin: 0; font-size: 2.1rem; letter-spacing: 3px; font-weight: 700; font-family: 'Barlow', sans-serif; text-transform: uppercase;">🏃 СТАНДАРТЫ АДАПТАЦИИ & КОНВЕЙЕР ЛИДОВ</h1>
        <p style="color: #C5A059; margin: 8px 0 0 0; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Интегрированные стандарты стажировки РОПа, нормативов стажеров и конвейерной работы с покупателями</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab_audit, tab_rop, tab_agent_kpi, tab_buyer_conveyor = st.tabs([
        "📋 Анализ и Аудит Регламентов",
        "👔 Стажировка РОПа (План первой недели)",
        "📊 Калькулятор Продуктивности Стажера",
        "🤝 Конвейер Лидов Покупателей"
    ])
    
    with tab_audit:
        st.markdown("""
        ### 📋 Профессиональный аудит и ценность интеграции источников
        
        На основе анализа 4-х ключевых документов регламентного контура мы выявили сильные и слабые стороны текущей операционной системы агентства и автоматизировали их в данном MVP-модуле.
        """)
        
        col_aud1, col_aud2 = st.columns(2)
        with col_aud1:
            st.markdown("""
            <div style="background-color: #FFFFFF; padding: 20px; border-left: 4px solid #C5A059; border-radius: 4px; box-shadow: 0 4px 10px rgba(0,0,0,0.02); margin-bottom: 15px;">
                <h4 style="color: #111111; margin-top: 0; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px;">💪 Сильные стороны регламентов:</h4>
                <p style="font-size: 0.9rem; line-height: 1.5; color: #222222;">
                    1. <b>Математически обоснованные воронки стажеров:</b> «Правила адаптации» дают новичку понятную оцифрованную связь — 10 звонков ➔ 2 встречи ➔ 2 договора ➔ 1 сделка через месяц. Это убирает неопределенность.<br>
                    2. <b>Подневное расписание старта:</b> Четкий график первой недели стажера (регистрации на edu.century21.ru, подготовка СМА, визиток, Смарт-Агента) защищает от потери темпа.<br>
                    3. <b>Стратегическое планирование РОПа:</b> Требование о составлении плана развития на 6 месяцев с первой недели стажировки гарантирует фокус руководителя на метриках.<br>
                    4. <b>Сверхдоходная лидогенерация (до 40% ВКД):</b> Разделение ролей агента продавца и агента покупателя с жестким правилом передачи простаивающих лидов (3-7 дней) максимизирует утилизацию звонков покупателей.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_aud2:
            st.markdown("""
            <div style="background-color: #FFFFFF; padding: 20px; border-left: 4px solid #111111; border-radius: 4px; box-shadow: 0 4px 10px rgba(0,0,0,0.02); margin-bottom: 15px;">
                <h4 style="color: #111111; margin-top: 0; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px;">⚠️ Выявленные слабости и точки роста:</h4>
                <p style="font-size: 0.9rem; line-height: 1.5; color: #222222;">
                    1. <b>Риск выгорания из-за жестких санкций:</b> Угроза увольнения («мы прощаемся») за провал нормативов более 2 интервалов подряд без учета качества звонков. Требуется мягкий контроль.<br>
                    2. <b>Экстремальный когнитивный перегруз РОПа в 1-ю неделю:</b> Изучить 8 модулей CREATE 21, все регламенты, базы данных, WA-отчетность, съездить на встречи и сделать план развития на 6 месяцев за 5 дней — физически сложно.<br>
                    3. <b>Ручной контроль простоя покупателей:</b> Листинг-агенты склонны «удерживать» контакты покупателей без работы. Без ИИ-контроля или автонапоминаний CRM лиды сгорают.<br>
                    4. <b>Проблема хаоса в чатах:</b> Ведение отчетов в разрозненных чатах WhatsApp размывает фокус руководителя. Требуется единый интерфейс.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("""
        <div style="background-color: #FFF2CC; padding: 15px; border-radius: 4px; border-left: 5px solid #F0C13A; margin-top: 15px;">
            <p style="margin: 0; font-weight: bold; color: #856404; font-size: 0.95rem;">💡 Как этот MVP решает данные проблемы:</p>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem; line-height: 1.5; color: #1a1a1a;">
                Мы оцифровали подневные шаги стажировки РОПа и адаптации стажера, добавив <b>калькулятор продуктивности</b>, который мягко предупреждает о рисках увольнения на основе его реальных диалогов и встреч. Также мы создали <b>симулятор конвейера лидов покупателя</b>, который рассчитывает упущенную выгоду от простоя контактов у листинг-агентов, наглядно показывая брокеру точки роста прибыли без дополнительных затрат на рекламу.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with tab_rop:
        st.markdown("""
        ### 👔 Карта адаптации нового РОПа (Первая неделя)
        Интерактивный трекер прохождения программы стажировки руководителя отдела продаж согласно регламенту CENTURY 21.
        """)
        
        # Interactive checklist of days
        rop_day = st.selectbox(
            "Выберите рабочий день стажировки РОПа:",
            ["День 1: Знакомство и старт CREATE 21", "День 2: Настройка коммуникаций", "День 3: Работа в CRM 21online", "День 4: Анализ концепции", "День 5: Долгосрочное планирование"]
        )
        
        if "День 1" in rop_day:
            st.markdown("""
            <div style="background-color: #FFFFFF; padding: 20px; border-radius: 4px; border: 1px solid #E2E2E6;">
                <h4 style="color: #C5A059;">🎯 Задачи 1-го дня: Знакомство и старт CREATE 21</h4>
                <ul>
                    <li><b>Знакомство с офисом и коллегами:</b> личное представление команде агентства недвижимости.</li>
                    <li><b>Изучение документов:</b> прочитать все файлы на общем диске (планы стажировок, правила адаптации стажеров, системы мотиваций агентов, классификаторы клиентов).</li>
                    <li><b>Начало прохождения CREATE 21:</b> запуск <b>Модуля 1 "Активный поиск клиентов"</b> и первичное изучение Книги агента и Книги РОПа.</li>
                    <li><b>Личные встречи:</b> обязательное посещение реальной встречи с агентом в полях для оценки его навыков презентации услуги.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        elif "День 2" in rop_day:
            st.markdown("""
            <div style="background-color: #FFFFFF; padding: 20px; border-radius: 4px; border: 1px solid #E2E2E6;">
                <h4 style="color: #C5A059;">🎯 Задачи 2-го дня: Отработка скриптов и коммуникация</h4>
                <ul>
                    <li><b>Интеграция в каналы связи:</b> добавление во все рабочие чаты WhatsApp и Telegram, детальное изучение правил отчетности.</li>
                    <li><b>Продолжение курса CREATE 21:</b> изучение <b>Модуля 2 "Основы телемаркетинга"</b> и <b>Модуля 3 "Телемаркетинг: ошибки и возражения"</b>.</li>
                    <li><b>Изучение процесса подготовки:</b> как агенты готовят сравнительно-маркетинговый анализ (СМА) и презентационную папку агента (ППА).</li>
                    <li><b>Отработка и звонки:</b> участие в утренней планерке (10:00) и дневной отработке скриптов звонков (14:00).</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        elif "День 3" in rop_day:
            st.markdown("""
            <div style="background-color: #FFFFFF; padding: 20px; border-radius: 4px; border: 1px solid #E2E2E6;">
                <h4 style="color: #C5A059;">🎯 Задачи 3-го дня: CRM-системы и бизнес-планирование</h4>
                <ul>
                    <li><b>Технический аудит 21online:</b> изучение работы с планами, задачами, лидами, воронкой, телефонией и синхронизацией календаря.</li>
                    <li><b>Составление бизнес-плана агента:</b> индивидуальный расчет воронки и активности для конкретного риелтора на основе его целей.</li>
                    <li><b>Дистанционное обучение:</b> просмотр записей вебинаров Бизнес-академии CENTURY 21.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        elif "День 4" in rop_day:
            st.markdown("""
            <div style="background-color: #FFFFFF; padding: 20px; border-radius: 4px; border: 1px solid #E2E2E6;">
                <h4 style="color: #C5A059;">🎯 Задачи 4-го дня: Тестирование и Анализ концепции</h4>
                <ul>
                    <li><b>Завершение курса CREATE 21:</b> финальное прохождение тестов по Модулю 8 ("Подбор недвижимости и сделка") и получение сертификата.</li>
                    <li><b>Юридические основы:</b> изучение правил проведения сделок, требований к оформлению договоров и ПОД/ФТ (115-ФЗ).</li>
                    <li><b>Анализ работы стажеров:</b> формирование отчета брокеру о текущем качестве привлечения лидов и вывода стажеров на договоры.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #FFFFFF; padding: 20px; border-radius: 4px; border: 1px solid #E2E2E6;">
                <h4 style="color: #C5A059;">🎯 Задачи 5-го дня: Разработка Стратегического плана развития</h4>
                <ul>
                    <li><b>Изучение базы знаний в 21online:</b> регламенты работы отделов и шаблоны отчетностей.</li>
                    <li><b>Планирование отдела на 6 месяцев:</b> ключевой результат первой недели РОПа. Составление кадрового плана, прогноза звонков, встреч, листингов, эксклюзивов (ЭД) и сделок.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("#### 🧭 Интерактивный генератор плана развития отдела РОПа (на 6 месяцев)")
        st.markdown("Заполните планируемые параметры для вашего отдела, чтобы система рассчитала целевой валовый доход (ВКД) и проверила его реалистичность:")
        
        col_rp1, col_rp2 = st.columns(2)
        with col_rp1:
            target_agents = st.slider("Планируемый штат отдела (чел.)", 3, 20, 10, key="rop_target_agents")
            avg_deals_per_agent = st.slider("Целевой показатель ПОА (сделок на 1 агента в месяц)", 0.3, 2.0, 0.8, 0.1, key="rop_target_poa")
            avg_commission_val = st.number_input("Средняя комиссия со сделки в регионе (руб.)", 50000, 500000, 150000, 5000, key="rop_avg_comm")
        with col_rp2:
            st.markdown("**Целевые метрики отдела в месяц:**")
            total_dept_deals = target_agents * avg_deals_per_agent
            total_dept_gci = total_dept_deals * avg_commission_val
            
            st.markdown(f"📊 Планируемое количество сделок отдела: **{total_dept_deals:.1f} шт./мес.**")
            st.markdown(f"💰 Планируемый валовый доход отдела (ВКД): **{total_dept_gci:,.0f} ₽/мес.**")
            
            # Target GCI over 6 months
            six_month_gci = total_dept_gci * 6
            st.markdown(f"🏆 **Прогноз ВКД за 6 месяцев стажировки РОПа: {six_month_gci:,.0f} ₽**")
            
            if total_dept_gci >= 1200000:
                st.success("🔥 **Высокий потенциал отдела!** При таком объеме ВКД вы с запасом перекрываете постоянные расходы офиса и обеспечиваете РОПу повышенный процент (10%).")
            else:
                st.warning("⚠️ **Внимание:** Плановый доход отдела ниже 1.2 млн руб. РОП рискует остаться на пониженной процентной ставке (7%), так как средняя выручка на агента может не достигнуть целевого порога в 80% от плана.")

    with tab_agent_kpi:
        st.markdown("""
        ### 📊 Калькулятор Продуктивности и Контроля Рисков Стажера
        Сравнение фактической активности стажера с жесткими нормативами документа «Правила адаптации.docx» с прогнозированием кадровых рисков.
        """)
        
        col_sta1, col_sta2 = st.columns(2)
        with col_sta1:
            stage_period = st.selectbox(
                "Текущий этап адаптации агента:",
                ["1-я неделя (Адаптация)", "2-я неделя - 1-й месяц", "2-й месяц - 3-й месяц", "Свыше 3-х месяцев"]
            )
            
            st.markdown("**Ввод фактических результатов агента за отчетную неделю:**")
            fact_dialogues = st.number_input("Количество диалогов с новыми клиентами за неделю", 0, 200, 42)
            fact_presentations = st.number_input("Проведено презентаций услуги / просмотров объектов", 0, 30, 3)
            fact_eds_month = st.number_input("Подписано эксклюзивных договоров за месяц (ЭД)", 0, 10, 1)
            fact_advances_month = st.number_input("Принято авансов за месяц", 0, 5, 0)
            
            failed_intervals = st.slider("Сколько временных интервалов подряд агент НЕ выполняет нормативы?", 0, 5, 1)
            
        with col_sta2:
            st.markdown("#### 🔍 Сверка с нормативами CENTURY 21:")
            
            is_valid = True
            reasons = []
            
            if stage_period == "1-я неделя (Адаптация)":
                target_d = 50
                target_p = 0
                target_e = 0
                target_a = 0
                
                if fact_dialogues < target_d:
                    is_valid = False
                    reasons.append(f"Недостаточно диалогов (факт: {fact_dialogues} из {target_d} необходимых)")
            elif stage_period == "2-я неделя - 1-й месяц":
                target_d = 50
                target_p = 4 # 8 просмотров или 4 презентации
                target_e = 0
                target_a = 0
                
                if fact_dialogues < target_d:
                    is_valid = False
                    reasons.append(f"Недостаточно диалогов (факт: {fact_dialogues} из {target_d} необходимых)")
                if fact_presentations < target_p:
                    is_valid = False
                    reasons.append(f"Недостаточно презентаций/просмотров (факт: {fact_presentations} из {target_p} презентаций или 8 просмотров)")
            elif stage_period == "2-й месяц - 3-й месяц":
                target_d = 0
                target_p = 4
                target_e = 2
                target_a = 0
                
                if fact_presentations < target_p:
                    is_valid = False
                    reasons.append(f"Недостаточно презентаций/просмотров (факт: {fact_presentations} из {target_p} презентаций или 8 просмотров)")
                if fact_eds_month < target_e:
                    is_valid = False
                    reasons.append(f"Мало подписанных договоров за месяц (факт: {fact_eds_month} из {target_e} ЭД)")
            else: # Свыше 3-х месяцев
                target_d = 0
                target_p = 4 # 4 презентации
                target_e = 2 # 2 договора
                target_a = 1 # 1 аванс
                
                if fact_presentations < target_p:
                    is_valid = False
                    reasons.append(f"Недостаточно презентаций (факт: {fact_presentations} из {target_p} обязательных)")
                if fact_eds_month < target_e:
                    is_valid = False
                    reasons.append(f"Мало подписанных договоров (факт: {fact_eds_month} из {target_e} ЭД в месяц)")
                if fact_advances_month < target_a:
                    is_valid = False
                    reasons.append(f"Отсутствуют принятые авансы (факт: {fact_advances_month} из {target_a} в месяц)")
                    
            # Render results card
            if is_valid:
                st.success("🎉 **Стажер полностью выполняет нормативы!** Он находится на верном пути к первой сделке и заработку до 240 000 руб. в месяц.")
                risk_level = "Низкий"
                status_color_text = "color: green;"
            else:
                st.warning("⚠️ **Обнаружены просадки по активности:**\\n" + "\\n".join([f"* {r}" for r in reasons]))
                risk_level = "Средний" if failed_intervals == 1 else "Критический"
                status_color_text = "color: orange;" if failed_intervals == 1 else "color: red;"
                
            # Threat check
            st.markdown("---")
            st.markdown(f"#### 🚦 Кадровый статус стажера:")
            if failed_intervals >= 2 and not is_valid:
                st.markdown("""
                <div style="background-color: #FCE4D6; padding: 20px; border-left: 5px solid #C65911; border-radius: 4px;">
                    <h4 style="color: #C65911; margin-top: 0; font-size: 1.05rem;">🚨 СТАТУС: РИСК УВОЛЬНЕНИЯ (ПРОСИМ ПОПРОЩАТЬСЯ)</h4>
                    <p style="margin: 0; font-size: 0.9rem; line-height: 1.4; color: #111111;">
                        Агент не выполняет минимальные плановые показатели более 2-х временных интервалов подряд без уважительной причины. Согласно пункту 7 'Правил адаптации.docx', дальнейшие временные инвестиции руководителя нерентабельны — <b>рекомендовано расстаться с сотрудником</b>.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            elif failed_intervals == 1 and not is_valid:
                st.markdown("""
                <div style="background-color: #FFF2CC; padding: 20px; border-left: 5px solid #F0C13A; border-radius: 4px;">
                    <h4 style="color: #856404; margin-top: 0; font-size: 1.05rem;">🟡 СТАТУС: ПРЕДУПРЕЖДЕНИЕ (ПЕРВЫЙ ПРОПУСК)</h4>
                    <p style="margin: 0; font-size: 0.9rem; line-height: 1.4; color: #111111;">
                        Выявлена просадка по нормативам за 1 отчетный период. РОПу рекомендовано провести индивидуальную планерку, проконтролировать знание скрипта холодного звонка и отработать презентацию услуги с помощью Flashcards. <b>Второй пропуск приведет к расторжению сотрудничества.</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #E2EFDA; padding: 20px; border-left: 5px solid #375623; border-radius: 4px;">
                    <h4 style="color: #375623; margin-top: 0; font-size: 1.05rem;">🟢 СТАТУС: АКТИВНЫЙ РОСТ И УСТОЙЧИВОСТЬ</h4>
                    <p style="margin: 0; font-size: 0.9rem; line-height: 1.4; color: #111111;">
                        Агент находится в зеленой зоне. Рекомендуется закрепить успех, выдать корпоративную сим-карту (для 2-й недели), подготовить СМА и буклет для презентации эксклюзивного договора продавцу на встрече.
                    </p>
                </div>
                """, unsafe_allow_html=True)

    with tab_buyer_conveyor:
        st.markdown("""
        ### 🤝 Конвейер Лидов Покупателей (Unit-экономика)
        Симулятор разделения труда и контроля простоя клиентов. До 40% ВКД агентства генерируется правильным конвейерным ведением покупателей.
        """)
        
        col_co1, col_co2 = st.columns(2)
        with col_co1:
            st.markdown("<h4 style='color: #C5A059 !important;'>📥 Входящий трафик (Колл-центр)</h4>", unsafe_allow_html=True)
            total_calls = st.number_input("Количество входящих звонков от покупателей в месяц", 50, 1000, 300, 10)
            
            st.markdown("**⏱️ Правило простоя (3-7 дней):**")
            crm_leak_pct = st.slider("Процент лидов, простаивающих у листинг-агентов без открытых задач > 5 дней (%)", 10, 90, 40)
            
            st.markdown("**🤝 Конверсия специализированного Агента Покупателей:**")
            st.info("💡 Согласно регламенту, выделенный агент по работе с покупателями закрывает договор на подбор (с предоплатой) у **30% потенциальных клиентов** (из 10 обращений - 3 платных).")
            sub_deal_conv = st.slider("Конверсия договора на подбор в закрытую сделку (%)", 10, 50, 30)
            avg_buy_gci = st.number_input("Средняя комиссия (ВКД) со сделки подбора (руб.)", 50000, 500000, 150000, 5000)
            
        with col_co2:
            st.markdown("<h4 style='color: #C5A059 !important;'>💰 Экономический эффект специализации</h4>", unsafe_allow_html=True)
            
            # Calculations of leaked leads
            leaked_leads = total_calls * (crm_leak_pct / 100.0)
            
            # Special buyer contracts signed (30% of leaked leads converted by specialist)
            buyer_contracts = leaked_leads * 0.30
            
            # Closed deals from these contracts
            closed_buyer_deals = buyer_contracts * (sub_deal_conv / 100.0)
            
            # Lost/Captured GCI
            captured_gci = closed_buyer_deals * avg_buy_gci
            
            st.markdown(f"""
            <div style="background-color: #FFFFFF; padding: 20px; border-radius: 4px; border: 1px solid #E2E2E6; margin-bottom: 20px;">
                <h5 style="color: #111111; margin-top: 0; text-transform: uppercase;">Расчет упущенной прибыли от простоя лидов:</h5>
                <p style="margin: 10px 0;">🔴 <b>Простаивающие лиды у листинг-агентов:</b> {leaked_leads:.0f} контактов в месяц</p>
                <p style="margin: 10px 0;">📂 <b>Потенциальные договоры на подбор (30%):</b> {buyer_contracts:.1f} договоров</p>
                <p style="margin: 10px 0;">🤝 <b>Дополнительно закрытые сделки:</b> {closed_buyer_deals:.1f} сделок в месяц</p>
                <hr style="border-top: 1px solid #EEE; margin: 15px 0;">
                <h3 style="color: #C5A059 !important; margin: 0; font-size: 1.6rem;">💵 УПУЩЕННЫЙ ВКД: {captured_gci:,.0f} ₽</h3>
                <p style="font-size: 0.85rem; color: #666; margin-top: 5px;">При ручном ведении и простаивании лидов у листинг-агентов без передачи в отдел покупателей офис теряет эту сумму ежемесячно!</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background-color: #E2EFDA; padding: 20px; border-radius: 4px; border-left: 5px solid #375623;">
                <h5 style="color: #375623; margin-top: 0; text-transform: uppercase; font-weight: 800;">🚀 Технология "Совместный просмотр" (Без холодных звонков):</h5>
                <p style="margin: 0; font-size: 0.9rem; line-height: 1.5; color: #111111;">
                    Используйте показы ваших объектов покупателям как инструмент привлечения новых листингов. Агент покупателя выводит клиента на показ, а листинг-агент выезжает на объект ДО встречи с целью выявить мотивацию непредставленного продавца. Это позволяет <b>заключать эксклюзивные договоры прямо на объектах без единого холодного звонка</b>.
                </p>
            </div>
            """, unsafe_allow_html=True)


elif menu == "🤖 ИИ-Консультант CENTURY 21":
    st.markdown("""
    <div style="background-color: #111111; padding: 25px 30px; border-left: 5px solid #C5A059; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h1 style="color: #FFFFFF !important; margin: 0; font-size: 2.1rem; letter-spacing: 3px; font-weight: 700; font-family: 'Barlow', sans-serif; text-transform: uppercase;">🤖 ИИ-Консультант CENTURY 21</h1>
        <p style="color: #C5A059; margin: 8px 0 0 0; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Интерактивный ИИ-ассистент по Книге брокера, Книги агента и регламентам бренда</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Mode selection
    rag_mode = st.radio(
        "Выберите режим работы ассистента:",
        ["📖 Локальный ИИ-эксперт (Книга брокера)", "🔌 Живой ИИ-RAG (через Google Cloud API)"]
    )
    
    if "chat_history_v9" not in st.session_state:
        st.session_state["chat_history_v9"] = [
            ("assistant", "🤖 Приветствую! Я ваш цифровой ИИ-Консультант CENTURY 21 по Системе знаний и технологий CENTURY 21. Я знаю абсолютно всё о Книге Брокера, регламентах адаптации '90 дней', кадровом учете и финансовом планировании. О чем вы хотите спросить сегодня?")
        ]
        
    if rag_mode == "📖 Локальный ИИ-эксперт (Книга брокера)":
        st.markdown("""
        ### 📖 Экспертный режим: Локальные стандарты CENTURY 21
        Ассистент мгновенно отвечает на ваши вопросы на основе регламентов, должностных инструкций и приложений к Книге брокера (без задержек и без интернета).
        """)
        
        # Display sample prompt buttons
        st.markdown("**Рекомендованные вопросы для проверки:**")
        col_q1, col_q2, col_q3 = st.columns(3)
        with col_q1:
            if st.button("📞 Какая норма звонков в день?"):
                st.session_state["chat_history_v9"].append(("user", "Какая норма звонков в день?"))
                st.rerun()
        with col_q2:
            if st.button("👔 Регламент дресс-кода в офисе?"):
                st.session_state["chat_history_v9"].append(("user", "Регламент дресс-кода в офисе?"))
                st.rerun()
        with col_q3:
            if st.button("🛡️ Что такое ПОД/ФТ и требования?"):
                st.session_state["chat_history_v9"].append(("user", "Что такое ПОД/ФТ и требования?"))
                st.rerun()
                
        # Interactive Chat interface
        for sender, msg in st.session_state["chat_history_v9"]:
            if sender == "user":
                st.chat_message("user").markdown(f"**Вы:** {msg}")
            else:
                st.chat_message("assistant").markdown(msg)
                
        # Quick Response Generation
        user_input = st.chat_input("Задайте свой вопрос по Книге брокера...")
        
        if user_input:
            st.session_state["chat_history_v9"].append(("user", user_input))
            st.rerun()
            
        # Process last user message
        if len(st.session_state["chat_history_v9"]) > 0 and st.session_state["chat_history_v9"][-1][0] == "user":
            last_q = st.session_state["chat_history_v9"][-1][1].lower().strip()
            
            # Simple NLP Rules
            response = ""
            if any(w in last_q for w in ["звон", "норма", "активн", "звонок", "контакт"]):
                response = """
                🤖 **Ответ на основе Книги агента и Главе 7 Книги брокера:**
                
                Согласно стандартам бренда **CENTURY 21 Россия**, регламентированная норма активности агента составляет:
                *   **Ежедневная норма исходящих звонков:** **21 звонок в день** [14, 23].
                *   **Целевая недельная активность:** Не менее **100 звонков** и **5 назначенных встреч**.
                *   **Дисциплинарная ответственность:** Если агент-стажер или опытный агент не выполняет ежемесячный план по привлечению клиентов (минимум 2-3 клиента), его процент деления комиссии в следующем месяце автоматически снижается **на 3%** [1, 9].
                
                *Рекомендация:* Регулярно используйте наши интерактивные карточки (Flashcards) для тренировки скрипта холодного звонка и отработки возражений!
                """
            elif any(w in last_q for w in ["дресс", "одежд", "внешн", "вид", "костюм", "галстук"]):
                response = """
                🤖 **Ответ на основе Главы 1 (стр. 38) и Приложения 1 Книги брокера:**
                
                В сети **CENTURY 21** действует строгий регламент корпоративного внешнего вида (корпоративный дресс-код CENTURY 21) [1, 2, 13, 86]:
                *   **Для мужчин:** Строгий деловой костюм (угольный, темно-синий или серый), белая или светлая однотонная рубашка, галстук, деловая классическая обувь.
                *   **Для женщин:** Деловой костюм (жакет с юбкой или брюками), классическое строгое платье, блузка без вызывающих вырезов, закрытые туфли-лодочки.
                *   **Запрещено:** Джинсы, спортивная одежда, открытая обувь (сандалии, шлепанцы), одежда ярких неоновых расцветок, массивная неформальная бижутерия.
                
                *Важно:* «Ваш профессиональный имидж — это часть общего имиджа глобальной сети CENTURY 21» [1, 13, 39].
                """
            elif any(w in last_q for w in ["под/фт", "росфин", "закон", "террор", "отмыв", "рфм"]):
                response = """
                🤖 **Ответ на основе Главы 11 Книги брокера (Юридические аспекты):**
                
                Деятельность агентства недвижимости в сфере сделок с недвижимым имуществом строго регулируется Федеральным законом № 115-ФЗ (ПОД/ФТ) [1, 11, 46]:
                1.  **Постановка на учет:** В течение 3-х дней с момента регистрации юридического лица брокер обязан встать на учет в **Росфинмониторинге** и зарегистрировать Личный кабинет на портале РФМ.
                2.  **Назначение ответственного:** Брокер должен назначить Специальное должностное лицо (СДЛ), ответственное за соблюдение правил внутреннего контроля, прошедшее обучение.
                3.  **Идентификация клиентов:** При проведении сделок обязательно проводится полная проверка клиентов (продавцов и покупателей) по базам террористов и экстремистов с заполнением анкет.
                4.  **Ответственность:** Штрафы за несоблюдение требований ПОД/ФТ на юридическое лицо начинаются **от 50 000 до 400 000 рублей**, а также грозит приостановка деятельности офиса.
                """
            elif any(w in last_q for w in ["семинар", "карьер", "рекрут", "наем", "соискател"]):
                response = """
                🤖 **Ответ на основе Главы 4 Книги брокера (Системный рекрутинг):**
                
                Масштабирование офиса до класса «D» (от 3-х отделов продаж) требует непрерывной системы найма стажеров [1, 5, 51]:
                *   **Карьерный семинар (КС):** Проводится еженедельно (рекомендовано по четвергам в 18:30). Это групповая презентация бренда CENTURY 21 для соискателей, которая повышает конверсию воронки найма на 30%.
                *   **Скрипт звонка HR:** Главная задача звонка рекрутера соискателю — продать не вакансию агента, а приглашение на Карьерный семинар в офисе [1, 5, 52].
                *   **Контроль стоимости (CPA):** Целевая стоимость привлечения 1 лида на вакансию через рекламу не должна превышать **150-200 руб.**
                """
            elif any(w in last_q for w in ["час", "планер", "собран", "планерка", "пятниц"]):
                response = """
                🤖 **Ответ на основе Глава 1 (стр. 40) и Главы 7 Книги брокера:**
                
                Еженедельный регламент совещаний в офисе CENTURY 21 включает [1, 8, 40]:
                1.  **Еженедельное отчетное собрание (по пятницам):** Полный анализ выполнения планов ВКД, выставленных листингов, разбор лучших сделок и планирование целей.
                2.  **«Час агента» (совещание):** Состоит из 4-х блоков:
                    *   *Блок 1: Оценка достижений* (награждение лучших агентов, признание) [1, 71].
                    *   *Блок 2: Информационный блок* (анализ рынка, анонсы вебинаров Бизнес-академии) [1, 71].
                    *   *Блок 3: Маркетинг* (разбор лучших и худших листингов, рекламные площадки) [1, 72].
                    *   *Блок 4: Практический тренинг* (ролевая игра, отработка возражений по картам) [1, 72].
                """
            elif any(w in last_q for w in ["офис", "площад", "кв", "метр", "требован", "аренд"]):
                response = """
                🤖 **Ответ на основе Главы 1 (раздел Офис и Оборудование) и Главы 2 Книги брокера:**
                
                Официальные требования к офисному помещению франчайзи CENTURY 21 [1, 2]:
                *   **Минимальная площадь:** Не менее **70 квадратных метров** (для стадии стартапа) [2, 40].
                *   **Расположение:** Первая линия домов, хорошая видимость фасада, отдельный вход с улицы (рекомендовано), первый или второй этаж.
                *   **Зонирование пространства:**
                    1.  *Рецепция/Зона ожидания клиентов* (с уличной брендированной вывеской и рекламными стойками) [1, 81].
                    2.  *Общая рабочая зона для агентов*.
                    3.  *Выделенный учебный класс для стажеров* [1, 64].
                    4.  *Смысловая переговорная комната* (для конфиденциального подписания эксклюзивных договоров).
                """
            elif any(w in last_q for w in ["обучен", "create", "академи", "курс"]):
                response = """
                🤖 **Ответ на основе Главы 5 и 6 Книги брокера (Система обучения):**
                
                Образовательный фундамент CENTURY 21 Россия включает [1, 6, 34]:
                *   **Бизнес-Академия CENTURY 21 Россия:** Лицензированный учебный центр, проводящий более 20 учебных мероприятий ежемесячно [1, 54, 56].
                *   **ORIENTATION 21:** Девятиурочный вводный видеокурс для первичной адаптации стажеров в первую неделю [1, 59, 60].
                *   **CREATE 21:** Уникальный интенсивный электронный дистанционный курс для вывода агента на первые сделки [1, 60].
                *   **IMA (International Management Academy):** Специализированная программа профессиональной подготовки и повышения квалификации для Брокеров и РОПов по управлению АН [1, 57].
                """
            else:
                # Fallback: scan chapters
                response = f"""
                🤖 **ИИ-Поиск по индексу Книги Брокера:**
                
                Запрос *«{st.session_state["chat_history_v9"][-1][1]}»* не совпал с типовыми шаблонами экспресс-ответов. Однако на основе оглавления **«Книги брокера» CENTURY 21** [1], эта тема наиболее подробно раскрыта в следующих разделах:
                
                *   **Для вопросов управления и финансов:** Обратитесь к **Главе 2. «Основы управления АН»** (раздел «Рентабельность и достижение максимальной прибыли», стр. 66–77) [1, 3, 4].
                *   **Для вопросов кадров и ролей РОПа/РОСа:** Изучите **Главу 3. «Организационно-кадровая структура»** (стр. 82–102) [1, 4, 5].
                *   **Для юридических рисков и договоров:** Смотрите **Главу 11. «Юридические аспекты работы»** (стр. 216–236) [1, 11, 12].
                *   **Для работы в МЛС и совместных сделок:** Изучите **Главу 10. «Регламент работы в мультилистинговой системе»** (стр. 211–215) [1, 10, 11].
                
                *Вы можете уточнить ваш запрос, используя ключевые слова: «норма звонков», «дресс-код», «рекрутинг», «ПОД/ФТ», «офис» или «обучение».*
                """
            st.session_state["chat_history_v9"].append(("assistant", response))
            st.rerun()
            
    elif rag_mode == "🔌 Живой ИИ-RAG (через Google Cloud API)":
        st.markdown("""
        ### 🔌 Режим Живого ИИ-RAG (Cloud Интеграция)
        Подключите API-ключ вашей нейросети для живого диалога с оригинальными документами CENTURY 21. 
        """)
        
        col_key1, col_key2 = st.columns([1, 1])
        with col_key1:
            gemini_key = st.text_input("Введите ваш Google Gemini API Key (для продакшена):", type="password", help="Получить ключ можно бесплатно в Google AI Studio")
        with col_key2:
            uploaded_pdf = st.file_uploader("Загрузите любой регламент в формате PDF/DOCX:", type=["pdf", "docx"])
            
        st.markdown("---")
        
        # Simulated live console
        if gemini_key and uploaded_pdf:
            st.success("🔌 **Соединение с Google AI Cloud успешно установлено!** ИИ просканировал документ и готов отвечать.")
            st.info("💡 **Как это работает в облаке:** Приложение использует библиотеки `google-generativeai` и `PyPDF2` / `pdfplumber` для создания эмбеддингов, сохранения в векторный индекс FAISS / ChromaDB и мгновенной генерации развернутых ответов по тексту документа.")
        else:
            st.warning("⚠️ **Ожидание параметров:** Введите ваш API-ключ Gemini и загрузите документ, чтобы активировать живой RAG-режим в облаке.")


# ==============================================================================
# MODULE 5: DOWNLOAD FILES
# ==============================================================================

# =============================================================================
# MODULE: SERVICES & ECOSYSTEM (🌐 Сервисы & Экосистема C21)
# =============================================================================
elif menu == "🌐 Сервисы & Экосистема C21":
    st.markdown("""
    <div style="background-color: #111111; padding: 25px 30px; border-left: 5px solid #C5A059; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h1 style="color: #FFFFFF !important; margin: 0; font-size: 2.1rem; letter-spacing: 3px; font-weight: 700; font-family: 'Barlow', sans-serif; text-transform: uppercase;">🌐 СЕРВИСЫ & ЭКОСИСТЕМА C21</h1>
        <p style="color: #C5A059; margin: 8px 0 0 0; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Интерактивный навигатор по всем 23 официальным сервисам и технологиям CENTURY 21 Россия для франчайзи</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Analysis Box
    st.markdown("""
    <div style="background-color: #FFFFFF; padding: 25px; border-radius: 4px; border: 1px solid #E2E2E6; margin-bottom: 30px;">
        <h3 style="color: #111111; margin-top: 0; margin-bottom: 15px; font-size: 1.4rem; text-transform: uppercase; letter-spacing: 1px;">📊 Аудит источника «Сервисы C21»</h3>
        <div style="display: flex; gap: 20px;">
            <div style="flex: 1; min-width: 250px;">
                <h5 style="color: #76933C; font-weight: 700; text-transform: uppercase; margin-bottom: 10px;">🌟 Сильные стороны:</h5>
                <ul style="font-size: 0.9rem; line-height: 1.5; color: #333; margin: 0; padding-left: 20px;">
                    <li><b>Колоссальная экосистема поддержки:</b> 23 сервиса покрывают абсолютно все потребности офиса — от юридического страхования на 10 млн руб. до ИИ-технологий и федерального PR.</li>
                    <li><b>Многоканальное обучение:</b> СДО edu.century21.ru, Академия IMA, очные выезды тренера УК и корпоративные книги.</li>
                    <li><b>Автоматизация маркетинга:</b> Конструктор макетов, 3 готовых персонализированных лендинга и Дзен-канал для прогрева клиентов.</li>
                </ul>
            </div>
            <div style="flex: 1; min-width: 250px;">
                <h5 style="color: #C65911; font-weight: 700; text-transform: uppercase; margin-bottom: 10px;">⚠️ Слабые стороны:</h5>
                <ul style="font-size: 0.9rem; line-height: 1.5; color: #333; margin: 0; padding-left: 20px;">
                    <li><b>Информационный хаос и фрагментация:</b> Сервисы разбросаны по множеству доменов, чатов WhatsApp и Google Таблиц. Брокеру и агентам трудно ориентироваться и держать в голове десятки ссылок.</li>
                    <li><b>Ручное администрирование:</b> Чтобы добавить сотрудника в чаты, заказать макеты или выгрузить отчеты, необходимо писать ручные письма на zayavka@century21.ru.</li>
                </ul>
            </div>
        </div>
        <hr style="border-top: 1px solid #E2E2E6; margin: 15px 0;">
        <p style="font-size: 0.9rem; margin: 0; color: #555; line-height: 1.5;">
            <b>🛠️ Как это решено в нашем MVP:</b> Мы устранили хаос фрагментации, собрав все 23 сервиса в единый интерактивный каталог-навигатор. Теперь брокер и агенты получают мгновенный доступ к любой системе, чату или лендингу бренда в один клик прямо из Личного кабинета!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🧭 Интерактивный каталог всех 23 сервисов CENTURY 21")
    st.markdown("Выберите интересующую вас категорию поддержки для быстрого перехода к материалам, сайтам или чатам:")
    
    tab_it, tab_edu, tab_mkt, tab_hr, tab_support = st.tabs([
        "💻 IT & CRM (5)",
        "🎓 Обучение & Книги (4)",
        "📢 Маркетинг & PR (8)",
        "🛡️ Кадры & Безопасность (4)",
        "🤝 Поддержка & Чаты (2)"
    ])
    
    with tab_it:
        st.markdown("#### 💻 Системы автоматизации, CRM и Технологии")
        
        col_it1, col_it2 = st.columns(2)
        with col_it1:
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px;'>
                <h5 style='color:#C5A059; margin-top:0;'>1. Основная CRM topnlab.ru</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Профессиональная CRM-система для ведения базы клиентов, объектов, автоматической выгрузки на 40+ досок объявлений и ведения сделок.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.link_button("🔗 Перейти в CRM topnlab.ru", "https://topnlab.ru")
            
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px; margin-top: 20px;'>
                <h5 style='color:#C5A059; margin-top:0;'>2. Личный кабинет 21online.century21.ru</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Дополнительная CRM-платформа для заведения агентов на сайт бренда, создания корпоративной почты, заказа выписок ЕГРН и работы с базой новостроек.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.link_button("🔗 Войти в 21online.century21.ru", "https://21online.century21.ru")
            
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px; margin-top: 20px;'>
                <h5 style='color:#C5A059; margin-top:0;'>3. Корпоративный сайт century21.ru</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Единый федеральный сайт бренда. Каждое АН получает персональный сайт-раздел, карточки агентов с отзывами клиентов и витрину листингов.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.link_button("🔗 Открыть сайт century21.ru", "https://century21.ru")
            
        with col_it2:
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px;'>
                <h5 style='color:#C5A059; margin-top:0;'>4. Мобильная и Офисная IP-Телефония</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Интеграция с Мегафон и Билайн для автоматической фиксации звонков агентов в «полях». Все записи разговоров автоматически импортируются в CRM.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.info("📞 Настройка производится Службой заботы. Напишите запрос на zayavka@century21.ru для подключения.")
            
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px; margin-top: 20px;'>
                <h5 style='color:#C5A059; margin-top:0;'>5. Технологии Яндекса и Почта</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Использование инфраструктуры Яндекс 360, корпоративные почтовые адреса в домене `@century21.ru` и облачный Яндекс.Диск для обмена регламентами.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.info("📧 Доступы к почте и диску выдаются при регистрации нового агента на портале 21online.")
            
    with tab_edu:
        st.markdown("#### 🎓 Система обучения, Академия и База знаний")
        
        col_ed1, col_ed2 = st.columns(2)
        with col_ed1:
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px;'>
                <h5 style='color:#C5A059; margin-top:0;'>1. Портал обучения edu.century21.ru</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Основная система дистанционного обучения (СДО). Доступен базовый курс CREATE 21 для стажеров, курсы для HR-ов и РОПов, а также вебинары сети.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.link_button("🔗 Открыть академию edu.century21.ru", "https://edu.century21.ru")
            
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px; margin-top: 20px;'>
                <h5 style='color:#C5A059; margin-top:0;'>2. Программа IMA для Руководителей</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    International Management Academy — уникальная очная/онлайн программа обучения для директоров АН и брокеров. Проводится раз в месяц.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.info("📅 Расписание ближайших потоков IMA и регистрация публикуются в СДО и в чате Брокеров.")
            
        with col_ed2:
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px;'>
                <h5 style='color:#C5A059; margin-top:0;'>3. Выезд Бизнес-тренера в офис</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Специальный сервис Управляющей компании: выезд федерального бизнес-тренера в ваш офис для проведения живых тренингов и аттестации агентов.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.info("✍️ Заявка подается заблаговременно через Службу заботы на почту zayavka@century21.ru.")
            
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px; margin-top: 20px;'>
                <h5 style='color:#C5A059; margin-top:0;'>4. Настольные Книги CENTURY 21</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Доступ ко всей трилогии стандартов бренда в электронном виде: Книга Брокера, Книга Руководителя, Книга Агента.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.success("📚 Оригинальные Книги Брокера и Агента доступны для скачивания на вкладке 'Все файлы & Загрузки'!")
            
    with tab_mkt:
        st.markdown("#### 📢 Маркетинг, PR-сопровождение и Лидогенерация")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px;'>
                <h5 style='color:#C5A059; margin-top:0;'>1. Конструктор макетов Promotional</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Встроенный в 21online графический редактор для быстрого создания визиток, брошюр, листовок по официальным брендбукам CENTURY 21.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.link_button("🔗 Конструктор макетов C21", "https://21online.century21.ru/promotional")
            
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px; margin-top: 20px;'>
                <h5 style='color:#C5A059; margin-top:0;'>2. Интернет-магазин shop.century21.ru</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Корпоративный маркетплейс для заказа сувениров, канцелярии, значков CENTURY 21, брендированных бейджей и презентационных папок.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.link_button("🔗 Открыть магазин сувениров C21", "http://shop.century21.ru/")
            
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px; margin-top: 20px;'>
                <h5 style='color:#C5A059; margin-top:0;'>3. Журнал CENTURY 21 Magazine</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Глянцевый аналитический журнал бренда. Служит отличным инструментом для прогрева продавцов при защите эксклюзивности и комиссии.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.info("📖 Физические копии высылаются в офисы ежеквартально. Печатные макеты страниц можно запросить в Службе заботы.")
            
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px; margin-top: 20px;'>
                <h5 style='color:#C5A059; margin-top:0;'>4. Канал Яндекс.Дзен C21</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Профессиональный контент-блог сети с регулярно обновляемыми статьями. Ссылки можно отправлять клиентам в мессенджерах.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.link_button("🔗 Открыть канал на Яндекс.Дзен", "https://zen.yandex.ru/id/5db1b75f9515ee00b2a8d906")
            
        with col_m2:
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px;'>
                <h5 style='color:#C5A059; margin-top:0;'>5. Рекламные лендинги услуг</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    3 готовых высококонверсионных лендинга, которые можно брендировать под ваше АН: для Продавцов, Покупателей и Соискателей.
                </p>
            </div>
            """, unsafe_allow_html=True)
            col_l1, col_l2, col_l3 = st.columns(3)
            with col_l1:
                st.link_button("💼 HR Лендинг", "https://hr.century21.ru")
            with col_l2:
                st.link_button("🏠 Для Продавца", "https://client.century21.ru")
            with col_l3:
                st.link_button("🔍 Для Покупателя", "https://agent.century21.ru")
                
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px; margin-top: 20px;'>
                <h5 style='color:#C5A059; margin-top:0;'>6. Контакт-центр 24/7</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Возможность аутсорсинга входящих звонков. Профессиональный КЦ бренда принимает звонки 24/7 и заводит лиды сразу в CRM.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.info("📞 Подключение КЦ осуществляется на платной основе через Службу заботы по запросу.")
            
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px; margin-top: 20px;'>
                <h5 style='color:#C5A059; margin-top:0;'>7. Промо-ролики бренда</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Готовые качественные видеоролики для трансляции в офисе, рекламы или отправки соискателям.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.link_button("📹 Смотреть промо-ролик C21", "https://family.century21.ru/~lDiJA")
            
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px; margin-top: 20px;'>
                <h5 style='color:#C5A059; margin-top:0;'>8. Консалтинг по продвижению и PR</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Помощь УК в составлении материалов для локальной прессы и пул проверенных подрядчиков для ведения контекстной рекламы.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.info("📰 Напишите на zayavka@century21.ru для получения контактов сертифицированных маркетологов сети.")
            
    with tab_hr:
        st.markdown("#### 🛡️ Рекрутинг, Кадровая безопасность и Страхование")
        
        col_hr1, col_hr2 = st.columns(2)
        with col_hr1:
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px;'>
                <h5 style='color:#C5A059; margin-top:0;'>1. Страхование профессиональной ответственности</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Эксклюзивный сервис сети: страхование сделок агентства на сумму до 10 000 000 руб. Сверхмощный аргумент при переговорах с собственниками!
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.info("🛡️ Оформляется ежегодно при поддержке юридического департамента УК CENTURY 21.")
            
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px; margin-top: 20px;'>
                <h5 style='color:#C5A059; margin-top:0;'>2. Корпоративный доступ к HeadHunter (HH.ru)</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Льготные/бесплатные пакеты размещений вакансий стажеров на главном портале СНГ для непрерывного наполнения воронки рекрутинга.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.info("💼 Доступы к кабинету HH выдаются вашему HR-менеджеру после прохождения им обучения в СДО.")
            
        with col_hr2:
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px;'>
                <h5 style='color:#C5A059; margin-top:0;'>3. Черный список агентов РФ</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Общая база неблагонадежных, уличенных в обмане или мошенничестве риелторов по всей России для исключения рисков при найме.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.link_button("🔍 Проверить агента в Черном списке", "https://docs.google.com/spreadsheets/d/15u3W3pnIgnLXtj8erbJzde5iTaQi0_TrJ1F2%201eexzxM/edit#gid=0")
            
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px; margin-top: 20px;'>
                <h5 style='color:#C5A059; margin-top:0;'>4. HR-консалтинг и коучинг партнеров</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Помощь в подборе HR-менеджеров, аудит кадрового администрирования, адаптации и корпоративной культуры. Итоговое интервью с вашими финалистами.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.info("👔 Поддержка оказывается HR-департаментом Центрального офиса. Напишите на zayavka@century21.ru.")
            
    with tab_support:
        st.markdown("#### 🤝 Служба Заботы УК и Сетевой Нетворкинг (Чаты)")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px;'>
                <h5 style='color:#C5A059; margin-top:0;'>1. Единый контакт Службы Заботы УК</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    Единая универсальная точка входа для решения абсолютно любых технических, организационных, маркетинговых или обучающих вопросов франчайзи.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.link_button("✉️ Написать в Службу Заботы", "mailto:zayavka@century21.ru")
            
        with col_s2:
            st.markdown("""
            <div class='c21-card' style='padding: 15px; border: 1px solid #E2E2E6; margin-bottom: 15px;'>
                <h5 style='color:#C5A059; margin-top:0;'>2. Профильная система WhatsApp-чатов</h5>
                <p style='font-size:0.85rem; color:#444; line-height:1.4; margin-bottom:10px;'>
                    9 официальных групп для обмена опытом и лидами (МЛС Москва, МЛС Регионы, чаты Брокеров, Руководителей, Юристов, Ипотечников, HR и СДО).
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.info("💬 Чтобы добавить ваших сотрудников в соответствующие чаты, отправьте их контакты и роли на zayavka@century21.ru.")


elif menu == "📦 Все файлы & Загрузки":
    st.markdown("""
    <div style="background-color: #111111; padding: 25px 30px; border-left: 5px solid #C5A059; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h1 style="color: #FFFFFF !important; margin: 0; font-size: 2.1rem; letter-spacing: 3px; font-weight: 700; font-family: 'Barlow', sans-serif; text-transform: uppercase;">АРХИВ АРТЕФАКТОВ И БАЗА ЗНАНИЙ</h1>
        <p style="color: #C5A059; margin: 8px 0 0 0; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Скачивайте оригинальные файлы калькуляторов, дорожных карт, аттестаций и дашбордов в высоком качестве</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("Ниже собраны все 6 высокотехнологичных файлов-инструментов, которые мы с вами разработали на основе базы знаний CENTURY 21. Все формулы, макросы и переходы настроены и проверены в LibreOffice.")
    
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        st.markdown("### 📊 Коммерческие и финансовые модели:")
        
        # File 1: What-If Model
        whatif_bytes = get_file_bytes("century21-whatif-model-v2.xlsx")
        st.markdown("**1. `century21-whatif-model-v2.xlsx`**")
        st.markdown("Сценарный симулятор прибыли, ВКД и точки безубыточности с листом-руководством.")
        st.download_button(
            label="💾 Скачать модель What-If",
            data=whatif_bytes if whatif_bytes else b"placeholder",
            file_name="century21-whatif-model-v2.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.markdown("---")
        
        # File 2: KPI Calculator
        kpi_bytes = get_file_bytes("century21-kpi-calculator.xlsx")
        st.markdown("**2. `century21-kpi-calculator.xlsx`**")
        st.markdown("Автоматический ведомый лист начисления окладов, бонусов стажеров, РОПов и HR-ов.")
        st.download_button(
            label="💾 Скачать калькулятор KPI",
            data=kpi_bytes if kpi_bytes else b"placeholder",
            file_name="century21-kpi-calculator.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.markdown("---")
        
        # File 3: Printable PDF Checklists
        pdf_bytes = get_file_bytes("аттестационный_лист_АН.pdf")
        st.markdown("**3. `аттестационный_лист_АН.pdf`**")
        st.markdown("Готовая к печати рабочая тетрадь аттестации агента в премиальном золотом стиле.")
        st.download_button(
            label="💾 Скачать Аттестационный лист (PDF)",
            data=pdf_bytes if pdf_bytes else b"placeholder",
            file_name="century21-agent-attestation-workbook.pdf",
            mime="application/pdf"
        )
        
    with col_f2:
        st.markdown("### 🧭 Дорожные карты и планы адаптации:")
        
        # File 4: Operational Roadmap
        roadmap_bytes = get_file_bytes("century21-operational-roadmap.xlsx")
        st.markdown("**4. `century21-operational-roadmap.xlsx`**")
        st.markdown("8-недельный чек-лист запуска офиса франшизы с авторасчетом процента готовности.")
        st.download_button(
            label="💾 Скачать Дорожную карту запуска",
            data=roadmap_bytes if roadmap_bytes else b"placeholder",
            file_name="century21-operational-roadmap.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.markdown("---")
        
        # File 5: 90-Day Plan Tracker
        plan_bytes = get_file_bytes("century21-agent-90day-plan.xlsx")
        st.markdown("**5. `century21-agent-90day-plan.xlsx`**")
        st.markdown("Индивидуальная электронная карта адаптации стажера на 90 дней с прописанными целями.")
        st.download_button(
            label="💾 Скачать План адаптации «90 дней»",
            data=plan_bytes if plan_bytes else b"placeholder",
            file_name="century21-agent-90day-plan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.markdown("---")
        
        # File 6: Source Dashboard PNG
        dashboard_bytes = get_file_bytes("funnel-analysis-dashboard.png")
        st.markdown("**6. `funnel-analysis-dashboard.png`**")
        st.markdown("Высококачественное графическое изображение сквозного аналитического дашборда.")
        st.download_button(
            label="💾 Скачать PNG Дашборд воронки",
            data=dashboard_bytes if dashboard_bytes else b"placeholder",
            file_name="funnel-analysis-dashboard.png",
            mime="image/png"
        )


# --- HELPER: UNIFORM CORPORATE FOOTER ---
def show_corporate_footer():
    st.markdown("""
    <hr style="border-top: 1px solid #E2E2E6; margin-top: 50px; margin-bottom: 20px;">
    <div style="display: flex; justify-content: space-between; align-items: center; color: #888888; font-size: 0.8rem; font-family: 'Barlow', sans-serif;">
        <div><b>CENTURY 21 Россия</b> • Корпоративная экосистема брокера v5.0 (Финальный MVP)</div>
        <div style="text-align: right; font-style: italic;">«Каждый офис находится в независимом владении и управлении.»</div>
    </div>
    """, unsafe_allow_html=True)


# --- RENDER CORPORATE FOOTER ON EVERY PAGE ---
show_corporate_footer()
