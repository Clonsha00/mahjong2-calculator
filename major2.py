import streamlit as st
import random

# --- 核心邏輯：擲骰子函數 ---
# 使用 session_state 儲存擲骰結果，確保頁面不亂跳
if 'dice_roll' not in st.session_state:
    st.session_state.dice_roll = None
if 'dice_sum' not in st.session_state:
    st.session_state.dice_sum = None

def roll_dice():
    """模擬擲兩顆六面骰"""
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    st.session_state.dice_roll = (d1, d2)
    st.session_state.dice_sum = d1 + d2

# --- 頁面基本設定 ---
st.set_page_config(
    page_title="雙人麻將計算器 v5.0",
    page_icon="🀄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 自定義樣式 (CSS) ---
st.markdown("""
    <style>
    div.stButton > button {
        height: 3rem;
        font-size: 1.2rem;
        font-weight: bold;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem;
    }
    .stAlert {
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 標題區 ---
st.title("🀄 雙人麻將：胡牌計算機")
st.caption("規則：無花牌、只看門風、字一色 = 16 台")

# --- 核心邏輯設定 ---
total_tai = 0
calculation_details = [] 

# ====================================================================
# === 區塊 0：骰莊與門風紀錄 =============================================
# ====================================================================
st.subheader("🎲 0. 骰莊與門風紀錄")

col_dice, col_result = st.columns([1, 2])

with col_dice:
    st.button("擲骰子 (決定莊位/開門)", on_click=roll_dice, type="primary", use_container_width=True)

with col_result:
    if st.session_state.dice_roll:
        d1, d2 = st.session_state.dice_roll
        total = st.session_state.dice_sum
        st.metric(label="骰子結果", value=f"{d1} + {d2} = {total}")
    else:
        st.metric(label="骰子結果", value="點擊按鈕擲骰")

st.info("💡 **雙人提示：** 骰子結果用於決定莊家，並從莊家開始算位。若開門處為東或西，請確認雙方門風是否正確。")
st.divider()

# 1. 基礎金額設定
with st.expander("⚙️ 設定底/台金額 (點擊展開)", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        base_score = st.number_input("底 ($)", value=100, step=50, key='base')
    with col2:
        point_value = st.number_input("台 ($)", value=20, step=10, key='point')

st.divider()

# ====================================================================
# === 區塊 A：風牌/字牌 智慧判斷 (只看門風) ================================
# ====================================================================

st.subheader("1. 門風/字牌判斷 (正位)")

# 風牌選擇清單
WIND_OPTIONS = ["東風", "南風", "西風", "北風"]

# 玩家輸入：門風 (座位)
st.markdown("🪑 **請選擇您的門風 (座位)**")
# 由於雙人通常只坐對家，我們仍列出四個選項，讓使用者根據實際座位決定
player_position = st.selectbox("我的門風", WIND_OPTIONS, index=1, key='player_pos', label_visibility="collapsed") 

st.write("---")

# 玩家輸入：自己手牌中的風牌刻子/槓子數量
st.write("請輸入**您有刻子或槓子**的風牌：")
col_input = st.columns(4)
player_wind_set = [] 
for i, wind in enumerate(WIND_OPTIONS):
    with col_input[i]:
        if st.checkbox(wind, key=f"wind_set_{i}"):
            player_wind_set.append(wind)

# 玩家輸入：三元牌刻子
st.write("---")
st.write("三元牌刻子：")
col_dragon = st.columns(3)
dragon_tai = 0
if col_dragon[0].checkbox("紅中刻子/槓子", key='dragon_red'):
    dragon_tai += 1
if col_dragon[1].checkbox("發財刻子/槓子", key='dragon_green'):
    dragon_tai += 1
if col_dragon[2].checkbox("白板刻子/槓子", key='dragon_white'):
    dragon_tai += 1

# 執行風台判斷
current_tai_wind = 0

# 1. 門風台判斷 (有刻子且與門風相同) - 這是唯一剩下的風台判斷
if player_position in player_wind_set:
    current_tai_wind += 1
    calculation_details.append(f"門風 ({player_position}) +1")

# 2. 三元牌台判斷 (用於提醒玩家可能組成大小三元)
if dragon_tai == 3:
    calculation_details.append("已湊齊三元牌刻子")

total_tai += current_tai_wind
st.success(f"🀅 門風/三元牌刻子總計：{current_tai_wind} 台")
st.divider()

# ====================================================================
# === 區塊 B：花牌判斷 (已移除) =========================================
# ====================================================================
# 此處為原來的花牌區，現已移除

# ====================================================================
# === 區塊 C：狀態與牌型 ===============================================
# ====================================================================

st.subheader("2. 狀態與牌型") # 原本是 3.，現改為 2.

# 莊家/連莊/自摸
col_status1, col_status2 = st.columns(2)
with col_status1:
    is_dealer = st.checkbox("我是莊家 (+1台)", key='chk_dealer')
    if is_dealer:
        total_tai += 1
        calculation_details.append("莊家 +1")

    is_self_draw = st.checkbox("自摸 (+1台)", key='chk_self')
    if is_self_draw:
        total_tai += 1
        calculation_details.append("自摸 +1")

with col_status2:
    lianzhuang = st.number_input("連莊次數 (n)", min_value=0, step=1, key='chk_lian')
    if lianzhuang > 0:
        tai_val = lianzhuang * 2
        total_tai += tai_val
        calculation_details.append(f"連{lianzhuang}拉{lianzhuang} +{tai_val}")

st.write("---")

# 定義牌型字典 (名稱: 台數)
YAKU_LIST = {
    "門清": 1,
    "門清自摸": 3,
    "平胡": 2,
    "全求人": 2,
    "湊一色 (混一色)": 4,
    "清一色": 8,
    "對對胡 (碰碰胡)": 4,
    "字一色 (全字牌)": 16, 
}

# 牌型勾選
cols = st.columns(2)
for i, (name, tai) in enumerate(YAKU_LIST.items()):
    with cols[i % 2]:
        if st.checkbox(f"{name} ({tai}台)", key=f"yaku_{i}"):
            total_tai += tai
            calculation_details.append(f"{name} +{tai}")

# 暗刻系列
st.write("---")
st.write("🌑 **暗刻計算** (擇一勾選)")
col_ank = st.columns(3)
if col_ank[0].checkbox("三暗刻 (2台)", key='chk_3ank'):
    total_tai += 2
    calculation_details.append("三暗刻 +2")
if col_ank[1].checkbox("四暗刻 (5台)", key='chk_4ank'):
    total_tai += 5
    calculation_details.append("四暗刻 +5")
if col_ank[2].checkbox("五暗刻 (8台)", key='chk_5ank'):
    total_tai += 8
    calculation_details.append("五暗刻 +8")

# 三元牌大牌
st.write("---")
st.write("🐲 **三元牌大牌**")
if st.checkbox("小三元 (4台)", key='chk_3dragon_s'):
    total_tai += 4
    calculation_details.append("小三元 +4")
if st.checkbox("大三元 (8台)", key='chk_3dragon_b'):
    total_tai += 8
    calculation_details.append("大三元 +8")

st.divider()

# ====================================================================
# === 結算區域 =========================================================
# ====================================================================

# 最終金額計算
total_money = base_score + (total_tai * point_value)

st.subheader("🎉 最終結算結果")

# 顯示明細
with st.expander("📝 完整台數明細 (點擊展開)", expanded=False):
    if calculation_details:
        st.code("\n".join(calculation_details))
    else:
        st.info("尚未勾選任何台數")

# 醒目的結果展示
r_col1, r_col2 = st.columns(2)
with r_col1:
    st.metric(label="總台數", value=f"{total_tai} 台")
with r_col2:
    st.metric(label="應收/應付金額", value=f"$ {total_money}")

if total_tai >= 16:
    st.success("超級大牌！恭喜胡牌！")
    st.balloons()
