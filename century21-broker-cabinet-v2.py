import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

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
    /* Main Background & Text Color */
    .stApp {
        background-color: #FAFAFA;
        color: #2F2F2F;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] p {
        color: #E6E6E6 !important;
    }
    
    /* Custom headers and text colors */
    h1, h2, h3 {
        color: #1A1A1A !important;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    .brand-gold-text {
        color: #C5A059 !important;
        font-weight: bold;
    }
    .brand-gold-bg {
        background-color: #C5A059 !important;
        color: #1A1A1A !important;
    }
    
    /* Metric Card styling */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    div[data-testid="metric-container"] label {
        color: #666666 !important;
        font-size: 0.9rem !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #1A1A1A !important;
        font-size: 1.8rem !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_with_html=True)

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
<div style="text-align: center; padding: 10px 0px;">
    <h1 style="color: #C5A059 !important; margin: 0; font-size: 1.8rem;">CENTURY 21</h1>
    <p style="color: #888888; font-size: 0.85rem; margin-top: 5px; text-transform: uppercase; letter-spacing: 2px;">Victory Group</p>
</div>
<hr style="border-top: 1px solid #333; margin: 10px 0 20px 0;">
""", unsafe_with_html=True)

menu = st.sidebar.radio(
    "НАВИГАЦИЯ ПО MVP",
    [
        "📊 Главный дашборд & What-If",
        "📈 Калькулятор KPI премий",
        "🗺️ Дорожная карта запуска",
        "🎓 Центр обучения & Адаптации",
        "📦 Все файлы & Загрузки"
    ]
)

st.sidebar.markdown("""
<hr style="border-top: 1px solid #333; margin: 20px 0;">
<div style="padding: 10px; border-radius: 5px; background-color: #252525; text-align: center;">
    <p style="font-size: 0.8rem; margin: 0; color: #C5A059;"><b>Версия MVP: 2.0</b></p>
    <p style="font-size: 0.75rem; margin: 5px 0 0 0; color: #888888;">Интегрированы все 10 продуктов CENTURY 21</p>
</div>
""", unsafe_with_html=True)

# ==============================================================================
# MODULE 1: MAIN DASHBOARD & WHAT-IF SIMULATOR
# ==============================================================================
if menu == "📊 Главный дашборд & What-If":
    st.markdown("""
    # 📊 Главный дашборд & Симулятор <span class="brand-gold-text">What-If</span>
    Сквозная воронка рекрутинга и продаж, совмещенная со сценарным финансовым симулятором.
    """, unsafe_with_html=True)
    
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
        st.markdown("<h4 style='color: #C5A059 !important;'>1. Рекрутинг и Кадры</h4>", unsafe_with_html=True)
        staff_exp = st.slider("Опытные агенты в штате", 1, 30, default_staff_exp)
        recruits_called = st.slider("Обзвон соискателей в месяц", 100, 2000, default_recruits, 50)
        conv_rec_meet = st.slider("Конверсия: Звонок -> Интервью HR (%)", 10.0, 80.0, default_conv_rec * 100.0, 1.0) / 100.0
        conv_meet_class = st.slider("Конверсия: Интервью -> Класс (%)", 10.0, 80.0, default_conv_class * 100.0, 1.0) / 100.0
        conv_class_start = st.slider("Конверсия: Класс -> Старт стажировки (%)", 10.0, 80.0, default_conv_start * 100.0, 1.0) / 100.0
        conv_start_end = st.slider("Конверсия: Выживаемость стажера (>2 нед.) (%)", 5.0, 50.0, default_conv_end * 100.0, 1.0) / 100.0
        
    with col_s2:
        st.markdown("<h4 style='color: #C5A059 !important;'>2. Активность и Продажи</h4>", unsafe_with_html=True)
        calls_per_day = st.slider("Звонков на 1 агента в день (лимит)", 5, 40, default_calls_day)
        working_days = st.slider("Рабочих дней в месяце", 15, 26, 22)
        conv_call_meet = st.slider("Конверсия: Звонок -> Встреча (%)", 2.0, 30.0, default_conv_call_meet * 100.0, 0.5) / 100.0
        conv_meet_ed = st.slider("Конверсия: Встреча -> Экскл. договор (%)", 5.0, 60.0, default_conv_meet_ed * 100.0, 1.0) / 100.0
        conv_ed_deal = st.slider("Конверсия: Договор -> Сделка (%)", 5.0, 60.0, default_conv_ed_deal * 100.0, 1.0) / 100.0
        
    with col_s3:
        st.markdown("<h4 style='color: #C5A059 !important;'>3. Финансовые допущения</h4>", unsafe_with_html=True)
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
        """, unsafe_with_html=True)
        
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
    # 📈 Калькулятор KPI премий всей команды
    Автоматический расчет премий и стипендий для Агентов-новичков, HR-менеджера и РОПа с автопроверкой порогов.
    """, unsafe_with_html=True)
    
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
            """, unsafe_with_html=True)
            
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
            """, unsafe_with_html=True)
            
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
            """, unsafe_with_html=True)

# ==============================================================================
# MODULE 3: Operational Launch Roadmap (8 sprints)
# ==============================================================================
elif menu == "🗺️ Дорожная карта запуска":
    st.markdown("""
    # 🗺️ Дорожная карта запуска офиса франшизы
    8-недельный операционный план запуска агентства недвижимости по стандартам CENTURY 21.
    """, unsafe_with_html=True)
    
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
        {"week": 7, "task": "Утверждение Положения о мотивации и шаблонов договоров", "dept": "Юрист", "pri": "Высокий", "status": "Не начата", "desc": "Официальный регламент деления комиссии и грейдовой сетки агентов Victory."},
        
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
        st.markdown(f"<h3 style='color: #C5A059 !important; margin: 0;'>{progress_percentage:.1f}% ГОТОВНОСТИ ОФИСА</h3>", unsafe_with_html=True)
        
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
    # 🎓 Академия стажеров CENTURY 21
    Полноценный обучающий хаб: интерактивные тесты, карточки возражений, аудио- и видеоподготовка стажера.
    """, unsafe_with_html=True)
    
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
            """, unsafe_with_html=True)
            
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
            """, unsafe_with_html=True)
        elif "большая комиссия" in card:
            st.markdown("""
            <div style="background-color: #FFF2CC; padding: 20px; border-left: 5px solid #F0C13A; border-radius: 4px;">
                <p style="margin: 0; font-weight: bold; color: #856404;">Речевой модуль отработки (скрипт):</p>
                <p style="margin: 10px 0 0 0; font-style: italic; color: #1A1A1A;">
                    «Иван Иванович, размер нашей комиссии полностью оправдан тем объемом работы и рекламного бюджета, который компания инвестирует в ваш объект еще ДО совершения сделки. Мы полностью берем на себя юридическую проверку покупателя, подготовку документов, организацию показов и агрессивный маркетинг на 40+ площадках. По сути, мы гарантируем безопасность и выгоду сделки. Если мы продадим квартиру на 5-10% дороже, чем вы планировали, вы ведь будете согласны оплатить качественную работу?»
                </p>
            </div>
            """, unsafe_with_html=True)
        else:
            st.markdown("""
            <div style="background-color: #FFF2CC; padding: 20px; border-left: 5px solid #F0C13A; border-radius: 4px;">
                <p style="margin: 0; font-weight: bold; color: #856404;">Речевой модуль отработки (скрипт):</p>
                <p style="margin: 10px 0 0 0; font-style: italic; color: #1A1A1A;">
                    «Иван Иванович, эксклюзивный договор — это не ограничение вашей свободы, а гарантия того, что агентство будет вкладывать 100% своих ресурсов и платного маркетинга именно в вашу квартиру. Когда объектом занимаются сразу 5 агентств, никто из них не несет ответственности, и объект обесценивается. При эксклюзиве я лично отвечаю перед вами головой и еженедельно предоставляю отчет о ходе рекламной кампании. Давайте я покажу вам преимущества эксклюзива на встрече?»
                </p>
            </div>
            """, unsafe_with_html=True)

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
# MODULE 5: DOWNLOAD FILES
# ==============================================================================
elif menu == "📦 Все файлы & Загрузки":
    st.markdown("""
    # 📦 Архив готовых расчетных моделей и шаблонов
    Скачивайте проверенные финансовые калькуляторы, дорожные карты и учебные планы на свой компьютер.
    """, unsafe_with_html=True)
    
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
