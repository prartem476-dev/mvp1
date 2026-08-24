import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Настройка страницы
st.set_page_config(
    page_title="CENTURY 21 - Личный кабинет Брокера",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стилизация под бренд CENTURY 21
st.markdown("""
<style>
    /* Основные цвета */
    :root {
        --c21-gold: #C5A059;
        --c21-dark: #1B2A47;
        --c21-light: #F4F6F9;
    }
    .main-title {
        color: #1B2A47;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        border-bottom: 3px solid #C5A059;
        padding-bottom: 10px;
        margin-bottom: 25px;
    }
    .section-header {
        color: #1B2A47;
        font-family: 'Arial', sans-serif;
        border-left: 5px solid #C5A059;
        padding-left: 10px;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-left: 5px solid #C5A059;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .sidebar-brand {
        text-align: center;
        background-color: #1B2A47;
        padding: 15px;
        border-radius: 5px;
        color: #ffffff;
        font-weight: bold;
        border-bottom: 4px solid #C5A059;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #1B2A47 !important;
        color: #ffffff !important;
        border: 1px solid #C5A059 !important;
    }
    .stButton>button:hover {
        background-color: #C5A059 !important;
        color: #1B2A47 !important;
    }
</style>
""", unsafe_allow_html=True)

# Боковая панель навигации
with st.sidebar:
    st.markdown('<div class="sidebar-brand">CENTURY 21<br>Broker Dashboard MVP</div>', unsafe_allow_html=True)
    menu = st.radio(
        "Навигация по модулям:",
        [
            "🏠 Главный дашборд и What-If",
            "🎓 Личный кабинет Агента",
            "💼 Личный кабинет РОПа",
            "🏛️ Организационная структура",
            "📚 База знаний & Материалы"
        ]
    )
    
    st.markdown("---")
    st.info("💡 **Статус MVP:** Подключен расчетный бэкенд на Python. Интегрированы данные из правил мотивации и оргструктуры.")

# ==========================================
# МОДУЛЬ 1: ГЛАВНЫЙ ДАШБОРД И WHAT-IF
# ==========================================
if menu == "🏠 Главный дашборд и What-If":
    st.markdown('<h1 class="main-title">🏠 Интерактивный симулятор "What-If" и Дашборд</h1>', unsafe_allow_html=True)
    st.write("Спрогнозируйте финансовую эффективность вашего офиса, управляя конверсиями продаж, структурой штата и расходами.")

    # Разделение экрана на панель управления и графики
    col_ctrl, col_visual = st.columns([1, 2])

    with col_ctrl:
        st.markdown('<h3 class="section-header">Входные параметры</h3>', unsafe_allow_html=True)
        
        # Сценарии по умолчанию
        scenario = st.selectbox(
            "Выбрать предустановленный сценарий:",
            ["Базовый (Текущий)", "Оптимистичный (Цель)", "Пессимистичный (Риски)"]
        )
        
        # Инициализация параметров в зависимости от сценария
        if scenario == "Базовый (Текущий)":
            agents_exp = 9
            agents_trainee = 8
            calls_per_day = 21
            conv_call_meet = 10.0
            conv_meet_ED = 25.0
            conv_ED_deal = 30.0
            avg_vkd = 150000
            fixed_costs = 195000
        elif scenario == "Оптимистичный (Цель)":
            agents_exp = 14
            agents_trainee = 6
            calls_per_day = 25
            conv_call_meet = 12.0
            conv_meet_ED = 35.0
            conv_ED_deal = 35.0
            avg_vkd = 180000
            fixed_costs = 196000
        else: # Пессимистичный
            agents_exp = 6
            agents_trainee = 4
            calls_per_day = 15
            conv_call_meet = 7.0
            conv_meet_ED = 15.0
            conv_ED_deal = 20.0
            avg_vkd = 120000
            fixed_costs = 210000

        # Слайдеры для ручной регулировки (What-If)
        st.write("**Ручные корректировки сценария:**")
        s_agents_exp = st.slider("Опытные агенты в штате (чел.):", 2, 30, agents_exp)
        s_agents_trainee = st.slider("Агенты-стажеры в штате (чел.):", 0, 20, agents_trainee)
        s_calls_per_day = st.slider("Исходящих звонков на агента в день:", 5, 40, calls_per_day)
        
        st.write("**Конверсии воронки (%):**")
        s_conv_call_meet = st.slider("Звонок ➔ Первая встреча (%):", 1.0, 50.0, conv_call_meet, 0.5)
        s_conv_meet_ED = st.slider("Встреча ➔ Договор (ЭД) (%):", 5.0, 80.0, conv_meet_ED, 0.5)
        s_conv_ED_deal = st.slider("Договор (ЭД) ➔ Сделка (%):", 5.0, 80.0, conv_ED_deal, 0.5)
        
        st.write("**Финансы:**")
        s_avg_vkd = st.number_input("Средняя комиссия (ВКД) со сделки (руб.):", 50000, 500000, avg_vkd, 5000)
        s_fixed_costs = st.number_input("Фиксированные расходы офиса в месяц (руб.):", 50000, 500000, fixed_costs, 5000)

    # Вычисления бэкенда на основе введенных слайдерами параметров
    total_agents = s_agents_exp + s_agents_trainee
    working_days = 22
    total_calls_month = total_agents * s_calls_per_day * working_days
    
    # Расчет по воронке продаж
    total_meetings = total_calls_month * (s_conv_call_meet / 100.0)
    total_contracts = total_meetings * (s_conv_meet_ED / 100.0)
    total_deals = total_contracts * (s_conv_ED_deal / 100.0)
    
    # Финансовый результат
    projected_vkd = total_deals * s_avg_vkd
    marketing_costs_per_object = 6000
    variable_marketing = total_contracts * marketing_costs_per_object
    cpa_recruitment = 150
    calls_recruitment_needed = 500
    recruitment_marketing = calls_recruitment_needed * cpa_recruitment
    
    total_opex = s_fixed_costs + variable_marketing + recruitment_marketing
    net_profit = projected_vkd - total_opex
    margin_pct = (net_profit / projected_vkd * 100.0) if projected_vkd > 0 else 0.0
    roi_pct = (net_profit / total_opex * 100.0) if total_opex > 0 else 0.0

    # Расчет безубыточности
    # ВКД на сделку за вычетом переменного маркетинга на сделку
    # Переменный маркетинг на сделку = маркетинг на ЭД (6000) / конверсия ЭД->сделка
    marketing_per_deal = marketing_costs_per_object / (s_conv_ED_deal / 100.0)
    contribution_margin_per_deal = s_avg_vkd - marketing_per_deal
    
    # Постоянные затраты включают фикс офиса + фикс маркетинг найма
    total_fixed_costs = s_fixed_costs + recruitment_marketing
    
    if contribution_margin_per_deal > 0:
        be_deals = total_fixed_costs / contribution_margin_per_deal
        be_vkd = be_deals * s_avg_vkd
        margin_of_safety = ((total_deals - be_deals) / total_deals * 100.0) if total_deals > 0 else -100.0
    else:
        be_deals = float('inf')
        be_vkd = float('inf')
        margin_of_safety = -100.0

    with col_visual:
        st.markdown('<h3 class="section-header">Ключевые показатели эффективности (KPI)</h3>', unsafe_allow_html=True)
        
        # Информационные карточки KPI
        card_col1, card_col2, card_col3, card_col4 = st.columns(4)
        with card_col1:
            st.markdown(f"""
            <div class="metric-card">
                <small>ЗВОНКОВ В МЕСЯЦ</small>
                <h3>{total_calls_month:,.0f}</h3>
                <small style="color:gray;">Штат: {total_agents} чел.</small>
            </div>
            """, unsafe_allow_html=True)
        with card_col2:
            st.markdown(f"""
            <div class="metric-card">
                <small>СДЕЛОК ЗАКРЫТО</small>
                <h3>{total_deals:.1f}</h3>
                <small style="color:gray;">ЭД в работе: {total_contracts:.1f}</small>
            </div>
            """, unsafe_allow_html=True)
        with card_col3:
            st.markdown(f"""
            <div class="metric-card">
                <small>ПРОГНОЗ ВКД</small>
                <h3>{projected_vkd:,.0f} ₽</h3>
                <small style="color:gray;">Ср. чек: {s_avg_vkd:,.0f} ₽</small>
            </div>
            """, unsafe_allow_html=True)
        with card_col4:
            color = "green" if net_profit > 0 else "red"
            st.markdown(f"""
            <div class="metric-card" style="border-left: 5px solid {color};">
                <small>ЧИСТАЯ ПРИБЫЛЬ</small>
                <h3 style="color:{color};">{net_profit:,.0f} ₽</h3>
                <small style="color:gray;">Маржинальность: {margin_pct:.1f}%</small>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<h3 class="section-header">Визуализация воронки продаж и финансовой прочности</h3>', unsafe_allow_html=True)
        
        # Отрисовка интерактивной воронки через Plotly
        funnel_data = dict(
            number=[total_calls_month, total_meetings, total_contracts, total_deals],
            stage=["Звонки", "Встречи", "Эксклюзивные договоры", "Сделки"]
        )
        fig_funnel = px.funnel(funnel_data, x='number', y='stage', color_discrete_sequence=['#C5A059'])
        fig_funnel.update_layout(title="Конверсионная воронка отдела продаж", height=300, margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig_funnel, use_container_width=True)

        # Вывод результатов анализа безубыточности
        st.markdown('<h3 class="section-header">Анализ безубыточности (Break-Even Analysis)</h3>', unsafe_allow_html=True)
        be_col1, be_col2, be_col3 = st.columns(3)
        
        with be_col1:
            st.metric("Точка безубыточности (в сделках)", f"{be_deals:.1f} сделок")
        with be_col2:
            st.metric("Точка безубыточности (оборот ВКД)", f"{be_vkd:,.0f} ₽")
        with be_col3:
            status_text = "✅ ОФИС ПРИБЫЛЕН" if margin_of_safety > 0 else "❌ ОФИС В УБЫТКЕ"
            st.metric("Запас финансовой прочности", f"{margin_of_safety:.1f}%", help="Процент, на который текущие продажи могут упасть до достижения точки безубыточности.")
            if margin_of_safety > 0:
                st.success(status_text)
            else:
                st.error(status_text)

# ==========================================
# МОДУЛЬ 2: ЛИЧНЫЙ КАБИНЕТ АГЕНТА
# ==========================================
elif menu == "🎓 Личный кабинет Агента":
    st.markdown('<h1 class="main-title">🎓 Личный кабинет Агента (Система Грейдов)</h1>', unsafe_allow_html=True)
    st.write("Изучите систему грейдов CENTURY 21 Victory, проверьте выполнение нормативов привлечения и рассчитайте комиссионное вознаграждение.")

    # Описание грейдов из источника "Мотивация агентов"
    st.markdown('<h3 class="section-header">Карьерная сетка и плановые грейды</h3>', unsafe_allow_html=True)
    
    grades_df = pd.DataFrame({
        "Грейд": ["Стажер", "Агент", "Эксперт", "Ведущий эксперт"],
        "Базовая ставка комиссии": ["30%", "35%", "40%", "50%"],
        "Ставка при сверхобъеме": ["30%", "45%", "50%", "60%"],
        "Квартальный план ВКД": ["Нет", "300 000 ₽", "400 000 ₽", "500 000 ₽"],
        "План привлечения (клиенты/мес.)": [2, 3, 3, 3],
        "Условие для перехода (сделки)": ["Старт", "3 закрытые сделки", "10 закрытых сделок", "20 закрытых сделок"]
    })
    st.table(grades_df)

    # Интерактивный калькулятор агента
    st.markdown('<h3 class="section-header">Интерактивный калькулятор вознаграждения агента</h3>', unsafe_allow_html=True)
    
    calc_col1, calc_col2 = st.columns(2)
    with calc_col1:
        agent_grade = st.selectbox(
            "Ваш текущий грейд:",
            ["Стажер (без оклада)", "Стажер (на окладе)", "Агент", "Эксперт", "Ведущий эксперт"]
        )
        
        if agent_grade == "Стажер (на окладе)":
            st.warning("⚠️ **Внимание:** Вы выбрали окладную модель (30 000 ₽: 15к оклад + 15к KPI). Ваша комиссия снижена до **20%**.")
            base_comm = 20.0
            over_comm = 20.0
            monthly_attract_plan = 2
        elif agent_grade == "Стажер (без оклада)":
            base_comm = 30.0
            over_comm = 30.0
            monthly_attract_plan = 2
        elif agent_grade == "Агент":
            base_comm = 35.0
            over_comm = 45.0
            monthly_attract_plan = 3
        elif agent_grade == "Эксперт":
            base_comm = 40.0
            over_comm = 50.0
            monthly_attract_plan = 3
        else: # Ведущий эксперт
            base_comm = 50.0
            over_comm = 60.0
            monthly_attract_plan = 3

        actual_attract = st.number_input("Сколько клиентов вы привлекли в этом месяце?", 0, 10, value=monthly_attract_plan)
        vkd_earned = st.number_input("Ваш личный валовый доход (ВКД) по закрытым сделкам за месяц (руб.):", 0, 1500000, value=150000, step=10000)
        
        # Дисциплинарные штрафы за пропуск плана привлечения
        applied_commission = base_comm
        penalty_msg = ""
        if actual_attract < monthly_attract_plan:
            applied_commission -= 3.0
            penalty_msg = f"❌ **Штраф:** План привлечения не выполнен ({actual_attract} из {monthly_attract_plan}). Комиссия на следующий месяц снижена на 3% и составит **{applied_commission}%**!"
            
    with calc_col2:
        st.write("**Результаты расчета премий:**")
        
        # Расчет итоговых выплат
        is_overachiever = False
        # Предполагаем перевыполнение, если ВКД больше 1/3 квартального плана
        quarterly_plans = {"Агент": 300000, "Эксперт": 400000, "Ведущий эксперт": 500000}
        if agent_grade in quarterly_plans:
            monthly_threshold = quarterly_plans[agent_grade] / 3
            if vkd_earned > monthly_threshold:
                is_overachiever = True
                
        final_rate = over_comm if is_overachiever else base_comm
        
        # Если стажер на окладе
        bonus_payout = vkd_earned * (final_rate / 100.0)
        
        if agent_grade == "Стажер (на окладе)":
            kpi_payout = 15000 if actual_attract >= monthly_attract_plan else (15000 * (actual_attract / monthly_attract_plan))
            total_earned = 15000 + kpi_payout + bonus_payout
            st.info(f"💵 **Окладная часть:** 15 000 ₽")
            st.info(f"🎯 **KPI по привлечению:** {kpi_payout:,.0f} ₽")
        else:
            total_earned = bonus_payout
            st.info(f"📈 **Применяемая ставка комиссии:** {final_rate}%" + (" (Повышенная за объемы)" if is_overachiever else ""))

        st.metric("Итого выплата за месяц (к начислению):", f"{total_earned:,.0f} ₽")
        
        if penalty_msg:
            st.error(penalty_msg)
        else:
            st.success("✅ **Отличный результат!** План привлечения выполнен. Ставка на следующий месяц сохранена в полном объеме.")

# ==========================================
# МОДУЛЬ 3: ЛИЧНЫЙ КАБИНЕТ РОПа
# ==========================================
elif menu == "💼 Личный кабинет РОПа":
    st.markdown('<h1 class="main-title">💼 Личный кабинет РОПа (Премии & Мотивация)</h1>', unsafe_allow_html=True)
    st.write("Модуль автоматического расчета комплексной мотивации Руководителя Отдела Продаж на основе показателей подчиненных.")

    # Правила РОПа из "Мотивация руководителей"
    st.markdown('<h3 class="section-header">Система начисления вознаграждений РОПа</h3>', unsafe_allow_html=True)
    st.write("""
    1. **Фиксированная часть:** **35 000 рублей** в месяц.
    2. **Процент со сделок стажеров (первые 3 сделки):** зависит от своевременности сделок по бизнес-плану:
       * **Вовремя:** **20%** комиссии
       * **Опоздание на 1 месяц:** **15%** комиссии
       * **Опоздание на 2 месяца:** **10%** комиссии
       * **Опоздание на 3 месяца:** **5%** комиссии
    3. **Процент со сделок опытных агентов:**
       * **Выполнение планов отдела > 80%:** **10%** от ВКД опытных агентов
       * **Выполнение планов отдела < 80%:** **7%** от ВКД опытных агентов
    *Примечание:* Сотрудники, не проявлявшие активность (проработавшие менее 14 дней в месяце), исключаются из расчета плана отдела.
    """)

    # Расчет премий РОПа
    st.markdown('<h3 class="section-header">Интерактивный расчет дохода РОПа</h3>', unsafe_allow_html=True)
    
    rop_col1, rop_col2 = st.columns(2)
    with rop_col1:
        st.write("**Параметры стажеров в подчинении:**")
        num_trainee_deals = st.number_input("Количество закрытых первых сделок стажерами в этом месяце:", 0, 10, value=2)
        
        trainee_vkd_list = []
        trainee_status_list = []
        for i in range(num_trainee_deals):
            st.write(f"**Сделка стажера №{i+1}:**")
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                v = st.number_input(f"ВКД по сделке стажера {i+1} (руб.):", 50000, 300000, value=120000, key=f"t_v_{i}")
                trainee_vkd_list.append(v)
            with sub_col2:
                s = st.selectbox(f"Соблюдение сроков стажером {i+1}:", ["Вовремя (20%)", "Опоздание на 1 мес. (15%)", "Опоздание на 2 мес. (10%)", "Опоздание на 3 мес. (5%)"], key=f"t_s_{i}")
                trainee_status_list.append(s)
        
        st.write("**Параметры отдела опытных агентов:**")
        active_agents = st.number_input("Количество опытных агентов (активных более 14 дней в месяце):", 1, 30, value=5)
        planned_vkd_agents = st.number_input("Плановый совокупный ВКД по опытным агентам (руб.):", 100000, 3000000, value=600000)
        actual_vkd_agents = st.number_input("Фактический совокупный ВКД по опытным агентам (руб.):", 0, 3000000, value=500000)

    with rop_col2:
        st.write("**Результаты расчета для РОПа:**")
        
        # 1. Фикс
        fixed_salary = 35000
        st.info(f"💵 **Базовый оклад РОПа:** {fixed_salary:,.0f} ₽")
        
        # 2. Бонус со стажеров
        total_trainee_bonus = 0.0
        for i in range(num_trainee_deals):
            status = trainee_status_list[i]
            if "Вовремя" in status:
                rate = 0.20
            elif "1 мес" in status:
                rate = 0.15
            elif "2 мес" in status:
                rate = 0.10
            else:
                rate = 0.05
            bonus_item = trainee_vkd_list[i] * rate
            total_trainee_bonus += bonus_item
        st.info(f"👶 **Итого бонус со сделок стажеров:** {total_trainee_bonus:,.0f} ₽")
        
        # 3. Бонус со сделок опытных агентов
        plan_met_pct = (actual_vkd_agents / planned_vkd_agents * 100.0) if planned_vkd_agents > 0 else 0.0
        
        if plan_met_pct >= 80.0:
            override_rate = 10.0
            override_payout = actual_vkd_agents * 0.10
            status_override = f"🔥 **Выполнение плана отдела: {plan_met_pct:.1f}% (>= 80%)**. Применена ставка **10%**!"
        else:
            override_rate = 7.0
            override_payout = actual_vkd_agents * 0.07
            status_override = f"⚠️ **Выполнение плана отдела: {plan_met_pct:.1f}% (< 80%)**. Ставка снижена до **7%**!"
            
        st.info(f"🚀 **Итого бонус с опытных агентов:** {override_payout:,.0f} ₽")
        
        # Вывод вердикта по проценту РОПа
        if plan_met_pct >= 80.0:
            st.success(status_override)
        else:
            st.warning(status_override)
            
        # Общий итог
        total_rop_payout = fixed_salary + total_trainee_bonus + override_payout
        st.metric("СУММАРНЫЙ НАЧИСЛЕННЫЙ ДОХОД РОПа ЗА МЕСЯЦ:", f"{total_rop_payout:,.0f} ₽")

# ==========================================
# МОДУЛЬ 4: ОРГАНИЗАЦИОННАЯ СТРУКТУРА
# ==========================================
elif menu == "🏛️ Организационная структура":
    st.markdown('<h1 class="main-title">🏛️ Динамическая организационная структура фирмы</h1>', unsafe_allow_html=True)
    st.write("Интерактивная карта распределения ролей в агентстве недвижимости CENTURY 21 в зависимости от стадии масштабирования бизнеса.")

    # Выбор фазы развития на основе "Организационная структура АН"
    phase = st.selectbox(
        "Выберите фазу развития вашего агентства:",
        [
            "Фаза 1: Start-Up (один РОС/РОП, до 5 стажеров/агентов)",
            "Фаза 2: Активный рост (РОП + РОС разделены, 10-15 сотрудников)",
            "Фаза 3: Сегментированное Агентство (отдельные группы по направлениям, 25+ сотрудников)"
        ]
    )

    if phase == "Фаза 1: Start-Up (один РОС/РОП, до 5 стажеров/агентов)":
        st.markdown('<h3 class="section-header">Организационная карта: Фаза Start-Up</h3>', unsafe_allow_html=True)
        st.info("💡 **Рекомендация по масштабированию:** Брокер временно совмещает роль Директора. Поддерживающие функции (Юрист, Бухгалтер) вынесены на **аутсорсинг** для минимизации постоянных затрат.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            **Руководство и Администрация:**
            *   👨‍💼 **Директор (Брокер):** Стратегическое управление
            *   👩‍💻 **Офис-менеджер:** Рецепция, административные задачи
            """)
        with col2:
            st.markdown("""
            **Коммерческий блок (Совмещенный):**
            *   🎓 **РОП/РОС (1 человек):** Адаптация новичков и координация сделок экспертов
            *   👥 **Штат:** 3 Агента + 2 Стажера
            """)
        with col3:
            st.markdown("""
            **Внешние сервисы (Аутсорсинг):**
            *   ⚖️ **Аутсорс-Юрист:** Юридическая проверка и сопровождение сделок
            *   🧮 **Аутсорс-Бухгалтер:** Налоги, расчеты
            """)
            
    elif phase == "Фаза 2: Активный рост (РОП + РОС разделены, 10-15 сотрудников)":
        st.markdown('<h3 class="section-header">Организационная карта: Фаза Активного Роста</h3>', unsafe_allow_html=True)
        st.info("💡 **Рекомендация по масштабированию:** Управленческий контур расширяется. Появился выделенный **HR-специалист** для ведения воронки рекрутинга. Функции РОСа и РОПа разделены для качественного ввода стажеров.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            **Руководство и Администрация:**
            *   👨‍💼 **Директор (Брокер):** Бизнес-процессы, франшиза
            *   👩‍💼 **HR-Менеджер:** Системный наем соискателей
            *   👩‍💻 **Офис-менеджер:** Административный блок
            """)
        with col2:
            st.markdown("""
            **Коммерческий блок (Разделенный):**
            *   🎓 **РОС (Руководитель отдела стажеров):** Обучение, тренинги, вывод на первые сделки
            *   🚀 **РОП (Руководитель отдела продаж):** Работа с опытными агентами-экспертами
            *   👥 **Штат:** 8 Агентов + 6 Стажеров
            """)
        with col3:
            st.markdown("""
            **Внешние сервисы:**
            *   ⚖️ **Штатный Юрист:** Полное погружение в сделки компании
            *   🧮 **Аутсорс-Бухгалтер:** Ведение финансовой отчетности
            """)

    else: # Фаза 3: Корпорация
        st.markdown('<h3 class="section-header">Организационная карта: Сегментированная структура</h3>', unsafe_allow_html=True)
        st.info("💡 **Рекомендация по масштабированию:** Офис сегментируется по направлениям рынка (Вторичный рынок, Первичная/Загородная недвижимость). Бухгалтерия полностью вводится в штат.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            **Руководство и Администрация:**
            *   👨‍💼 **Генеральный Директор (Брокер)**
            *   👥 **HR-Отдел (2 человека):** Массовый наем
            *   👩‍💻 **Рецепция и Бэк-офис:** 2 администратора
            """)
        with col2:
            st.markdown("""
            **Коммерческий блок (Сегментированный):**
            *   🎓 **РОС:** Ведет стажерские группы (первые 90 дней)
            *   🏢 **РОП 1 (Вторичный рынок):** Группа из 12 экспертов
            *   🏗️ **РОП 2 (Новостройки/Загородный рынок):** Группа из 10 экспертов
            *   👥 **Совокупный штат:** 22 Агента + 10 Стажеров
            """)
        with col3:
            st.markdown("""
            **Внутренние службы безопасности:**
            *   ⚖️ **Юридический отдел:** 2 юриста (сопровождение сделок)
            *   🧮 **Штатный Бухгалтер:** Внутренний финансовый учет
            """)

    # Схема масштабирования оргструктуры
    st.markdown('<h3 class="section-header">Триггеры найма персонала при масштабировании</h3>', unsafe_allow_html=True)
    triggers_data = {
        "Текущая численность отдела": ["До 5 агентов", "От 8 агентов", "От 15 агентов", "От 25 агентов"],
        "Критическое действие брокера": [
            "Привлечь Юриста и Бухгалтера на аутсорсинг",
            "Нанять HR-специалиста для организации воронки найма соискателей",
            "Разделить роли РОПа и РОСа. Вывести РОСа на обучение стажеров",
            "Сегментировать отделы на Вторичный / Первичный рынок. Ввести бухгалтера в штат"
        ]
    }
    st.table(pd.DataFrame(triggers_data))

# ==========================================
# МОДУЛЬ 5: БАЗА ЗНАНИЙ & МАТЕРИАЛЫ
# ==========================================
else:
    st.markdown('<h1 class="main-title">📚 База знаний & Материалы MVP</h1>', unsafe_allow_html=True)
    st.write("Все оцифрованные, интерактивные и аналитические материалы, которые мы создали для экосистемы CENTURY 21 в одном месте.")

    st.markdown("""
    В ходе проектирования MVP мы полностью переработали ключевые текстовые инструкции бренда в **10 цифровых рабочих инструментов**, доступных для скачивания или взаимодействия на боковой панели:
    """)

    # Карточки материалов
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown("""
        ### 📊 Аналитические и Расчетные инструменты (Excel/PNG)
        1. **`funnel-analysis-dashboard.png`** — Профессиональный аналитический дашборд воронки рекрутинга и продаж в фирменном стиле.
        2. **`century21-whatif-model-v2.xlsx`** — Интерактивная Excel-модель What-If анализа для РОПа с автоматическим расчетом безубыточности и запаса финансовой прочности.
        3. **`century21-kpi-calculator.xlsx`** — Умный расчетный лист KPI премий для Агентов, HR и РОПа с автопроверкой лимитов.
        4. **`century21-operational-roadmap.xlsx`** — Дорожная карта запуска франшизы по 8 недельным спринтам.
        5. **`century21-agent-90day-plan.xlsx`** — Цифровой учебный трекер адаптации новичка «Первые 90 дней».
        """)
    with m_col2:
        st.markdown("""
        ### 🎓 Обучающие и Аттестационные инструменты (App/PDF)
        6. **`аттестационный_лист_АН.pdf`** — Презентабельный печатный шаблон аттестационной тетради стажера с оценочными чек-боксами.
        7. **Интерактивный тест (Quiz) CENTURY 21** — Находится на вашей панели Studio. Тест-опросник на знание стандартов бренда и регламента курса CREATE 21.
        8. **Интерактивные карточки (Flashcards)** — Расположены в панели Studio. Предназначены для тренировки навыков проработки возражений собственников.
        9. **Аудиоподкаст «Детский врач»** — Аудио-брифинг в формате живого диалога для быстрого вовлечения агента в стандарты проспектинга.
        10. **Видеообзор «Цикл успешной сделки»** — Вовлекающий экскурс в бизнес-архитектуру сделки CENTURY 21 для брокеров.
        """)

    st.success("🎉 **Поздравляем!** Все 10 артефактов успешно синхронизированы в вашей панели Studio и готовы к работе.")
