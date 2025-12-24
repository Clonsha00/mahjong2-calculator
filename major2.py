import streamlit as st
import random

# --- 核心邏輯：擲骰子與風位判定 (不變) ---
if 'dice_roll' not in st.session_state: st.session_state.dice_roll = None
if 'dice_sum' not in st.session_state: st.session_sum = None
if 'wind_tai_type' not in st.session_state: st.session_state.wind_tai_type = None
if 'wind_tai_set' not in st.session_state: st.session_state.wind_tai_set = []
if 'is_double' not in st.session_state: st.session_state.is_double = False

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

# --- 狀態初始化 (不變) ---
for i in range(4): st.session_state.setdefault(f"wind_set_{i}", False)
st.session_state.setdefault('chk_dealer', False)
st.session_state.setdefault('chk_self', False)
st.session_state.setdefault('chk_lian', 0)
st.session_state.setdefault('chk_3ank', False)
st.session_state.setdefault('chk_4ank', False)
st.session_state.setdefault('chk_3dragon_s', False)
st.session_state.setdefault('chk_3dragon_b', False)
st.session_state.setdefault('dragon_red', False)
st.session_state.setdefault('dragon_green', False)
st.session_state.setdefault('dragon_white', False)
st.session_state.setdefault('chk_4wind_s', False) 
st.session_state.setdefault('chk_4wind_b', False) 
for i in range(8): st.session_state.setdefault(f"yaku_{i}", False)
st.session_state.setdefault('base', 100)
st.session_state.setdefault('point', 20)

# --- 一鍵清除所有狀態函數 (不變) ---
def clear_all_states():
    """重置所有與計算相關的 session_state 鍵值。"""
    for i in range(4): st.session_state[f"wind_set_{i}"] = False
    st.session_state['chk_dealer'] = False
    st.session_state['chk_self'] = False
    st.session_state['chk_lian'] = 0
    st.session_state['chk_3ank'] = False
    st.session_state['chk_4ank'] = False
    st.session_state['chk_3dragon_s'] = False
    st.session_state['chk_3dragon_b'] = False
    st.session_state['dragon_red'] = False
    st.session_state['dragon_green'] = False
    st.session_state['dragon_white'] = False
    st.session_state['chk_4wind_s'] = False
    st.session_state['chk_4wind_b'] = False
    for i in range(8): st.session_state[f"yaku_{i}"] = False
    
    st.session_state.dice_roll = None
    st.session_state.dice_sum = None
    st.session_state.wind_tai_type = None
    st.session_state.wind_tai_set = []
    st.session_state.is_double = False
    
    handle_state_exclusion()
    
# --- 輔助函數：檢查字牌刻子數量是否達到上限 (不變) ---
def is_max_koutsu_reached(current_key=None):
    koutsu_keys = [f"wind_set_{i}" for i in range(4)] + ['dragon_red', 'dragon_green', 'dragon_white']
    current_count = 0
    for key in koutsu_keys:
        if st.session_state.get(key, False):
            current_count += 1
    return current_count >= 4

# --- 介面層級強制互斥與自動勾選函數 (不變) ---
def handle_state_exclusion():
    wind_sets_count = sum(st.session_state.get(f"wind_set_{i}", False) for i in range(4))
    dragon_sets_count = sum(st.session_state.get(d, False) for d in ['dragon_red', 'dragon_green', 'dragon_white'])
    
    # 1. 大三元 (3 箭刻子)
    if dragon_sets_count >= 3:
        st.session_state['chk_3dragon_b'] = True 
        st.session_state['chk_3dragon_s'] = False 
    else:
        st.session_state['chk_3dragon_b'] = False
        st.session_state['chk_3dragon_s'] = False # 這裡只清被動觸發的，手動勾小三元在下面處理

    # 2. 大四喜 (4 風刻子)
    if wind_sets_count >= 4:
        st.session_state['chk_4wind_b'] = True 
        st.session_state['chk_4wind_s'] = False 
    else:
        st.session_state['chk_4wind_b'] = False
        st.session_state['chk_4wind_s'] = False
    
    # 互斥處理
    if st.session_state.get('chk_4wind_b'):
        st.session_state['chk_3dragon_b'] = False
        st.session_state['chk_3dragon_s'] = False
    elif st.session_state.get('chk_3dragon_b'):
        st.session_state['chk_4wind_b'] = False
        st.session_state['chk_4wind_s'] = False
        
    if st.session_state.get('chk_4ank'): st.session_state['chk_3ank'] = False
    if st.session_state.get('chk_3dragon_b'): st.session_state['chk_3dragon_s'] = False
    if st.session_state.get('chk_4wind_b'): st.session_state['chk_4wind_s'] = False

    if st.session_state.get('yaku_7'): 
        st.session_state['yaku_5'] = False 
        st.session_state['yaku_4'] = False 
    elif st.session_state.get('yaku_5'): 
        st.session_state['yaku_4'] = False 
        
    if st.session_state.get('yaku_1'): 
        st.session_state['yaku_0'] = False  
        st.session_state['chk_self'] = False 

    if st.session_state.get('yaku_3') and st.session_state.get('chk_self'):
        st.session_state['chk_self'] = False

    if st.session_state.get('yaku_2') and st.session_state.get('yaku_6'):
         st.session_state['yaku_6'] = False
    elif st.session_state.get('yaku_6') and st.session_state.get('yaku_2'):
         st.session_state['yaku_2'] = False

# --- 牌型結構檢查函數 (不變) ---
def structural_check(st_session):
    errors = []
    basic_koutsu_count = sum(st_session.get(f"wind_set_{i}", False) for i in range(4))
    basic_koutsu_count += sum(st_session.get(d, False) for d in ['dragon_red', 'dragon_green', 'dragon_white'])
    
    K_total = 0
    is_4_sets_koutsu_yaku = st_session.get('yaku_6', False) or st_session.get('chk_4ank', False) or st_session.get('chk_4wind_b', False)
    
    if is_4_sets_koutsu_yaku: K_total = 4
    elif st_session.get('chk_3dragon_b', False): K_total = 3
    elif st.session_state.get('chk_4wind_s', False): K_total = 3
    elif st.session_state.get('chk_3dragon_s', False): K_total = 2
    elif st.session_state.get('chk_3ank', False): K_total = 3
    
    if K_total == 0: K_total = min(basic_koutsu_count, 4)

    is_all_shuntsu = st_session.get('yaku_2', False)
    S_total = 4 if is_all_shuntsu else 0
    total_sets = K_total + S_total
    
    if total_sets > 4:
        errors.append(f"❌ **牌型結構超限 ({total_sets} 面子)**：14 張牌最多只有 4 個面子。")
    elif total_sets < 4 and st_session.get('yaku_0', False):
        errors.append(f"⚠️ **結構不完整 (面子不足)**：您勾選了門清等牌型但面子總數只有 {total_sets} 組。")

    dragon_count = sum(st_session.get(d, False) for d in ['dragon_red', 'dragon_green', 'dragon_white'])
    wind_count = sum(st_session.get(f"wind_set_{i}", False) for i in range(4))
    
    if st.session_state.get('chk_3dragon_b', False) and dragon_count < 3:
        errors.append(f"⚠️ **大三元刻子不足**：大三元要求 3 個刻子。")
    if st.session_state.get('chk_4wind_b', False) and wind_count < 4:
        errors.append(f"⚠️ **大四喜刻子不足**：大四喜要求 4 個刻子。")

    return errors


# --- 最終計算函數 (★ 修改重點：加入三元牌台數) ---
def get_final_tai(st_session):
    final_tai = 0
    details = []
    
    # 讀取狀態
    is_menqing_self_draw = st_session.get('yaku_1', False)
    is_self_draw = st_session.get('chk_self', False)
    is_menqing = st_session.get('yaku_0', False)
    
    is_ziyise = st.session_state.get('yaku_7', False)
    is_qingyise = st.session_state.get('yaku_5', False)
    is_cuyise = st.session_state.get('yaku_4', False)
    
    # 1. 莊家 & 連莊
    if st_session.get('chk_dealer', False):
        final_tai += 1
        details.append("莊家 +1")

    lianzhuang = st_session.get('chk_lian', 0)
    if lianzhuang > 0:
        tai_val = lianzhuang * 2 + 1 
        final_tai += tai_val
        details.append(f"連{lianzhuang}拉{lianzhuang} +{tai_val}")

    # 2. 自摸/門清
    if is_menqing_self_draw:
        final_tai += 3
        details.append("門清自摸 +3")
    elif is_self_draw:
        final_tai += 1
        details.append("自摸 +1")
    if is_menqing:
        final_tai += 1
        details.append("門清 +1")

    # 3. 風台 (門風)
    current_tai_wind = 0
    player_wind_set = []
    for i in range(4):
        if st_session.get(f"wind_set_{i}", False):
            player_wind_set.append(["東風", "南風", "西風", "北風"][i]) 
    
    if st_session.get('wind_tai_set'):
        for wind in player_wind_set:
            if wind in st_session.get('wind_tai_set'):
                current_tai_wind += 1
                details.append(f"門風台 ({wind}) +1")
    final_tai += current_tai_wind
    
    # 4. ★ NEW: 三元牌 (箭牌) 台數 ★
    # 邏輯：只有在 "沒有" 大三元或小三元時，才單獨計算中發白每刻 +1。
    # 因為大三元 (8台) 和小三元 (4台) 已經包含了這些刻子的台數價值。
    has_big_dragon = st.session_state.get('chk_3dragon_b', False)
    has_small_dragon = st.session_state.get('chk_3dragon_s', False)
    
    if not has_big_dragon and not has_small_dragon:
        if st_session.get('dragon_red', False):
            final_tai += 1
            details.append("紅中 +1")
        if st_session.get('dragon_green', False):
            final_tai += 1
            details.append("發財 +1")
        if st_session.get('dragon_white', False):
            final_tai += 1
            details.append("白板 +1")
    
    
    # 5. 牌型台數
    if is_ziyise:
        final_tai += 16
        details.append("字一色 +16")
    elif is_qingyise: 
        final_tai += 8
        details.append("清一色 +8")
    elif is_cuyise: 
        final_tai += 4
        details.append("湊一色 +4")
    
    YAKU_LIST_MAP = {
        'yaku_2': {"name": "平胡", "tai": 2},
        'yaku_3': {"name": "全求人", "tai": 2}, 
        'yaku_6': {"name": "對對胡", "tai": 4},
    }
    for key, data in YAKU_LIST_MAP.items():
        if st_session.get(key, False):
            final_tai += data["tai"]
            details.append(f"{data['name']} +{data['tai']}")

    # 6. 暗刻
    if st.session_state.get('chk_4ank', False):
        final_tai += 5
        details.append("四暗刻 +5")
    elif st.session_state.get('chk_3ank', False):
        final_tai += 2
        details.append("三暗刻 +2")
        
    # 7. 三元牌大牌
    if has_big_dragon:
        final_tai += 8
        details.append("大三元 +8")
    elif has_small_dragon:
        final_tai += 4
        details.append("小三元 +4")
        
    # 8. 四喜牌
    if st.session_state.get('chk_4wind_b', False):
        final_tai += 16 
        details.append("大四喜 +16")
    elif st.session_state.get('chk_4wind_s', False):
        final_tai += 8 
        details.append("小四喜 +8")
        
    # 提醒
    if has_big_dragon or has_small_dragon:
         details.append("💡 三元牌提醒: 大/小三元已包含單獨箭牌台數，不重複計算。")

    return final_tai, details


# --- 頁面基本設定 ---
st.set_page_config(
    page_title="雙人麻將計算器 v23.0 (三元牌修正)",
    page_icon="🀄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 自定義樣式 (不變) ---
st.markdown("""
    <style>
    div.stButton > button { height: 3rem; font-size: 1.2rem; font-weight: bold; }
    div[data-testid="stMetricValue"] { font-size: 2.5rem; }
    .stAlert { font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 介面呈現 ---
st.title("🀄 雙人麻將：胡牌計算機")
st.caption("規則：台灣底台制，v23.0 修正三元牌(中發白)單獨台數")

st.button("🔄 一鍵清除所有選項", on_click=clear_all_states, type="secondary", use_container_width=True)

# 區塊 0
st.subheader("🎲 0. 擲骰子判定風台")
col_dice, col_result = st.columns([1, 2])
with col_dice:
    st.button("擲骰子", on_click=roll_dice, type="primary", use_container_width=True)
with col_result:
    if st.session_state.dice_roll:
        d1, d2 = st.session_state.dice_roll
        total = st.session_state.dice_sum
        st.metric("骰子結果", f"{d1} + {d2} = {total}")
    else:
        st.metric("骰子結果", "點擊按鈕擲骰")

if st.session_state.wind_tai_type:
    st.warning(f"當前門風：{st.session_state.wind_tai_type}。{st.session_state.wind_tai_set} 刻子 +1。")

multiplier = 1
if st.session_state.is_double:
    st.error("🚨 **豹子/圍骰！** 金額兩倍。")
    multiplier = 2

st.divider()

with st.expander("⚙️ 設定底/台金額", expanded=False):
    col1, col2 = st.columns(2)
    with col1: st.number_input("底 ($)", value=st.session_state.get('base'), step=50, key='base')
    with col2: st.number_input("台 ($)", value=st.session_state.get('point'), step=10, key='point')

st.divider()

# 區塊 A
st.subheader("1. 風/三元牌刻子輸入")
is_koutsu_max = is_max_koutsu_reached()

st.write("風牌刻子：")
WIND_OPTIONS = ["東風", "南風", "西風", "北風"]
col_input = st.columns(4)
for i, wind in enumerate(WIND_OPTIONS):
    key = f"wind_set_{i}"
    disabled = is_koutsu_max and not st.session_state.get(key, False)
    with col_input[i]:
        st.checkbox(wind, key=key, on_change=handle_state_exclusion, disabled=disabled)

st.write("三元牌刻子 (+1台)：")
col_dragon = st.columns(3)
dragon_keys = ['dragon_red', 'dragon_green', 'dragon_white']
for i, name in enumerate(['紅中', '發財', '白板']):
    key = dragon_keys[i]
    disabled = is_koutsu_max and not st.session_state.get(key, False)
    with col_dragon[i]:
        st.checkbox(name, key=key, on_change=handle_state_exclusion, disabled=disabled)

if is_koutsu_max: st.info("ℹ️ 字牌刻子已達上限。")
st.divider()

# 區塊 B
st.subheader("2. 狀態與牌型") 
col_status1, col_status2 = st.columns(2)
with col_status1:
    st.checkbox("我是莊家 (+1)", key='chk_dealer', on_change=handle_state_exclusion)
    is_self_draw_disabled = st.session_state.get('yaku_1', False) or st.session_state.get('yaku_3', False)
    st.checkbox("自摸 (+1)", key='chk_self', on_change=handle_state_exclusion, disabled=is_self_draw_disabled)
with col_status2:
    st.number_input("連莊次數", min_value=0, step=1, key='chk_lian', on_change=handle_state_exclusion)

st.write("---")

YAKU_LIST = {
    "門清": 1, "門清自摸": 3, "平胡": 2, "全求人": 2,
    "湊一色": 4, "清一色": 8, "對對胡": 4, "字一色": 16,
}
cols = st.columns(4)
for i, (name, tai) in enumerate(YAKU_LIST.items()):
    key = f"yaku_{i}"
    is_disabled = False
    if key == 'yaku_0': is_disabled = st.session_state.get('yaku_1', False)
    elif key == 'yaku_4': is_disabled = st.session_state.get('yaku_5', False) or st.session_state.get('yaku_7', False)
    elif key == 'yaku_5': is_disabled = st.session_state.get('yaku_7', False)
    elif key == 'yaku_2': is_disabled = st.session_state.get('yaku_6', False)
    elif key == 'yaku_6': is_disabled = st.session_state.get('yaku_2', False)
    
    with cols[(i*2) % 4]:
        st.checkbox(f"{name} ({tai})", key=key, on_change=handle_state_exclusion, disabled=is_disabled)

st.write("---")
st.write("🌑 **暗刻計算**")
col_ank = st.columns(4) 
is_3ank_disabled = st.session_state.get('chk_4ank', False) 
col_ank[0].checkbox("三暗刻 (2台)", key='chk_3ank', on_change=handle_state_exclusion, disabled=is_3ank_disabled)
col_ank[2].checkbox("四暗刻 (5台)", key='chk_4ank', on_change=handle_state_exclusion) 

st.write("---")
st.write("🐲 **三元牌大牌**")
col_dragon_yaku = st.columns(4)
is_s_3dragon_disabled = st.session_state.get('chk_3dragon_b', False) or st.session_state.get('chk_4wind_b', False)
col_dragon_yaku[0].checkbox("小三元 (4台)", key='chk_3dragon_s', on_change=handle_state_exclusion, disabled=is_s_3dragon_disabled)
is_b_3dragon_disabled = st.session_state.get('chk_4wind_b', False)
col_dragon_yaku[2].checkbox("大三元 (8台)", key='chk_3dragon_b', on_change=handle_state_exclusion, disabled=is_b_3dragon_disabled)

st.write("---")
st.write("💨 **四喜牌**")
col_wind_yaku = st.columns(4)
is_s_4wind_disabled = st.session_state.get('chk_4wind_b', False) or st.session_state.get('chk_3dragon_b', False)
col_wind_yaku[0].checkbox("小四喜 (8台)", key='chk_4wind_s', on_change=handle_state_exclusion, disabled=is_s_4wind_disabled)
is_b_4wind_disabled = st.session_state.get('chk_3dragon_b', False)
col_wind_yaku[2].checkbox("大四喜 (16台)", key='chk_4wind_b', on_change=handle_state_exclusion, disabled=is_b_4wind_disabled)

st.divider()

structural_errors = structural_check(st.session_state)
st.subheader("⚖️ 結構檢查")
if structural_errors:
    for error in structural_errors: st.error(error)
else:
    st.success("✅ 牌型結構正常")

st.divider()

total_tai, calculation_details = get_final_tai(st.session_state)
calculated_amount = st.session_state.get('base') + (total_tai * st.session_state.get('point'))
final_money = calculated_amount * multiplier

st.subheader("🎉 結算結果")
with st.expander("📝 台數明細", expanded=False):
    if calculation_details: st.code("\n".join(calculation_details))
    else: st.info("無")

r_col1, r_col2 = st.columns(2)
with r_col1: st.metric("總台數", f"{total_tai} 台")
with r_col2: st.metric("應收/付", f"$ {final_money}")

if total_tai >= 16:
    st.success("超級大牌！")
    st.balloons()
