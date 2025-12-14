import streamlit as st
import random

# =========================================================
# 0. Session State 初始化
# =========================================================
if 'dice_roll' not in st.session_state: st.session_state.dice_roll = None
if 'dice_sum' not in st.session_state: st.session_state.dice_sum = None
if 'wind_tai_type' not in st.session_state: st.session_state.wind_tai_type = None
if 'wind_tai_set' not in st.session_state: st.session_state.wind_tai_set = []
if 'is_double' not in st.session_state: st.session_state.is_double = False

for i in range(4):
    st.session_state.setdefault(f"wind_set_{i}", False)

st.session_state.setdefault('chk_dealer', False)
st.session_state.setdefault('chk_self', False)
st.session_state.setdefault('chk_lian', 0)

st.session_state.setdefault('chk_3ank', False)
st.session_state.setdefault('chk_4ank', False)
st.session_state.setdefault('chk_5ank', False)

st.session_state.setdefault('dragon_red', False)
st.session_state.setdefault('dragon_green', False)
st.session_state.setdefault('dragon_white', False)

st.session_state.setdefault('chk_3dragon_s', False)
st.session_state.setdefault('chk_3dragon_b', False)

for i in range(8):
    st.session_state.setdefault(f"yaku_{i}", False)

st.session_state.setdefault('base', 100)
st.session_state.setdefault('point', 20)

# =========================================================
# 1. 擲骰子判定門風
# =========================================================
def roll_dice():
    d1, d2 = random.randint(1, 6), random.randint(1, 6)
    total = d1 + d2
    st.session_state.dice_roll = (d1, d2)
    st.session_state.dice_sum = total
    st.session_state.is_double = (d1 == d2)

    if total % 2:
        st.session_state.wind_tai_type = "奇數（東 / 西）"
        st.session_state.wind_tai_set = ["東風", "西風"]
    else:
        st.session_state.wind_tai_type = "偶數（南 / 北）"
        st.session_state.wind_tai_set = ["南風", "北風"]

# =========================================================
# 2. 介面層級互斥與自動判定
# =========================================================
def handle_state_exclusion():

    # ---- 暗刻互斥：五 > 四 > 三 ----
    if st.session_state.chk_5ank:
        st.session_state.chk_4ank = False
        st.session_state.chk_3ank = False
    elif st.session_state.chk_4ank:
        st.session_state.chk_3ank = False

    # ---- 三元牌刻子 → 自動判定大小三元 ----
    dragon_count = sum([
        st.session_state.dragon_red,
        st.session_state.dragon_green,
        st.session_state.dragon_white
    ])

    if dragon_count == 3:
        st.session_state.chk_3dragon_b = True
        st.session_state.chk_3dragon_s = False
    elif dragon_count == 2:
        st.session_state.chk_3dragon_s = True
        st.session_state.chk_3dragon_b = False
    else:
        st.session_state.chk_3dragon_s = False
        st.session_state.chk_3dragon_b = False

    # ---- 清一色 > 混一色 ----
    if st.session_state.yaku_5:
        st.session_state.yaku_4 = False

    # ---- 門清自摸 > 門清 + 自摸 ----
    if st.session_state.yaku_1:
        st.session_state.yaku_0 = False
        st.session_state.chk_self = False

    # ---- 全求人 強制點砲 ----
    if st.session_state.yaku_3:
        st.session_state.chk_self = False

# =========================================================
# 3. 純計算函數（不改狀態）
# =========================================================
def get_final_tai(s):
    tai = 0
    details = []

    # 莊家 / 連莊
    if s.chk_dealer:
        tai += 1
        details.append("莊家 +1")

    if s.chk_lian > 0:
        val = s.chk_lian * 2 + 1
        tai += val
        details.append(f"連{ s.chk_lian }拉 +{val}")

    # 門清 / 自摸
    if s.yaku_1:
        tai += 3
        details.append("門清自摸 +3")
    else:
        if s.chk_self:
            tai += 1
            details.append("自摸 +1")
        if s.yaku_0:
            tai += 1
            details.append("門清 +1")

    # 門風台
    winds = ["東風", "南風", "西風", "北風"]
    for i in range(4):
        if s[f"wind_set_{i}"] and winds[i] in s.wind_tai_set:
            tai += 1
            details.append(f"{winds[i]} 門風台 +1")

    # 牌型
    YAKU_MAP = {
        'yaku_2': ("平胡", 2),
        'yaku_3': ("全求人", 2),
        'yaku_4': ("混一色", 4),
        'yaku_5': ("清一色", 8),
        'yaku_6': ("對對胡", 4),
        'yaku_7': ("字一色", 16),
    }

    for k, (name, val) in YAKU_MAP.items():
        if s[k]:
            tai += val
            details.append(f"{name} +{val}")

    # 暗刻
    if s.chk_5ank:
        tai += 8; details.append("五暗刻 +8")
    elif s.chk_4ank:
        tai += 5; details.append("四暗刻 +5")
    elif s.chk_3ank:
        tai += 2; details.append("三暗刻 +2")

    # 三元牌
    if s.chk_3dragon_b:
        tai += 8; details.append("大三元 +8")
    elif s.chk_3dragon_s:
        tai += 4; details.append("小三元 +4")

    return tai, details

# =========================================================
# 4. UI
# =========================================================
st.set_page_config("雙人麻將計算器 v11.1", "🀄", layout="centered")
st.title("🀄 雙人麻將胡牌計算器")
st.caption("v11.1｜完整功能・自動互斥・穩定版")

st.button("🎲 擲骰子", on_click=roll_dice)

if st.session_state.dice_roll:
    d1, d2 = st.session_state.dice_roll
    st.metric("骰子結果", f"{d1} + {d2} = {st.session_state.dice_sum}")

if st.session_state.is_double:
    st.error("🚨 圍骰（豹子）！最終金額 ×2")

st.divider()

st.subheader("三元牌刻子")
st.checkbox("紅中", key='dragon_red', on_change=handle_state_exclusion)
st.checkbox("發財", key='dragon_green', on_change=handle_state_exclusion)
st.checkbox("白板", key='dragon_white', on_change=handle_state_exclusion)

st.divider()

total_tai, details = get_final_tai(st.session_state)
money = (st.session_state.base + total_tai * st.session_state.point) * (2 if st.session_state.is_double else 1)

st.subheader("🎉 結算結果")
st.metric("總台數", total_tai)
st.metric("金額", f"$ {money}")

with st.expander("📝 台數明細"):
    st.code("\n".join(details) if details else "尚未選擇任何項目")
