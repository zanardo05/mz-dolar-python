from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

import secrets
import hashlib
import base64
import requests
import websocket
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth Client ID
CLIENT_ID = "33i32GbNdYrf99M2AM24V"

# APP ID websocket
APP_ID = "74231"  # TROQUE PELO SEU APP ID NUMÉRICO

# FRONTEND
FRONTEND_URL = (
    "https://mz-dolar.vercel.app"
)

# CALLBACK
REDIRECT_URI = (
    "https://mz-dolar-python.onrender.com/auth/callback"
)

# armazenamento PKCE
pkce_storage = {}

# sessão OAuth
deriv_oauth_token = None

# gera PKCE
def generate_pkce():

    code_verifier = (
        secrets.token_urlsafe(64)
    )

    challenge = hashlib.sha256(
        code_verifier.encode()
    ).digest()

    code_challenge = (
        base64
        .urlsafe_b64encode(challenge)
        .decode()
        .replace("=", "")
    )

    return (
        code_verifier,
        code_challenge
    )

@app.get("/")
def home():

    return {
        "status": "online",
        "api": "MZ Dólar Backend"
    }

# LOGIN DERIV
@app.get("/auth/login")
def login():

    state = (
        secrets.token_urlsafe(16)
    )

    code_verifier, code_challenge = (
        generate_pkce()
    )

    pkce_storage[state] = (
        code_verifier
    )

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

        if not code:

            return {
                "erro":
                "OAuth code não encontrado"
            }

        code_verifier = (
            pkce_storage.get(state)
        )

        if not code_verifier:

            return {
                "erro":
                "Code verifier não encontrado"
            }

        # troca code por access_token
        token_url = (
            "https://auth.deriv.com/oauth2/token"
        )

        payload = {
            "grant_type":
                "authorization_code",
            "code":
                code,
            "client_id":
                CLIENT_ID,
            "redirect_uri":
                REDIRECT_URI,
            "code_verifier":
                code_verifier
        }

        response = requests.post(
            token_url,
            data=payload
        )

        oauth_data = (
            response.json()
        )

        print(
            "OAUTH:",
            oauth_data
        )

        oauth_token = (
            oauth_data.get(
                "access_token"
            )
        )

        if not oauth_token:

            return oauth_data

        # salva sessão OAuth
        global deriv_oauth_token
        deriv_oauth_token = oauth_token

        return RedirectResponse(
            f"{FRONTEND_URL}/#/dashboard"
        )

    except Exception as e:

        print(str(e))

        return {
            "erro": str(e)
        }

# SALDO DERIV
@app.get("/balance")
def balance():

    try:

        global deriv_oauth_token

        if not deriv_oauth_token:

            return {
                "erro":
                "Usuário não autenticado"
            }

        ws = websocket.create_connection(
            f"wss://ws.derivws.com/websockets/v3?app_id={APP_ID}"
        )

        # authorize
        ws.send(
            json.dumps({
                "authorize":
                    deriv_oauth_token
            })
        )

        auth_response = (
            json.loads(
                ws.recv()
            )
        )

        print(
            "AUTH:",
            auth_response
        )

        if auth_response.get("error"):

            return auth_response

        # balance
        ws.send(
            json.dumps({
                "balance": 1
            })
        )

        balance_response = (
            json.loads(
                ws.recv()
            )
        )

        print(
            "BALANCE:",
            balance_response
        )

        return balance_response

    except Exception as e:

        print(str(e))

        return {
            "erro": str(e)
        }
