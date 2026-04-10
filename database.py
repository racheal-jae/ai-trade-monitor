import sqlite3


# ---------- INIT DATABASE ----------
def create_table():
    conn = sqlite3.connect("market_data.db")
    cursor = conn.cursor()

    # Prices table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        coin TEXT,
        price REAL
    )
    """)

    # Predictions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        coin TEXT,
        predicted_price REAL
    )
    """)

    conn.commit()
    conn.close()


# ---------- PRICE FUNCTIONS ----------
def insert_price(coin, price):
    conn = sqlite3.connect("market_data.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO prices (coin, price) VALUES (?, ?)",
        (coin, price)
    )

    conn.commit()
    conn.close()


def get_history(coin):
    conn = sqlite3.connect("market_data.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT price FROM prices WHERE coin=?",
        (coin,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]


# ---------- PREDICTION FUNCTIONS ----------
def save_prediction(coin, price):
    conn = sqlite3.connect("market_data.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO predictions (coin, predicted_price) VALUES (?, ?)",
        (coin, price)
    )

    conn.commit()
    conn.close()


def get_last_prediction(coin):
    conn = sqlite3.connect("market_data.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT predicted_price FROM predictions WHERE coin=? ORDER BY id DESC LIMIT 1",
        (coin,)
    )

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


def get_prediction_stats():
    conn = sqlite3.connect("market_data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT predicted_price FROM predictions")
    predictions = cursor.fetchall()

    cursor.execute("SELECT price FROM prices")
    prices = cursor.fetchall()

    conn.close()

    correct = 0
    total = min(len(predictions), len(prices))

    for i in range(total):
        try:
            predicted = float(predictions[i][0])
            actual = float(prices[i][0])

            error = abs(predicted - actual) / actual * 100

            if error < 1:
                correct += 1
        except:
            pass

    if total == 0:
        return 0

    return round((correct / total) * 100, 2)