from fastapi import APIRouter, Query
import pandas as pd
from typing import List

router = APIRouter()

data_url = 'https://assets.upstox.com/market-quote/instruments/exchange/complete.json.gz'
df = pd.read_json(data_url)
df['expiry'] = pd.to_datetime(df['expiry'], unit='ms')
df['expiry_date'] = df['expiry'].dt.date

@router.get("/instrument_keys")
def get_instrument_keys(
    underlying_symbol: str = Query(...),
    instrument_type: str = Query(...),
    expiry_date: str = Query(...),
    strike_prices: List[int] = Query(...)
):
    expiry_date_obj = pd.to_datetime(expiry_date).date()
    filtered = df[
        (df['underlying_symbol'] == underlying_symbol) &
        (df['instrument_type'] == instrument_type) &
        (df['strike_price'].isin(strike_prices)) &
        (df['expiry_date'] == expiry_date_obj)
    ]
    result = filtered[['trading_symbol', 'expiry', 'strike_price', 'instrument_key']].to_dict(orient='records')
    return {"count": len(result), "data": result}
