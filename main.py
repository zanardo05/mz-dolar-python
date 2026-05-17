from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

import secrets
import hashlib
import base64
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth Client ID Deriv
CLIENT_ID = "33i32GbNdYrf99M2AM24V"

# Frontend
FRONTEND_URL = (
    "https://mz-dolar.vercel.app"
)

# Callback Render
REDIRECT_URI = (
    "https://mz-dolar-python.onrender.com/auth/callback"
)

# Memória temporária PKCE
pkce_storage = {}

# Gera PKCE
def generate_pkce():

    code_verifier = (
        secrets.token_urlsafe(64)
    )

    challenge = hashlib.sha256(
        code_verifier.encode()
    ).digest()

    code_challenge = base64.urlsafe_b64encode(
        challenge
    ).decode().replace("=", "")

    return (
        code_verifier,
        code_challenge
    )

@app.get("/")
def home():

    return {
        "status": "online",
        "api": "MZ Dólar Python Backend"
    }

# LOGIN DERIV
@app.get("/auth/login")
def login():

    state = secrets.token_urlsafe(16)

    code_verifier, code_challenge = generate_pkce()

    # salva verifier
    pkce_storage[state] = code_verifier

    auth_url = (
        "https://auth.deriv.com/oauth2/auth"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=trade account_manage"
        f"&state={state}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
    )

    print("AUTH URL:", auth_url)

    return RedirectResponse(
        auth_url
    )

# CALLBACK DERIV
@app.get("/auth/callback")
def callback(
    code: str = None,
    state: str = None
):

    try:

        print("CODE:", code)
        print("STATE:", state)

        if not code:

            return {
                "erro": "OAuth code não encontrado"
            }

        code_verifier = pkce_storage.get(state)

        print(
            "CODE VERIFIER:",
            code_verifier
        )

        if not code_verifier:

            return {
                "erro": "Code verifier não encontrado"
            }

        token_url = (
            "https://auth.deriv.com/oauth2/token"
        )

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": code_verifier
        }

        print(
            "PAYLOAD:",
            payload
        )

        response = requests.post(
            token_url,
            data=payload
        )

        print(
            "STATUS:",
            response.status_code
        )

        print(
            "TEXT:",
            response.text
        )

        try:

            data = response.json()

        except Exception:

            return {
                "erro": "Resposta não JSON",
                "texto": response.text
            }

        print(
            "JSON:",
            data
        )

        access_token = data.get(
            "access_token"
        )

        if not access_token:

            return data

        # volta para frontend
        redirect = (
            f"{FRONTEND_URL}/#/dashboard?token={access_token}"
        )

        print(
            "REDIRECT:",
            redirect
        )

        return RedirectResponse(
            redirect
        )

    except Exception as e:

        print(
            "ERRO:",
            str(e)
        )

        return {
            "erro": str(e)
        }
