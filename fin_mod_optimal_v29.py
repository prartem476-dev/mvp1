import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io

# Проверяем доступность openpyxl для экспорта в Excel без падения приложения
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    openpyxl_available = True
except ImportError:
    openpyxl_available = False

# Установка конфигурации страницы
st.set_page_config(
    page_title="CENTURY 21 Financial Model (Бюджет Оптимальный) v24",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# ПОМОЩНИКИ ДЛЯ РУЧНЫХ КОРРЕКТИРОВОК P&L, ДРАЙВЕРОВ И КАДРОВ
# ----------------------------------------------------
# Initialize session state for detailed driver conversions/ratios
if 'start_driver_leads_per_agent' not in st.session_state:
    st.session_state['start_driver_leads_per_agent'] = 60.0
if 'start_driver_meetings_pct' not in st.session_state:
    st.session_state['start_driver_meetings_pct'] = 10.0
if 'start_driver_contracts_pct' not in st.session_state:
    st.session_state['start_driver_contracts_pct'] = 15.0
if 'start_driver_prepayments_pct' not in st.session_state:
    st.session_state['start_driver_prepayments_pct'] = 70.0
if 'start_driver_secondary_pct' not in st.session_state:
    st.session_state['start_driver_secondary_pct'] = 90.0
if 'start_driver_primary_pct' not in st.session_state:
    st.session_state['start_driver_primary_pct'] = 10.0
if 'start_driver_rent_val' not in st.session_state:
    st.session_state['start_driver_rent_val'] = 3.0
if 'start_driver_suburban_val' not in st.session_state:
    st.session_state['start_driver_suburban_val'] = 0.0
if 'start_driver_overseas_val' not in st.session_state:
    st.session_state['start_driver_overseas_val'] = 0.0
if 'start_driver_other_pct' not in st.session_state:
    st.session_state['start_driver_other_pct'] = 0.5
if 'start_driver_mortgage_pct' not in st.session_state:
    st.session_state['start_driver_mortgage_pct'] = 17.0
if 'start_driver_insurance_pct' not in st.session_state:
    st.session_state['start_driver_insurance_pct'] = 10.0
if 'start_driver_legal_pct' not in st.session_state:
    st.session_state['start_driver_legal_pct'] = 17.0

# Initialize commissions in session state
if 'comm_secondary' not in st.session_state:
    st.session_state['comm_secondary'] = 360000.0
if 'comm_primary' not in st.session_state:
    st.session_state['comm_primary'] = 440000.0
if 'comm_rent_val' not in st.session_state:
    st.session_state['comm_rent_val'] = 80000.0
if 'comm_suburban' not in st.session_state:
    st.session_state['comm_suburban'] = 500000.0
if 'comm_overseas' not in st.session_state:
    st.session_state['comm_overseas'] = 220000.0
if 'comm_other_p' not in st.session_state:
    st.session_state['comm_other_p'] = 252000.0
if 'comm_mortgage' not in st.session_state:
    st.session_state['comm_mortgage'] = 70000.0
if 'comm_insurance' not in st.session_state:
    st.session_state['comm_insurance'] = 18000.0
if 'comm_legal' not in st.session_state:
    st.session_state['comm_legal'] = 150000.0

if 'rate_agent_D' not in st.session_state: st.session_state['rate_agent_D'] = 35.0
if 'rate_agent_C' not in st.session_state: st.session_state['rate_agent_C'] = 40.0
if 'rate_agent_B' not in st.session_state: st.session_state['rate_agent_B'] = 45.0
if 'rate_agent_A' not in st.session_state: st.session_state['rate_agent_A'] = 50.0

if 'rate_rop_C_bonus' not in st.session_state: st.session_state['rate_rop_C_bonus'] = 3.0
if 'rate_rop_B_bonus' not in st.session_state: st.session_state['rate_rop_B_bonus'] = 12.0
if 'rate_admin_bonus' not in st.session_state: st.session_state['rate_admin_bonus'] = 10.0

if 'rate_hr_bonus' not in st.session_state: st.session_state['rate_hr_bonus'] = 4500.0
if 'rate_ros_bonus' not in st.session_state: st.session_state['rate_ros_bonus'] = 50000.0
if 'rate_jurist_bonus' not in st.session_state: st.session_state['rate_jurist_bonus'] = 5.0
if 'rate_mort_bonus' not in st.session_state: st.session_state['rate_mort_bonus'] = 10.0
if 'rate_listing_bonus' not in st.session_state: st.session_state['rate_listing_bonus'] = 500.0
if 'rate_photo_bonus' not in st.session_state: st.session_state['rate_photo_bonus'] = 30000.0
if 'rate_smm_bonus' not in st.session_state: st.session_state['rate_smm_bonus'] = 150000.0

if 'sal_rop_C' not in st.session_state: st.session_state['sal_rop_C'] = 70000.0
if 'sal_rop_B' not in st.session_state: st.session_state['sal_rop_B'] = 100000.0
if 'sal_admin' not in st.session_state: st.session_state['sal_admin'] = 70000.0
if 'sal_hr' not in st.session_state: st.session_state['sal_hr'] = 100000.0
if 'sal_ros' not in st.session_state: st.session_state['sal_ros'] = 100000.0
if 'sal_jurist' not in st.session_state: st.session_state['sal_jurist'] = 150000.0
if 'sal_mort' not in st.session_state: st.session_state['sal_mort'] = 180000.0
if 'sal_listing' not in st.session_state: st.session_state['sal_listing'] = 50000.0
if 'sal_smm' not in st.session_state: st.session_state['sal_smm'] = 150000.0
if 'sal_photo' not in st.session_state: st.session_state['sal_photo'] = 30000.0

if 'taxes_payroll_rate' not in st.session_state: st.session_state['taxes_payroll_rate'] = 43.0

if 'opex_internet' not in st.session_state: st.session_state['opex_internet'] = 5000.0
if 'opex_mobile' not in st.session_state: st.session_state['opex_mobile'] = 600.0
if 'opex_kanc' not in st.session_state: st.session_state['opex_kanc'] = 500.0
if 'opex_reklama' not in st.session_state: st.session_state['opex_reklama'] = 7000.0
if 'opex_hh' not in st.session_state: st.session_state['opex_hh'] = 45000.0
if 'opex_buh' not in st.session_state: st.session_state['opex_buh'] = 20000.0
if 'opex_bank' not in st.session_state: st.session_state['opex_bank'] = 2000.0
if 'opex_cleaning' not in st.session_state: st.session_state['opex_cleaning'] = 15000.0
if 'opex_gsm' not in st.session_state: st.session_state['opex_gsm'] = 5000.0
if 'opex_courier' not in st.session_state: st.session_state['opex_courier'] = 10000.0
if 'opex_events' not in st.session_state: st.session_state['opex_events'] = 10000.0
if 'opex_rent_price_m2' not in st.session_state: st.session_state['opex_rent_price_m2'] = 2500.0
if 'opex_db_services' not in st.session_state: st.session_state['opex_db_services'] = 0.0

if 'role_active' not in st.session_state:
    st.session_state['role_active'] = {
        'Агент: категория D': True,
        'Агент: категория C': True,
        'Агент: категория B': True,
        'Агент: категория A': True,
        'РОП: категория C': True,
        'РОП: категория B': True,
        'Администратор офиса': True,
        'HR/рекрутер': True,
        'РОС/тренер': True,
        'Юрист': True,
        'Ипотечный Брокер': True,
        'Листинг-менеджер': True,
        'Фотограф': True,
        'Маркетолог/SMM': True
    }

if 'pl_overrides' not in st.session_state:
    st.session_state['pl_overrides'] = {}
if 'add_rop_m3' not in st.session_state:
    st.session_state['add_rop_m3'] = False
if 'add_admin_m6' not in st.session_state:
    st.session_state['add_admin_m6'] = False
if 'driver_overrides' not in st.session_state:
    st.session_state['driver_overrides'] = {}
if 'headcount_overrides' not in st.session_state:
    st.session_state['headcount_overrides'] = {}
if 'prepayment_rate' not in st.session_state:
    st.session_state['prepayment_rate'] = 70.0
if 'secondary_ratio' not in st.session_state:
    st.session_state['secondary_ratio'] = 90.0
if 'conversion_meeting' not in st.session_state:
    st.session_state['conversion_meeting'] = 10.0
if 'conversion_deal' not in st.session_state:
    st.session_state['conversion_deal'] = 15.0
if 'capex_pau_fee' not in st.session_state:
    st.session_state['capex_pau_fee'] = 577500.0  # Moscow by default
if 'capex_rospatent' not in st.session_state:
    st.session_state['capex_rospatent'] = 17000.0
if 'capex_office_area' not in st.session_state:
    st.session_state['capex_office_area'] = 60.0
if 'capex_norm_m2' not in st.session_state:
    st.session_state['capex_norm_m2'] = 6.0
if 'capex_workstations' not in st.session_state:
    st.session_state['capex_workstations'] = 10
if 'capex_renov_price' not in st.session_state:
    st.session_state['capex_renov_price'] = 10000.0
if 'capex_brand_price' not in st.session_state:
    st.session_state['capex_brand_price'] = 2000.0
if 'capex_table_price' not in st.session_state:
    st.session_state['capex_table_price'] = 12000.0
if 'capex_stool_price' not in st.session_state:
    st.session_state['capex_stool_price'] = 7000.0
if 'capex_computer_price' not in st.session_state:
    st.session_state['capex_computer_price'] = 45000.0
if 'capex_add_furniture' not in st.session_state:
    st.session_state['capex_add_furniture'] = 150000.0
if 'capex_router_printer' not in st.session_state:
    st.session_state['capex_router_printer'] = 25000.0

def get_override(metric_name, col_name, default_val):
    key = (metric_name, col_name)
    if key in st.session_state['pl_overrides']:
        return st.session_state['pl_overrides'][key]
    return default_val

def get_driver_override(driver_name, col_name, default_val):
    key = (driver_name, col_name)
    if key in st.session_state['driver_overrides']:
        return st.session_state['driver_overrides'][key]
    return default_val

def get_headcount_override(role_name, col_name, default_val):
    key = (role_name, col_name)
    if key in st.session_state['headcount_overrides']:
        return st.session_state['headcount_overrides'][key]
    return default_val

def parse_value(val):
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).replace(' ', '').replace('₽', '').replace(',', '.').strip()
    if s == "" or s == "-" or s == "0":
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0

def fmt(v, is_header_row=False):
    if is_header_row or v is None or v == "":
        return ""
    if isinstance(v, str):
        return v
    try:
        return f"{float(v):,.0f} ₽".replace(",", " ")
    except (ValueError, TypeError):
        return str(v)


# ----------------------------------------------------
# АВТОРИЗАЦИЯ ПОЛЬЗОВАТЕЛЯ
# ----------------------------------------------------
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    # Beautiful custom styling for login
    st.markdown("""
    <style>
        /* Импорт шрифта */
        @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600;700;800&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #FFFFFF;
            color: #252526;
        }
        
        .login-title {
            color: #252526;
            font-size: 26px;
            font-weight: 800;
            text-align: center;
            margin-top: 10px;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .brand-accent {
            color: #BEAF87; /* Relentless Gold */
        }
        .login-sub {
            color: #808285; /* Medium Grey */
            font-size: 14px;
            text-align: center;
            margin-bottom: 30px;
        }
        div.stButton > button {
            background-color: #BEAF87 !important;
            color: #FFFFFF !important;
            font-weight: bold !important;
            border: none !important;
            border-radius: 5px !important;
            padding: 12px 24px !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            box-shadow: 0 2px 5px rgba(190, 175, 135, 0.3) !important;
        }
        div.stButton > button:hover {
            background-color: #A19276 !important; /* Dark Gold */
            box-shadow: 0 4px 12px rgba(161, 146, 118, 0.5) !important;
            transform: translateY(-1px);
        }
        
        /* Контейнер для монограммы с соблюдением охранного поля 0.5X */
        .brand-monogram-container {
            display: block;
            margin: 35px auto; /* Охранное поле 0.5X для монограммы высотой 70px */
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Встраиваем монограмму C21 согласно Brandbook (в один цвет Relentless Gold, с охранным полем 0.5X)
        st.markdown("""
        <div class="brand-monogram-container">
            <svg viewBox="0 0 100 100" width="70" height="70" style="display: block; margin: 0 auto;">
                <path d="M 75,25 A 35,35 0 1,0 75,75" fill="none" stroke="#BEAF87" stroke-width="8" stroke-linecap="round" />
                <text x="48" y="59" font-family="'Segoe UI', Arial, sans-serif" font-weight="bold" font-size="26" fill="#BEAF87" text-anchor="middle">21</text>
            </svg>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='login-title'>CENTURY 21 <span class='brand-accent'>Financial MVP</span></div>", unsafe_allow_html=True)
        st.markdown("<div class='login-sub'>Интерактивная финансовая модель | Кейс: Бюджет Оптимальный</div>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center; color: #252526; font-weight: 700; margin-bottom: 20px;'>Вход в личный кабинет</h4>", unsafe_allow_html=True)
            username = st.text_input("Логин", placeholder="Введите имя пользователя")
            password = st.text_input("Пароль", type="password", placeholder="Введите ваш пароль")
            
            st.markdown("<div style='margin-top: 20px;'>", unsafe_allow_html=True)
            if st.button("Войти в систему"):
                if username == "admin" and password == "c21admin":
                    st.session_state['authenticated'] = True
                    st.success("Успешная авторизация! Загрузка модели...")
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль. Попробуйте еще раз.")
            st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

# Пользовательский CSS-стилинг в корпоративных цветах Century 21 (Premium Light Theme)
st.markdown("""
<style>
    /* Импорт шрифта */
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Segoe UI', Arial, sans-serif;
        background-color: #FFFFFF;
        color: #252526;
    }
    
    /* Стилизация боковой панели */
    [data-testid="stSidebar"] {
        background-color: #E6E7E8 !important;
        border-right: 1px solid #D3D3D3;
        padding-top: 20px;
    }
    
    [data-testid="stSidebar"] * {
        color: #252526 !important;
    }
    
    /* Красивые карточки KPI */
    div[data-testid="stMetric"] {
        background-color: #F8F9FA;
        border: 1px solid #E6E7E8;
        border-left: 5px solid #BEAF87;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    div[data-testid="stMetric"] label {
        color: #777779 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #252526 !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        margin-top: 5px;
    }
    
    /* Кнопки */
    div.stButton > button {
        background-color: #BEAF87 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 5px rgba(190, 175, 135, 0.3) !important;
        width: 100% !important;
    }
    
    div.stButton > button:hover {
        background-color: #A19276 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(161, 146, 118, 0.5) !important;
        transform: translateY(-1px);
    }
    
    /* Заголовки */
    .main-title {
        color: #252526;
        font-size: 30px;
        font-weight: 800;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 5px;
        letter-spacing: 0.5px;
    }
    
    .brand-accent {
        color: #A19276;
    }
    
    .sub-title {
        color: #777779;
        font-size: 15px;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 400;
    }
    
    /* Вкладки */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #E6E7E8;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #F8F9FA;
        border: 1px solid #E6E7E8;
        border-bottom: none;
        border-radius: 6px 6px 0px 0px;
        padding: 10px 24px;
        color: #777779;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #A19276 !important;
        border-top: 3px solid #BEAF87 !important;
        border-left: 1px solid #BEAF87 !important;
        border-right: 1px solid #BEAF87 !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# ОПРЕДЕЛЕНИЕ ДАННЫХ ЛИСТА "БЮДЖЕТ ОПТИМАЛЬНЫЙ" (C21)
# ----------------------------------------------------

months = [str(i) for i in range(1, 25)]

optimal_baseline = {
    'leads': [440, 880, 1320, 1760, 2200, 2640, 3080, 3520, 3960, 4400, 4840, 5280,
              6160, 6600, 7040, 7480, 7920, 8360, 8800, 9240, 9680, 10120, 10560, 11000],
    'meetings': [44, 88, 132, 176, 220, 264, 308, 352, 396, 440, 484, 528,
                 616, 660, 704, 748, 792, 836, 880, 924, 968, 1012, 1056, 1100],
    'contracts': [0, 2, 4, 7, 9, 11, 13, 15, 18, 20, 22, 24,
                  26, 31, 33, 35, 37, 40, 42, 44, 46, 48, 51, 53],
    'prepayments': [0.0, 1.5, 3.0, 5.3, 6.8, 8.3, 9.8, 11.3, 13.5, 15.0, 16.5, 18.0,
                    19.5, 23.3, 24.8, 26.3, 27.8, 30.0, 31.5, 33.0, 34.5, 36.0, 38.3, 39.8],
    
    # Декомпозиция ДОХОДОВ (ВКД)
    'rev_sec': [0, 0, 0, 360000, 1080000, 1603800, 2138400, 2673000, 3207600, 3742200, 4276800, 4811400,
                5346000, 5880600, 6415200, 7484400, 8019000, 8553600, 9088200, 9622800, 10157400, 10692000, 11226600, 11761200],
    'rev_prim': [0, 0, 0, 440000, 440000, 440000, 440000, 880000, 880000, 880000, 880000, 880000,
                 653400, 718740, 784080, 914760, 980100, 1045440, 1110780, 1176120, 1241460, 1306800, 1372140, 1437480],
    'rev_rent': [0, 0, 0, 0, 0, 80000, 0, 0, 80000, 0, 0, 80000,
                 240000, 240000, 280000, 280000, 320000, 320000, 360000, 400000, 440000, 440000, 480000, 480000],
    'rev_sub': [0, 0, 0, 0, 0, 500000, 0, 0, 500000, 0, 0, 500000,
                1000000, 1000000, 1000000, 1000000, 1500000, 1500000, 2000000, 2000000, 2500000, 2500000, 2500000, 2500000],
    'rev_overseas': [0]*17 + [220000] + [0]*4 + [220000] + [0],
    'rev_other_p': [0]*12 + [75600]*12,
    'rev_mort': [0]*8 + [106029, 123701, 141372, 159044, 176715, 194387, 212058, 247401, 265073, 282744, 300416, 318087, 335759, 353430, 371102, 388773],
    'rev_ins': [0]*8 + [27265, 31809, 36353, 40897, 45441, 49985, 54529, 63617, 68162, 72706, 77250, 81794, 86338, 90882, 95426, 99970],
    'rev_legal': [0]*6 + [138600, 161700, 184800, 207900, 231000, 254100, 277200, 323400, 346500, 369600, 392700, 415800, 438900, 462000, 485100, 508200, 531300, 554400],
    'revenue': [0, 0, 0, 800000, 1520000, 2623800, 2717000, 3714700, 4985694, 4985609, 5565525, 6725440,
                7814356, 8482712, 9167967, 10435378, 11620634, 12485890, 13451145, 14136401, 15321656, 15966912, 16872168, 17297423],

    # Декомпозиция РАСХОДОВ - ФОТ
    'salaries': [214935, 214935, 214935, 214935, 214935, 144935, 144935, 144935, 144935, 144935, 144935, 144935,
                 963068, 964023, 966913, 1126564, 1129454, 1462344, 1608235, 1611125, 1764015, 1766905, 1769796, 1772686],
    'salary_taxes': [44935]*12 + [143068, 144023, 146913, 156564, 159454, 162344, 208235, 211125, 214015, 216905, 219796, 222686],
    'agent_comm': [0, 0, 0, 338500, 612100, 1053409, 1314265, 1784222, 2332633, 2318694, 2629481, 3171647,
                   4103166, 4502709, 4855674, 5449734, 6035280, 6593359, 7120893, 7473269, 8061122, 8387655, 8822681, 9066321],

    # Декомпозиция OPEX
    'opex': [150000, 286300, 321300, 357400, 393500, 464600, 535700, 606800, 677900, 749000, 820100, 896200,
             569750, 601530, 769250, 1136970, 809690, 827910, 851130, 868850, 892070, 1399290, 927010, 944730],

    # Декомпозиция ВЫПЛАТ ЦО
    'hq_royalty_fix': [0, 0, 0, 45675, 45675, 45675, 45675, 78750, 78750, 78750, 78750, 78750,
                       111825, 111825, 111825, 111825, 111825, 111825, 111825, 111825, 111825, 111825, 111825, 111825],
    'hq_royalty_deal': [0, 0, 0, 4200, 8400, 13556, 14574, 19793, 25011, 26030, 29148, 34367,
                        39134, 42564, 45994, 52855, 58385, 61816, 67346, 70776, 76307, 79737, 83167, 86598],
    'hq_crm_and_others': [19400, 5500, 5500, 68375, 72575, 77731, 78749, 117043, 188908, 201034, 215260, 231587,
                          194303, 191657, 195549, 202872, 208864, 278757, 218749, 222641, 228634, 232526, 302418, 240311],
    'capex': [0]*24
}

# Реальные базовые оклады backoffice специалистов для расчета при изменении кадровой структуры
BASE_SALARY_RATES = {
    'РОП: категория C': 70000.0,
    'РОП: категория B': 100000.0,
    'Администратор офиса': 70000.0,
    'HR/рекрутер': 100000.0,
    'РОС/тренер': 100000.0,
    'Юрист': 150000.0,
    'Ипотечный Брокер': 180000.0,
    'Листинг-менеджер': 50000.0,
    'Фотограф': 30000.0,
    'Маркетолог/SMM': 150000.0
}

# Дефолтная структура штатного расписания (чел.) по месяцам
DEFAULT_HEADCOUNTS = {
    'РОП: категория C': [1]*12 + [1]*12,
    'РОП: категория B': [0]*12 + [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    'Администратор офиса': [0]*12 + [1]*12,
    'HR/рекрутер': [1]*12 + [2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3],
    'РОС/тренер': [0]*12 + [1]*12,
    'Юрист': [0]*12 + [1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3],
    'Ипотечный Брокер': [0]*12 + [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2],
    'Листинг-менеджер': [0]*12 + [1]*12,
    'Фотограф': [1]*12 + [1]*12,
    'Маркетолог/SMM': [0]*5 + [1]*7 + [0]*5 + [1]*7,
    
    # Агенты
    'Агент: категория D': [1, 2, 3, 4, 5, 5, 6, 7, 8, 9, 9, 10] + [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    'Агент: категория C': [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1] + [4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 7, 7],
    'Агент: категория B': [0]*10 + [1, 1] + [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3],
    'Агент: категория A': [0]*12 + [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2]
}

# Операционные драйверы (базовые массивы из Excel)
base_deals_rent = [3, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 3, 3, 4, 4, 4, 4, 5, 5, 6, 6, 6, 6]
base_deals_suburban = [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 2, 2, 2, 2, 3, 3, 4, 4, 5, 5, 5, 5]
base_deals_overseas = [0]*14 + [1] + [0]*4 + [1] + [0] + [2, 1, 0]
base_deals_other = [0]*12 + [0.3]*12
base_services_mortgage = [0]*8 + [1.5, 1.8, 2.0, 2.3] + [3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6]
base_services_insurance = [0]*8 + [1.5, 1.8, 2.0, 2.3] + [3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6]
base_services_legal = [0]*6 + [0.9, 1.1, 1.2, 1.4, 1.5, 1.7] + [2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4]

# Региональные параметры и пресеты
REGIONAL_PRESETS = {
    "Москва": {
        "pau_fee": 577500,
        "comm_sec": 360000,
        "comm_prim": 440000,
        "comm_sub": 500000,
        "comm_rent": 80000,
        "rent_base": 150000,
        "salary_mult": 1.0,
        "royalty_fix_factor": 1.0,
        "royalty_deal": 2100,
    },
    "Московская область (МО)": {
        "pau_fee": 500000,
        "comm_sec": 280000,
        "comm_prim": 330000,
        "comm_sub": 400000,
        "comm_rent": 60000,
        "rent_base": 100000,
        "salary_mult": 0.85,
        "royalty_fix_factor": 0.85,
        "royalty_deal": 2000,
    },
    "Крупные города (население > 800к)": {
        "pau_fee": 450000,
        "comm_sec": 220000,
        "comm_prim": 260000,
        "comm_sub": 320000,
        "comm_rent": 45000,
        "rent_base": 80000,
        "salary_mult": 0.75,
        "royalty_fix_factor": 0.75,
        "royalty_deal": 2000,
    },
    "Средние города (население 400к - 800к)": {
        "pau_fee": 350000,
        "comm_sec": 160000,
        "comm_prim": 200000,
        "comm_sub": 240000,
        "comm_rent": 35000,
        "rent_base": 55000,
        "salary_mult": 0.60,
        "royalty_fix_factor": 0.60,
        "royalty_deal": 1800,
    },
    "Малые города (население < 400к)": {
        "pau_fee": 270000,
        "comm_sec": 110000,
        "comm_prim": 140000,
        "comm_sub": 180000,
        "comm_rent": 25000,
        "rent_base": 38000,
        "salary_mult": 0.45,
        "royalty_fix_factor": 0.45,
        "royalty_deal": 1500,
    }
}

# ----------------------------------------------------
# ШАПКА ПРИЛОЖЕНИЯ
# ----------------------------------------------------
st.markdown("<div class='main-title'>💼 CENTURY 21 <span class='brand-accent'>Optimal Budget Case</span></div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Интерактивная финансовая модель и декомпозиция доходов/расходов на основе листа «Бюджет Оптимальный»</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# БОКОВАЯ ПАНЕЛЬ С УПРАВЛЕНИЕМ & ТУЛТИПАМИ
# ----------------------------------------------------
st.sidebar.markdown("""
<div style='text-align: center; margin: 30px auto; display: block;'>
    <svg viewBox="0 0 100 100" width="60" height="60" style="display: block; margin: 0 auto;">
        <path d="M 75,25 A 35,35 0 1,0 75,75" fill="none" stroke="#252526" stroke-width="8" stroke-linecap="round" />
        <text x="48" y="59" font-family="'Segoe UI', Arial, sans-serif" font-weight="bold" font-size="26" fill="#252526" text-anchor="middle">21</text>
    </svg>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<h2 style='color:#252526; text-align:center; font-weight:800; margin-top: 10px;'>Управление моделью</h2>", unsafe_allow_html=True)

if st.sidebar.button("🔓 Выйти из системы", use_container_width=True):
    st.session_state['authenticated'] = False
    st.rerun()

st.sidebar.markdown("---")

# Регион
region_select = st.sidebar.selectbox(
    "🌍 Выберите регион / тип города:",
    options=list(REGIONAL_PRESETS.keys()),
    help="Каждый пресет автоматически настраивает средние чеки сделок, стоимость аренды офиса, оклады бэк-офиса и fixed-роялти франшизы под экономический уровень выбранной территории."
)
preset = REGIONAL_PRESETS[region_select]

# Sync pau_fee if region select changed
if 'last_region_select' not in st.session_state or st.session_state['last_region_select'] != region_select:
    st.session_state['last_region_select'] = region_select
    st.session_state['capex_pau_fee'] = float(preset["pau_fee"])
    st.session_state['comm_secondary'] = float(preset["comm_sec"])
    st.session_state['comm_primary'] = float(preset["comm_prim"])
    st.session_state['comm_suburban'] = float(preset["comm_sub"])
    st.session_state['comm_rent_val'] = float(preset["comm_rent"])

# Фиксированный сценарий "Бюджет Оптимальный"
st.sidebar.info("📌 **Выбран кейс: Бюджет Оптимальный (Интенсивный старт)**\\n\\nДанный кейс моделирует агрессивный запуск с первого месяца: в Месяце 0 производится закупка оборудования и ремонт офиса на сумму 1 335 000 ₽, а воронка масштабируется на базе 440 базовых лидов на старте с выходом на 11 000 лидов к 24 месяцу.")

st.sidebar.markdown("### 🎚️ Настройки калибровки")

# Разделы параметров
with st.sidebar.expander("📈 1. Конверсии и Воронка", expanded=True):
    conversion_meeting = st.slider(
        "Конверсия лид -> встреча, %",
        min_value=2.0, max_value=20.0, value=st.session_state.get('conversion_meeting', 10.0), step=0.5,
        help="Какая часть позвонивших клиентов доходит до личной встречи в офисе. Базовый корпоративный стандарт Century 21 составляет 10%.",
        key="sb_conversion_meeting_widget"
    )
    st.session_state['conversion_meeting'] = conversion_meeting
    
    conversion_deal = st.slider(
        "Конверсия встреча -> договор, %",
        min_value=1.0, max_value=30.0, value=st.session_state.get('conversion_deal', 15.0), step=0.5,
        help="Эффективность работы агентов при переговорах. Показывает долю встреч, переходящих в подписанные эксклюзивные договоры. Базовый уровень равен 15%.",
        key="sb_conversion_deal_widget"
    )
    st.session_state['conversion_deal'] = conversion_deal
    
    prepayment_rate = st.slider(
        "Конверсия договор -> задаток, %",
        min_value=10.0, max_value=100.0, value=st.session_state.get('prepayment_rate', 70.0), step=1.0,
        help="Какая часть договоров переходит в задаток/аванс. Базовый стандарт сети — 70%.",
        key="sb_prepayment_rate_widget"
    )
    st.session_state['prepayment_rate'] = prepayment_rate
    
    secondary_ratio = st.slider(
        "Доля вторички от задатков, %",
        min_value=0.0, max_value=100.0, value=st.session_state.get('secondary_ratio', 90.0), step=1.0,
        help="Доля сделок вторичного рынка. Оставшаяся часть автоматически распределяется на первичный рынок.",
        key="sb_secondary_ratio_widget"
    )
    st.session_state['secondary_ratio'] = secondary_ratio
    primary_ratio = 100.0 - secondary_ratio
    st.markdown(f"**🏗️ Доля первички от задатков:** `{primary_ratio:.1f}%` (авто-расчет)")

with st.sidebar.expander("💰 2. Средние комиссии", expanded=False):
    comm_secondary = st.number_input(
        "Вторичный рынок, ₽", min_value=50000, max_value=1000000, value=preset["comm_sec"], step=10000,
        help="Средний комиссионный доход агентства с одной сделки купли-продажи на вторичном рынке недвижимости."
    )
    comm_primary = st.number_input(
        "Первичный рынок, ₽", min_value=50000, max_value=1000000, value=preset["comm_prim"], step=10000,
        help="Средняя комиссия, получаемая от девелоперов за продажу новостройки."
    )
    comm_suburban = st.number_input(
        "Загородная недвижимость, ₽", min_value=50000, max_value=1000000, value=preset["comm_sub"], step=10000,
        help="Средний комиссионный чек со сделок по загородным домам, коттеджам и участкам."
    )
    comm_rent_val = st.number_input(
        "Аренда (жилая/коммерческая), ₽", min_value=10000, max_value=200000, value=preset["comm_rent"], step=5000,
        help="Комиссионный доход со сделок аренды жилой и коммерческой недвижимости."
    )

with st.sidebar.expander("👥 3. Персонал и Выплаты", expanded=False):
    agent_commission_pct = st.slider(
        "Средний % выплат агентам", min_value=25, max_value=60, value=38, step=1,
        help="Средний процент от комиссии по сделкам, выплачиваемый агентам. Отражает мотивационную сетку Century 21 (35%-50% в зависимости от категории)."
    )
    backoffice_salary_mult = st.slider(
        "Индекс окладов бэк-офиса, % к базе", min_value=50, max_value=150, value=100, step=5,
        help="Шкала фиксированных окладов бэк-офиса (РОП, HR/рекрутер, юрист, ипотечный брокер, листинг-менеджер, администратор)."
    )

with st.sidebar.expander("🏢 4. OPEX и Налоги", expanded=False):
    office_rent_custom = st.number_input(
        "Аренда офиса в месяц, ₽", min_value=10000, max_value=500000, value=preset["rent_base"], step=5000,
        help="Стоимость аренды офисного помещения. Применяются поправки на ранних этапах запуска офиса."
    )
    tax_rate = st.sidebar.slider(
        "Ставка налога УСН, %", min_value=3, max_value=15, value=7, step=1,
        help="Действующая налоговая ставка по УСН (доходы) с учетом региональных субсидий и льгот."
    )
    marketing_mult = st.slider(
        "Реклама и маркетинг, % к базе", min_value=50, max_value=200, value=100, step=10,
        help="Регулирует объем затрат на рекламу объектов и лидогенерацию."
    )

with st.sidebar.expander("🛠️ 5. Регулировка CAPEX", expanded=False):
    st.markdown("**💸 Регистрация и Паушальный:**")
    st.number_input("Паушальный взнос, ₽", min_value=150000, max_value=1500000, key="sb_pau_fee_widget", value=int(st.session_state['capex_pau_fee']), step=10000)
    st.session_state['capex_pau_fee'] = float(st.session_state.sb_pau_fee_widget)
    
    st.number_input("Роспатент, ₽", min_value=1000, max_value=100000, key="sb_rospatent_widget", value=int(st.session_state['capex_rospatent']), step=1000)
    st.session_state['capex_rospatent'] = float(st.session_state.sb_rospatent_widget)
    
    st.markdown("**🏢 Помещение офиса:**")
    st.slider("Площадь офиса, м²", min_value=40, max_value=140, key="sb_office_area_widget", value=int(st.session_state['capex_office_area']), step=5)
    st.session_state['capex_office_area'] = float(st.session_state.sb_office_area_widget)
    
    st.slider("Норма м² на человека", min_value=4.0, max_value=12.0, key="sb_norm_m2_widget", value=float(st.session_state['capex_norm_m2']), step=0.5)
    st.session_state['capex_norm_m2'] = float(st.session_state.sb_norm_m2_widget)
    
    st.markdown("**💻 Рабочие места:**")
    st.number_input("Количество мест (чел.)", min_value=5, max_value=50, key="sb_workstations_widget", value=int(st.session_state['capex_workstations']), step=1)
    st.session_state['capex_workstations'] = int(st.session_state.sb_workstations_widget)
    
    st.markdown("---")
    st.info("💡 *Вы можете настроить все цены (ремонт за метр, стол, стул, ПК и др.) в отдельном режиме 'Калькулятор CAPEX'!*")

with st.sidebar.expander("🏢 6. Выплаты в ЦО", expanded=False):
    royalty_deal_custom = st.number_input(
        "Роялти за каждую сделку, ₽", min_value=1000, max_value=5000, value=preset["royalty_deal"], step=100,
        help="Фиксированный роялти за сделку. По умолчанию зафиксирован на уровне 2 100 ₽."
    )

# ----------------------------------------------------
# ВЫЧИСЛИТЕЛЬНОЕ ЯДРО МОДЕЛИ (Декомпозиция Оптимальный)
# ----------------------------------------------------
base = optimal_baseline.copy()
salary_mult = preset["salary_mult"]
royalty_fix_mult = preset["royalty_fix_factor"]

# Инициализация всех массивов
adj_leads = []
adj_meetings = []
adj_contracts = []
adj_prepayments = []

rev_secondary_list = []
rev_primary_list = []
rev_rent_list = []
rev_suburban_list = []
rev_overseas_list = []
rev_other_p_list = []
rev_mortgage_list = []
rev_insurance_list = []
rev_legal_list = []
rev_total_list = []

# Декомпозированный ФОТ
agent_D_list = []
agent_C_list = []
agent_B_list = []
agent_A_list = []
payouts_agents_list = []

rop_C_list = []
rop_B_list = []
admin_list = []
hr_list = []
ros_list = []
jurist_list = []
mort_broker_list = []
listing_list = []
photographer_list = []
smm_list = []
salaries_backoffice_list = []

taxes_payroll_list = []
total_payroll_list = []

# Расходы - OPEX
rent_list = []
internet_list = []
mobile_list = []
kanc_list = []
reklama_list = []
hh_list = []
buh_list = []
bank_list = []
cleaning_list = []
gsm_list = []
courier_list = []
events_list = []
total_opex_list = []

# Выплаты ЦО
hq_royalty_fix_list = []
hq_royalty_deal_list = []
hq_crm_list = []
hq_kc_list = []
total_hq_payments_list = []

taxes_usn_list = []
capex_franchise_list = [0]*24
capex_renovation_list = [0]*24
capex_equipment_list = [0]*24
total_capex_list = []
adj_net_profit = []

capex_renovation_list[14] = 520000
capex_equipment_list[14] = 815000
capex_equipment_list[19] = 790000

# No global leads_mult or overall_voeronka_factor needed

base_internet = [5000]*12 + [950]*12
base_mobile = [7800]*2 + [8400] + [9000] + [9600] + [10200] + [10800] + [11400] + [12000] + [12600] + [13200] + [13800] + [18000] + [18480] + [19800] + [21120] + [22440] + [23760] + [25080] + [26400] + [27720] + [29040] + [30360] + [31680]
base_rent_list = [150000]*12 + [150000]*2 + [300000]*10
base_kanc = [6500]*2 + [7000] + [7500] + [8000] + [8500] + [9000] + [9500] + [10000] + [10500] + [11000] + [11500] + [15000] + [15500] + [16500] + [17500] + [18500] + [20000] + [21500] + [22500] + [24000] + [24500] + [25500] + [26500]
base_reklama = [35000] + [70000] + [105000] + [140000] + [210000] + [280000] + [350000] + [420000] + [490000] + [560000] + [630000] + [700000] + [184800] + [215600] + [231000] + [246400] + [261800] + [277200] + [292600] + [308000] + [323400] + [338800] + [354200] + [369600]
base_hh = [45000]*12 + [90000]*12
base_buh = [20000]*12 + [40000]*12
base_bank = [2000]*12 + [6000]*12
base_cleaning = [15000]*12 + [45000]*12
base_gsm = [0]*10 + [5000]*2 + [10000]*4 + [15000]*2 + [20000]*2 + [25000]*4
base_courier = [0]*11 + [10000]*13

base_events = [0]*24
base_events[11] = 100000
base_events[15] = 350000
base_events[21] = 490000

# Load dynamically synchronized variables from session state
scaling_leads = float(st.session_state.get('scaling_leads', 100.0))
leads_mult = scaling_leads / 100.0

conversion_meeting = float(st.session_state.get('start_driver_meetings_pct', 10.0))
conversion_deal = float(st.session_state.get('start_driver_contracts_pct', 15.0))
prepayment_rate = float(st.session_state.get('start_driver_prepayments_pct', 70.0))
secondary_ratio = float(st.session_state.get('start_driver_secondary_pct', 90.0))
primary_ratio = float(st.session_state.get('start_driver_primary_pct', 10.0))

conv_meet_rate = conversion_meeting / 10.0
conv_deal_rate = conversion_deal / 5.0
overall_voeronka_factor = leads_mult * conv_meet_rate * conv_deal_rate

comm_secondary = float(st.session_state.get('comm_secondary', preset["comm_sec"]))
comm_primary = float(st.session_state.get('comm_primary', preset["comm_prim"]))
comm_suburban = float(st.session_state.get('comm_suburban', preset["comm_sub"]))
comm_rent_val = float(st.session_state.get('comm_rent_val', preset["comm_rent"]))
comm_overseas = float(st.session_state.get('comm_overseas', 220000.0))
comm_other_p = float(st.session_state.get('comm_other_p', 252000.0))
comm_mortgage = float(st.session_state.get('comm_mortgage', 70000.0))
comm_insurance = float(st.session_state.get('comm_insurance', 18000.0))
comm_legal = float(st.session_state.get('comm_legal', 150000.0))

for i in range(24):
    # Fetch agents categories for Month i (Month i is i+1 in st.session_state)
    ag_D_count = get_headcount_override('  ├─ Агент: категория D', str(i+1), DEFAULT_HEADCOUNTS['Агент: категория D'][i])
    ag_C_count = get_headcount_override('  ├─ Агент: категория C', str(i+1), DEFAULT_HEADCOUNTS['Агент: категория C'][i])
    ag_B_count = get_headcount_override('  ├─ Агент: категория B', str(i+1), DEFAULT_HEADCOUNTS['Агент: категория B'][i])
    ag_A_count = get_headcount_override('  └─ Агент: категория A', str(i+1), DEFAULT_HEADCOUNTS['Агент: категория A'][i])
    total_agents_i = ag_D_count + ag_C_count + ag_B_count + ag_A_count
    
    # 1. Лиды и воронка
    default_leads_m = 60 * total_agents_i
    L = int(get_driver_override('  ├─ Звонки/лиды', str(i+1), default_leads_m))
    adj_leads.append(L)
    
    default_meetings_m = int(L * (conversion_meeting / 100.0))
    meetings = int(get_driver_override('  ├─ Встречи', str(i+1), default_meetings_m))
    adj_meetings.append(meetings)
    
    default_contracts_m = int(meetings * (conversion_deal / 100.0))
    contracts = int(get_driver_override('  ├─ Договоры', str(i+1), default_contracts_m))
    adj_contracts.append(contracts)
    
    default_prepayments_m = contracts * (prepayment_rate / 100.0)
    prepayments = float(get_driver_override('  ├─ Задаток/аванс', str(i+1), default_prepayments_m))
    adj_prepayments.append(prepayments)
    
    # Сделки в штуках (динамические по умолчанию)
    default_deals_sec_vol = prepayments * (secondary_ratio / 100.0)
    deals_sec_vol = float(get_driver_override('  ├─ Сделки: вторичный рынок', str(i+1), default_deals_sec_vol))
    
    default_deals_prim_vol = prepayments * (primary_ratio / 100.0)
    deals_prim_vol = float(get_driver_override('  ├─ Сделки: первичный рынок', str(i+1), default_deals_prim_vol))
    
    deals_rent_vol = float(get_driver_override('  ├─ Сделки: аренда', str(i+1), base_deals_rent[i]))
    deals_sub_vol = float(get_driver_override('  ├─ Сделки: загородная', str(i+1), base_deals_suburban[i]))
    deals_overseas_vol = float(get_driver_override('  ├─ Сделки: зарубежная', str(i+1), base_deals_overseas[i]))
    
    total_transactions_m = deals_sec_vol + deals_prim_vol + deals_rent_vol + deals_sub_vol + deals_overseas_vol
    default_deals_other_vol = total_transactions_m * 0.005
    deals_other_vol = float(get_driver_override('  ├─ Сделки: прочее (МЛС, срочновыкуп, сайт)', str(i+1), default_deals_other_vol))
    
    default_serv_mort_vol = contracts * 0.17
    serv_mort_vol = float(get_driver_override('  ├─ Сервисы: ипотека', str(i+1), default_serv_mort_vol))
    
    default_serv_ins_vol = contracts * 0.10
    serv_ins_vol = float(get_driver_override('  ├─ Сервисы: страхование', str(i+1), default_serv_ins_vol))
    
    default_serv_legal_vol = contracts * 0.17
    serv_legal_vol = float(get_driver_override('  └─ Сервисы: юр. сопровождение', str(i+1), default_serv_legal_vol))
    # 2. ДОХОДЫ (Рассчитываются динамически по умолчанию для всех месяцев 1-24)
    rev_sec = get_override('  ├─ Вторичный рынок', str(i+1), deals_sec_vol * comm_secondary)
    rev_prim = get_override('  ├─ Первичный рынок', str(i+1), deals_prim_vol * comm_primary)
    rev_rent = get_override('  ├─ Аренда (жилая/коммерческая)', str(i+1), deals_rent_vol * comm_rent_val)
    rev_sub = get_override('  ├─ Загородная недвижимость', str(i+1), deals_sub_vol * comm_suburban)
    rev_overseas = get_override('  ├─ Зарубежная недвижимость', str(i+1), deals_overseas_vol * comm_overseas)
    rev_other_p = get_override('  ├─ Сделки: прочее (МЛС, срочновыкуп)', str(i+1), deals_other_vol * comm_other_p)
    rev_mort = get_override('  ├─ Сервисы: ипотека', str(i+1), serv_mort_vol * comm_mortgage)
    rev_ins = get_override('  ├─ Сервисы: страхование', str(i+1), serv_ins_vol * comm_insurance)
    rev_legal = get_override('  └─ Сервисы: юр. сопровождение', str(i+1), serv_legal_vol * comm_legal)
        
    rev_secondary_list.append(rev_sec)
    rev_primary_list.append(rev_prim)
    rev_rent_list.append(rev_rent)
    rev_suburban_list.append(rev_sub)
    rev_overseas_list.append(rev_overseas)
    rev_other_p_list.append(rev_other_p)
    rev_mortgage_list.append(rev_mort)
    rev_insurance_list.append(rev_ins)
    rev_legal_list.append(rev_legal)
    
    total_revenue_month = rev_sec + rev_prim + rev_rent + rev_sub + rev_overseas + rev_other_p + rev_mort + rev_ins + rev_legal
    rev_total_list.append(total_revenue_month)
    
    # 3. РАСХОДЫ - ФОТ АГЕНТЫ
    # Proportional deal commission based on headcount and custom rates
    total_comm_revenue_month = rev_sec + rev_prim + rev_rent + rev_sub + rev_overseas + rev_other_p
    
    rev_share_D = total_comm_revenue_month * (ag_D_count / total_agents_i) if total_agents_i > 0 else 0.0
    rev_share_C = total_comm_revenue_month * (ag_C_count / total_agents_i) if total_agents_i > 0 else 0.0
    rev_share_B = total_comm_revenue_month * (ag_B_count / total_agents_i) if total_agents_i > 0 else 0.0
    rev_share_A = total_comm_revenue_month * (ag_A_count / total_agents_i) if total_agents_i > 0 else 0.0
    
    agent_D_val_def = rev_share_D * (st.session_state.get('rate_agent_D', 35.0) / 100.0) if st.session_state.get('role_active', {}).get('Агент: категория D', True) else 0.0
    agent_C_val_def = rev_share_C * (st.session_state.get('rate_agent_C', 40.0) / 100.0) if st.session_state.get('role_active', {}).get('Агент: категория C', True) else 0.0
    agent_B_val_def = rev_share_B * (st.session_state.get('rate_agent_B', 45.0) / 100.0) if st.session_state.get('role_active', {}).get('Агент: категория B', True) else 0.0
    agent_A_val_def = rev_share_A * (st.session_state.get('rate_agent_A', 50.0) / 100.0) if st.session_state.get('role_active', {}).get('Агент: категория A', True) else 0.0
    
    agent_D_val = get_override('  ├─ Агент: категория D', str(i+1), agent_D_val_def)
    agent_C_val = get_override('  ├─ Агент: категория C', str(i+1), agent_C_val_def)
    agent_B_val = get_override('  ├─ Агент: категория B', str(i+1), agent_B_val_def)
    agent_A_val = get_override('  ├─ Агент: категория A', str(i+1), agent_A_val_def)
    
    agent_payouts_total_month = agent_D_val + agent_C_val + agent_B_val + agent_A_val
    payouts_agents_list.append(agent_payouts_total_month)
    agent_D_list.append(agent_D_val)
    agent_C_list.append(agent_C_val)
    agent_B_list.append(agent_B_val)
    agent_A_list.append(agent_A_val)
    
    # 4. РАСХОДЫ - ФОТ БЭК-ОФИС (Кадры и Штатное расписание)
    # Fixed salaries
    sal_rop_C_rate = st.session_state.get('sal_rop_C', 70000.0)
    sal_rop_B_rate = st.session_state.get('sal_rop_B', 100000.0)
    sal_admin_rate = st.session_state.get('sal_admin', 70000.0)
    sal_hr_rate = st.session_state.get('sal_hr', 100000.0)
    sal_ros_rate = st.session_state.get('sal_ros', 100000.0)
    sal_jurist_rate = st.session_state.get('sal_jurist', 150000.0)
    sal_mort_rate = st.session_state.get('sal_mort', 180000.0)
    sal_listing_rate = st.session_state.get('sal_listing', 50000.0)
    sal_photo_rate = st.session_state.get('sal_photo', 30000.0)
    sal_smm_rate = st.session_state.get('sal_smm', 150000.0)
    
    v_rop_C_sal = (rop_C_count * sal_rop_C_rate) * salary_mult if st.session_state.get('role_active', {}).get('РОП: категория C', True) else 0.0
    v_rop_B_sal = (rop_B_count * sal_rop_B_rate) * salary_mult if st.session_state.get('role_active', {}).get('РОП: категория B', True) else 0.0
    v_admin_sal = (admin_count * sal_admin_rate) * salary_mult if st.session_state.get('role_active', {}).get('Администратор офиса', True) else 0.0
    v_hr_sal = (hr_count * sal_hr_rate) * salary_mult if st.session_state.get('role_active', {}).get('HR/рекрутер', True) else 0.0
    v_ros_sal = (ros_count * sal_ros_rate) * salary_mult if st.session_state.get('role_active', {}).get('РОС/тренер', True) else 0.0
    v_jurist_sal = (jurist_count * sal_jurist_rate) * salary_mult if st.session_state.get('role_active', {}).get('Юрист', True) else 0.0
    v_mort_broker_sal = (mort_broker_count * sal_mort_rate) * salary_mult if st.session_state.get('role_active', {}).get('Ипотечный Брокер', True) else 0.0
    v_listing_sal = (listing_count * sal_listing_rate) * salary_mult if st.session_state.get('role_active', {}).get('Листинг-менеджер', True) else 0.0
    v_photographer_sal = (photographer_count * sal_photo_rate) * salary_mult if st.session_state.get('role_active', {}).get('Фотограф', True) else 0.0
    v_smm_sal = (smm_count * sal_smm_rate) * salary_mult if st.session_state.get('role_active', {}).get('Маркетолог/SMM', True) else 0.0
    
    # Dynamic Back Office bonuses / variable commissions
    rop_C_bonus_def = total_comm_revenue_month * rop_C_count * (st.session_state.get('rate_rop_C_bonus', 3.0) / 100.0) if st.session_state.get('role_active', {}).get('РОП: категория C', True) else 0.0
    rop_B_bonus_def = total_comm_revenue_month * rop_B_count * (st.session_state.get('rate_rop_B_bonus', 12.0) / 100.0) if st.session_state.get('role_active', {}).get('РОП: категория B', True) else 0.0
    admin_bonus_def = total_comm_revenue_month * admin_count * (st.session_state.get('rate_admin_bonus', 10.0) / 100.0) if st.session_state.get('role_active', {}).get('Администратор офиса', True) else 0.0
    
    hr_bonus_def = hr_count * total_agents_i * st.session_state.get('rate_hr_bonus', 4500.0) if st.session_state.get('role_active', {}).get('HR/рекрутер', True) else 0.0
    ros_bonus_def = ros_count * st.session_state.get('rate_ros_bonus', 50000.0) if st.session_state.get('role_active', {}).get('РОС/тренер', True) else 0.0
    jurist_bonus_def = rev_legal * (st.session_state.get('rate_jurist_bonus', 5.0) / 100.0) if st.session_state.get('role_active', {}).get('Юрист', True) else 0.0
    mort_bonus_def = rev_mort * (st.session_state.get('rate_mort_bonus', 10.0) / 100.0) if st.session_state.get('role_active', {}).get('Ипотечный Брокер', True) else 0.0
    
    total_transactions_m = deals_sec_vol + deals_prim_vol + deals_rent_vol + deals_sub_vol + deals_overseas_vol
    listing_bonus_def = listing_count * total_transactions_m * st.session_state.get('rate_listing_bonus', 500.0) if st.session_state.get('role_active', {}).get('Листинг-менеджер', True) else 0.0
    photo_bonus_def = photographer_count * st.session_state.get('rate_photo_bonus', 30000.0) if st.session_state.get('role_active', {}).get('Фотограф', True) else 0.0
    smm_bonus_def = smm_count * st.session_state.get('rate_smm_bonus', 150000.0) if st.session_state.get('role_active', {}).get('Маркетолог/SMM', True) else 0.0
    
    v_rop_C = get_override('  ├─ РОП: категория C', str(i+1), v_rop_C_sal + rop_C_bonus_def)
    v_rop_B = get_override('  ├─ РОП: категория B', str(i+1), v_rop_B_sal + rop_B_bonus_def)
    v_admin = get_override('  ├─ Администратор офиса', str(i+1), v_admin_sal + admin_bonus_def)
    v_hr = get_override('  ├─ HR/рекрутер', str(i+1), v_hr_sal + hr_bonus_def)
    v_ros = get_override('  ├─ РОС/тренер', str(i+1), v_ros_sal + ros_bonus_def)
    v_jurist = get_override('  ├─ Юрист', str(i+1), v_jurist_sal + jurist_bonus_def)
    v_mort_broker = get_override('  ├─ Ипотечный Брокер', str(i+1), v_mort_broker_sal + mort_bonus_def)
    v_listing = get_override('  ├─ Листинг-менеджер', str(i+1), v_listing_sal + listing_bonus_def)
    v_photographer = get_override('  ├─ Фотограф', str(i+1), v_photographer_sal + photo_bonus_def)
    v_smm = get_override('  ├─ Маркетолог/SMM', str(i+1), v_smm_sal + smm_bonus_def)
    
    salaries_back_total_month = v_rop_C + v_rop_B + v_admin + v_hr + v_ros + v_jurist + v_mort_broker + v_listing + v_photographer + v_smm
    salaries_backoffice_list.append(salaries_back_total_month)
    
    rop_C_list.append(v_rop_C)
    rop_B_list.append(v_rop_B)
    admin_list.append(v_admin)
    hr_list.append(v_hr)
    ros_list.append(v_ros)
    jurist_list.append(v_jurist)
    mort_broker_list.append(v_mort_broker)
    listing_list.append(v_listing)
    photographer_list.append(v_photographer)
    smm_list.append(v_smm)
    
    # Налоги на ФОТ оклады (с учетом ручной корректировки в P&L)
    taxes_payroll_base = (
        v_rop_C_sal + v_rop_B_sal + v_admin_sal + v_hr_sal + v_ros_sal + v_jurist_sal + v_mort_broker_sal + v_listing_sal + v_photographer_sal + v_smm_sal +
        rop_C_bonus_def + rop_B_bonus_def + admin_bonus_def + hr_bonus_def + ros_bonus_def + jurist_bonus_def + mort_bonus_def + listing_bonus_def + photo_bonus_def + smm_bonus_def
    ) * (st.session_state.get('taxes_payroll_rate', 43.0) / 100.0)
    taxes_payroll = get_override('  └─ Налоги на ФОТ оклады', str(i+1), taxes_payroll_base)
    taxes_payroll_list.append(taxes_payroll)
    
    total_payroll_list.append(agent_payouts_total_month + salaries_back_total_month + taxes_payroll)
    
    # 5. OPEX + КОРРЕКТИРОВКИ
    rent_val = get_override('  ├─ Аренда офиса', str(i+1), office_area_val * st.session_state.get('opex_rent_price_m2', 2500.0))
    rent_list.append(rent_val)
    
    internet_val = get_override('  ├─ Интернет', str(i+1), st.session_state.get('opex_internet', 5000.0))
    internet_list.append(internet_val)
    
    mobile_val = get_override('  ├─ Сотовая связь', str(i+1), st.session_state.get('opex_mobile', 600.0) * (total_agents_i if total_agents_i > 0 else 1.0))
    mobile_list.append(mobile_val)
    
    kanc_val = get_override('  ├─ Канцелярия', str(i+1), st.session_state.get('opex_kanc', 500.0) * (total_agents_i if total_agents_i > 0 else 1.0))
    kanc_list.append(kanc_val)
    
    reklama_val = get_override('  ├─ Реклама объектов', str(i+1), st.session_state.get('opex_reklama', 7000.0) * (total_agents_i if total_agents_i > 0 else 1.0))
    reklama_list.append(reklama_val)
    
    hh_val = get_override('  ├─ HeadHunter.ru', str(i+1), st.session_state.get('opex_hh', 45000.0))
    hh_list.append(hh_val)
    
    buh_val = get_override('  ├─ Бухгалтерия: аутсорс', str(i+1), st.session_state.get('opex_buh', 20000.0))
    buh_list.append(buh_val)
    
    bank_val = get_override('  ├─ Услуги банка', str(i+1), st.session_state.get('opex_bank', 2000.0))
    bank_list.append(bank_val)
    
    cleaning_val = get_override('  ├─ Уборка офиса', str(i+1), st.session_state.get('opex_cleaning', 15000.0))
    cleaning_list.append(cleaning_val)
    
    gsm_val = get_override('  ├─ ГСМ', str(i+1), st.session_state.get('opex_gsm', 5000.0))
    gsm_list.append(gsm_val)
    
    courier_val = get_override('  ├─ Доставка/курьер', str(i+1), st.session_state.get('opex_courier', 10000.0))
    courier_list.append(courier_val)
    
    events_val = get_override('  └─ OPEX: Корпоративы', str(i+1), st.session_state.get('opex_events', 10000.0) + st.session_state.get('opex_db_services', 0.0))
    events_list.append(events_val)
    
    total_opex = rent_val + internet_val + mobile_val + kanc_val + reklama_val + hh_val + buh_val + bank_val + cleaning_val + gsm_val + courier_val + events_val
    total_opex_list.append(total_opex)
    
    # 6. ВЫПЛАТЫ ЦО (Франшиза)
    hq_fix = get_override('  ├─ Роялти FIX (вкл. НРФ)', str(i+1), base['hq_royalty_fix'][i] * royalty_fix_mult)
    hq_royalty_fix_list.append(hq_fix)
    
    hq_deal = get_override('  ├─ Роялти со сделок', str(i+1), (deals_sec_vol + deals_prim_vol + deals_sub_vol + deals_rent_vol) * royalty_deal_custom)
    hq_royalty_deal_list.append(hq_deal)
    
    hq_crm = get_override('  ├─ CRM-система', str(i+1), 5500 if i < 12 else 11000)
    hq_crm_list.append(hq_crm)
    
    hq_kc_val = get_override('  └─ Колл-центр и прочие сервисы', str(i+1), max(0.0, base['hq_crm_and_others'][i] - hq_crm))
    hq_kc_list.append(hq_kc_val)
    
    total_hq_payments = hq_fix + hq_deal + hq_crm + hq_kc_val
    total_hq_payments_list.append(total_hq_payments)
    
    # 7. НАЛОГИ
    tax_month = get_override('★ НАЛОГ УСН', str(i+1), total_revenue_month * (tax_rate / 100.0))
    taxes_usn_list.append(tax_month)
    
    # 8. CAPEX
    capex_fran = get_override('  ├─ Франшиза (Паушальный взнос + Роспатент)', str(i+1), capex_franchise_list[i])
    capex_renov = get_override('  ├─ Ремонт и Брендирование офиса', str(i+1), capex_renovation_list[i])
    capex_equip = get_override('  └─ Мебель, компьютеры и оборудование', str(i+1), capex_equipment_list[i])
    
    capex_franchise_list[i] = capex_fran
    capex_renovation_list[i] = capex_renov
    capex_equipment_list[i] = capex_equip
    
    tot_capex_month = capex_fran + capex_renov + capex_equip
    total_capex_list.append(tot_capex_month)
    
    total_expenses_month = agent_payouts_total_month + salaries_back_total_month + taxes_payroll + total_opex + total_hq_payments + tax_month
    net_profit_month = total_revenue_month - total_expenses_month - tot_capex_month
    adj_net_profit.append(net_profit_month)

# Detailed CAPEX calculations based on interactive widgets from session state
pau_fee_val = st.session_state.get('capex_pau_fee', float(preset["pau_fee"]))
rospatent_val = st.session_state.get('capex_rospatent', 17000.0)
office_area_val = st.session_state.get('capex_office_area', 60.0)
norm_m2_val = st.session_state.get('capex_norm_m2', 6.0)
workstations_val = st.session_state.get('capex_workstations', 10)
renov_price_val = st.session_state.get('capex_renov_price', 10000.0)
brand_price_val = st.session_state.get('capex_brand_price', 2000.0)
table_price_val = st.session_state.get('capex_table_price', 12000.0)
stool_price_val = st.session_state.get('capex_stool_price', 7000.0)
computer_price_val = st.session_state.get('capex_computer_price', 45000.0)
add_furniture_val = st.session_state.get('capex_add_furniture', 150000.0)
router_printer_val = st.session_state.get('capex_router_printer', 25000.0)

calc_franchise = pau_fee_val + rospatent_val
calc_renovation = office_area_val * renov_price_val + office_area_val * brand_price_val
calc_equipment = workstations_val * (table_price_val + stool_price_val + computer_price_val) + add_furniture_val + router_printer_val

# Расчет Месяца 0 (Старт)
capex_m0_franchise = get_override('  ├─ Франшиза (Паушальный взнос + Роспатент)', 'Старт', calc_franchise)
capex_m0_renovation = get_override('  ├─ Ремонт и Брендирование офиса', 'Старт', calc_renovation)
capex_m0_equipment = get_override('  └─ Мебель, компьютеры и оборудование', 'Старт', calc_equipment)
total_capex_m0 = capex_m0_franchise + capex_m0_renovation + capex_m0_equipment

start_rent = get_override('  ├─ Аренда офиса', 'Старт', office_area_val * st.session_state.get('opex_rent_price_m2', 2500.0))
start_opex_total = start_rent + (
        st.session_state.get('opex_internet', 5000.0) +
        st.session_state.get('opex_hh', 45000.0) +
        st.session_state.get('opex_buh', 20000.0) +
        st.session_state.get('opex_bank', 2000.0) +
        st.session_state.get('opex_cleaning', 15000.0) +
        st.session_state.get('opex_gsm', 5000.0) +
        st.session_state.get('opex_courier', 10000.0) +
        st.session_state.get('opex_events', 10000.0) +
        st.session_state.get('opex_db_services', 0.0)
    )

cum_flow = []
running_sum = -total_capex_m0 - start_opex_total
cum_flow.append(running_sum)

for i in range(24):
    running_sum += adj_net_profit[i]
    cum_flow.append(running_sum)

# KPI
total_revenue_2years = sum(rev_total_list)
total_profit_2years = sum(adj_net_profit) - total_capex_m0 - start_opex_total
max_investment = abs(min(cum_flow))

payback_month = "Н/Д"
for idx, val in enumerate(cum_flow):
    if val >= 0:
        payback_month = f"{idx} мес."
        break

breakeven_month = "Н/Д"
for idx, val in enumerate(adj_net_profit):
    if val > 0:
        breakeven_month = f"{idx + 1} мес."
        break

# Карточки KPI
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💼 Общая выручка (2 года)", f"{total_revenue_2years:,.0f} ₽".replace(",", " "))
with col2:
    st.metric("📈 Итоговая чистая прибыль", f"{total_profit_2years:,.0f} ₽".replace(",", " "))
with col3:
    st.metric("📉 Пик инвестиций (CAPEX+OPEX)", f"{max_investment:,.0f} ₽".replace(",", " "))
with col4:
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("🎯 Без-ость", breakeven_month)
    with col_b:
        st.metric("⏳ Окупаемость", payback_month)


# Пре-расчет значений для колонки Старт (Месяц 0)
v_m0_rev_sec = get_override('  ├─ Вторичный рынок', 'Старт', 0.0)
v_m0_rev_prim = get_override('  ├─ Первичный рынок', 'Старт', 0.0)
v_m0_rev_rent = get_override('  ├─ Аренда (жилая/коммерческая)', 'Старт', 0.0)
v_m0_rev_sub = get_override('  ├─ Загородная недвижимость', 'Старт', 0.0)
v_m0_rev_overseas = get_override('  ├─ Зарубежная недвижимость', 'Старт', 0.0)
v_m0_rev_other_p = get_override('  ├─ Сделки: прочее (МЛС, срочновыкуп)', 'Старт', 0.0)
v_m0_rev_mort = get_override('  ├─ Сервисы: ипотека', 'Старт', 0.0)
v_m0_rev_ins = get_override('  ├─ Сервисы: страхование', 'Старт', 0.0)
v_m0_rev_legal = get_override('  └─ Сервисы: юр. сопровождение', 'Старт', 0.0)
v_m0_rev_total = v_m0_rev_sec + v_m0_rev_prim + v_m0_rev_rent + v_m0_rev_sub + v_m0_rev_overseas + v_m0_rev_other_p + v_m0_rev_mort + v_m0_rev_ins + v_m0_rev_legal

v_m0_agent_D = get_override('  ├─ Агент: категория D', 'Старт', 0.0)
v_m0_agent_C = get_override('  ├─ Агент: категория C', 'Старт', 0.0)
v_m0_agent_B = get_override('  ├─ Агент: категория B', 'Старт', 0.0)
v_m0_agent_A = get_override('  ├─ Агент: категория A', 'Старт', 0.0)

v_m0_agent_compact = get_override('  ├─ Выплаты агентам (% комиссионных)', 'Старт', 0.0)
if v_m0_agent_compact > 0.0 and (v_m0_agent_D + v_m0_agent_C + v_m0_agent_B + v_m0_agent_A == 0.0):
    v_m0_agent_D = v_m0_agent_compact * 0.30
    v_m0_agent_C = v_m0_agent_compact * 0.35
    v_m0_agent_B = v_m0_agent_compact * 0.25
    v_m0_agent_A = v_m0_agent_compact * 0.10
v_m0_agent_total = v_m0_agent_D + v_m0_agent_C + v_m0_agent_B + v_m0_agent_A
if v_m0_agent_compact == 0.0 and v_m0_agent_total > 0.0:
    v_m0_agent_compact = v_m0_agent_total

v_m0_rop_C = get_override('  ├─ РОП: категория C', 'Старт', 0.0)
v_m0_rop_B = get_override('  ├─ РОП: категория B', 'Старт', 0.0)
v_m0_admin = get_override('  ├─ Администратор офиса', 'Старт', 0.0)
v_m0_hr = get_override('  ├─ HR/рекрутер', 'Старт', 0.0)
v_m0_ros = get_override('  ├─ РОС/тренер', 'Старт', 0.0)
v_m0_jurist = get_override('  ├─ Юрист', 'Старт', 0.0)
v_m0_mort_broker = get_override('  ├─ Ипотечный Брокер', 'Старт', 0.0)
v_m0_listing = get_override('  ├─ Листинг-менеджер', 'Старт', 0.0)
v_m0_photographer = get_override('  ├─ Фотограф', 'Старт', 0.0)
v_m0_smm = get_override('  ├─ Маркетолог/SMM', 'Старт', 0.0)

v_m0_back_compact = get_override('  ├─ Оклады бэк-офиса (оклады)', 'Старт', 0.0)
if v_m0_back_compact > 0.0 and (v_m0_rop_C + v_m0_rop_B + v_m0_admin + v_m0_hr + v_m0_ros + v_m0_jurist + v_m0_mort_broker + v_m0_listing + v_m0_photographer + v_m0_smm == 0.0):
    v_m0_rop_C = v_m0_back_compact * 0.15
    v_m0_rop_B = v_m0_back_compact * 0.15
    v_m0_admin = v_m0_back_compact * 0.10
    v_m0_hr = v_m0_back_compact * 0.10
    v_m0_ros = v_m0_back_compact * 0.10
    v_m0_jurist = v_m0_back_compact * 0.10
    v_m0_mort_broker = v_m0_back_compact * 0.10
    v_m0_listing = v_m0_back_compact * 0.08
    v_m0_photographer = v_m0_back_compact * 0.04
    v_m0_smm = v_m0_back_compact * 0.08
v_m0_back_total = v_m0_rop_C + v_m0_rop_B + v_m0_admin + v_m0_hr + v_m0_ros + v_m0_jurist + v_m0_mort_broker + v_m0_listing + v_m0_photographer + v_m0_smm
if v_m0_back_compact == 0.0 and v_m0_back_total > 0.0:
    v_m0_back_compact = v_m0_back_total

v_m0_salary_taxes = get_override('  └─ Налоги на ФОТ оклады', 'Старт', 0.0)
v_m0_fot_total = v_m0_agent_total + v_m0_back_total + v_m0_salary_taxes

v_m0_rent = start_rent
v_m0_internet = get_override('  ├─ Интернет', 'Старт', 0.0)
v_m0_mobile = get_override('  ├─ Сотовая связь', 'Старт', 0.0)
v_m0_kanc = get_override('  ├─ Канцелярия', 'Старт', 0.0)
v_m0_reklama = get_override('  ├─ Реклама объектов', 'Старт', 0.0)
v_m0_hh = get_override('  ├─ HeadHunter.ru', 'Старт', 0.0)
v_m0_buh = get_override('  ├─ Бухгалтерия: аутсорс', 'Старт', 0.0)
v_m0_bank = get_override('  ├─ Услуги банка', 'Старт', 0.0)
v_m0_cleaning = get_override('  ├─ Уборка офиса', 'Старт', 0.0)
v_m0_gsm = get_override('  ├─ ГСМ', 'Старт', 0.0)
v_m0_courier = get_override('  ├─ Доставка/курьер', 'Старт', 0.0)
v_m0_events = get_override('  └─ OPEX: Корпоративы', 'Старт', 0.0)
v_m0_opex_total = v_m0_rent + v_m0_internet + v_m0_mobile + v_m0_kanc + v_m0_reklama + v_m0_hh + v_m0_buh + v_m0_bank + v_m0_cleaning + v_m0_gsm + v_m0_courier + v_m0_events

v_m0_hq_fix = get_override('  ├─ Роялти FIX (вкл. НРФ)', 'Старт', 0.0)
v_m0_hq_deal = get_override('  ├─ Роялти со сделок', 'Старт', 0.0)
v_m0_hq_crm = get_override('  ├─ CRM-система', 'Старт', 0.0)
v_m0_hq_kc = get_override('  └─ Колл-центр и прочие сервисы', 'Старт', 0.0)
v_m0_hq_total = v_m0_hq_fix + v_m0_hq_deal + v_m0_hq_crm + v_m0_hq_kc

v_m0_tax = get_override('★ НАЛОГ УСН', 'Старт', 0.0)
v_m0_opex_tax_total = v_m0_fot_total + v_m0_opex_total + v_m0_hq_total + v_m0_tax

# Глобальные списки строк для P&L
revenue_rows_def = [
    ('Вторичный рынок', rev_secondary_list, v_m0_rev_sec, '  ├─ Вторичный рынок'),
    ('Первичный рынок', rev_primary_list, v_m0_rev_prim, '  ├─ Первичный рынок'),
    ('Аренда (жилая/коммерческая)', rev_rent_list, v_m0_rev_rent, '  ├─ Аренда (жилая/коммерческая)'),
    ('Загородная недвижимость', rev_suburban_list, v_m0_rev_sub, '  ├─ Загородная недвижимость'),
    ('Зарубежная недвижимость', rev_overseas_list, v_m0_rev_overseas, '  ├─ Зарубежная недвижимость'),
    ('Сделки: прочее (МЛС, срочновыкуп)', rev_other_p_list, v_m0_rev_other_p, '  ├─ Сделки: прочее (МЛС, срочновыкуп)'),
    ('Сервисы: ипотека', rev_mortgage_list, v_m0_rev_mort, '  ├─ Сервисы: ипотека'),
    ('Сервисы: страхование', rev_insurance_list, v_m0_rev_ins, '  ├─ Сервисы: страхование'),
    ('Сервисы: юр. сопровождение', rev_legal_list, v_m0_rev_legal, '  └─ Сервисы: юр. сопровождение'),
    ('★ ИТОГО ДОХОДЫ', rev_total_list, v_m0_rev_total, None)
]

fot_rows_def = [
    ('Выплаты агентам (% комиссионных)', payouts_agents_list, v_m0_agent_total, '  ├─ Выплаты агентам (% комиссионных)'),
    ('Оклады бэк-офиса (оклады)', salaries_backoffice_list, v_m0_back_total, '  ├─ Оклады бэк-офиса (оклады)'),
    ('Налоги на ФОТ оклады', taxes_payroll_list, v_m0_salary_taxes, '  └─ Налоги на ФОТ оклады'),
    ('★ ИТОГО ФОТ', total_payroll_list, v_m0_fot_total, None)
]

opex_rows_def = [
    ('Аренда офиса', rent_list, v_m0_rent, '  ├─ Аренда офиса'),
    ('Интернет', internet_list, v_m0_internet, '  ├─ Интернет'),
    ('Сотовая связь', mobile_list, v_m0_mobile, '  ├─ Сотовая связь'),
    ('Канцелярия', kanc_list, v_m0_kanc, '  ├─ Канцелярия'),
    ('Реклама объектов', reklama_list, v_m0_reklama, '  ├─ Реклама объектов'),
    ('HeadHunter.ru', hh_list, v_m0_hh, '  ├─ HeadHunter.ru'),
    ('Бухгалтерия: аутсорс', buh_list, v_m0_buh, '  ├─ Бухгалтерия: аутсорс'),
    ('Услуги банка', bank_list, v_m0_bank, '  ├─ Услуги банка'),
    ('Уборка офиса', cleaning_list, v_m0_cleaning, '  ├─ Уборка офиса'),
    ('ГСМ', gsm_list, v_m0_gsm, '  ├─ ГСМ'),
    ('Доставка/курьер', courier_list, v_m0_courier, '  ├─ Доставка/курьер'),
    ('Корпоративные мероприятия', events_list, v_m0_events, '  └─ OPEX: Корпоративы'),
    ('★ ИТОГО OPEX', total_opex_list, v_m0_opex_total, None)
]

hq_rows_def = [
    ('Роялти FIX (вкл. НРФ)', hq_royalty_fix_list, v_m0_hq_fix, '  ├─ Роялти FIX (вкл. НРФ)'),
    ('Роялти со сделок', hq_royalty_deal_list, v_m0_hq_deal, '  ├─ Роялти со сделок'),
    ('CRM-система', hq_crm_list, v_m0_hq_crm, '  ├─ CRM-система'),
    ('Колл-центр и прочие сервисы', hq_kc_list, v_m0_hq_kc, '  └─ Колл-центр и прочие сервисы'),
    ('★ ИТОГО ВЫПЛАТЫ ЦО', total_hq_payments_list, v_m0_hq_total, None)
]

capex_rows_def = [
    ('Франшиза (Паушальный взнос + Роспатент)', capex_franchise_list, capex_m0_franchise, '  ├─ Франшиза (Паушальный взнос + Роспатент)'),
    ('Ремонт и Брендирование офиса', capex_renovation_list, capex_m0_renovation, '  ├─ Ремонт и Брендирование офиса'),
    ('Мебель, компьютеры и оборудование', capex_equipment_list, capex_m0_equipment, '  └─ Мебель, компьютеры и оборудование'),
    ('★ ИТОГО CAPEX', total_capex_list, total_capex_m0, None)
]

# Вспомогательная функция для агрегации метрик по Кварталам / Годам
def aggregate_metric(m_list, m0_val, scale):
    if scale == "Месячный (24 месяца)":
        return [m0_val] + list(m_list)
    elif scale == "Квартальный (8 кварталов)":
        q_vals = [m0_val]
        for q in range(8):
            sub_list = m_list[q*3:(q+1)*3]
            q_vals.append(sum(sub_list))
        return q_vals
    else:
        y_vals = [m0_val]
        y1 = sum(m_list[:12])
        y2 = sum(m_list[12:])
        y_vals.extend([y1, y2])
        return y_vals

# ----------------------------------------------------
# ТАБЫ: ГРАФИКИ, ДЕТАЛИЗАЦИЯ И СРАВНЕНИЕ
# ----------------------------------------------------


# ==============================================================================
# РЕВОЛЮЦИОННЫЙ ИНТЕРАКТИВНЫЙ ИНТЕРФЕЙС (v18)
# ==============================================================================

# Селектор режима работы на самом верху экрана (Sales vs Calculator vs Success)
app_mode = st.radio(
    "⚡ **Выберите режим работы приложения:**",
    options=[
        "🎯 Презентация и Шаговый конструктор запуска (Sales)", 
        "📐 Детальный Интерактивный Калькулятор (Calculator)",
        "🛠️ Сопровождение и Диагностика офиса (Success)"
    ],
    horizontal=True,
    help="Выберите режим: Sales — для защиты бизнес-плана перед потенциальным франчайзи в виде пошаговой бизнес-игры; Success — для аудита показателей действующего офиса и выработки рецептов роста."
)

st.markdown("<div style='border-top: 2px solid #BEAF87; margin-top: 10px; margin-bottom: 25px;'></div>", unsafe_allow_html=True)

if app_mode == "🎯 Презентация и Шаговый конструктор запуска (Sales)":
    # ----------------------------------------------------
    # РЕЖИМ SALES: ПОШАГОВЫЙ КОНСТРУКТОР С ЗАУЧЕННЫМИ СЦЕНАРИЯМИ
    # ----------------------------------------------------
    st.markdown("### 🎯 Шаговый интерактивный конструктор запуска офиса CENTURY 21")
    st.markdown("ℹ️ *Сконструируйте будущий бизнес за 5 простых шагов, переключаясь между кнопками и ползунками. Таблицы скрыты, все расчеты производятся в реальном времени!*")
    
    # Линейный прогресс-бар шагов
    step = st.select_slider(
        "📍 **Текущий шаг планирования:**",
        options=[
            "1. Локация и Масштаб",
            "2. Обустройство и CAPEX",
            "3. Команда мечты (Кадры)",
            "4. Двигатель продаж (Воронка)",
            "5. Экономика успеха (Результат)"
        ],
        value="1. Локация и Масштаб"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if step == "1. Локация и Масштаб":
        col_left, col_right = st.columns([2, 1.2])
        with col_left:
            st.markdown("#### 🌍 Шаг 1: Выбор локации и базовых чеков")
            st.info(f"📌 **Текущий регион:** {region_select}\n\nВсе базовые финансовые параметры (средние комиссии, оклады персонала, стоимость аренды) уже автоматически подстроены под экономику вашей территории. Вы можете скорректировать их ниже:")
            
            # Размещаем ключевые настройки в аккуратные карточки
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**💰 Паушальный взнос (с НДС):**")
                pau_val = st.number_input(
                    "Паушальный взнос, ₽", 
                    min_value=150000, max_value=1500000, value=int(preset["pau_fee"]), step=50000,
                    key="sales_step1_pau"
                )
                if pau_val != preset["pau_fee"]:
                    st.session_state['pau_fee_val'] = pau_val
                    st.rerun()
                    
            with c2:
                st.markdown("**🏢 Аренда офиса в месяц:**")
                rent_val_inp = st.number_input(
                    "Базовая аренда, ₽/мес", 
                    min_value=10000, max_value=500000, value=int(preset["rent_base"]), step=10000,
                    key="sales_step1_rent"
                )
                if rent_val_inp != preset["rent_base"]:
                    st.session_state['office_rent_custom'] = rent_val_inp
                    st.rerun()
            
            # Доп чеки
            c3, c4 = st.columns(2)
            with c3:
                st.markdown("**🤝 Средняя комиссия (Вторичка):**")
                sec_comm_inp = st.number_input(
                    "Вторичный рынок, ₽", 
                    min_value=50000, max_value=1000000, value=int(preset["comm_sec"]), step=10000,
                    key="sales_step1_sec"
                )
                if sec_comm_inp != preset["comm_sec"]:
                    # Мы можем временно перезаписать в pl_overrides или в сайдбар-переменные
                    st.session_state['comm_secondary'] = sec_comm_inp
                    st.rerun()
            with c4:
                st.markdown("**🏗️ Средняя комиссия (Первичка):**")
                prim_comm_inp = st.number_input(
                    "Первичный рынок, ₽", 
                    min_value=50000, max_value=1000000, value=int(preset["comm_prim"]), step=10000,
                    key="sales_step1_prim"
                )
                if prim_comm_inp != preset["comm_prim"]:
                    st.session_state['comm_primary'] = prim_comm_inp
                    st.rerun()
                    
        with col_right:
            st.markdown(f"""
            <div style='background-color: #F8F9FA; padding: 20px; border-radius: 8px; border-left: 5px solid #BEAF87;'>
                <h5 style='color: #252526; font-weight: 700; margin-top:0;'>💡 Шпаргалка Эксперта (Шаг 1)</h5>
                <p style='font-size: 13px; color: #777779; line-height: 1.5;'>
                    <b>Фокус внимания франчайзи:</b> Обратите внимание клиента на то, что средняя комиссия по сделкам — это подтвержденная практикой планка сети. Мы не берем цифры "с потолка".
                </p>
                <p style='font-size: 13px; color: #777779; line-height: 1.5;'>
                    <b>Сценарий разговора (скрипт):</b><br>
                    <i>"Уважаемый партнер, для {region_select} базовые параметры окупаемости уже заложены в систему. Мы установили средний чек вторички на уровне {comm_secondary:,.0f} ₽. Это абсолютно безопасный норматив. Давайте перейдем к шагу обустройства офиса, чтобы посмотреть, сколько составят ваши стартовые инвестиции."</i>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    elif step == "2. Обустройство и CAPEX":
        col_left, col_right = st.columns([2.2, 1.3])
        with col_left:
            st.markdown("#### 🛠️ Шаг 2: Капитальные вложения (CAPEX) — Конструктор")
            st.write("Настройте площадь офиса, количество рабочих мест и нормативы площади. Все расчеты производятся автоматически:")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.slider("Площадь офиса, м²", min_value=40, max_value=140, key="step2_office_area_widget", value=int(st.session_state['capex_office_area']), step=5)
                st.session_state['capex_office_area'] = float(st.session_state.step2_office_area_widget)
            with c2:
                st.slider("Норма м² на человека", min_value=4.0, max_value=12.0, key="step2_norm_m2_widget", value=float(st.session_state['capex_norm_m2']), step=0.5)
                st.session_state['capex_norm_m2'] = float(st.session_state.step2_norm_m2_widget)
            with c3:
                st.number_input("Рабочие места (чел.)", min_value=5, max_value=50, key="step2_workstations_widget", value=int(st.session_state['capex_workstations']), step=1)
                st.session_state['capex_workstations'] = int(st.session_state.step2_workstations_widget)
                
            st.markdown("##### 💻 Цены и комплектация оборудования (руб.):")
            c4, c5, c6 = st.columns(3)
            with c4:
                st.number_input("Цена стола, ₽/шт.", min_value=1000, max_value=50000, key="step2_table_price_widget", value=int(st.session_state['capex_table_price']), step=1000)
                st.session_state['capex_table_price'] = float(st.session_state.step2_table_price_widget)
            with c5:
                st.number_input("Цена стула, ₽/шт.", min_value=1000, max_value=50000, key="step2_stool_price_widget", value=int(st.session_state['capex_stool_price']), step=1000)
                st.session_state['capex_stool_price'] = float(st.session_state.step2_stool_price_widget)
            with c6:
                st.number_input("Цена компьютера/ПК, ₽/шт.", min_value=10000, max_value=200000, key="step2_computer_price_widget", value=int(st.session_state['capex_computer_price']), step=5000)
                st.session_state['capex_computer_price'] = float(st.session_state.step2_computer_price_widget)
                
            with st.expander("🛠️ Тонкие настройки цен ремонта и прочих вложений", expanded=False):
                c7, c8 = st.columns(2)
                with c7:
                    st.number_input("Стоимость ремонта, ₽/м²", min_value=1000, max_value=50000, key="step2_renov_price_widget", value=int(st.session_state['capex_renov_price']), step=1000)
                    st.session_state['capex_renov_price'] = float(st.session_state.step2_renov_price_widget)
                    st.number_input("Доп. мебель (шкаф, тумба), ₽", min_value=10000, max_value=1000000, key="step2_add_furniture_widget", value=int(st.session_state['capex_add_furniture']), step=10000)
                    st.session_state['capex_add_furniture'] = float(st.session_state.step2_add_furniture_widget)
                with c8:
                    st.number_input("Стоимость брендирования, ₽/м²", min_value=500, max_value=20000, key="step2_brand_price_widget", value=int(st.session_state['capex_brand_price']), step=500)
                    st.session_state['capex_brand_price'] = float(st.session_state.step2_brand_price_widget)
                    st.number_input("Роутер, принтер, сеть, всего ₽", min_value=5000, max_value=200000, key="step2_router_printer_widget", value=int(st.session_state['capex_router_printer']), step=5000)
                    st.session_state['capex_router_printer'] = float(st.session_state.step2_router_printer_widget)
                    
            # Recalculate totals for display
            p_area = st.session_state['capex_office_area']
            p_work = st.session_state['capex_workstations']
            p_norm = st.session_state['capex_norm_m2']
            p_pau = st.session_state['capex_pau_fee']
            p_rospat = st.session_state['capex_rospatent']
            p_renov = st.session_state['capex_renov_price']
            p_brand = st.session_state['capex_brand_price']
            p_table = st.session_state['capex_table_price']
            p_stool = st.session_state['capex_stool_price']
            p_comp = st.session_state['capex_computer_price']
            p_add = st.session_state['capex_add_furniture']
            p_rout = st.session_state['capex_router_printer']
            
            calc_franchise_val = p_pau + p_rospat
            calc_renovation_val = p_area * p_renov + p_area * p_brand
            calc_equipment_val = p_work * (p_table + p_stool + p_comp) + p_add + p_rout
            calc_total_capex = calc_franchise_val + calc_renovation_val + calc_equipment_val
            
            # Display Space check warning
            req_space = p_work * p_norm
            if p_area < req_space:
                st.warning(f"⚠️ **Площадь офиса ниже нормы!** Для {p_work} рабочих мест при норме {p_norm} м²/чел., рекомендуемая площадь — от **{req_space:.0f} м²**. Ваша площадь **{p_area:.0f} м²** может быть тесной.")
            else:
                st.success(f"🟢 **Площадь офиса в норме!** Площадь **{p_area:.0f} м²** достаточна для {p_work} мест при норме {p_norm} м²/чел.")
                
            # Render beautiful table
            capex_table_df = pd.DataFrame({
                "Категория / Статья CAPEX": [
                    "► РЕГИСТРАЦИЯ И ФРАНШИЗА",
                    "  ├─ Паушальный взнос (франшиза)",
                    "  ├─ Госпошлина (Роспатент)",
                    "★ ИТОГО РЕГИСТРАЦИЯ",
                    "► ОБУСТРОЙСТВО ОФИСА",
                    "  ├─ Ремонт помещения",
                    "  ├─ Брендирование и вывески",
                    "  ├─ Офисные столы",
                    "  ├─ Офисные стулья",
                    "  ├─ Компьютеры / Мониторы",
                    "  ├─ Доп. мебель (шкаф, тумба)",
                    "  └─ Роутер, принтер, сеть",
                    "★ ИТОГО ОФИС",
                    "🏆 ВСЕГО СТАРТОВЫЕ ИНВЕСТИЦИИ (CAPEX)"
                ],
                "Кол-во / Параметр": [
                    "", "1", "1", "", "", f"{p_area:.0f} м²", f"{p_area:.0f} м²", f"{p_work} шт.", f"{p_work} шт.", f"{p_work} шт.", "1", "1", "", ""
                ],
                "Цена / Тариф": [
                    "",
                    f"{p_pau:,.0f} ₽".replace(",", " "),
                    f"{p_rospat:,.0f} ₽".replace(",", " "),
                    "",
                    "",
                    f"{p_renov:,.0f} ₽/м²".replace(",", " "),
                    f"{p_brand:,.0f} ₽/м²".replace(",", " "),
                    f"{p_table:,.0f} ₽/шт.".replace(",", " "),
                    f"{p_stool:,.0f} ₽/шт.".replace(",", " "),
                    f"{p_comp:,.0f} ₽/шт.".replace(",", " "),
                    f"{p_add:,.0f} ₽".replace(",", " "),
                    f"{p_rout:,.0f} ₽".replace(",", " "),
                    "",
                    ""
                ],
                "Сумма": [
                    "",
                    f"{p_pau:,.0f} ₽".replace(",", " "),
                    f"{p_rospat:,.0f} ₽".replace(",", " "),
                    f"{calc_franchise_val:,.0f} ₽".replace(",", " "),
                    "",
                    f"{p_area * p_renov:,.0f} ₽".replace(",", " "),
                    f"{p_area * p_brand:,.0f} ₽".replace(",", " "),
                    f"{p_work * p_table:,.0f} ₽".replace(",", " "),
                    f"{p_work * p_stool:,.0f} ₽".replace(",", " "),
                    f"{p_work * p_comp:,.0f} ₽".replace(",", " "),
                    f"{p_add:,.0f} ₽".replace(",", " "),
                    f"{p_rout:,.0f} ₽".replace(",", " "),
                    f"{calc_renovation_val + calc_equipment_val:,.0f} ₽".replace(",", " "),
                    f"{calc_total_capex:,.0f} ₽".replace(",", " ")
                ]
            })
            st.dataframe(capex_table_df, use_container_width=True, height=450)
            
        with col_right:
            st.markdown(f"""
            <div style='background-color: #F8F9FA; padding: 20px; border-radius: 8px; border-left: 5px solid #BEAF87;'>
                <h5 style='color: #252526; font-weight: 700; margin-top:0;'>💡 Шпаргалка Эксперта (Шаг 2)</h5>
                <p style='font-size: 13px; color: #777779; line-height: 1.5;'>
                    <b>Фокус внимания франчайзи:</b> Сделайте акцент на то, что ремонт и оборудование по стандартам CENTURY 21 — это инвестиция в капитализацию бизнеса. Брокерский офис — это витрина франшизы.
                </p>
                <p style='font-size: 13px; color: #777779; line-height: 1.5;'>
                    <b>Сценарий разговора (скрипт):</b><br>
                    <i>"Наш калькулятор автоматически рассчитал все затраты. Ремонт и брендирование офиса площадью {p_area:.0f} м² составили {calc_renovation_val:,.0f} ₽. Мебель и компьютеры для {p_work} рабочих мест составят {calc_equipment_val:,.0f} ₽. Это полностью готовая смета. Давайте перейдем к шагу подбора команды."</i>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Donut chart
            st.markdown("<br>", unsafe_allow_html=True)
            capex_structure = {
                'Паушальный + Роспатент': calc_franchise_val,
                'Ремонт и Брендирование': p_area * p_renov + p_area * p_brand,
                'Мебель и Техника': p_work * (p_table + p_stool) + p_work * p_comp,
                'Прочие и доп.мебель': p_add + p_rout,
                'Стартовый резерв': start_opex_total
            }
            fig_capex_donut = go.Figure(data=[go.Pie(
                labels=list(capex_structure.keys()),
                values=list(capex_structure.values()),
                hole=.4,
                marker=dict(colors=['#BEAF87', '#A19276', '#252526', '#777779', '#CCCCCC']),
                textinfo='percent',
                texttemplate='%{label}:<br>%{percent}'
            )])
            fig_capex_donut.update_layout(
                title=f"Стартовые инвестиции: {calc_total_capex + start_opex_total:,.0f} ₽".replace(",", " "),
                template="plotly_white",
                height=260,
                margin=dict(t=40, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_capex_donut, use_container_width=True)
            
    elif step == "3. Команда мечты (Кадры)":
        col_left, col_right = st.columns([2, 1.2])
        with col_left:
            st.markdown("#### 👥 Шаг 3: Кадровое планирование и численность (чел.)")
            st.write("Настройте штат бэк-офиса и плановое количество агентов на первый/второй год с помощью интерактивных переключателей:")
            
            # Компактный кадровый слайдер
            st.markdown("**🚀 Масштаб кадрового набора агентов:**")
            agent_intensity = st.select_slider(
                "Выберите темп найма агентов (по умолчанию используется Оптимальный):",
                options=["Медленный (до 15 агентов к 24 мес.)", "Оптимальный (до 37 агентов к 24 мес.)", "Интенсивный (до 50 агентов к 24 мес.)"],
                value="Оптимальный (до 37 агентов к 24 мес.)",
                key="sales_step3_agent_intensity"
            )
            # В зависимости от темпа мы можем скорректировать headcount_overrides в сессии!
            if agent_intensity == "Медленный (до 15 агентов к 24 мес.)":
                for m_idx in range(1, 25):
                    st.session_state['headcount_overrides'][('  ├─ Агент: категория D', str(m_idx))] = int(max(1, int(DEFAULT_HEADCOUNTS['Агент: категория D'][m_idx-1] * 0.4)))
                    st.session_state['headcount_overrides'][('  ├─ Агент: категория C', str(m_idx))] = int(DEFAULT_HEADCOUNTS['Агент: категория C'][m_idx-1] * 0.4)
                    st.session_state['headcount_overrides'][('  ├─ Агент: категория B', str(m_idx))] = int(DEFAULT_HEADCOUNTS['Агент: category B' if 'category B' in DEFAULT_HEADCOUNTS else 'Агент: категория B'][m_idx-1] * 0.4)
                    st.session_state['headcount_overrides'][('  └─ Агент: категория A', str(m_idx))] = int(DEFAULT_HEADCOUNTS['Агент: категория A'][m_idx-1] * 0.4)
            elif agent_intensity == "Интенсивный (до 50 агентов к 24 мес.)":
                for m_idx in range(1, 25):
                    st.session_state['headcount_overrides'][('  ├─ Агент: категория D', str(m_idx))] = int(DEFAULT_HEADCOUNTS['Агент: категория D'][m_idx-1] * 1.3)
                    st.session_state['headcount_overrides'][('  ├─ Агент: категория C', str(m_idx))] = int(DEFAULT_HEADCOUNTS['Агент: категория C'][m_idx-1] * 1.3)
                    st.session_state['headcount_overrides'][('  ├─ Агент: категория B', str(m_idx))] = int(DEFAULT_HEADCOUNTS['Агент: category B' if 'category B' in DEFAULT_HEADCOUNTS else 'Агент: категория B'][m_idx-1] * 1.3)
                    st.session_state['headcount_overrides'][('  └─ Агент: категория A', str(m_idx))] = int(DEFAULT_HEADCOUNTS['Агент: категория A'][m_idx-1] * 1.3)
            else:
                # Reset agents overrides
                for m_idx in range(1, 25):
                    st.session_state['headcount_overrides'].pop(('  ├─ Агент: категория D', str(m_idx)), None)
                    st.session_state['headcount_overrides'].pop(('  ├─ Агент: категория C', str(m_idx)), None)
                    st.session_state['headcount_overrides'].pop(('  ├─ Агент: категория B', str(m_idx)), None)
                    st.session_state['headcount_overrides'].pop(('  └─ Агент: категория A', str(m_idx)), None)
            
            # Бэк-офис кликеры
            st.markdown("<br>**👔 Ключевые штатные единицы бэк-офиса:**", unsafe_allow_html=True)
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                rop_count = st.number_input("Количество РОПов:", min_value=0, max_value=5, value=2, step=1, key="bo_rop_input")
                # Записываем оверрайд во вторую половину проекта
                for m_idx in range(13, 25):
                    st.session_state['headcount_overrides'][('  ├─ РОП: категория C', str(m_idx))] = int(rop_count // 2 + rop_count % 2)
                    st.session_state['headcount_overrides'][('  ├─ РОП: категория B', str(m_idx))] = int(rop_count // 2)
            with col_b2:
                hr_count = st.number_input("Количество HR-рекрутеров:", min_value=0, max_value=5, value=2, step=1, key="bo_hr_input")
                for m_idx in range(13, 25):
                    st.session_state['headcount_overrides'][('  ├─ HR/рекрутер', str(m_idx))] = int(hr_count)
            with col_b3:
                jur_count = st.number_input("Количество Юристов в штате:", min_value=0, max_value=3, value=1, step=1, key="bo_jur_input")
                for m_idx in range(13, 25):
                    st.session_state['headcount_overrides'][('  ├─ Юрист', str(m_idx))] = int(jur_count)
            
            # Donut chart of headcount in month 13
            m13_back = {
                'РОПы': rop_count,
                'HR-рекрутеры': hr_count,
                'Юристы': jur_count,
                'Администратор': 1,
                'РОС/тренер': 1,
                'Листинг/СММ/Фото': 3,
                'Агенты (D, C, B, A)': int(get_headcount_override('  ├─ Агент: категория D', '13', DEFAULT_HEADCOUNTS['Агент: категория D'][12]) + 
                                           get_headcount_override('  ├─ Агент: категория C', '13', DEFAULT_HEADCOUNTS['Агент: категория C'][12]) + 
                                           get_headcount_override('  ├─ Агент: категория B', '13', DEFAULT_HEADCOUNTS['Агент: категория B' if 'category B' in DEFAULT_HEADCOUNTS else 'Агент: категория B'][12]) + 
                                           get_headcount_override('  └─ Агент: категория A', '13', DEFAULT_HEADCOUNTS['Агент: категория A'][12]))
            }
            st.markdown("<br>", unsafe_allow_html=True)
            fig_staff_pie = go.Figure(data=[go.Pie(
                labels=list(m13_back.keys()),
                values=list(m13_back.values()),
                hole=.4,
                marker=dict(colors=['#BEAF87', '#A19276', '#CCCCCC', '#CCCCCC', '#CCCCCC', '#E6E7E8', '#252526']),
                textinfo='value+label',
                showlegend=False
            )])
            fig_staff_pie.update_layout(
                title=f"Проектируемый штат команды (13-й месяц): {sum(m13_back.values())} чел.".replace(",", " "),
                template="plotly_white",
                height=280,
                margin=dict(t=40, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_staff_pie, use_container_width=True)
            
        with col_right:
            st.markdown(f"""
            <div style='background-color: #F8F9FA; padding: 20px; border-radius: 8px; border-left: 5px solid #BEAF87;'>
                <h5 style='color: #252526; font-weight: 700; margin-top:0;'>💡 Шпаргалка Эксперта (Шаг 3)</h5>
                <p style='font-size: 13px; color: #777779; line-height: 1.5;'>
                    <b>Фокус внимания франчайзи:</b> Покажите партнеру каскадную зависимость: HR-рекрутер — это топливо для найма агентов, а агенты — это генераторы сделок. Не экономьте на рекрутинге во 2-й год!
                </p>
                <p style='font-size: 13px; color: #777779; line-height: 1.5;'>
                    <b>Сценарий разговора (скрипт):</b><br>
                    <i>"Во второй год воронка резко вырастает, поэтому мы переходим на профессиональную структуру: добавляем {rop_count} руководителей отделов продаж, которые заберут на себя управление и выведут агентов на новые показатели. Давайте перейдем к воронке продаж, чтобы оцифровать сделки."</i>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    elif step == "4. Двигатель продаж (Воронка)":
        col_left, col_right = st.columns([2, 1.2])
        with col_left:
            st.markdown("#### 📈 Шаг 4: Двигатель продаж и калибровка воронки")
            st.write("Оцифруйте входящий поток клиентов и эффективность работы агентов:")
            
            # Слайдеры для калибровки
            s_meet = st.slider(
                "🤝 Конверсия лид -> встреча, %:",
                min_value=2.0, max_value=20.0, value=float(conversion_meeting), step=0.5,
                help="Стандарт сети Century 21 составляет 10%.",
                key="sales_step4_meet"
            )
            if s_meet != conversion_meeting:
                st.session_state['conversion_meeting'] = s_meet
                st.rerun()
                
            s_deal = st.slider(
                "✍️ Конверсия встреча -> договор, %:",
                min_value=1.0, max_value=30.0, value=float(conversion_deal), step=0.5,
                help="Норматив Century 21 — 15%.",
                key="sales_step4_deal"
            )
            if s_deal != conversion_deal:
                st.session_state['conversion_deal'] = s_deal
                st.rerun()

            s_prepy = st.slider(
                "💰 Конверсия договор -> задаток, %:",
                min_value=10.0, max_value=100.0, value=float(prepayment_rate), step=1.0,
                help="Норматив Century 21 — 70%.",
                key="sales_step4_prepy"
            )
            if s_prepy != prepayment_rate:
                st.session_state['prepayment_rate'] = s_prepy
                st.rerun()

            s_sec = st.slider(
                "🏢 Доля вторичного рынка, %:",
                min_value=0.0, max_value=100.0, value=float(secondary_ratio), step=1.0,
                help="Доля сделок вторичного рынка.",
                key="sales_step4_sec"
            )
            if s_sec != secondary_ratio:
                st.session_state['secondary_ratio'] = s_sec
                st.rerun()
                
            # Funnel chart of month 13
            m13_leads = adj_leads[12]
            m13_meetings = adj_meetings[12]
            m13_contracts = adj_contracts[12]
            m13_prepy = int(adj_prepayments[12])
            
            fig_funnel = go.Figure(go.Funnel(
                y = ["📞 Входящие лиды", "🤝 Встречи в офисе", "✍️ Эксклюзивные Договоры", "💰 Закрытые Сделки"],
                x = [m13_leads, m13_meetings, m13_contracts, m13_prepy],
                textinfo = "value+percent initial",
                marker = dict(color=["#E6E7E8", "#CCCCCC", "#A19276", "#BEAF87"])
            ))
            fig_funnel.update_layout(
                title=f"Прогнозируемая воронка продаж за месяц (13-й месяц проекта)",
                template="plotly_white",
                height=260,
                margin=dict(t=40, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_funnel, use_container_width=True)
            
        with col_right:
            st.markdown(f"""
            <div style='background-color: #F8F9FA; padding: 20px; border-radius: 8px; border-left: 5px solid #BEAF87;'>
                <h5 style='color: #252526; font-weight: 700; margin-top:0;'>💡 Шпаргалка Эксперта (Шаг 4)</h5>
                <p style='font-size: 13px; color: #777779; line-height: 1.5;'>
                    <b>Фокус внимания франчайзи:</b> Покажите партнеру, как всего лишь небольшое увеличение конверсии встреч в договоры (например, с 5% до 6.5%) лавинообразно увеличивает количество сделок за счет роста мастерства обученных агентов.
                </p>
                <p style='font-size: 13px; color: #777779; line-height: 1.5;'>
                    <b>Сценарий разговора (скрипт):</b><br>
                    <i>"При базовых конверсиях {conversion_meeting}% во встречи и {conversion_deal}% в договоры ваш офис к 13-му месяцу будет совершать около {m13_prepy} закрытых сделок в месяц. При среднем чеке это принесет внушительные доходы. Давайте посмотрим на итоговую экономику!"</i>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    elif step == "5. Экономика успеха (Результат)":
        # 1. Сводные метрики триумфа
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric("🏆 Общая выручка ВКД (2 года):", f"{total_revenue_2years:,.0f} ₽".replace(",", " "))
        with col_res2:
            st.metric("📈 Чистая прибыль за 2 года:", f"{total_profit_2years:,.0f} ₽".replace(",", " "))
        with col_res3:
            st.metric("⏳ Срок полной окупаемости:", payback_month)
            
        # J-Curve
        st.markdown("<br>", unsafe_allow_html=True)
        fig_cum_res = go.Figure()
        fig_cum_res.add_trace(go.Scatter(
            x=list(range(25)), y=cum_flow, mode='lines+markers', name='Накопленный кэш-флоу',
            line=dict(color='#BEAF87', width=4),
            marker=dict(size=8, color='#FFFFFF', line=dict(color='#BEAF87', width=2))
        ))
        fig_cum_res.add_shape(type="line", x0=0, y0=0, x1=24, y1=0, line=dict(color="#777779", width=2, dash="dash"))
        fig_cum_res.update_layout(
            title="Интерактивная кривая накопленного кэш-флоу проекта (J-Curve)",
            xaxis_title="Месяцы проекта (0 - старт)", yaxis_title="Баланс кэша, ₽",
            template="plotly_white", height=320, margin=dict(t=40, b=20, l=10, r=10)
        )
        st.plotly_chart(fig_cum_res, use_container_width=True)
        
        # Excel download
        col_ex_1, col_ex_2 = st.columns([2, 1])
        with col_ex_1:
            st.success("🎉 Поздравляем! Финансовая модель вашего будущего офиса CENTURY 21 успешно сгенерирована с учетом всех индивидуальных калибровок!")
        with col_ex_2:
            if openpyxl_available:
                excel_data = generate_excel()
                st.download_button(
                    label="📥 Скачать индивидуальный бизнес-план (Excel)",
                    data=excel_data,
                    file_name=f"C21_Optimal_BusinessPlan_{region_select}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        # Скрытый спойлер со всеми таблицами для экономистов
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📋 Открыть детальный финансовый отчет P&L (для экономистов и аудиторов)", expanded=False):
            st.markdown("ℹ️ *Ниже приведена детальная 35-строчная таблица со всеми зависимыми расчетами, соответствующая оригинальному листу «Бюджет Оптимальный»*")
            
            # Отрисовываем таблицы из v17
            st.markdown("##### 🟢 Раздел P&L 1: Доходы (ВКД)")
            st.dataframe(pd.DataFrame({
                'Показатель': [r[0] for r in revenue_rows_def],
                'Старт': [fmt(r[2]) for r in revenue_rows_def],
                **{str(m): [fmt(aggregate_metric(r[1], r[2], "Месячный (24 месяца)")[m]) for r in revenue_rows_def] for m in range(1, 25)}
            }), use_container_width=True, height=220)
            
            st.markdown("##### 👥 Раздел P&L 2: Расходы на персонал (ФОТ)")
            st.dataframe(pd.DataFrame({
                'Показатель': [r[0] for r in fot_rows_def],
                'Старт': [fmt(r[2]) for r in fot_rows_def],
                **{str(m): [fmt(aggregate_metric(r[1], r[2], "Месячный (24 месяца)")[m]) for r in fot_rows_def] for m in range(1, 25)}
            }), use_container_width=True, height=220)
            
            st.markdown("##### 🏢 Раздел P&L 3: Операционные расходы (OPEX)")
            st.dataframe(pd.DataFrame({
                'Показатель': [r[0] for r in opex_rows_def],
                'Старт': [fmt(r[2]) for r in opex_rows_def],
                **{str(m): [fmt(aggregate_metric(r[1], r[2], "Месячный (24 месяца)")[m]) for r in opex_rows_def] for m in range(1, 25)}
            }), use_container_width=True, height=220)
            
            st.markdown("##### 👑 Раздел P&L 4: Выплаты в ЦО")
            st.dataframe(pd.DataFrame({
                'Показатель': [r[0] for r in hq_rows_def],
                'Старт': [fmt(r[2]) for r in hq_rows_def],
                **{str(m): [fmt(aggregate_metric(r[1], r[2], "Месячный (24 месяца)")[m]) for r in hq_rows_def] for m in range(1, 25)}
            }), use_container_width=True, height=180)
            
            st.markdown("##### 🛠️ Раздел P&L 5: Капитальные вложения (CAPEX)")
            st.dataframe(pd.DataFrame({
                'Показатель': [r[0] for r in capex_rows_def],
                'Старт': [fmt(r[2]) for r in capex_rows_def],
                **{str(m): [fmt(aggregate_metric(r[1], r[2], "Месячный (24 месяца)")[m]) for r in capex_rows_def] for m in range(1, 25)}
            }), use_container_width=True, height=150)

elif app_mode == "📐 Детальный Интерактивный Калькулятор (Calculator)":
    st.markdown("### 📐 Детальный Интерактивный Калькулятор CAPEX & Финансовой модели")
    st.markdown("ℹ️ *Этот режим предоставляет полный контроль над финансовым моделированием. Вы можете детально настроить CAPEX, кадровый план, воронку продаж и мгновенно увидеть результат в виде интерактивного P&L-отчета.*")
    
    calc_tab1, calc_tab1_exp, calc_tab2, calc_tab3, calc_tab4, calc_tab5 = st.tabs([
        "📐 1. Калькулятор CAPEX (Старт)",
        "📐 2. Калькулятор Расходов & ФОТ",
        "📋 3. Финансовый отчет P&L (₽)",
        "📈 4. Операционная воронка (шт.)",
        "👥 5. Кадровое планирование (чел.)",
        "📝 6. Справочник и Методология"
    ])
    
    with calc_tab1:
        st.markdown("#### 📐 Интерактивный калькулятор CAPEX")
        st.write("Настройте параметры помещения, цены на ремонт, мебель и технику. Результаты мгновенно обновят Month 0 в P&L:")
        
        col_calc_left, col_calc_right = st.columns([2.2, 1.3])
        with col_calc_left:
            b1, b2 = st.columns(2)
            with b1:
                st.markdown("**💸 Регистрация и франшиза:**")
                st.number_input("Паушальный взнос (с НДС), ₽", min_value=150000, max_value=1500000, key="calc_pau_fee_widget", value=int(st.session_state['capex_pau_fee']), step=10000)
                st.session_state['capex_pau_fee'] = float(st.session_state.calc_pau_fee_widget)
                
                st.number_input("Роспатент, ₽", min_value=1000, max_value=100000, key="calc_rospatent_widget", value=int(st.session_state['capex_rospatent']), step=1000)
                st.session_state['capex_rospatent'] = float(st.session_state.calc_rospatent_widget)
                
                st.markdown("**🏢 Параметры помещения:**")
                st.slider("Площадь офиса, м²", min_value=40, max_value=140, key="calc_office_area_widget", value=int(st.session_state['capex_office_area']), step=5)
                st.session_state['capex_office_area'] = float(st.session_state.calc_office_area_widget)
                
                st.slider("Норма м² на человека", min_value=4.0, max_value=12.0, key="calc_norm_m2_widget", value=float(st.session_state['capex_norm_m2']), step=0.5)
                st.session_state['capex_norm_m2'] = float(st.session_state.calc_norm_m2_widget)
                
            with b2:
                st.markdown("**💻 Рабочие места (мебель и ПК):**")
                st.number_input("Количество рабочих мест (чел.)", min_value=5, max_value=50, key="calc_workstations_widget", value=int(st.session_state['capex_workstations']), step=1)
                st.session_state['capex_workstations'] = int(st.session_state.calc_workstations_widget)
                
                st.number_input("Стоимость стола, ₽/шт.", min_value=1000, max_value=50000, key="calc_table_price_widget", value=int(st.session_state['capex_table_price']), step=1000)
                st.session_state['capex_table_price'] = float(st.session_state.calc_table_price_widget)
                
                st.number_input("Стоимость стула, ₽/шт.", min_value=1000, max_value=50000, key="calc_stool_price_widget", value=int(st.session_state['capex_stool_price']), step=1000)
                st.session_state['capex_stool_price'] = float(st.session_state.calc_stool_price_widget)
                
                st.number_input("Стоимость компьютера/ПК, ₽/шт.", min_value=10000, max_value=200000, key="calc_computer_price_widget", value=int(st.session_state['capex_computer_price']), step=5000)
                st.session_state['capex_computer_price'] = float(st.session_state.calc_computer_price_widget)
                
            with st.expander("🛠️ Тонкие настройки цен ремонта и прочих вложений", expanded=False):
                b3, b4 = st.columns(2)
                with b3:
                    st.number_input("Стоимость ремонта, ₽/м²", min_value=1000, max_value=50000, key="calc_renov_price_widget", value=int(st.session_state['capex_renov_price']), step=1000)
                    st.session_state['capex_renov_price'] = float(st.session_state.calc_renov_price_widget)
                    
                    st.number_input("Доп. мебель (шкаф, тумба), всего ₽", min_value=10000, max_value=1000000, key="calc_add_furniture_widget", value=int(st.session_state['capex_add_furniture']), step=10000)
                    st.session_state['capex_add_furniture'] = float(st.session_state.calc_add_furniture_widget)
                with b4:
                    st.number_input("Стоимость брендирования, ₽/м²", min_value=500, max_value=20000, key="calc_brand_price_widget", value=int(st.session_state['capex_brand_price']), step=500)
                    st.session_state['capex_brand_price'] = float(st.session_state.calc_brand_price_widget)
                    
                    st.number_input("Роутер, принтер, сеть, всего ₽", min_value=5000, max_value=200000, key="calc_router_printer_widget", value=int(st.session_state['capex_router_printer']), step=5000)
                    st.session_state['capex_router_printer'] = float(st.session_state.calc_router_printer_widget)
            
            p_area = st.session_state['capex_office_area']
            p_work = st.session_state['capex_workstations']
            p_norm = st.session_state['capex_norm_m2']
            p_pau = st.session_state['capex_pau_fee']
            p_rospat = st.session_state['capex_rospatent']
            p_renov = st.session_state['capex_renov_price']
            p_brand = st.session_state['capex_brand_price']
            p_table = st.session_state['capex_table_price']
            p_stool = st.session_state['capex_stool_price']
            p_comp = st.session_state['capex_computer_price']
            p_add = st.session_state['capex_add_furniture']
            p_rout = st.session_state['capex_router_printer']
            
            calc_franchise_val = p_pau + p_rospat
            calc_renovation_val = p_area * p_renov + p_area * p_brand
            calc_equipment_val = p_work * (p_table + p_stool + p_comp) + p_add + p_rout
            calc_total_capex = calc_franchise_val + calc_renovation_val + calc_equipment_val
            
            req_space = p_work * p_norm
            if p_area < req_space:
                st.warning(f"⚠️ **Площадь офиса ниже нормы!** Для {p_work} рабочих мест при норме {p_norm} м²/чел., рекомендуемая площадь — от **{req_space:.0f} м²**. Ваша площадь **{p_area:.0f} м²** может быть тесной.")
            else:
                st.success(f"🟢 **Площадь офиса в норме!** Площадь **{p_area:.0f} м²** достаточна для {p_work} мест при норме {p_norm} м²/чел.")
                
            capex_table_df = pd.DataFrame({
                "Категория / Статья CAPEX": [
                    "► РЕГИСТРАЦИЯ И ФРАНШИЗА",
                    "  ├─ Паушальный взнос (франшиза)",
                    "  ├─ Госпошлина (Роспатент)",
                    "★ ИТОГО РЕГИСТРАЦИЯ",
                    "► ОБУСТРОЙСТВО ОФИСА",
                    "  ├─ Ремонт помещения",
                    "  ├─ Брендирование и вывески",
                    "  ├─ Офисные столы",
                    "  ├─ Офисные стулья",
                    "  ├─ Компьютеры / Мониторы",
                    "  ├─ Доп. мебель (шкаф, тумба)",
                    "  └─ Роутер, принтер, сеть",
                    "★ ИТОГО ОФИС",
                    "🏆 ВСЕГО СТАРТОВЫЕ ИНВЕСТИЦИИ (CAPEX)"
                ],
                "Кол-во / Параметр": [
                    "", "1", "1", "", "", f"{p_area:.0f} м²", f"{p_area:.0f} м²", f"{p_work} шт.", f"{p_work} шт.", f"{p_work} шт.", "1", "1", "", ""
                ],
                "Цена / Тариф": [
                    "",
                    f"{p_pau:,.0f} ₽".replace(",", " "),
                    f"{p_rospat:,.0f} ₽".replace(",", " "),
                    "",
                    "",
                    f"{p_renov:,.0f} ₽/м²".replace(",", " "),
                    f"{p_brand:,.0f} ₽/м²".replace(",", " "),
                    f"{p_table:,.0f} ₽/шт.".replace(",", " "),
                    f"{p_stool:,.0f} ₽/шт.".replace(",", " "),
                    f"{p_comp:,.0f} ₽/шт.".replace(",", " "),
                    f"{p_add:,.0f} ₽".replace(",", " "),
                    f"{p_rout:,.0f} ₽".replace(",", " "),
                    "",
                    ""
                ],
                "Сумма": [
                    "",
                    f"{p_pau:,.0f} ₽".replace(",", " "),
                    f"{p_rospat:,.0f} ₽".replace(",", " "),
                    f"{calc_franchise_val:,.0f} ₽".replace(",", " "),
                    "",
                    f"{p_area * p_renov:,.0f} ₽".replace(",", " "),
                    f"{p_area * p_brand:,.0f} ₽".replace(",", " "),
                    f"{p_work * p_table:,.0f} ₽".replace(",", " "),
                    f"{p_work * p_stool:,.0f} ₽".replace(",", " "),
                    f"{p_work * p_comp:,.0f} ₽".replace(",", " "),
                    f"{p_add:,.0f} ₽".replace(",", " "),
                    f"{p_rout:,.0f} ₽".replace(",", " "),
                    f"{calc_renovation_val + calc_equipment_val:,.0f} ₽".replace(",", " "),
                    f"{calc_total_capex:,.0f} ₽".replace(",", " ")
                ]
            })
            st.dataframe(capex_table_df, use_container_width=True, height=450)
            
        with col_calc_right:
            capex_structure_calc = {
                'Паушальный + Роспатент': calc_franchise_val,
                'Ремонт и Брендирование': p_area * p_renov + p_area * p_brand,
                'Мебель и Техника': p_work * (p_table + p_stool) + p_work * p_comp,
                'Прочие и доп.мебель': p_add + p_rout,
                'Стартовый резерв': start_opex_total
            }
            fig_calc_donut = go.Figure(data=[go.Pie(
                labels=list(capex_structure_calc.keys()),
                values=list(capex_structure_calc.values()),
                hole=.4,
                marker=dict(colors=['#BEAF87', '#A19276', '#252526', '#777779', '#CCCCCC']),
                textinfo='percent',
                texttemplate='%{label}:<br>%{percent}'
            )])
            fig_calc_donut.update_layout(
                title=f"Стартовый бюджет (Месяц 0): {calc_total_capex + start_opex_total:,.0f} ₽".replace(",", " "),
                template="plotly_white",
                height=280,
                margin=dict(t=40, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_calc_donut, use_container_width=True)
            
            st.markdown(f"""
            <div style='background-color: #F8F9FA; padding: 15px; border-radius: 8px; border-left: 5px solid #BEAF87; margin-top:15px;'>
                <h6 style='color: #252526; font-weight: 700; margin-top:0;'>💡 Бизнес-подсказка:</h6>
                <p style='font-size: 12px; color: #777779; line-height: 1.5;'>
                    Норматив площади на 1 человека — важный маркер для поддержания комфортного микроклимата. Для столов шириной 1.2м рекомендуется закладывать от <b>{norm_m2_val} м²</b> на место.<br><br>
                    При площади офиса <b>{p_area:.0f} м²</b> вы получаете оптимальную плотность и соблюдаете требования франшизы к качеству рабочей зоны.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    with calc_tab1_exp:
        st.markdown("#### 📐 Интерактивный калькулятор расходов, ФОТ и OPEX")
        st.write("Настройте ставки вознаграждения, fixed-оклады бэк-офиса, payroll-налоги и статьи операционных расходов:")
        
        col_exp_l, col_exp_r = st.columns([1, 1])
        with col_exp_l:
            st.markdown("##### 💼 ФОТ: агентское вознаграждение & комиссии")
            st.write("Установите процентные ставки со сделок или фиксированные премии за период/сделку. Чекбокс отключает позицию из расчета:")
            
            # Helper for layout
            def render_payout_row(label, session_key, min_v, max_v, step_v, is_percent=True):
                col_chk, col_val = st.columns([0.15, 0.85])
                with col_chk:
                    is_active = st.checkbox("", value=st.session_state['role_active'].get(label, True), key=f"chk_active_{session_key}")
                    st.session_state['role_active'][label] = is_active
                with col_val:
                    if is_percent:
                        v = st.number_input(f"{label} (% ставку):", min_value=float(min_v), max_value=float(max_v), value=float(st.session_state[session_key]), step=float(step_v), key=f"inp_rate_{session_key}")
                    else:
                        v = st.number_input(f"{label} (₽ тариф):", min_value=float(min_v), max_value=float(max_v), value=float(st.session_state[session_key]), step=float(step_v), key=f"inp_rate_{session_key}")
                    st.session_state[session_key] = v
                    
            render_payout_row("Агент: категория D", "rate_agent_D", 10, 100, 1)
            render_payout_row("Агент: категория C", "rate_agent_C", 10, 100, 1)
            render_payout_row("Агент: категория B", "rate_agent_B", 10, 100, 1)
            render_payout_row("Агент: категория A", "rate_agent_A", 10, 100, 1)
            
            render_payout_row("РОП: категория C", "rate_rop_C_bonus", 0.1, 30.0, 0.5)
            render_payout_row("РОП: категория B", "rate_rop_B_bonus", 0.1, 30.0, 0.5)
            render_payout_row("Администратор офиса", "rate_admin_bonus", 0.1, 30.0, 0.5)
            
            render_payout_row("HR/рекрутер", "rate_hr_bonus", 500, 50000, 100, is_percent=False)
            render_payout_row("РОС/тренер", "rate_ros_bonus", 5000, 200000, 1000, is_percent=False)
            render_payout_row("Юрист", "rate_jurist_bonus", 0.5, 50.0, 0.5)
            render_payout_row("Ипотечный Брокер", "rate_mort_bonus", 0.5, 50.0, 0.5)
            render_payout_row("Листинг-менеджер", "rate_listing_bonus", 100, 10000, 50, is_percent=False)
            render_payout_row("Фотограф", "rate_photo_bonus", 5000, 100000, 1000, is_percent=False)
            render_payout_row("Маркетолог/SMM", "rate_smm_bonus", 10000, 500000, 5000, is_percent=False)

        with col_exp_r:
            st.markdown("##### 👔 ФОТ: оклады & налоги")
            st.write("Настройте гарантированные оклады специалистов бэк-офиса:")
            
            def render_salary_row(label, session_key, min_v, max_v, step_v):
                v = st.number_input(f"Оклад {label}, ₽", min_value=int(min_v), max_value=int(max_v), value=int(st.session_state[session_key]), step=int(step_v), key=f"sal_{session_key}_widget")
                st.session_state[session_key] = float(v)
                
            render_salary_row("РОП: категория C", "sal_rop_C", 10000, 300000, 5000)
            render_salary_row("РОП: категория B", "sal_rop_B", 10000, 400000, 5000)
            render_salary_row("Администратор офиса", "sal_admin", 10000, 200000, 5000)
            render_salary_row("HR/рекрутер", "sal_hr", 10000, 300000, 5000)
            render_salary_row("РОС/тренер", "sal_ros", 10000, 300000, 5000)
            render_salary_row("Юрист", "sal_jurist", 10000, 400000, 5000)
            render_salary_row("Ипотечный Брокер", "sal_mort", 10000, 400000, 5000)
            render_salary_row("Листинг-менеджер", "sal_listing", 10000, 200000, 5000)
            render_salary_row("Маркетолог/SMM", "sal_smm", 10000, 400000, 5000)
            render_salary_row("Фотограф", "sal_photo", 10000, 200000, 5000)
            
            st.markdown("<br>", unsafe_allow_html=True)
            taxes_pr = st.slider("ФОТ: налоги, %", min_value=10, max_value=60, value=int(st.session_state['taxes_payroll_rate']), step=1, key="taxes_payroll_rate_widget")
            st.session_state['taxes_payroll_rate'] = float(taxes_pr)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("##### 🏢 Операционные расходы (OPEX)")
        col_opex_1, col_opex_2, col_opex_3 = st.columns(3)
        with col_opex_1:
            st.number_input("Интернет, ₽", value=int(st.session_state['opex_internet']), step=500, key="inp_op_internet")
            st.session_state['opex_internet'] = float(st.session_state.inp_op_internet)
            
            st.number_input("Сотовая связь, ₽/чел", value=int(st.session_state['opex_mobile']), step=100, key="inp_op_mobile")
            st.session_state['opex_mobile'] = float(st.session_state.inp_op_mobile)
            
            st.number_input("Сервисы по набору базы, ₽", value=int(st.session_state['opex_db_services']), step=500, key="inp_op_db")
            st.session_state['opex_db_services'] = float(st.session_state.inp_op_db)
            
            st.number_input("Канцелярия, ₽/чел", value=int(st.session_state['opex_kanc']), step=100, key="inp_op_kanc")
            st.session_state['opex_kanc'] = float(st.session_state.inp_op_kanc)
            
        with col_opex_2:
            st.number_input("Реклама объектов, ₽/чел", value=int(st.session_state['opex_reklama']), step=500, key="inp_op_reklama")
            st.session_state['opex_reklama'] = float(st.session_state.inp_op_reklama)
            
            st.number_input("HeadHunter.ru, ₽/мес", value=int(st.session_state['opex_hh']), step=5000, key="inp_op_hh")
            st.session_state['opex_hh'] = float(st.session_state.inp_op_hh)
            
            st.number_input("Бухгалтерия: аутсорс, ₽", value=int(st.session_state['opex_buh']), step=1000, key="inp_op_buh")
            st.session_state['opex_buh'] = float(st.session_state.inp_op_buh)
            
            st.number_input("Услуги банка, ₽", value=int(st.session_state['opex_bank']), step=500, key="inp_op_bank")
            st.session_state['opex_bank'] = float(st.session_state.inp_op_bank)
            
        with col_opex_3:
            st.number_input("Аренда офиса (цена за м²), ₽/м²", value=int(st.session_state['opex_rent_price_m2']), step=100, key="inp_op_rent")
            st.session_state['opex_rent_price_m2'] = float(st.session_state.inp_op_rent)
            
            st.number_input("Уборка офиса, ₽", value=int(st.session_state['opex_cleaning']), step=1000, key="inp_op_cleaning")
            st.session_state['opex_cleaning'] = float(st.session_state.inp_op_cleaning)
            
            st.number_input("ГСМ, ₽", value=int(st.session_state['opex_gsm']), step=500, key="inp_op_gsm")
            st.session_state['opex_gsm'] = float(st.session_state.inp_op_gsm)
            
            st.number_input("Доставка/курьер, ₽", value=int(st.session_state['opex_courier']), step=1000, key="inp_op_courier")
            st.session_state['opex_courier'] = float(st.session_state.inp_op_courier)
            
            st.number_input("Корпоративные мероприятия, ₽", value=int(st.session_state['opex_events']), step=1000, key="inp_op_events")
            st.session_state['opex_events'] = float(st.session_state.inp_op_events)

        if st.button("⚡ Применить расходы и пересчитать финансовую модель", use_container_width=True, key="btn_apply_expenses"):
            st.success("Все расходные сетки, оклады, социальные налоги и операционные затраты успешно сохранены в сессию. Пересчет всей модели...")
            st.rerun()
    with calc_tab2:
        st.markdown("#### 📋 Финансовый отчет P&L (₽)")
        st.markdown("ℹ️ *Все показатели пересчитываются автоматически на основе ваших корректировок CAPEX в Tab 1!*")
        
        calc_time_scale = st.radio(
            "📅 Масштаб времени отчета (Калькулятор):",
            options=["Месячный (24 месяца)", "Квартальный (8 кварталов)", "Годовой (2 года)"],
            horizontal=True,
            key="calc_time_scale_widget"
        )
        
        st.markdown("##### 🟢 Раздел P&L 1: Доходы (ВКД)")
        st.dataframe(pd.DataFrame({
            'Показатель': [r[0] for r in revenue_rows_def],
            'Старт': [fmt(r[2]) for r in revenue_rows_def],
            **{str(m): [fmt(aggregate_metric(r[1], r[2], calc_time_scale)[m]) for r in revenue_rows_def] for m in range(1, len(aggregate_metric(revenue_rows_def[0][1], revenue_rows_def[0][2], calc_time_scale)))}
        }), use_container_width=True, height=220)
        
        st.markdown("##### 👥 Раздел P&L 2: Расходы на персонал (ФОТ)")
        st.dataframe(pd.DataFrame({
            'Показатель': [r[0] for r in fot_rows_def],
            'Старт': [fmt(r[2]) for r in fot_rows_def],
            **{str(m): [fmt(aggregate_metric(r[1], r[2], calc_time_scale)[m]) for r in fot_rows_def] for m in range(1, len(aggregate_metric(fot_rows_def[0][1], fot_rows_def[0][2], calc_time_scale)))}
        }), use_container_width=True, height=220)
        
        st.markdown("##### 🏢 Раздел P&L 3: Операционные расходы (OPEX)")
        st.dataframe(pd.DataFrame({
            'Показатель': [r[0] for r in opex_rows_def],
            'Старт': [fmt(r[2]) for r in opex_rows_def],
            **{str(m): [fmt(aggregate_metric(r[1], r[2], calc_time_scale)[m]) for r in opex_rows_def] for m in range(1, len(aggregate_metric(opex_rows_def[0][1], opex_rows_def[0][2], calc_time_scale)))}
        }), use_container_width=True, height=220)
        
        st.markdown("##### 👑 Раздел P&L 4: Выплаты в ЦО")
        st.dataframe(pd.DataFrame({
            'Показатель': [r[0] for r in hq_rows_def],
            'Старт': [fmt(r[2]) for r in hq_rows_def],
            **{str(m): [fmt(aggregate_metric(r[1], r[2], calc_time_scale)[m]) for r in hq_rows_def] for m in range(1, len(aggregate_metric(hq_rows_def[0][1], hq_rows_def[0][2], calc_time_scale)))}
        }), use_container_width=True, height=180)
        
        st.markdown("##### 🛠️ Раздел P&L 5: Капитальные вложения (CAPEX)")
        st.dataframe(pd.DataFrame({
            'Показатель': [r[0] for r in capex_rows_def],
            'Старт': [fmt(r[2]) for r in capex_rows_def],
            **{str(m): [fmt(aggregate_metric(r[1], r[2], calc_time_scale)[m]) for r in capex_rows_def] for m in range(1, len(aggregate_metric(capex_rows_def[0][1], capex_rows_def[0][2], calc_time_scale)))}
        }), use_container_width=True, height=150)
        
    with calc_tab3:
        st.markdown("#### 📈 Операционные показатели и Драйверы воронки (шт.)")
        st.markdown("ℹ️ *Здесь настраиваются плановые показатели воронки продаж и конверсии (в штуках) по месяцам 1-24. Вы можете редактировать ячейки **колонки Старт (коэффициенты, % и нормативы)** или месяцев 1-24 вручную, и вся цепочка мгновенно пересчитается.*")
        
        drivers_labels = [
            '  ├─ Звонки/лиды',
            '  ├─ Встречи',
            '  ├─ Договоры',
            '  ├─ Задаток/аванс',
            '  ├─ Сделки: вторичный рынок',
            '  ├─ Сделки: первичный рынок',
            '  ├─ Сделки: аренда',
            '  ├─ Сделки: загородная',
            '  ├─ Сделки: зарубежная',
            '  ├─ Сделки: прочее (МЛС, срочновыкуп, сайт)',
            '  ├─ Сервисы: ипотека',
            '  ├─ Сервисы: страхование',
            '  └─ Сервисы: юр. сопровождение'
        ]
        
        df_drivers_data = {'Категория / Статья': drivers_labels}
        
        # Pull numeric values from session state for Start column
        df_drivers_data['Старт'] = [
            float(st.session_state.get('start_driver_leads_per_agent', 60.0)),
            float(st.session_state.get('start_driver_meetings_pct', 10.0)),
            float(st.session_state.get('start_driver_contracts_pct', 15.0)),
            float(st.session_state.get('start_driver_prepayments_pct', 70.0)),
            float(st.session_state.get('start_driver_secondary_pct', 90.0)),
            float(st.session_state.get('start_driver_primary_pct', 10.0)),
            float(st.session_state.get('start_driver_rent_val', 3.0)),
            float(st.session_state.get('start_driver_suburban_val', 0.0)),
            float(st.session_state.get('start_driver_overseas_val', 0.0)),
            float(st.session_state.get('start_driver_other_pct', 0.5)),
            float(st.session_state.get('start_driver_mortgage_pct', 17.0)),
            float(st.session_state.get('start_driver_insurance_pct', 10.0)),
            float(st.session_state.get('start_driver_legal_pct', 17.0))
        ]
        
        for idx, col in enumerate(months):
            ag_D_c = get_headcount_override('  ├─ Агент: категория D', col, DEFAULT_HEADCOUNTS['Агент: категория D'][idx])
            ag_C_c = get_headcount_override('  ├─ Агент: категория C', col, DEFAULT_HEADCOUNTS['Агент: категория C'][idx])
            ag_B_c = get_headcount_override('  ├─ Агент: категория B', col, DEFAULT_HEADCOUNTS['Агент: категория B'][idx])
            ag_A_c = get_headcount_override('  └─ Агент: категория A', col, DEFAULT_HEADCOUNTS['Агент: категория A'][idx])
            t_agents_idx = ag_D_c + ag_C_c + ag_B_c + ag_A_c
            
            # Use current session state factors for calculation
            leads_factor = float(st.session_state.get('start_driver_leads_per_agent', 60.0))
            meetings_factor = float(st.session_state.get('start_driver_meetings_pct', 10.0)) / 100.0
            contracts_factor = float(st.session_state.get('start_driver_contracts_pct', 15.0)) / 100.0
            prepy_factor = float(st.session_state.get('start_driver_prepayments_pct', 70.0)) / 100.0
            sec_factor = float(st.session_state.get('start_driver_secondary_pct', 90.0)) / 100.0
            prim_factor = float(st.session_state.get('start_driver_primary_pct', 10.0)) / 100.0
            other_factor = float(st.session_state.get('start_driver_other_pct', 0.5)) / 100.0
            mort_factor = float(st.session_state.get('start_driver_mortgage_pct', 17.0)) / 100.0
            ins_factor = float(st.session_state.get('start_driver_insurance_pct', 10.0)) / 100.0
            legal_factor = float(st.session_state.get('start_driver_legal_pct', 17.0)) / 100.0
            
            d_leads = leads_factor * t_agents_idx
            d_meetings = int(d_leads * meetings_factor)
            d_contracts = int(d_meetings * contracts_factor)
            d_prepayments = d_contracts * prepy_factor
            
            d_sec = d_prepayments * sec_factor
            d_prim = d_prepayments * prim_factor
            d_rent = get_driver_override('  ├─ Сделки: аренда', col, float(base_deals_rent[idx]) if idx > 0 else float(st.session_state.get('start_driver_rent_val', 3.0)))
            d_sub = get_driver_override('  ├─ Сделки: загородная', col, float(base_deals_suburban[idx]) if idx > 0 else float(st.session_state.get('start_driver_suburban_val', 0.0)))
            d_overseas = get_driver_override('  ├─ Сделки: зарубежная', col, float(base_deals_overseas[idx]) if idx > 0 else float(st.session_state.get('start_driver_overseas_val', 0.0)))
            
            d_total_trans = d_sec + d_prim + d_rent + d_sub + d_overseas
            d_other = d_total_trans * other_factor
            
            d_mort = d_contracts * mort_factor
            d_ins = d_contracts * ins_factor
            d_legal = d_contracts * legal_factor
            
            df_drivers_data[col] = [
                get_driver_override('  ├─ Звонки/лиды', col, d_leads),
                get_driver_override('  ├─ Встречи', col, d_meetings),
                get_driver_override('  ├─ Договоры', col, d_contracts),
                get_driver_override('  ├─ Задаток/аванс', col, d_prepayments),
                get_driver_override('  ├─ Сделки: вторичный рынок', col, d_sec),
                get_driver_override('  ├─ Сделки: первичный рынок', col, d_prim),
                get_driver_override('  ├─ Сделки: аренда', col, d_rent),
                get_driver_override('  ├─ Сделки: загородная', col, d_sub),
                get_driver_override('  ├─ Сделки: зарубежная', col, d_overseas),
                get_driver_override('  ├─ Сделки: прочее (МЛС, срочновыкуп, сайт)', col, d_other),
                get_driver_override('  ├─ Сервисы: ипотека', col, d_mort),
                get_driver_override('  ├─ Сервисы: страхование', col, d_ins),
                get_driver_override('  └─ Сервисы: юр. сопровождение', col, d_legal)
            ]
        df_drivers = pd.DataFrame(df_drivers_data)
        
        col_config_drv = {
            "Категория / Статья": st.column_config.TextColumn(disabled=True),
            "Старт": st.column_config.NumberColumn(label="Старт (Параметр/%/Норма)", format="%.1f", min_value=0.0)
        }
        for col in df_drivers.columns[2:]: # Skip 'Категория / Статья' and 'Старт'
            col_config_drv[col] = st.column_config.NumberColumn(format="%.1f", min_value=0.0)
            
        edited_drivers_df = st.data_editor(
            df_drivers,
            use_container_width=True,
            disabled=["Категория / Статья"],
            column_config=col_config_drv,
            key="drivers_editor_calc_tab3",
            height=450
        )
        
        drivers_changed = False
        for idx_row in range(len(df_drivers)):
            row_name = df_drivers.at[idx_row, 'Категория / Статья']
            
            # Detect changes in 'Старт' column
            val_base_start = df_drivers.at[idx_row, 'Старт']
            val_edited_start = edited_drivers_df.at[idx_row, 'Старт']
            if float(val_base_start) != float(val_edited_start):
                parsed_val = float(parse_value(val_edited_start))
                if idx_row == 0: st.session_state['start_driver_leads_per_agent'] = parsed_val
                elif idx_row == 1: st.session_state['start_driver_meetings_pct'] = parsed_val
                elif idx_row == 2: st.session_state['start_driver_contracts_pct'] = parsed_val
                elif idx_row == 3: st.session_state['start_driver_prepayments_pct'] = parsed_val
                elif idx_row == 4:
                    st.session_state['start_driver_secondary_pct'] = parsed_val
                    st.session_state['start_driver_primary_pct'] = 100.0 - parsed_val
                elif idx_row == 5:
                    st.session_state['start_driver_primary_pct'] = parsed_val
                    st.session_state['start_driver_secondary_pct'] = 100.0 - parsed_val
                elif idx_row == 6: st.session_state['start_driver_rent_val'] = parsed_val
                elif idx_row == 7: st.session_state['start_driver_suburban_val'] = parsed_val
                elif idx_row == 8: st.session_state['start_driver_overseas_val'] = parsed_val
                elif idx_row == 9: st.session_state['start_driver_other_pct'] = parsed_val
                elif idx_row == 10: st.session_state['start_driver_mortgage_pct'] = parsed_val
                elif idx_row == 11: st.session_state['start_driver_insurance_pct'] = parsed_val
                elif idx_row == 12: st.session_state['start_driver_legal_pct'] = parsed_val
                drivers_changed = True
                
            # Detect changes in Months columns
            for col in df_drivers.columns[2:]: # Skip 'Категория / Статья' and 'Старт'
                val_base = df_drivers.at[idx_row, col]
                val_edited = edited_drivers_df.at[idx_row, col]
                if float(val_base) != float(val_edited):
                    st.session_state['driver_overrides'][(row_name, col)] = parse_value(val_edited)
                    drivers_changed = True
                    
        if drivers_changed:
            st.success("Драйверы воронки обновлены! Пересчет финансовой модели...")
            st.rerun()
            
        if st.button("🔄 Сбросить ручные изменения воронки (шт.)", use_container_width=True):
            st.session_state['driver_overrides'] = {}
            st.session_state['start_driver_leads_per_agent'] = 60.0
            st.session_state['start_driver_meetings_pct'] = 10.0
            st.session_state['start_driver_contracts_pct'] = 15.0
            st.session_state['start_driver_prepayments_pct'] = 70.0
            st.session_state['start_driver_secondary_pct'] = 90.0
            st.session_state['start_driver_primary_pct'] = 10.0
            st.session_state['start_driver_rent_val'] = 3.0
            st.session_state['start_driver_suburban_val'] = 0.0
            st.session_state['start_driver_overseas_val'] = 0.0
            st.session_state['start_driver_other_pct'] = 0.5
            st.session_state['start_driver_mortgage_pct'] = 17.0
            st.session_state['start_driver_insurance_pct'] = 10.0
            st.session_state['start_driver_legal_pct'] = 17.0
            st.success("Все кадровые/драйверные корректировки сброшены!")
            st.rerun()

        # --- SECOND TABLE: COMMISSION VKD ---
        st.markdown("<br><h4>💰 Финансовая воронка доходов — Комиссия ВКД (₽)</h4>", unsafe_allow_html=True)
        st.markdown("ℹ️ *Здесь настраиваются средние тарифы/комиссии в колонке **Старт**, а доходы за месяцы 1-24 рассчитываются автоматически как произведение тарифа на количество сделок из воронки выше.*")
        
        vkd_labels = [
            '  ├─ Сделки: вторичный рынок',
            '  ├─ Сделки: первичный рынок',
            '  ├─ Сделки: аренда',
            '  ├─ Сделки: загородная',
            '  ├─ Сделки: зарубежная',
            '  ├─ Сделки: прочее (МЛС, срочновыкуп, сайт)',
            '  ├─ Сервисы: ипотека',
            '  ├─ Сервисы: страхование',
            '  ├─ Сервисы: юр. сопровождение',
            '★ ИТОГО ДОХОДЫ',
            '★ НАЛОГ УСН (7%)'
        ]
        
        df_vkd_data = {'Направление ВКД': vkd_labels}
        df_vkd_data['Старт'] = [
            float(st.session_state.get('comm_secondary', 360000.0)),
            float(st.session_state.get('comm_primary', 440000.0)),
            float(st.session_state.get('comm_rent_val', 80000.0)),
            float(st.session_state.get('comm_suburban', 500000.0)),
            float(st.session_state.get('comm_overseas', 220000.0)),
            float(st.session_state.get('comm_other_p', 252000.0)),
            float(st.session_state.get('comm_mortgage', 70000.0)),
            float(st.session_state.get('comm_insurance', 18000.0)),
            float(st.session_state.get('comm_legal', 150000.0)),
            0.0,
            0.0
        ]
        
        for idx, col in enumerate(months):
            df_vkd_data[col] = [
                float(rev_secondary_list[idx]),
                float(rev_primary_list[idx]),
                float(rev_rent_list[idx]),
                float(rev_suburban_list[idx]),
                float(rev_overseas_list[idx]),
                float(rev_other_p_list[idx]),
                float(rev_mortgage_list[idx]),
                float(rev_insurance_list[idx]),
                float(rev_legal_list[idx]),
                float(rev_total_list[idx]),
                float(taxes_usn_list[idx])
            ]
            
        df_vkd = pd.DataFrame(df_vkd_data)
        
        col_config_vkd = {
            "Направление ВКД": st.column_config.TextColumn(disabled=True),
            "Старт": st.column_config.NumberColumn(label="Старт (Тариф)", format="%d ₽", min_value=0.0)
        }
        for col in df_vkd.columns[2:]: # months
            col_config_vkd[col] = st.column_config.NumberColumn(format="%d ₽", min_value=0.0)
            
        edited_vkd_df = st.data_editor(
            df_vkd,
            use_container_width=True,
            disabled=["Направление ВКД"] + months,
            column_config=col_config_vkd,
            key="vkd_editor_calc_tab3",
            height=400
        )
        
        vkd_changed = False
        for idx_row in range(len(df_vkd)):
            if idx_row >= 9:
                continue
            val_base = df_vkd.at[idx_row, 'Старт']
            val_edited = edited_vkd_df.at[idx_row, 'Старт']
            if float(val_base) != float(val_edited):
                parsed_val = float(parse_value(val_edited))
                if idx_row == 0: st.session_state['comm_secondary'] = parsed_val
                elif idx_row == 1: st.session_state['comm_primary'] = parsed_val
                elif idx_row == 2: st.session_state['comm_rent_val'] = parsed_val
                elif idx_row == 3: st.session_state['comm_suburban'] = parsed_val
                elif idx_row == 4: st.session_state['comm_overseas'] = parsed_val
                elif idx_row == 5: st.session_state['comm_other_p'] = parsed_val
                elif idx_row == 6: st.session_state['comm_mortgage'] = parsed_val
                elif idx_row == 7: st.session_state['comm_insurance'] = parsed_val
                elif idx_row == 8: st.session_state['comm_legal'] = parsed_val
                vkd_changed = True
                
        if vkd_changed:
            st.success("Тарифы комиссий ВКД обновлены! Пересчет финансовой модели...")
            st.rerun()
            
        # --- NEW: DETAILED MATHEMATICAL VOLUMETRIC FUNNEL GUIDE ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background-color: #F8F9FA; padding: 20px; border-radius: 8px; border-left: 5px solid #BEAF87;'>
            <h5 style='color: #252526; font-weight: 700; margin-top:0;'>🧠 Логика и формулы каскадного расчета воронки (в штуках):</h5>
            <p style='font-size: 13px; color: #555; line-height: 1.6;'>
                Старая статическая воронка полностью заменена на <b>динамическую каскадную модель</b>, в которой каждый последующий шаг математически вытекает из предыдущего, а вся цепочка начинается от <b>реального количества активных агентов в офисе</b> (настраивается во вкладке 4):
            </p>
            <ul style='font-size: 12.5px; color: #555; padding-left: 20px; line-height: 1.6;'>
                <li>📞 <b>Звонки/лиды (в единицах):</b> Рассчитываются автоматически по формуле: <code>60 звонков в месяц на каждого работающего агента</code> (сумма категорий D, C, B, A). С ростом вашего штата лавинообразно и пропорционально растет входящий трафик!</li>
                <li>🤝 <b>Встречи (в единицах):</b> Базовый расчет равен <code>10.0%</code> от количества звонков/лидов. Этот процент выставляется вручную в сайдбаре воронки или в ячейках таблицы.</li>
                <li>✍️ <b>Договоры (в единицах):</b> Базовый расчет равен <code>15.0%</code> от количества встреч (конверсия из встречи в подписанный эксклюзивный договор).</li>
                <li>💰 <b>Задаток/аванс (в единицах):</b> Базовый расчет равен <code>70.0%</code> от договоров (конверсия из эксклюзивного договора в полученный задаток).</li>
                <li>🏢 <b>Сделки: вторичный рынок (в единицах):</b> Базовый расчет равен <code>90.0%</code> от задатков/авансов (доля вторичного рынка в структуре сделок).</li>
                <li>🏗️ <b>Сделки: первичный рынок (в единицах):</b> Базовый расчет равен <code>10.0%</code> от задатков/авансов (доля новостроек). 
                    <br><i><b>UX-Фишка:</b> Чтобы исключить математические ошибки, сумма долей вторичного и первичного рынков зафиксирована на уровне 100%. При регулировке ползунка вторички доля первички пересчитывается автоматически!</i></li>
                <li>🔑 <b>Сделки: аренда, загородная, зарубежная:</b> Поля полностью разблокированы для ручного ввода нужного вам количества единиц в таблице (по умолчанию подтягиваются базовые значения).</li>
                <li>🔄 <b>Сделки: прочее (МЛС, срочновыкуп, сайт) в единицах:</b> Рассчитываются автоматически как <code>0.5%</code> от общего количества закрытых транзакций (сумма вторички, первички, аренды, загородной и зарубежной недвижимости).</li>
                <li>🏦 <b>Сервисы: ипотека (в единицах):</b> Автоматический расчет равен <code>17.0%</code> от количества договоров (проникновение ипотечного сервиса).</li>
                <li>🛡️ <b>Сервисы: страхование (в единицах):</b> Автоматический расчет равен <code>10.0%</code> от количества договоров.</li>
                <li>⚖️ <b>Сервисы: юр. сопровождение (в единицах):</b> Автоматический расчет равен <code>17.0%</code> от количества договоров.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with calc_tab4:
        st.markdown("### 👥 Кадровое планирование и симулятор штата (1-й год)")
        st.markdown("ℹ️ *Здесь настраивается штат бэк-офиса и агентов на первые 12 месяцев. Вы можете редактировать ячейки вручную или использовать **Генератор темпа роста в %** для автоматического планирования динамики.*")
        
        # --- NEW: RAPID EXPANSION TOGGLES ---
        st.markdown("##### 🚀 Быстрое кадровое масштабирование")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            add_rop_m3_val = st.checkbox(
                "Добавить +1 РОП: категория C (с 3-го месяца)", 
                value=st.session_state.get('add_rop_m3', False),
                key="add_rop_m3_widget"
            )
            if add_rop_m3_val != st.session_state.get('add_rop_m3', False):
                st.session_state['add_rop_m3'] = add_rop_m3_val
                st.rerun()
        with col_t2:
            add_admin_m6_val = st.checkbox(
                "Добавить +1 Офис-менеджер (Администратор) (с 6-го месяца)", 
                value=st.session_state.get('add_admin_m6', False),
                key="add_admin_m6_widget"
            )
            if add_admin_m6_val != st.session_state.get('add_admin_m6', False):
                st.session_state['add_admin_m6'] = add_admin_m6_val
                st.rerun()
        
        # Pre-initialize Month 1 for HR and ROP if they are not set
        if ('  ├─ HR/рекрутер', '1') not in st.session_state['headcount_overrides']:
            st.session_state['headcount_overrides'][('  ├─ HR/рекрутер', '1')] = 1
        if ('  ├─ РОП: категория C', '1') not in st.session_state['headcount_overrides']:
            st.session_state['headcount_overrides'][('  ├─ РОП: категория C', '1')] = 1
            
        bo_labels = [
            '  ├─ РОП: категория C',
            '  ├─ РОП: категория B',
            '  ├─ Администратор офиса',
            '  ├─ HR/рекрутер',
            '  ├─ РОС/тренер',
            '  ├─ Юрист',
            '  ├─ Ипотечный Брокер',
            '  ├─ Листинг-менеджер',
            '  └─ Маркетолог/SMM'
        ]
        
        agent_labels = [
            '  ├─ Агент: категория D',
            '  ├─ Агент: категория C',
            '  ├─ Агент: категория B',
            '  ├─ Агент: категория A',
            '  └─ Итого: агенты'
        ]
        
        staff_labels_1year = bo_labels + agent_labels
        
        # Default headcount function helper
        def get_def_hc(role_clean, month_idx):
            clean_role = role_clean.replace('  ├─ ', '').replace('  └─ ', '').replace('Маркетолог/SMM', 'Маркетолог/SMM').strip()
            if clean_role == 'Итого: агенты':
                return 0
            base_hc = DEFAULT_HEADCOUNTS.get(clean_role, [0]*24)[month_idx]
            if clean_role == 'РОП: категория C' and (month_idx + 1) >= 3 and st.session_state.get('add_rop_m3', False):
                base_hc += 1
            if clean_role == 'Администратор офиса' and (month_idx + 1) >= 6 and st.session_state.get('add_admin_m6', False):
                base_hc += 1
            return base_hc
            
        # Build 12-month staffing DataFrame
        m_cols = [str(m) for m in range(1, 13)]
        df_staff_data = {'Категория / Должность': staff_labels_1year}
        
        for m_str in m_cols:
            m_idx = int(m_str) - 1
            col_vals = []
            
            # 1. Backoffice roles
            for r in bo_labels:
                col_vals.append(get_headcount_override(r, m_str, get_def_hc(r, m_idx)))
                
            # 2. Agent roles
            agent_sum = 0
            for r in agent_labels[:-1]: # skip 'Итого: агенты'
                val = get_headcount_override(r, m_str, get_def_hc(r, m_idx))
                col_vals.append(val)
                agent_sum += val
                
            # 3. Add 'Итого: агенты'
            col_vals.append(agent_sum)
            df_staff_data[m_str] = col_vals
            
        df_staff_1y = pd.DataFrame(df_staff_data)
        
        col_gen_left, col_gen_right = st.columns([1.8, 1.4])
        with col_gen_left:
            st.markdown("""
            <div style='background-color: #F8F9FA; padding: 15px; border-radius: 8px; border-left: 5px solid #BEAF87; margin-bottom:15px;'>
                <span style='font-weight: 700; color: #252526; font-size: 14px;'>📈 Автоматический генератор темпа роста в %</span><br>
                <span style='font-size: 11px; color: #777779;'>Позволяет быстро заполнить динамику роста штата по выбранной позиции на 12 месяцев на основе темпа прироста:</span>
            </div>
            """, unsafe_allow_html=True)
            
            g_role = st.selectbox(
                "Выберите должность для планирования роста:",
                options=[r for r in agent_labels[:-1]], # Только категории агентов
                key="gen_staff_role_widget"
            )
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                g_start = st.number_input("Старт в Месяце 1 (чел.):", min_value=0, max_value=100, value=1 if "РОП" in g_role or "HR" in g_role else 1, key="gen_staff_start_widget")
            with col_g2:
                g_rate = st.slider("Темп прироста в месяц (%):", min_value=-50, max_value=100, value=20, step=5, key="gen_staff_rate_widget")
                
            g_round = st.radio(
                "Метод округления значений:",
                options=["Ближайшее целое", "В большую сторону (ceil)", "В меньшую сторону (floor)"],
                horizontal=True,
                key="gen_staff_round_widget"
            )
            
            if st.button("⚡ Сгенерировать и применить рост в %", use_container_width=True):
                import math
                current_val = float(g_start)
                st.session_state['headcount_overrides'][(g_role, '1')] = int(g_start)
                
                for m_idx in range(2, 13):
                    current_val = current_val * (1.0 + g_rate / 100.0)
                    if "большую" in g_round:
                        rounded_val = math.ceil(current_val)
                    elif "меньшую" in g_round:
                        rounded_val = math.floor(current_val)
                    else:
                        rounded_val = round(current_val)
                    st.session_state['headcount_overrides'][(g_role, str(m_idx))] = int(max(0, rounded_val))
                st.success(f"Успешно применен рост {g_rate}% в месяц для '{g_role}' с начальным значением {g_start} чел.!")
                st.rerun()
                
        with col_gen_right:
            # Render Stacked Bar Chart
            m_labels = [f"М-{m}" for m in range(1, 13)]
            bo_totals = []
            ag_totals = []
            
            for m_str in m_cols:
                col_vals = df_staff_1y[m_str]
                bo_totals.append(sum(col_vals[:9]))
                ag_totals.append(sum(col_vals[9:13]))
                
            fig_staff_hist = go.Figure()
            fig_staff_hist.add_trace(go.Bar(
                x=m_labels,
                y=bo_totals,
                name="Бэк-офис",
                marker_color="#252526"
            ))
            fig_staff_hist.add_trace(go.Bar(
                x=m_labels,
                y=ag_totals,
                name="Агенты",
                marker_color="#BEAF87"
            ))
            fig_staff_hist.update_layout(
                title="Прогноз численности штата в 1-й год (чел.)",
                barmode="stack",
                template="plotly_white",
                height=250,
                margin=dict(t=40, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_staff_hist, use_container_width=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 📋 Интерактивная таблица кадрового расписания (Months 1-12)")
        st.write("Вы можете дважды кликнуть на любую ячейку бэк-офиса или категорий агентов для ручного изменения количества персонала:")
        
        # Configure st.data_editor columns
        col_config_stf_1y = {"Категория / Должность": st.column_config.TextColumn(disabled=True)}
        for m_str in m_cols:
            col_config_stf_1y[m_str] = st.column_config.NumberColumn(format="%d", min_value=0)
            
        edited_staff_1y_df = st.data_editor(
            df_staff_1y,
            use_container_width=True,
            disabled=["Категория / Должность", "Итого: агенты"],
            column_config=col_config_stf_1y,
            key="staff_editor_1year_calc",
            height=450
        )
        
        # Detect manual changes
        staff_changed_1y = False
        for idx_row in range(len(df_staff_1y)):
            row_name = df_staff_1y.at[idx_row, 'Категория / Должность']
            if "Итого" in row_name:
                continue
                
            for m_str in m_cols:
                val_base = df_staff_1y.at[idx_row, m_str]
                val_edited = edited_staff_1y_df.at[idx_row, m_str]
                if int(val_base) != int(val_edited):
                    st.session_state['headcount_overrides'][(row_name, m_str)] = int(parse_value(val_edited))
                    staff_changed_1y = True
                    
        if staff_changed_1y:
            st.success("Кадровое расписание обновлено! Пересчет финансовой модели...")
            st.rerun()
            
        if st.button("🔄 Сбросить все изменения штатного расписания", use_container_width=True):
            st.session_state['headcount_overrides'] = {}
            st.success("Все кадровые корректировки сброшены!")
            st.rerun()
            
        # --- NEW: DETAILED ROLES & MOTIVATION HANDBOOK (EXPANDER) ---
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📚 Справочник должностей, KPI и мотивации CENTURY 21", expanded=True):
            st.markdown("""
            ### 👔 Раздел I. Руководители отделов продаж (РОП)
            В системе CENTURY 21 деятельность и доходы РОПа жестко привязаны к категории управляемого им отдела и скорости интеграции новых сотрудников.
            
            #### 1. Классификация отделов продаж:
            *   **Отдел 1-й категории:** Стартовый статус любого создаваемого отдела. Присваивается подразделениям, приносящим валовый комиссионный доход (ВКД) компании ниже установленного ежемесячного лимита.
            *   **Отдел высшей категории:** Премиальный статус подразделения, стабильно генерирующего выручку выше установленного ежемесячного лимита. Перерасчет и подтверждение категории происходят дважды в год — 1 января и 1 июля на основе среднего значения ВКД за предшествующие 6 месяцев.
            
            #### 2. Метрики мотивации и контроля РОПа:
            *   **Окладная часть:** Фиксированная выплата в размере **35 000 рублей** в месяц при обеспечении нормативной численности отдела.
            *   **Процент со сделок опытных агентов:** Доля от ВКД отдела, зависящая от выполнения плана выручки на каждого сотрудника:
                *   **7% от ВКД** — если план выполнен менее чем на 80%.
                *   **10% от ВКД** — если план выполнен более чем на 80%.
            *   **Штраф по эксклюзивам:** **-2%** от ставки РОПа при провале планового объема эксклюзивных договоров отдела за месяц.
            
            ---
            
            ### 💼 Раздел II. Классификация и мотивационная сетка агентов
            
            *   **🌱 Стажер:** Начинающий специалист без опыта.
                *   *Планы:* квартальный план по ВКД — отсутствует; месячный план по привлечению — 2 клиента.
                *   *Сплит:* **30% агенту / 70% агентству**.
                *   *Альтернатива:* Возможность работы на окладе 30 000 рублей (15к фикс + 15к KPI за звонки, встречи и расклейку), при этом ставка снижается до 20%.
            *   **🏅 Агент (Уровень «А» / Стажер после 1-й сделки):** Специалист, совершивший первый подтвержденный результат.
                *   *Подтверждение:* 1 заключенный договор в месяц.
                *   *Гарантированный минимум:* выплачивается при наличии в активной работе от 3 договоров.
                *   *Планы:* квартальный план по ВКД — 300 000 рублей; привлечение — 3 клиента в месяц.
                *   *Сплит:* Базовый — **35%**, повышенный при перевыполнении планов — **45%**.
            *   **⭐ Эксперт (Уровень «B» / Креативный бунтарь):** Стабильный агент с опытом работы.
                *   *Подтверждение:* 2 заключенных договора в месяц.
                *   *Гарантированный минимум:* выплачивается при наличии от 5 договоров в активном портфеле.
                *   *Планы:* квартальный план по ВКД — 400 000 рублей; привлечение — 3 клиента в месяц.
                *   *Сплит:* Базовый — **40%**, повышенный при перевыполнении планов — **50%**.
            *   **👑 Ведущий эксперт (Уровень «C» / Профи):** Эксперт, показывающий высокие системные результаты.
                *   *Подтверждение:* не менее 3 договоров и 1 аванса (контрольный период — 3 месяца).
                *   *Гарантированный минимум:* выплачивается при ведении от 6 договоров одновременно.
                *   *Планы:* квартальный план по ВКД — 500 000 рублей; привлечение — 4 клиента в месяц.
                *   *Сплит:* Базовый — **50%**, повышенный при перевыполнении планов — **60%**.
            *   **🔥 Уровень «D» (Высшая лига):** Топ-агент, работающий интуитивно на накопленном авторитете.
                *   *Подтверждение:* не менее 4 договоров и 1 аванса (контрольный период — 3 месяца).
            """)
        
    with calc_tab5:
        st.markdown("""
        ### 📖 Справочник стандартов мотивации и классификации кадров CENTURY 21
        
        #### 💼 Раздел I. Руководители отделов продаж (РОП)
        В системе CENTURY 21 деятельность и доходы РОПа жестко привязаны к категории управляемого им отдела и скорости интеграции новых сотрудников.
        
        ##### 1. Классификация отделов продаж:
        *   **Отдел 1-й категории:** Стартовый статус любого создаваемого отдела. Присваивается подразделениям, приносящим валовый комиссионный доход (ВКД) компании ниже установленного ежемесячного лимита.
        *   **Отдел высшей категории:** Премиальный статус подразделения, стабильно генерирующего выручку выше установленного ежемесячного лимита. Перерасчет и подтверждение категории происходят дважды в год — 1 января и 1 июля на основе среднего значения ВКД за предшествующие 6 месяцев.
        
        ##### 2. Метрики мотивации и контроля РОПа:
        *   **Окладная часть:** Фиксированная выплата в размере **35 000 рублей** в месяц при обеспечении нормативной численности отдела.
        *   **Процент со сделок опытных агентов:** Доля от ВКД отдела, зависящая от выполнения плана выручки на каждого сотрудника:
            *   **7% от ВКД** — если план выполнен менее чем на 80%.
            *   **10% от ВКД** — если план выполнен более чем на 80%.
            *   *Штраф по эксклюзивам:* **-2%** от ставки РОПа при провале планового объема эксклюзивных договоров отдела за месяц.
            
        ---
        
        #### 👥 Раздел II. Категории агентов и квалификационные уровни
        
        ##### 1. Квалификационные стандарты должностей:
        *   **Стажер:** Начинающий специалист без опыта.
            *   *Планы:* квартальный план по ВКД — отсутствует; месячный план по привлечению — 2 клиента.
            *   *Сплит:* **30%** агенту / **70%** агентству.
            *   *Альтернатива:* Возможность работы на окладе **30 000 рублей** (15к фикс + 15к KPI за звонки, встречи и расклейку), при этом ставка снижается до **20%**.
        *   **Агент (Уровень «А»):** Специалист, преодолевший адаптацию и закрывший 3 сделки.
            *   *Планы:* квартальный план по ВКД — **300 000 рублей**; привлечение — 3 клиента в месяц.
            *   *Сплит:* Базовый — **35%**, повышенный при перевыполнении планов — **45%**.
            *   *Подтверждение статуса:* 1 заключенный договор в месяц.
            *   *Гарантированный минимум:* выплачивается при наличии в активной работе от 3 договоров.
        *   **Эксперт (Уровень «B»):** Опытный профессионал, закрывший 10 сделок.
            *   *Планы:* квартальный план по ВКД — **400 000 рублей**; привлечение — 3 клиента в месяц.
            *   *Сплит:* Базовый — **40%**, повышенный при перевыполнении планов — **50%**.
            *   *Подтверждение статуса:* 2 заключенных договора в месяц.
            *   *Гарантированный минимум:* выплачивается при наличии от 5 договоров в активном портфеле.
        *   **Ведущий эксперт (Уровень «C»):** Лидер продаж, закрывший 20 сделок.
            *   *Планы:* квартальный план по ВКД — **500 000 рублей**; привлечение — 4 клиента в месяц.
            *   *Сплит:* Базовый — **50%**, повышенный при перевыполнении планов — **60%**.
            *   *Подтверждение статуса:* не менее 3 договоров и 1 аванса (контрольный период — 3 месяца).
            *   *Гарантированный минимум:* выплачивается при ведении от 6 договоров одновременно.
        *   **Уровень «D» (Высшая лига):** Топ-агент, работающий интуитивно на накопленном авторитете.
            *   *Подтверждение статуса:* не менее 4 договоров и 1 аванса (контрольный период — 3 месяца).
        """)
else:
    # ----------------------------------------------------
    # РЕЖИМ SUCCESS: ДИАГНОСТИЧЕСКИЙ ЧЕК-ЛИСТ И СВЕТОФОР
    # ----------------------------------------------------
    st.markdown("### 🛠️ Панель диагностики и сопровождения действующего офиса (Success)")
    st.markdown("ℹ️ *Введите фактические текущие показатели офиса франчайзи. Программа сравнит их с Оптимальным планом на выбранный месяц, выявит отклонения и выдаст готовый Playbook лечения.*")
    
    col_inputs, col_light = st.columns([1.5, 2])
    with col_inputs:
        st.markdown("**🔍 Текущие показатели франчайзи:**")
        
        target_month_ins = st.select_slider(
            "📅 Целевой месяц для сравнения (например, 13-й месяц):",
            options=[str(m) for m in range(1, 25)],
            value="13",
            key="diag_target_month"
        )
        idx_t = int(target_month_ins) - 1
        
        fact_agents = st.slider("👥 Текущий штат активных агентов (чел.):", min_value=1, max_value=50, value=15, key="diag_fact_agents")
        fact_leads = st.slider("📞 Входящий поток лидов за месяц (звонки):", min_value=100, max_value=5000, value=400, key="diag_fact_leads")
        fact_meet_conv = st.slider("🤝 Конверсия лид -> встреча, %:", min_value=1.0, max_value=20.0, value=7.5, step=0.5, key="diag_fact_meet")
        fact_deal_conv = st.slider("✍️ Конверсия встреча -> договор, %:", min_value=1.0, max_value=15.0, value=3.5, step=0.5, key="diag_fact_deal")
        fact_commission = st.number_input("💰 Средняя комиссия за сделку, ₽:", min_value=50000, max_value=1000000, value=250000, step=10000, key="diag_fact_comm")

    # Target values for comparison from Month T
    target_agents_t = int(get_headcount_override('  ├─ Агент: категория D', target_month_ins, DEFAULT_HEADCOUNTS['Агент: категория D'][idx_t]) + 
                          get_headcount_override('  ├─ Агент: категория C', target_month_ins, DEFAULT_HEADCOUNTS['Агент: категория C'][idx_t]) + 
                          get_headcount_override('  ├─ Агент: категория B', target_month_ins, DEFAULT_HEADCOUNTS['Агент: категория B' if 'category B' in DEFAULT_HEADCOUNTS else 'Агент: категория B'][idx_t]) + 
                          get_headcount_override('  └─ Агент: категория A', target_month_ins, DEFAULT_HEADCOUNTS['Агент: категория A'][idx_t]))
    target_leads_t = int(adj_leads[idx_t])
    target_meet_conv_t = float(conversion_meeting)
    target_deal_conv_t = float(conversion_deal)
    target_commission_t = float(comm_secondary)
    
    # Calculate variances
    v_agents_pct = (fact_agents - target_agents_t) / target_agents_t if target_agents_t > 0 else 0
    v_leads_pct = (fact_leads - target_leads_t) / target_leads_t if target_leads_t > 0 else 0
    v_meet_pct = (fact_meet_conv - target_meet_conv_t) / target_meet_conv_t
    v_deal_pct = (fact_deal_conv - target_deal_conv_t) / target_deal_conv_t
    v_comm_pct = (fact_commission - target_commission_t) / target_commission_t
    
    with col_light:
        st.markdown("**🚦 Светофор здоровья офиса (Traffic Lights):**")
        
        # Function to draw status cards
        def draw_status_card(name, fact_v, target_v, pct_v, is_percentage=False, suffix=""):
            if pct_v >= -0.10:
                color_bullet = "🟢"
                status_text = "Норма"
                color_style = "border-left: 5px solid #28a745; background-color: #f4fbf5;"
            elif pct_v >= -0.25:
                color_bullet = "🟡"
                status_text = "В зоне риска"
                color_style = "border-left: 5px solid #ffc107; background-color: #fffdf0;"
            else:
                color_bullet = "🔴"
                status_text = "Критично!"
                color_style = "border-left: 5px solid #dc3545; background-color: #fdf5f5;"
                
            fact_f = f"{fact_v:.1f}%" if is_percentage else (f"{fact_v:,.0f}{suffix}" if suffix else f"{fact_v:,.0f}")
            target_f = f"{target_v:.1f}%" if is_percentage else (f"{target_v:,.0f}{suffix}" if suffix else f"{target_v:,.0f}")
            
            st.markdown(f"""
            <div style='padding: 10px 15px; border-radius: 6px; margin-bottom: 8px; {color_style}'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <span style='font-weight:700; font-size:13px; color:#252526;'>{color_bullet} {name}</span>
                    <span style='font-weight:700; font-size:12px; color:#252526;'>{status_text} (Откл: {pct_v*100:+.1f}%)</span>
                </div>
                <div style='display:flex; justify-content:space-between; font-size:11px; color:#777779; margin-top:4px;'>
                    <span>Факт: <b>{fact_f}</b></span>
                    <span>План (М-{target_month_ins}): <b>{target_f}</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        draw_status_card("Штат активных агентов", fact_agents, target_agents_t, v_agents_pct, suffix=" чел.")
        draw_status_card("Количество входящих лидов", fact_leads, target_leads_t, v_leads_pct, suffix=" звонков")
        draw_status_card("Конверсия лид -> встреча", fact_meet_conv, target_meet_conv_t, v_meet_pct, is_percentage=True)
        draw_status_card("Конверсия встреча -> договор", fact_deal_conv, target_deal_conv_t, v_deal_pct, is_percentage=True)
        draw_status_card("Средняя комиссия за сделку", fact_commission, target_commission_t, v_comm_pct, suffix=" ₽")

    # Diagnostic Playbook (Рецепты лечения)
    st.markdown("<br><h4>📋 Интеллектуальный Playbook Сопровожденца (Рецепт лечения)</h4>", unsafe_allow_html=True)
    
    has_issues = False
    
    if v_leads_pct < -0.15:
        has_issues = True
        st.markdown(f"""
        <div style='background-color: #fdf5f5; padding: 15px; border-radius: 6px; border-left: 4px solid #dc3545; margin-bottom: 12px;'>
            <span style='font-weight:700; color:#c00000; font-size:14px;'>🚨 Проблема: Падение входящего потока лидов (Отклонение: {v_leads_pct*100:.1f}%)</span><br>
            <p style='font-size:12px; color:#555; margin-top:5px; line-height:1.4;'>
                <b>Диагноз из Книги Брокера:</b> Офис недополучает входящие звонки. Это ведет к простою агентов и кассовому разрыву через 2 месяца.<br>
                <b>Решение для сопровожденца:</b> <br>
                1. Проверить распределение рекламного бюджета: норматив рекламы на Циан/Авито должен быть полностью освоен.<br>
                2. Проверить своевременность выгрузки объектов листинг-менеджером в CRM.<br>
                3. Запустить таргетированную лидогенерацию на новостройки.<br>
                <b>🗣️ Речевой скрипт разговора с брокером:</b><br>
                <i>"Уважаемый партнер, мы видим, что ваш трафик просел на {abs(v_leads_pct)*100:.1f}%. Ваши агенты недополучают контакты. Давайте увеличим бюджет рекламы объектов до норматива, и это принесет вам дополнительно {abs(v_leads_pct)*target_leads_t*0.1*0.05*comm_secondary:,.0f} ₽ чистой прибыли в течение 60 дней."</i>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    if v_meet_pct < -0.10:
        has_issues = True
        st.markdown(f"""
        <div style='background-color: #fffdf0; padding: 15px; border-radius: 6px; border-left: 4px solid #ffc107; margin-bottom: 12px;'>
            <span style='font-weight:700; color:#7f6000; font-size:14px;'>⚠️ Проблема: Слабая конверсия лидов во встречи (Отклонение: {v_meet_pct*100:.1f}%)</span><br>
            <p style='font-size:12px; color:#555; margin-top:5px; line-height:1.4;'>
                <b>Диагноз из Книги Брокера:</b> Агенты не умеют 'продавать встречу' по телефону, соглашаясь на дистанционную работу.<br>
                <b>Решение для сопровожденца:</b> <br>
                1. Прослушать записи телефонных разговоров агентов в CRM.<br>
                2. Назначить РОПу проведение тренинга по теме 'Сценарий телефонного звонка CENTURY 21'.<br>
                3. Проконтролировать, чтобы администратор офиса вел жесткий учет непринятых вызовов.<br>
                <b>🗣️ Речевой скрипт разговора с брокером:</b><br>
                <i>"Мы проанализировали звонки ваших агентов. Главная ошибка — они пытаются консультировать по цене вместо продажи визита в офис. Если мы поднимем конверсию звонка во встречу до плановых {target_meet_conv_t}%, количество сделок вырастет в 1.5 раза без увеличения расходов на рекламу!"</i>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    if v_deal_pct < -0.10:
        has_issues = True
        st.markdown(f"""
        <div style='background-color: #fdf5f5; padding: 15px; border-radius: 6px; border-left: 4px solid #dc3545; margin-bottom: 12px;'>
            <span style='font-weight:700; color:#c00000; font-size:14px;'>🚨 Проблема: Катастрофический спад конверсии встреч в договоры (Отклонение: {v_deal_pct*100:.1f}%)</span><br>
            <p style='font-size:12px; color:#555; margin-top:5px; line-height:1.4;'>
                <b>Диагноз из Книги Брокера:</b> Агенты проваливают личные переговоры и не могут обосновать ценность эксклюзивного договора и комиссии агентства.<br>
                <b>Решение для сопровожденца:</b> <br>
                1. Проверить, используют ли агенты фирменную папку презентации услуг CENTURY 21 при встрече.<br>
                2. Направить РОПа и ключевых агентов на переаттестацию по теме 'Работа с возражениями и подписание эксклюзива'.<br>
                3. Назначить РОС/тренеру проведение практических ролевых игр 'Брокер-Клиент' три раза в неделю.<br>
                <b>🗣️ Речевой скрипт разговора с брокером:</b><br>
                <i>"У вас отличный поток встреч, но конверсия в договоры всего {fact_deal_conv_t:.1f}% вместо норматива {target_deal_conv_t}%. Ваши люди теряют самых горячих клиентов. Давайте внедрим обязательное использование папки презентации услуг и проведем аттестацию агентов. Рост этого показателя до нормы принесет вам дополнительно {abs(v_deal_pct)*target_meet_conv_t*0.01*fact_leads*comm_secondary:,.0f} ₽ уже в следующем квартале."</i>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    if v_agents_pct < -0.15:
        has_issues = True
        st.markdown(f"""
        <div style='background-color: #fffdf0; padding: 15px; border-radius: 6px; border-left: 4px solid #ffc107; margin-bottom: 12px;'>
            <span style='font-weight:700; color:#7f6000; font-size:14px;'>⚠️ Проблема: Отставание по штатной численности агентов (Отклонение: {v_agents_pct*100:.1f}%)</span><br>
            <p style='font-size:12px; color:#555; margin-top:5px; line-height:1.4;'>
                <b>Диагноз из Книги Брокера:</b> Спад рекрутинговой активности. Текущих агентов недостаточно для обработки входящих лидов, реклама тратится впустую.<br>
                <b>Решение для сопровожденца:</b> <br>
                1. Проверить ежедневный KPI рекрутера по количеству приглашений на собеседования.<br>
                2. Провести ревизию воронки найма на HeadHunter.<br>
                3. Проконтролировать РОПа по внедрению системы адаптации и наставничества для исключения отсева новичков.<br>
                <b>🗣️ Речевой скрипт разговора с брокером:</b><br>
                <i>"Вы тратите деньги на рекламу лидов, но их некому качественно обрабатывать, так как штат отстает на {abs(fact_agents - target_agents_t)} агентов. Нам нужно срочно ускорить наем. Давайте поставим рекрутеру жесткий план — 5 новых стажеров в ближайшую группу обучения, и это выведет ваш офис на запланированные {target_agents_t} человек."</i>
            </p>
        </div>
        """, unsafe_allow_html=True)

    if not has_issues:
        st.markdown(f"""
        <div style='background-color: #f4fbf5; padding: 20px; border-radius: 8px; border-left: 5px solid #28a745;'>
            <h5 style='color: #28a745; font-weight: 700; margin-top:0;'>🟢 Диагноз: Офис полностью здоров!</h5>
            <p style='font-size: 13px; color: #555; line-height: 1.5;'>
                Фактические показатели франчайзи соответствуют или превышают плановые значения «Оптимального Бюджета» CENTURY 21 для {target_month_ins}-го месяца проекта!<br>
                <b>Рекомендация сопровожденцу:</b> Поддерживайте текущий темп рекрутинга и качество адаптации стажеров. Офис находится на траектории максимальной чистой прибыли. Переходите к масштабированию и увеличению среднего чека.
            </p>
        </div>
        """, unsafe_allow_html=True)
