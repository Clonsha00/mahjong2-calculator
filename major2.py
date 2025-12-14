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

# --- 狀態初始化 (必須保留) ---
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


# --- 介面層級強制互斥與自動勾選函數 (v19.0 不變) ---
def handle_state_exclusion():
    """在每次互動後，先執行自動勾選，再強制修正衝突的 session state 值 (清除低階選項的勾選狀態)"""
    
    # === 階段 A: 智能自動勾選 (Auto-Inclusion) ===
    
    # 1. 自動判斷大三元
    if (st.session_state.get('dragon_red') and 
        st.session_state.get('dragon_green') and 
        st.session_state.get('dragon_white')):
        st.session_state['chk_3dragon_b'] = True 
        st.session_state['chk_3dragon_s'] = False 

    # 2. 自動判斷大四喜
    wind_sets_count = sum(st.session_state.get(f"wind_set_{i}", False) for i in range(4))
    
    if wind_sets_count == 4:
        st.session_state['chk_4wind_b'] = True 
        st.session_state['chk_4wind_s'] = False 
    

    # === 階段 B: 介面狀態強制互斥與覆蓋 (清除狀態) ===
    
    # 0. 絕對互斥: 大四喜 vs 大三元
    if st.session_state.get('chk_4wind_b'):
        st.session_state['chk_3dragon_b'] = False
        st.session_state['chk_3dragon_s'] = False
    elif st.session_state.get('chk_3dragon_b'):
        st.session_state['chk_4wind_b'] = False
        st.session_state['chk_4wind_s'] = False
        
    # 1. 暗刻衝突處理 (四 > 三)
    if st.session_state.get('chk_4ank'):
        st.session_state['chk_3ank'] = False

    # 2. 三元牌衝突處理 (大 > 小) 
    if st.session_state.get('chk_3dragon_b'):
        st.session_state['chk_3dragon_s'] = False
        
    # 3. 四喜衝突處理 (大 > 小) 
    if st.session_state.get('chk_4wind_b'):
        st.session_state['chk_4wind_s'] = False

    # 4. 顏色牌衝突 (字一色 > 清一色 > 混一色)
    if st.session_state.get('yaku_7'): # 字一色 (最高級)
        st.session_state['yaku_5'] = False # 清一色
        st.session_state['yaku_4'] = False # 混一色
    elif st.session_state.get('yaku_5'): # 清一色 (次高級)
        st.session_state['yaku_4'] = False # 混一色
        
    # 5. 門清自摸 vs 門清/自摸 衝突處理 (門清自摸 3台 優先)
    if st.session_state.get('yaku_1'): 
        st.session_state['yaku_0'] = False  # 門清
        st.session_state['chk_self'] = False # 自摸

    # 6. 全求人 vs 自摸 衝突處理 (全求人優先，強制點砲)
    if st.session_state.get('yaku_3') and st.session_state.get('chk_self'):
        st.session_state['chk_self'] = False

    # 7. 平胡 vs 碰碰和 絕對互斥
    if st.session_state.get('yaku_2') and st.session_state.get('yaku_6'):
         st.session_state['yaku_6'] = False
         
    elif st.session_state.get('yaku_6') and st.session_state.get('yaku_2'):
         st.session_state['yaku_2'] = False

# --- 牌型結構檢查函數 (v19.0 增強: 基礎刻子計數) ---
def structural_check(st_session):
    """
    檢查牌型結構是否超過 4 個面子 (14張牌規則)
    """
    errors = []
    
    # 1. 刻子數計算 (K_total)
    
    # 計算所有基礎字牌刻子數量 (作為面子來源)
    basic_koutsu_count = sum(st_session.get(f"wind_set_{i}", False) for i in range(4))
    basic_koutsu_count += sum(st_session.get(d, False) for d in ['dragon_red', 'dragon_green', 'dragon_white'])
    
    K_total = 0
    
    # 檢查是否有任何 4 面子牌型成立 (優先級高，直接設置 K_total = 4)
    is_4_sets_koutsu_yaku = st_session.get('yaku_6', False) or st_session.get('chk_4ank', False) or st_session.get('chk_4wind_b', False)
    
    if is_4_sets_koutsu_yaku:
        K_total = 4
        
    # 如果沒有 4 面子牌型，則計算 3/2/1 面子的組合
    elif st_session.get('chk_3dragon_b', False): # 大三元 = 3 刻子
        K_total = 3
    elif st_session.get('chk_4wind_s', False): # 小四喜 = 3 刻子
        K_total = 3
    elif st_session.get('chk_3dragon_s', False): # 小三元 = 2 刻子
        K_total = 2
    elif st_session.get('chk_3ank', False): # 三暗刻 = 3 刻子
        K_total = 3
    
    # 如果 K_total 仍然是 0，則使用基礎字牌刻子計數，但不超過 4
    if K_total == 0:
        K_total = min(basic_koutsu_count, 4)

    # 2. 順子數計算 (S_total)
    is_all_shuntsu = st_session.get('yaku_2', False) # 平胡 (4順子)
    S_total = 0
    if is_all_shuntsu:
        S_total = 4

    # 3. 總面子檢查
    total_sets = K_total + S_total
    
    if total_sets > 4:
        errors.append(f"❌ **牌型結構超限 ({total_sets} 面子)**：14 張牌最多只有 4 個面子。請只保留 4 個刻子或 4 個順子 (或混合，但總數必須是 4)。")
    elif total_sets < 4 and st_session.get('yaku_0', False):
        errors.append(f"⚠️ **結構不完整 (面子不足)**：您勾選了門清等牌型但面子總數只有 {total_sets} 組。請確認是否遺漏刻子或順子。")


    # 4. 風牌/箭牌刻子數量與大牌結構檢查 (輔助提醒)
    
    # 計算風/箭刻子實際數量 (來自基礎勾選)
    dragon_count = sum(st_session.get(d, False) for d in ['dragon_red', 'dragon_green', 'dragon_white'])
    wind_count = sum(st_session.get(f"wind_set_{i}", False) for i in range(4))
    
    if st_session.get('chk_3dragon_b', False) and dragon_count < 3:
        errors.append(f"⚠️ **大三元刻子不足**：大三元要求中發白 3 個刻子，但您只勾選了 {dragon_count} 個。")
    if st_session.get('chk_4wind_b', False) and wind_count < 4:
        errors.append(f"⚠️ **大四喜刻子不足**：大四喜要求東南西北 4 個刻子，但您只勾選了 {wind_count} 個。")

    return errors


# --- 最終計算函數 (v19.0) ---
def get_final_tai(st_session):
    """
    計算總台數，基於已由 handle_state_exclusion 修正的 session_state。
    所有操作均為只讀 (Read-Only)
    """
    final_tai = 0
    details = []
    
    # 讀取最終狀態
    is_menqing_self_draw = st_session.get('yaku_1', False)
    is_self_draw = st_session.get('chk_self', False)
    is_menqing = st_session.get('yaku_0', False)
    
    is_all_collect = st_session.get('yaku_3', False)
    is_qingyise = st.session_state.get('yaku_5', False)
    is_cuyise = st.session_state.get('yaku_4', False)
    is_ziyise = st.session_state.get('yaku_7', False)
    
    # --- 1. 狀態台數：莊家 & 連莊 ---
    if st_session.get('chk_dealer', False):
        final_tai += 1
        details.append("莊家 +1")

    # 連莊 (2N+1 台)
    lianzhuang = st_session.get('chk_lian', 0)
    if lianzhuang > 0:
        tai_val = lianzhuang * 2 + 1 
        final_tai += tai_val
        details.append(f"連{lianzhuang}拉{lianzhuang} +{tai_val} (2N+1 算法)")

    
    # --- 2. 自摸/門清 衝突處理 (已在 handle_state_exclusion 中處理完畢) ---
    
    if is_menqing_self_draw:
        final_tai += 3
        details.append("門清自摸 +3")
    
    elif is_self_draw: # 此時已確認沒有與全求人/門清自摸衝突
        final_tai += 1
        details.append("自摸 +1")
            
    if is_menqing:
        final_tai += 1
        details.append("門清 +1")

    
    # --- 3. 風台 (由程式自動判斷) ---
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
    
    
    # --- 4. 牌型台數 (YAKU_LIST) ---
    
    # A. 顏色牌衝突處理 (字一色 > 清一色 > 混一色)
    if is_ziyise:
        final_tai += 16
        details.append("字一色 +16 (自動排除清一色/湊一色)")
    elif is_qingyise: 
        final_tai += 8
        details.append("清一色 +8 (自動排除湊一色)")
    elif is_cuyise: 
        final_tai += 4
        details.append("湊一色 (混一色) +4")
    
    # B. 處理剩餘的 YAKU_LIST 項目 (平胡, 全求人, 碰碰胡)
    YAKU_LIST_MAP = {
        'yaku_2': {"name": "平胡", "tai": 2},
        'yaku_3': {"name": "全求人", "tai": 2}, 
        'yaku_6': {"name": "對對胡 (碰碰胡)", "tai": 4},
    }
    
    for key, data in YAKU_LIST_MAP.items():
        if st_session.get(key, False):
            final_tai += data["tai"]
            details.append(f"{data['name']} +{data['tai']}")


    # --- 5. 暗刻衝突處理 (只保留最大) ---
    if st.session_state.get('chk_4ank', False):
        final_tai += 5
        details.append("四暗刻 +5")
    elif st.session_state.get('chk_3ank', False):
        final_tai += 2
        details.append("三暗刻 +2")
        
    
    # --- 6. 三元牌衝突處理 (只保留最大) ---
    if st.session_state.get('chk_3dragon_b', False):
        final_tai += 8
        details.append("大三元 +8")
    elif st.session_state.get('chk_3dragon_s', False):
        final_tai += 4
        details.append("小三元 +4")
        
    # --- 7. 四喜牌衝突處理 (只保留最大) ---
    if st.session_state.get('chk_4wind_b', False):
        final_tai += 16 
        details.append("大四喜 +16")
    elif st.session_state.get('chk_4wind_s', False):
        final_tai += 8 
        details.append("小四喜 +8")
        
    
    # --- 8. 介面提醒 (針對被強制排除的選項) ---
    if st.session_state.get('chk_4ank', False) and st.session_state.get('chk_3ank', False):
         details.append("💡 排除提醒: 四暗刻已成立，三暗刻已自動排除計數。")
    if st.session_state.get('chk_3dragon_b', False) and st.session_state.get('chk_3dragon_s', False):
         details.append("💡 排除提醒: 大三元已成立，小三元已自動排除計數。")
    if st.session_state.get('chk_4wind_b', False) and st.session_state.get('chk_4wind_s', False):
         details.append("💡 排除提醒: 大四喜已成立，小四喜已自動排除計數。")
    if st.session_state.get('chk_4wind_b', False) and (st.session_state.get('chk_3dragon_b', False) or st.session_state.get('chk_3dragon_s', False)):
         details.append("💡 排除提醒: 大四喜已成立，三元牌系列已自動排除計數。")
    elif st.session_state.get('chk_3dragon_b', False) and (st.session_state.get('chk_4wind_b', False) or st.session_state.get('chk_4wind_s', False)):
         details.append("💡 排除提醒: 大三元已成立，四喜牌系列已自動排除計數。")
         
    if is_ziyise and (is_qingyise or is_cuyise):
         details.append("💡 排除提醒: 字一色已成立，清/混一色已自動排除計數。")
    elif is_qingyise and is_cuyise:
         details.append("💡 排除提醒: 清一色已成立，湊一色已自動排除計數。")
    if st.session_state.get('yaku_2', False) and st.session_state.get('yaku_6', False):
         details.append("💡 排除提醒: 平胡與碰碰和互斥，後勾選的已自動排除計數。")
    if st.session_state.get('yaku_1', False) and (st.session_state.get('yaku_0', False) or st.session_state.get('chk_self', False)):
         details.append("💡 排除提醒: 門清自摸 (3台) 已成立，門清/自摸 (1+1) 已自動排除計數。")
    if st.session_state.get('yaku_3', False) and st.session_state.get('chk_self', False):
         details.append("💡 排除提醒: 全求人成立，自摸台數因衝突已自動排除計數。")
    if st.session_state.get('chk_4wind_b', False) or st.session_state.get('chk_3dragon_b', False):
         details.append("💡 刻子提醒: 大四喜/大三元已包含單獨的風刻/箭刻台數。")


    return final_tai, details


# --- 頁面基本設定 ---
st.set_page_config(
    page_title="雙人麻將計算器 v19.0 (修正基礎刻子計數)",
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
st.caption("規則：台灣底台制，**13張起始/14張胡牌**，介面禁用與結構檢查")

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
        st.number_input("底 ($)", value=st.session_state.get('base'), step=50, key='base')
    with col2:
        st.number_input("台 ($)", value=st.session_state.get('point'), step=10, key='point')

st.divider()

# ====================================================================
# === 區塊 A：字牌刻子輸入與自動判斷風台 (不變) ===============================
# ====================================================================

st.subheader("1. 風/三元牌刻子輸入與台數")

st.write("請輸入**您有刻子或槓子**的風牌：")
# 風牌選擇清單 (東南西北)
WIND_OPTIONS = ["東風", "南風", "西風", "北風"]
col_input = st.columns(4)
for i, wind in enumerate(WIND_OPTIONS):
    with col_input[i]:
        st.checkbox(wind, key=f"wind_set_{i}", on_change=handle_state_exclusion)

# 玩家輸入：三元牌刻子
st.write("---")
st.write("三元牌刻子：")
col_dragon = st.columns(3)
col_dragon[0].checkbox("紅中刻子/槓子", key='dragon_red', on_change=handle_state_exclusion)
col_dragon[1].checkbox("發財刻子/槓子", key='dragon_green', on_change=handle_state_exclusion)
col_dragon[2].checkbox("白板刻子/槓子", key='dragon_white', on_change=handle_state_exclusion)

st.info("💡 **風/三元台數** 將在下方結算區**自動計算**。")
st.divider()


# ====================================================================
# === 區塊 B：狀態與牌型 (加入禁用邏輯) ======================================
# ====================================================================

st.subheader("2. 狀態與牌型") 

# 莊家/連莊/自摸
col_status1, col_status2 = st.columns(2)

with col_status1:
    st.checkbox("我是莊家 (+1台)", key='chk_dealer', on_change=handle_state_exclusion)
    
    # 衝突項目：自摸 (chk_self)
    is_self_draw_disabled = st.session_state.get('yaku_1', False) or st.session_state.get('yaku_3', False)
    
    st.checkbox("自摸 (+1台)", key='chk_self', on_change=handle_state_exclusion, disabled=is_self_draw_disabled)
    if is_self_draw_disabled:
        st.caption("因門清自摸/全求人衝突而禁用") 
        
with col_status2:
    st.number_input("連莊次數 (n)", min_value=0, step=1, key='chk_lian', on_change=handle_state_exclusion)

st.write("---")

# 定義牌型字典 (名稱: 台數)
YAKU_LIST = {
    "門清": 1,         # yaku_0
    "門清自摸": 3,     # yaku_1
    "平胡": 2,         # yaku_2
    "全求人": 2,         # yaku_3
    "湊一色 (混一色)": 4, # yaku_4
    "清一色": 8,       # yaku_5
    "對對胡 (碰碰胡)": 4, # yaku_6
    "字一色 (全字牌)": 16, # yaku_7
}

# 牌型勾選
cols = st.columns(4)
for i, (name, tai) in enumerate(YAKU_LIST.items()):
    key = f"yaku_{i}"
    
    # 判斷禁用狀態
    is_disabled = False
    
    if key == 'yaku_0': # 門清
        is_disabled = st.session_state.get('yaku_1', False)
    elif key == 'yaku_4': # 混一色
        is_disabled = st.session_state.get('yaku_5', False) or st.session_state.get('yaku_7', False)
    elif key == 'yaku_5': # 清一色
        is_disabled = st.session_state.get('yaku_7', False)
    elif key == 'yaku_2': # 平胡
        is_disabled = st.session_state.get('yaku_6', False)
    elif key == 'yaku_6': # 碰碰胡
        is_disabled = st.session_state.get('yaku_2', False)
    
    with cols[(i*2) % 4]:
        st.checkbox(f"{name} ({tai}台)", key=key, on_change=handle_state_exclusion, disabled=is_disabled)
    
    # 加入禁用提醒
    with cols[(i*2) % 4 + 1]:
        if is_disabled:
            st.caption("因衝突選項已禁用")
            
# 暗刻系列
st.write("---")
st.write("🌑 **暗刻計算** (擇一勾選)")
col_ank = st.columns(4) 

is_3ank_disabled = st.session_state.get('chk_4ank', False) 
col_ank[0].checkbox("三暗刻 (2台)", key='chk_3ank', on_change=handle_state_exclusion, disabled=is_3ank_disabled)
if is_3ank_disabled:
    col_ank[1].caption("被四暗刻禁用") 

col_ank[2].checkbox("四暗刻 (5台)", key='chk_4ank', on_change=handle_state_exclusion) 


# 三元牌大牌
st.write("---")
st.write("🐲 **三元牌大牌**")
col_dragon_yaku = st.columns(4)

is_s_3dragon_disabled = st.session_state.get('chk_3dragon_b', False) or st.session_state.get('chk_4wind_b', False)
col_dragon_yaku[0].checkbox("小三元 (4台)", key='chk_3dragon_s', on_change=handle_state_exclusion, disabled=is_s_3dragon_disabled)
if is_s_3dragon_disabled:
    st.caption("被大牌禁用")
    
is_b_3dragon_disabled = st.session_state.get('chk_4wind_b', False) # 大三元被大四喜禁用
col_dragon_yaku[2].checkbox("大三元 (8台)", key='chk_3dragon_b', on_change=handle_state_exclusion, disabled=is_b_3dragon_disabled)
if is_b_3dragon_disabled: 
    col_dragon_yaku[3].caption("被大四喜禁用")


# 四喜牌 
st.write("---")
st.write("💨 **四喜牌**")
col_wind_yaku = st.columns(4)

is_s_4wind_disabled = st.session_state.get('chk_4wind_b', False) or st.session_state.get('chk_3dragon_b', False)
col_wind_yaku[0].checkbox("小四喜 (8台)", key='chk_4wind_s', on_change=handle_state_exclusion, disabled=is_s_4wind_disabled)
if is_s_4wind_disabled:
    col_wind_yaku[1].caption("被大牌禁用")
    
is_b_4wind_disabled = st.session_state.get('chk_3dragon_b', False) # 大四喜被大三元禁用
col_wind_yaku[2].checkbox("大四喜 (16台)", key='chk_4wind_b', on_change=handle_state_exclusion, disabled=is_b_4wind_disabled)
if is_b_4wind_disabled: 
    col_wind_yaku[3].caption("被大三元禁用")

st.divider()

# ====================================================================
# === 結構檢查結果 (新區塊) ==================================================
# ====================================================================

structural_errors = structural_check(st.session_state)

st.subheader("⚖️ 牌型結構檢查結果")
if structural_errors:
    for error in structural_errors:
        st.error(error)
else:
    st.success("✅ 牌型結構符合 14 張牌 (4 面子 + 1 將眼) 的基本要求。")

st.divider()

# ====================================================================
# === 結算區域 (執行最終計算與衝突排除) =====================================
# ====================================================================

# 執行最終計算與衝突排除 
total_tai, calculation_details = get_final_tai(st.session_state)

# 最終金額計算
calculated_amount = st.session_state.get('base') + (total_tai * st.session_state.get('point'))
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
