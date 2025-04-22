import streamlit as st
import yfinance as yf
import pandas as pd
from ta.trend import MACD
from ta.momentum import RSIIndicator
import plotly.graph_objs as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Forex Анализатор", layout="wide")
st.title("📈 Бесплатный анализатор Форекс рынка (15-минутный прогноз)")

symbol = st.text_input("Введите валютную пару (пример: EURUSD=X):", "EURUSD=X")

if st.button("Анализировать"):
    try:
        end = datetime.utcnow()
        start = end - timedelta(days=1)

        df = yf.download(symbol, start=start, end=end, interval="15m")

        if df.empty:
            st.warning("Не удалось загрузить данные. Попробуйте другую пару.")
        else:
            df.dropna(inplace=True)

            # Индикаторы
            rsi = RSIIndicator(close=df['Close']).rsi()
            macd = MACD(close=df['Close']).macd_diff()

            df["RSI"] = rsi
            df["MACD"] = macd

            # Последние значения индикаторов
            latest_rsi = rsi.iloc[-1]
            latest_macd = macd.iloc[-1]

            # Прогноз логики
            if latest_rsi < 30 and latest_macd > 0:
                prediction = "📈 Ожидается рост цены в течение 15 минут."
            elif latest_rsi > 70 and latest_macd < 0:
                prediction = "📉 Ожидается падение цены в течение 15 минут."
            else:
                prediction = "⏳ Направление неясно. Рынок нейтрален."

            st.subheader("Прогноз:")
            st.info(prediction)

            # График
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Курс'
            ))
            fig.update_layout(title="Свечной график", xaxis_title="Время", yaxis_title="Цена")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Технические индикаторы (последние значения):")
            st.write(f"**RSI**: {latest_rsi:.2f}")
            st.write(f"**MACD Diff**: {latest_macd:.5f}")

    except Exception as e:
        st.error(f"Ошибка: {e}")
