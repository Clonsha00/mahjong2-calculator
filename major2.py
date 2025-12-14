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
    page_title="麻將台數計算器 v4.0",
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
st.title("🀄 我的胡牌計算機")
st.caption("台灣16張 | 🚩 字一色 = 16 台 🚩")

# --- 核心邏輯設定 ---
total_tai = 0
calculation_details = [] 

# ====================================================================
# === 區塊 0：骰莊與門風紀錄 (新區塊) =====================================
# ====================================================================
st.subheader("🎲 0. 骰莊與門風紀錄")

col_dice, col_result = st.columns([1, 2])

with col_dice:
    # 擲骰按鈕，點擊後會呼叫 roll_dice 函數
    st.button("擲骰子 (決定莊位/開門)", on_click=roll_dice, type="primary", use_container_width=True)

with col_result:
    # 顯示擲骰結果
    if st.session_state.dice_roll:
        d1, d2 = st.session_state.dice_roll
        total = st.session_state.dice_sum
        st.metric(label="骰子結果", value=f"{d1} + {d2} = {total}")
    else:
        st.metric(label="骰子結果", value="點擊按鈕擲骰")

st.info("💡 請依照擲骰結果判斷莊家/門風，並手動設定下方「我是莊家」與「我的門風」選項。")
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
# === 區塊 A：風牌/字牌 智慧判斷 (使用擲骰結果設定門風) =====================
# ====================================================================

st.subheader("1. 風台/字牌判斷 (正風)")

# 風牌選擇清單
WIND_OPTIONS = ["東風", "南風", "西風", "北風"]

# 玩家輸入：圈風和門風 (用於判斷正風台)
col_setup1, col_setup2 = st.columns(2)
with col_setup1:
    current_wind = st.selectbox("🎯 目前圈風 (場風)", WIND_OPTIONS, index=0, key='circle_wind')
with col_setup2:
    player_position = st.selectbox("🪑 我的門風 (座位)", WIND_OPTIONS, index=1, key='player_pos') # 手動選擇門風

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

# 1. 圈風台判斷 (有刻子且與圈風相同)
if current_wind in player_wind_set:
    current_tai_wind += 1
    calculation_details.append(f"圈風 ({current_wind}) +1")

# 2. 門風台判斷 (有刻子且與門風相同)
if player_position in player_wind_set:
    current_tai_wind += 1
    calculation_details.append(f"門風 ({player_position}) +1")

# 3. 三元牌台判斷 (用於提醒玩家可能組成大小三元)
if dragon_tai == 3:
    calculation_details.append("已湊齊三元牌刻子")

total_tai += current_tai_wind
st.success(f"🀅 正風/三元牌刻子總計：{current_tai_wind} 台")
st.divider()


# ====================================================================
# === 區塊 B：花牌判斷 ==================================================
# ====================================================================
st.subheader("2. 花牌判斷")

st.warning(f"您的門風是 **{player_position}**。")
st.info("門風對應正花：東=梅(1)/竹(5)，南=蘭(2)/菊(6)，西=竹(3)/蘭(7)，北=菊(4)/梅(8)。")

col_flower_input = st.columns(2)
with col_flower_input[0]:
    total_flower_count = st.number_input("手上花牌總張數 (1~8)", min_value=0, max_value=8, step=1, key='flower_count')

with col_flower_input[1]:
    correct_flower_count = st.number_input("其中是「正花」張數", min_value=0, max_value=8, step=1, key='correct_flower')

current_tai_flower = 0

# 1. 正花台數
if correct_flower_count > 0:
    current_tai_flower = correct_flower_count
    calculation_details.append(f"正花 +{current_tai_flower}")

# 2. 特殊大牌判斷
if total_flower_count == 8:
    current_tai_flower += 8 # 八仙過海
    calculation_details.append("八仙過海 +8")
    st.balloons()
elif total_flower_count == 7:
    if st.checkbox("確認為七搶一 (+8台，對方一張花)", key='chk_7_1'):
        current_tai_flower += 8
        calculation_details.append("七搶一 +8")

total_tai += current_tai_flower
st.success(f"🌸 花牌總計：{current_tai_flower} 台")
st.divider()

# ====================================================================
# === 區塊 C：狀態與牌型 ===============================================
# ====================================================================

st.subheader("3. 狀態與牌型")

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
