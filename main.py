import uvicorn
from fastapi import FastAPI
from instrument_api import router as instrument_router
from vwap_api import router as vwap_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.include_router(instrument_router)
app.include_router(vwap_router)
origins = [
    "http://localhost:3000",   # your frontend origin
    "https://trythonapi.onrender.com", # Allow your own domain
    "https://tradesync-gray.vercel.app", # Allow your own domain
    # Add more origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
