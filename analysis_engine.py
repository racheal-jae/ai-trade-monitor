# ---------- BASIC SIGNAL ----------
def generate_signal(price):
    try:
        price = float(price)
    except:
        return "HOLD"

    if price < 100:
        return "BUY"
    elif price > 500:
        return "SELL"
    else:
        return "HOLD"


# ---------- MOVING AVERAGE ----------
def moving_average(prices, window=5):
    clean = []

    for p in prices:
        try:
            clean.append(float(p))
        except:
            continue

    if len(clean) < window:
        return None

    return sum(clean[-window:]) / window


# ---------- RSI ----------
def calculate_rsi(prices, period=14):
    clean = []

    for p in prices:
        try:
            clean.append(float(p))
        except:
            continue

    if len(clean) < period:
        return None

    gains = []
    losses = []

    for i in range(1, len(clean)):
        diff = clean[i] - clean[i - 1]

        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# ---------- CONFIDENCE ----------
def calculate_confidence(prediction, current_price):
    try:
        prediction = float(prediction)
        current_price = float(current_price)
    except:
        return 0

    if current_price == 0:
        return 0

    error = abs(prediction - current_price) / current_price * 100
    return round(max(0, 100 - error), 2)


# ---------- MAIN PAGE RENDER ----------
def render_coin_page(coin_name, prices):

    import streamlit as st
    import plotly.graph_objects as go
    from database import get_history, save_prediction, get_last_prediction
    from ai_model import predict_price

    st.markdown(f"# 🚀 {coin_name} AI Dashboard")

    # ---------- CURRENT PRICE ----------
    try:
        current_price = float(prices.get(coin_name, 0))
    except:
        current_price = 0

    st.metric(f"{coin_name} Price", f"${current_price}")

    # ---------- HISTORY ----------
    history = get_history(coin_name)

    if not history:
        st.warning("No historical data yet — collecting data...")

    fig = go.Figure(data=[go.Scatter(y=history if history else [])])

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0")
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------- CLEAN DATA ----------
    clean = []

    for p in history:
        try:
            clean.append(float(p))
        except:
            continue

    # ---------- AI PREDICTION ----------
    st.markdown("## 🤖 AI Prediction")

    if len(clean) < 5:

        st.warning("⚠️ Not enough data yet — using estimated prediction")

        if current_price > 0:
            prediction = current_price * 1.02  # demo prediction

            st.success(f"Estimated Price: ${round(prediction,2)}")

            if prediction > current_price:
                st.success("📈 BUY Signal")
            else:
                st.error("📉 SELL Signal")

    else:
        prediction = predict_price(clean)

        try:
            prediction = float(prediction)
        except:
            prediction = None

        if prediction is not None and current_price > 0:

            st.success(f"Predicted Price: ${round(prediction, 2)}")

            confidence = calculate_confidence(prediction, current_price)
            st.info(f"Confidence: {confidence}%")

            if prediction > current_price:
                st.success("📈 BUY Signal")
            else:
                st.error("📉 SELL Signal")

            save_prediction(coin_name, prediction)

        else:
            st.warning("Prediction unavailable")

    # ---------- INDICATORS ----------
    st.markdown("### 📊 Technical Indicators")

    ma = moving_average(clean)
    rsi = calculate_rsi(clean)

    if ma is not None:
        st.write(f"Moving Average: ${round(ma, 2)}")

        if current_price > ma:
            st.success("Uptrend 📈")
        else:
            st.warning("Downtrend 📉")

    if rsi is not None:
        st.write(f"RSI: {round(rsi, 2)}")

        if rsi > 70:
            st.error("Overbought → SELL")
        elif rsi < 30:
            st.success("Oversold → BUY")
        else:
            st.info("Neutral Market")

    # ---------- VALIDATION ----------
    last = get_last_prediction(coin_name)

    if last is not None:

        try:
            last = float(last)
        except:
            last = None

        if last is not None:

            st.markdown("### 🔍 Prediction Validation")

            st.write(f"Previous Prediction: ${last}")
            st.write(f"Current Price: ${current_price}")

            diff = abs(current_price - last)

            if diff < 10:
                st.success("Prediction Correct ✅")
            else:
                st.error("Prediction Incorrect ❌")