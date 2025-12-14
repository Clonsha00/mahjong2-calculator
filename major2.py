import streamlit as st

# --- 迭代 1: 頁面配置與標題 ---
# 設定頁面為手機友善模式，標題置中
st.set_page_config(
    page_title="雙人麻將對戰計算機",
    page_icon="🀄",
    layout="centered", # 手機上 centered 比較聚焦
    initial_sidebar_state="collapsed" # 隱藏側邊欄爭取空間
)

st.title("🀄 雙人麻將-台數計算")
st.caption("手機最佳化版 | 台灣 16 張規則")

# --- 迭代 4: 定義計算函數 (核心邏輯) ---
def calculate_score(base_score, point_value, manual_tai, selected_yaku_sum):
    """計算總台數與金額"""
    total_tai = manual_tai + selected_yaku_sum
    # 計算公式：底 + (總台數 * 每台金額)
    # 雙人對戰通常是一家全賠
    total_amount = base_score + (total_tai * point_value)
    return total_tai, total_amount

# --- 台型字典定義 (可以持續擴充) ---
# 為了手機排版簡潔，這裡選錄最常用的
YAKU_OPTIONS = {
    "基本": {
        "莊家": 1,
        "連莊 (每連一次+2)": 0, # 需要特殊處理
        "自摸": 1,
        "門清 (無吃碰)": 1,
        "門清自摸 (加計)": 3, # 通常門清1+自摸1=2，但有些規則門清自摸算3
    },
    "常見牌型": {
        "平胡": 2,
        "對對胡": 2,
        "三暗刻": 2,
        "全求人": 2,
        "湊一色 (混一色)": 3,
    },
    "大牌與特殊": {
        "清一色": 8,
        "五暗刻": 8,
        "小三元": 4,
        "大三元": 8,
        "小四喜": 8,
        "大四喜": 16,
        "七搶一": 8,
        "八仙過海": 8,
    }
}

# --- 迭代 1 & 2: 主介面結構與輸入 ---

# 使用分頁切換玩家，節省空間
tab_a, tab_b = st.tabs(["👤 玩家 A 獲勝", "👤 玩家 B 獲勝"])

def render_player_tab(player_name):
    """渲染單一玩家結算頁面的函數"""
    st.header(f"{player_name} 結算輸入")

    # 使用 Expander 收折設定，讓畫面更清爽
    with st.expander("⚙️ 對局設定 (底/台)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            base_score = st.number_input("底 (金額)", min_value=0, value=100, step=50, key=f"{player_name}_base")
        with col2:
            point_value = st.number_input("每台 (金額)", min_value=0, value=20, step=10, key=f"{player_name}_point")
    
    st.divider()

    # --- 迭代 3: 台型勾選 (手機優化重點) ---
    selected_yaku_sum = 0
    
    st.subheader("✅ 台型勾選")
    
    # 1. 基本狀況折疊區
    with st.expander("🔹 基本狀況 (莊家/自摸...)"):
        # 特殊處理連莊
        lianzhuang = st.number_input("連莊次數 (n連莊)", min_value=0, value=0, step=1, key=f"{player_name}_lian")
        selected_yaku_sum += (lianzhuang * 2)
        if lianzhuang > 0:
             st.caption(f"連莊加台: {lianzhuang*2} 台")

        # 其他基本選項
        for yaku, tai in YAKU_OPTIONS["基本"].items():
            if yaku != "連莊 (每連一次+2)": # 跳過已處理的
                if st.checkbox(f"{yaku} ({tai}台)", key=f"{player_name}_{yaku}"):
                    selected_yaku_sum += tai

    # 2. 常見牌型折疊區
    with st.expander("🔹 常見牌型 (平胡/對對胡...)"):
         for yaku, tai in YAKU_OPTIONS["常見牌型"].items():
                if st.checkbox(f"{yaku} ({tai}台)", key=f"{player_name}_{yaku}"):
                    selected_yaku_sum += tai
                    
    # 3. 大牌折疊區
    with st.expander("🔥 大牌與特殊"):
         for yaku, tai in YAKU_OPTIONS["大牌與特殊"].items():
                if st.checkbox(f"{yaku} ({tai}台)", key=f"{player_name}_{yaku}"):
                    selected_yaku_sum += tai

    st.divider()

    # 額外手動輸入
    manual_tai = st.number_input("手動額外加台 (例如: 花牌、風牌)", min_value=0, value=0, step=1, key=f"{player_name}_manual")

    # --- 迭代 4: 計算與結果顯示 ---
    if st.button(f"計算 {player_name} 獲利", type="primary", use_container_width=True):
        total_tai, total_amount = calculate_score(base_score, point_value, manual_tai, selected_yaku_sum)
        
        st.divider()
        st.subheader("🎉 計算結果")
        
        # 使用 Metric 組件顯示重要數據，手機上看起來很專業
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric(label="總台數", value=f"{total_tai} 台")
        with m_col2:
            st.metric(label="向對方收取", value=f"${total_amount}")
            
        if total_tai >= 8:
             st.balloons() # 大牌特效

# 在對應的分頁渲染內容
with tab_a:
    render_player_tab("玩家 A")
with tab_b:
    render_player_tab("玩家 B")

# --- 頁尾提示 ---
st.divider()
st.caption("💡 提示：雙人模式下，通常由輸家全額支付給贏家。請根據實際約定調整底/台金額。")