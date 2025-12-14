import streamlit as st
import random

# --- 核心邏輯：擲骰子與風位判定 (不變) ---
if 'dice_roll' not in st.session_state:
    st.session_state.dice_roll = None
if 'dice_sum' not in st.session_state:
    st.session_state.dice_sum = None
if 'wind_tai_type' not in st.session_state: 
    st.session_state.wind_tai_type = None
if 'wind_tai_set' not in st.session_state: 
    st.session_state.wind_tai_set = []
if 'is_double' not in st.session_state: 
    st.session_state.is_double = False

def roll_dice():
    """模擬擲兩顆六面骰，判斷奇偶風位，並檢查是否點數相同"""
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    total = d1 + d2
    
    st.session_state.dice_roll = (d1, d2)
    st.session_state.dice_sum = total
    st.session_state.is_double = (d1 == d2) 
    
    if total % 2 != 0:
        st.session_state.wind_tai_type = "奇數 (東/西)"
        st.session_state.wind_tai_set = ["東風", "西風"]
    else:
        st.session_state.wind_tai_type = "偶數 (南/北)"
        st.session_state.wind_tai_set = ["南風", "北風"]


# --- 最終計算與衝突排除函數 (核心修正) ---
def get_final_tai(st_session):
    """
    計算總台數，並自動處理衝突選項，只保留最大的或互斥的。
    """
    final_tai = 0
    details = []
    
    # --- 1. 狀態台數 ---
    # 莊家 (不互斥)
    if st_session.get('chk_dealer'):
        final_tai += 1
        details.append("莊家 +1")

    # 連莊 (不互斥)
    lianzhuang = st_session.get('chk_lian', 0)
    if lianzhuang > 0:
        tai_val = lianzhuang * 2
        final_tai += tai_val
        details.append(f"連{lianzhuang}拉{lianzhuang} +{tai_val}")

    # 自摸 (需要檢查是否與全求人衝突)
    is_self_draw = st_session.get('chk_self')
    is_all_collect = st_session.get('yaku_3') # yaku_3 = 全求人
    
    if is_self_draw and not is_all_collect:
        final_tai += 1
        details.append("自摸 +1")
    elif is_self_draw and is_all_collect:
        # 強制排除：全求人必須是點砲，若勾選自摸，我們假設使用者勾錯，自動忽略自摸台數。
        details.append("自摸台數因與全求人衝突，自動排除 (點砲優先)")


    # --- 2. 風台 (由程式自動判斷，不互斥) ---
    current_tai_wind = 0
    player_wind_set = []
    for i in range(4):
        if st_session.get(f"wind_set_{i}"):
            player_wind_set.append(st_session.get(f"wind_tai_set", [])[i % 2])

    if st_session.get('wind_tai_set'):
        for wind in player_wind_set:
            if wind in st_session.get('wind_tai_set'):
                current_tai_wind += 1
                details.append(f"門風台 ({wind}) +1")

    final_tai += current_tai_wind
    
    
    # --- 3. 牌型台數 (YAKU_LIST) ---
    YAKU_LIST_MAP = {
        'yaku_0': {"name": "門清", "tai": 1},
        'yaku_1': {"name": "門清自摸", "tai": 3},
        'yaku_2': {"name": "平胡", "tai": 2},
        'yaku_3': {"name": "全求人", "tai": 2}, # 已處理自摸衝突
        'yaku_4': {"name": "湊一色 (混一色)", "tai": 4},
        'yaku_5': {"name": "清一色", "tai": 8},
        'yaku_6': {"name": "對對胡 (碰碰胡)", "tai": 4},
        'yaku_7': {"name": "字一色 (全字牌)", "tai": 16},
    }
    
    for key, data in YAKU_LIST_MAP.items():
        if st_session.get(key):
            # 全求人已經在上面處理完衝突了，其他都獨立計算
            if key == 'yaku_3' and not is_all_collect: # 避免自摸衝突下重複加入
                 continue
                 
            final_tai += data["tai"]
            details.append(f"{data['name']} +{data['tai']}")


    # --- 4. 暗刻衝突處理 (只保留最大) ---
    ank_tai = 0
    if st_session.get('chk_5ank'):
        ank_tai = 8
        details.append("五暗刻 +8 (自動排除三/四暗刻)")
    elif st_session.get('chk_4ank'):
        ank_tai = 5
        details.append("四暗刻 +5 (自動排除三暗刻)")
    elif st_session.get('chk_3ank'):
        ank_tai = 2
        details.append("三暗刻 +2")
        
    final_tai += ank_tai
    
    # --- 5. 三元牌衝突處理 (只保留最大) ---
    dragon_tai = 0
    if st_session.get('chk_3dragon_b'):
        dragon_tai = 8
        details.append("大三元 +8 (自動排除小三元)")
    elif st_session.get('chk_3dragon_s'):
        dragon_tai = 4
        details.append("小三元 +4")
        
    final_tai += dragon_tai


    return final_tai, details


# --- 頁面基本設定 ---
st.set_page_config(
    page_title="雙人麻將計算器 v10.0 (自動排除衝突)",
    page_icon="🀄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 自定義樣式 (CSS) (不變) ---
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

# --- 標題區 (不變) ---
st.title("🀄 雙人麻將：胡牌計算機")
st.caption("規則：極簡模式，**自動處理台數衝突**")

# --- 核心邏輯設定 ---
# total_tai, calculation_details 在最終計算時決定

# ====================================================================
# === 區塊 0：骰莊與門風紀錄 (不變) =======================================
# ====================================================================
st.subheader("🎲 0. 擲骰子判定風台")

col_dice, col_result = st.columns([1, 2])

with col_dice:
    st.button("擲骰子 (決定莊位/風台)", on_click=roll_dice, type="primary", use_container_width=True)

with col_result:
    if st.session_state.dice_roll:
        d1, d2 = st.session_state.dice_roll
        total = st.session_state.dice_sum
        st.metric(label="骰子結果", value=f"{d1} + {d2} = {total}")
    else:
        st.metric(label="骰子結果", value="點擊按鈕擲骰")

# 顯示風台判斷結果
if st.session_state.wind_tai_type:
    st.warning(f"當前門風台：擲骰為 **{st.session_state.wind_tai_type}**。只有 **{st.session_state.wind_tai_set[0]}** 和 **{st.session_state.wind_tai_set[1]}** 的刻子算台 (+1)。")

# 檢查並顯示點數相同加倍提醒
multiplier = 1
if st.session_state.is_double:
    st.error("🚨 **點數相同 (圍骰/豹子)！** 本局總金額需 **乘以兩倍**。")
    multiplier = 2

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
# === 區塊 A：字牌刻子輸入與自動判斷風台 ====================================
# ====================================================================

st.subheader("1. 風/三元牌刻子輸入與台數")

st.write("請輸入**您有刻子或槓子**的風牌：")
# 風牌選擇清單 (東南西北)
WIND_OPTIONS = ["東風", "南風", "西風", "北風"]
col_input = st.columns(4)
for i, wind in enumerate(WIND_OPTIONS):
    with col_input[i]:
        # 這裡的 checkbox 只是用來設定 session_state，真正的計算在 get_final_tai 進行
        st.checkbox(wind, key=f"wind_set_{i}")

# 玩家輸入：三元牌刻子
st.write("---")
st.write("三元牌刻子：")
col_dragon = st.columns(3)
col_dragon[0].checkbox("紅中刻子/槓子", key='dragon_red')
col_dragon[1].checkbox("發財刻子/槓子", key='dragon_green')
col_dragon[2].checkbox("白板刻子/槓子", key='dragon_white')

# 這裡不再顯示即時台數，因為計算已移到結算區
st.info("💡 **風/三元台數** 將在下方結算區**自動計算**。")
st.divider()


# ====================================================================
# === 區塊 B：狀態與牌型 (僅負責輸入，不計算) =================================
# ====================================================================

st.subheader("2. 狀態與牌型") 

# 莊家/連莊/自摸
col_status1, col_status2 = st.columns(2)

with col_status1:
    st.checkbox("我是莊家 (+1台)", key='chk_dealer')
    st.checkbox("自摸 (+1台)", key='chk_self')
        
with col_status2:
    st.number_input("連莊次數 (n)", min_value=0, step=1, key='chk_lian')

st.write("---")

# 定義牌型字典 (名稱: 台數)
YAKU_LIST = {
    "門清": 1,
    "門清自摸": 3,
    "平胡": 2,
    "全求人": 2, # yaku_3
    "湊一色 (混一色)": 4,
    "清一色": 8,
    "對對胡 (碰碰胡)": 4,
    "字一色 (全字牌)": 16, 
}

# 牌型勾選
cols = st.columns(2)
for i, (name, tai) in enumerate(YAKU_LIST.items()):
    with cols[i % 2]:
        # 這裡只負責將狀態寫入 session_state
        st.checkbox(f"{name} ({tai}台)", key=f"yaku_{i}")

# 暗刻系列
st.write("---")
st.write("🌑 **暗刻計算** (擇一勾選)")
col_ank = st.columns(3)
col_ank[0].checkbox("三暗刻 (2台)", key='chk_3ank')
col_ank[1].checkbox("四暗刻 (5台)", key='chk_4ank')
col_ank[2].checkbox("五暗刻 (8台)", key='chk_5ank')

# 三元牌大牌
st.write("---")
st.write("🐲 **三元牌大牌**")
st.checkbox("小三元 (4台)", key='chk_3dragon_s')
st.checkbox("大三元 (8台)", key='chk_3dragon_b')

st.divider()

# ====================================================================
# === 結算區域 (執行最終計算與衝突排除) =====================================
# ====================================================================

# 執行最終計算與衝突排除
total_tai, calculation_details = get_final_tai(st.session_state)

# 最終金額計算
calculated_amount = base_score + (total_tai * point_value)
final_money = calculated_amount * multiplier # 乘以加倍乘數

st.subheader("🎉 最終結算結果")

# 顯示明細
with st.expander("📝 完整台數明細 (點擊展開)", expanded=False):
    if calculation_details:
        st.code("\n".join(calculation_details))
    else:
        st.info("尚未勾選任何選項")

# 醒目的結果展示
r_col1, r_col2 = st.columns(2)
with r_col1:
    st.metric(label="總台數", value=f"{total_tai} 台")
with r_col2:
    if multiplier > 1:
        st.metric(label="應收/應付金額 (加倍後)", value=f"$ {final_money}")
        st.caption(f"原始金額: ${calculated_amount} x {multiplier} 倍")
    else:
        st.metric(label="應收/應付金額", value=f"$ {final_money}")

if total_tai >= 16:
    st.success("超級大牌！恭喜胡牌！")
    st.balloons()
