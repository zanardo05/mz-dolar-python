from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

import secrets
import hashlib
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLIENT_ID = "33i32GbNdYrf99M2AM24V"

FRONTEND_URL = (
    "https://mz-dolar.vercel.app"
)

REDIRECT_URI = (
    "https://mz-dolar-python.onrender.com/auth/callback"
)

# PKCE
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
        "status": "online"
    }

# LOGIN
@app.get("/auth/login")
def login():

    state = secrets.token_urlsafe(16)

    code_verifier, code_challenge = generate_pkce()

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

# CALLBACK
@app.get("/auth/callback")
def callback(
    code: str = None,
    state: str = None
):

    print("CODE:", code)

    if not code:

        return {
            "erro": "OAuth code não encontrado"
        }

    redirect = (
        f"{FRONTEND_URL}/#/dashboard?code={code}"
    )

    return RedirectResponse(
        redirect
    )
