from fastapi import APIRouter, Query
import pandas as pd
from typing import List

router = APIRouter()

data_url = 'https://assets.upstox.com/market-quote/instruments/exchange/complete.json.gz'
# df = pd.read_json(data_url)
# df['expiry'] = pd.to_datetime(df['expiry'], unit='ms')
# df['expiry_date'] = df['expiry'].dt.date
INSTRUMENTS_DF = None
@router.get("/")
def read_root():
    # ADDED: A more informative status response for the frontend check
    return {"status": "success", "message": "Hello, I am up! You can proceed..."}
def get_instrument_df():
    """Loads the DataFrame once and caches it for subsequent calls."""
    global INSTRUMENTS_DF
    if INSTRUMENTS_DF is None:
        print("--- Loading instrument data into memory (FIRST RUN ONLY) ---")
        df_local = pd.read_json(data_url)
        df_local['expiry'] = pd.to_datetime(df_local['expiry'], unit='ms')
        df_local['expiry_date'] = df_local['expiry'].dt.date
        INSTRUMENTS_DF = df_local
    return INSTRUMENTS_DF
@router.get("/instrument_keys")
def get_instrument_keys(
    underlying_symbol: str = Query(...),
    instrument_type: str = Query(...),  # "CE" or "PE"
    expiry_date: str = Query(...),
    strike_price: int = Query(...)  # Single strike price input
):
    df = get_instrument_df()
    expiry_date_obj = pd.to_datetime(expiry_date).date()

    # Generate list of strike prices: input strike price +/- 50 * n (n=1 to 10)
    # For example, if strike_price=26000, this includes [25500, 25550, ..., 26500]
    strike_prices = [strike_price + i * 50 for i in range(-10, 11)]

    # Filter dataframe based on input and generated strike prices
    filtered = df[
        (df['underlying_symbol'] == underlying_symbol) &
        (df['instrument_type'] == instrument_type) &
        (df['strike_price'].isin(strike_prices)) &
        (df['expiry_date'] == expiry_date_obj)
    ]

    # Format response as requested
    result = filtered[['trading_symbol', 'expiry', 'strike_price', 'instrument_key']]
    result=result.sort_values(by='strike_price',ascending=False)
    result_dict = result.to_dict(orient='records')

    return {"count": len(result_dict), "data": result_dict}
