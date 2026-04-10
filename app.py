import streamlit as st
from streamlit_autorefresh import st_autorefresh
from data_fetcher import get_crypto_prices
from analysis_engine import render_coin_page
from database import get_history, insert_price, create_table


# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Trade Monitor Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ✅ FIX: create DB tables at startup
create_table()


# ---------- UI STYLE ----------
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a, #1e3a8a);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* REMOVE SIDEBAR */
section[data-testid="stSidebar"],
button[kind="header"],
div[data-testid="collapsedControl"] {
    display: none !important;
}

/* HEADER */
h1 {
    color: #facc15;
    text-align: center;
    font-weight: 800;
    letter-spacing: 1px;
    animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
    from { text-shadow: 0 0 5px rgba(250, 204, 21, 0.4); }
    to { text-shadow: 0 0 12px rgba(250, 204, 21, 0.7); }
}

h2, h3 {
    color: #38bdf8;
}

/* METRIC CARDS */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #0f172a, #020617);
    border-radius: 15px;
    padding: 18px;
    border: 1px solid #38bdf8;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
    transition: 0.3s;
}

div[data-testid="stMetric"]:hover {
    transform: scale(1.05);
    box-shadow: 0 0 30px rgba(56, 189, 248, 0.8);
}

/* BUTTONS */
div.stButton > button {
    background: linear-gradient(135deg, #1e3a8a, #0f172a);
    color: white;
    border-radius: 12px;
    border: 1px solid #38bdf8;
    padding: 10px 20px;
    font-weight: bold;
    transition: 0.3s;
}

div.stButton > button:hover {
    transform: scale(1.08);
    background: linear-gradient(135deg, #2563eb, #1e40af);
}

/* SEARCH BOX */
div[data-baseweb="select"] {
    background-color: #0f172a !important;
    color: white !important;
}

/* REMOVE PADDING */
.main .block-container {
    padding-top: 1rem;
}

</style>
""", unsafe_allow_html=True)


# ---------- AUTO REFRESH ----------
st_autorefresh(interval=30000, key="refresh")


# ---------- FETCH DATA ----------
new_prices = get_crypto_prices()

if "prices_cache" not in st.session_state:
    st.session_state.prices_cache = {}

if "error_count" not in st.session_state:
    st.session_state.error_count = 0

if new_prices:
    st.session_state.prices_cache = new_prices
    st.session_state.error_count = 0
else:
    st.session_state.error_count += 1

    if st.session_state.error_count >= 3:
        st.info("🔄 Reconnecting to live data...")

prices = st.session_state.prices_cache

if not prices:
    st.stop()

coins = list(prices.keys())


# ---------- STATE ----------
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "selected_coin" not in st.session_state:
    st.session_state.selected_coin = coins[0]


# ---------- HEADER ----------
st.markdown("# 🚀 AI Trade Monitor Pro")
st.caption("Real-time Crypto Intelligence • AI Powered Decisions")
st.markdown("---")


# ---------- LIVE TICKER ----------
ticker_text = "   |   ".join([f"{coin}: ${round(float(prices[coin]),2)}" for coin in coins])

st.markdown(f"""
<div style="overflow:hidden; white-space:nowrap;">
  <div style="display:inline-block; padding-left:100%; animation: scroll 20s linear infinite;">
    {ticker_text}
  </div>
</div>

<style>
@keyframes scroll {{
  from {{ transform: translateX(0); }}
  to {{ transform: translateX(-100%); }}
}}
</style>
""", unsafe_allow_html=True)


# ---------- SEARCH ----------
st.markdown("### 🔍 Search Coin")

selected_coin = st.selectbox("Select a coin", coins)

col1, col2 = st.columns(2)

with col1:
    if st.button("Go to Coin Page 🚀"):
        st.session_state.selected_coin = selected_coin
        st.session_state.page = "Coin"
        st.rerun()

with col2:
    if st.button("🏠 Back to Home"):
        st.session_state.page = "Home"
        st.rerun()


# ---------- SAVE PRICES ----------
for coin in coins:
    try:
        price = float(prices[coin])
        insert_price(coin, price)
    except:
        continue


# ---------- % CHANGE ----------
changes = {}

for coin in coins:
    history = get_history(coin)

    clean = []
    for h in history:
        try:
            clean.append(float(h))
        except:
            continue

    if len(clean) >= 5:
        old = clean[-5]
        new = clean[-1]

        if old != 0:
            change = ((new - old) / old) * 100
            changes[coin] = round(change, 2)
        else:
            changes[coin] = 0
    else:
        changes[coin] = 0


# ---------- HOME ----------
if st.session_state.page == "Home":

    sorted_coins = sorted(changes.items(), key=lambda x: x[1], reverse=True)

    gainers = sorted_coins[:3]
    losers = sorted_coins[-3:]

    colA, colB = st.columns(2)

    with colA:
        st.markdown("### 🟢 Top Gainers")
        for coin, change in gainers:
            st.success(f"{coin}: +{change}%")

    with colB:
        st.markdown("### 🔴 Top Losers")
        for coin, change in losers:
            st.error(f"{coin}: {change}%")

    st.markdown("## 💰 Market Overview")

    cols = st.columns(4)

    for i, coin in enumerate(coins):
        col = cols[i % 4]

        price = float(prices[coin])
        change = changes[coin]

        color = "🟢" if change >= 0 else "🔴"

        col.metric(
            label=f"{color} {coin}",
            value=f"${round(price,2)}",
            delta=f"{change}%"
        )

        if col.button(f"View {coin}"):
            st.session_state.selected_coin = coin
            st.session_state.page = "Coin"
            st.rerun()


# ---------- COIN PAGE ----------
elif st.session_state.page == "Coin":

    st.markdown(f"# 📊 {st.session_state.selected_coin} Analysis")

    render_coin_page(st.session_state.selected_coin, prices)