from fastapi import FastAPI, HTTPException
import requests
import pandas as pd
from datetime import date

app = FastAPI()

@app.get("/calculate_vwap")
def calculate_vwap(
    instrument_key: str,
    from_date: date,
    to_date: date,
    interval: str,
    access_token: str
):
    """
    Calculates the Volume-Weighted Average Price (VWAP) for a given instrument.

    Parameters:
    - instrument_key: The instrument key (e.g., "NSE_FO|40570")
    - from_date: The start date (e.g., "2025-09-05")
    - to_date: The end date (e.g., "2025-09-05")
    - interval: The time interval (e.g., "5")
    - access_token: Your Upstox OAuth token
    """
    url = f"https://api.upstox.com/v3/historical-candle/{instrument_key}/minutes/{interval}/{to_date}/{from_date}"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    try:
        resp = requests.get(url, headers=headers).json()

        if resp.get("status") != "success":
            raise HTTPException(status_code=400, detail=resp.get("message", "API call failed"))

        candles = resp.get("data", {}).get("candles")
        if not candles:
            raise HTTPException(status_code=404, detail="No candles data found for the specified period.")

        df = pd.DataFrame(candles, columns=[
            "timestamp", "open", "high", "low", "close", "volume", "open_interest"
        ])

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        df = df.sort_index(ascending=True)

        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
        df['cum_volume'] = df['volume'].cumsum()
        df['cum_vp'] = (df['typical_price'] * df['volume']).cumsum()
        df['vwap'] = df['cum_vp'] / df['cum_volume']

        # Convert DataFrame to a dictionary and return it as a JSON response
        result_df = df[['open', 'high', 'low', 'close', 'volume', 'vwap', 'open_interest']]
        return result_df.to_dict(orient='index')

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")