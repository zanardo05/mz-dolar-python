from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_URL = "https://mz-dolar.vercel.app"
APP_ID = "1089"

@app.get("/")
def home():
    return {
        "status": "online",
        "api": "MZ Dólar Python Backend"
    }

# LOGIN DERIV
@app.get("/auth/login")
def login_deriv():

    redirect_uri = (
        "https://mz-dolar-python.onrender.com/auth/callback"
    )

    oauth_url = (
        f"https://oauth.deriv.com/oauth2/authorize"
        f"?app_id={APP_ID}"
        f"&redirect_uri={redirect_uri}"
    )

    return RedirectResponse(oauth_url)

# CALLBACK
@app.get("/auth/callback")
def callback(code: str = None):

    print("CODE:", code)

    if not code:
        return {
            "error": "OAuth code não encontrado"
        }

    # volta para frontend
    redirect = (
        f"{FRONTEND_URL}/#/dashboard?code={code}"
    )

    return RedirectResponse(redirect)
