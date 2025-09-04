# Cyclos exposes OIDC discovery and these endpoints:
# Well-known: https://your-cyclos.example/.well-known/openid-configuration
# Authorize: …/api/oidc/authorize
# Token: …/api/oidc/token
# UserInfo: …/api/oidc/userinfo
#
#
#
#
#
#
#
import os
from urllib.parse import urljoin

from flask import Flask, redirect, url_for, session, jsonify, request
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import requests

load_dotenv()

CYCLOS_BASE = os.environ["CYCLOS_BASE_URL"].rstrip("/")
CLIENT_ID = os.environ["OIDC_CLIENT_ID"]
CLIENT_SECRET = os.environ["OIDC_CLIENT_SECRET"]
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "change-me")
REDIRECT_PATH = os.environ.get("REDIRECT_PATH", "/auth/callback")

app = Flask(__name__)
app.secret_key = SECRET_KEY

oauth = OAuth(app)

# Register Cyclos as an OIDC provider using discovery
oauth.register(
    name="cyclos",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url=f"{CYCLOS_BASE}/.well-known/openid-configuration",
    client_kwargs={
        # Request OIDC + Cyclos API scopes; include offline_access for refresh tokens if allowed
        "scope": "openid profile email account_status account_history offline_access"
    }
)

@app.route("/")
def home():
    token = session.get("token")
    user = session.get("user")
    return jsonify({
        "logged_in": bool(token),
        "user": user,
        "endpoints": {
            "login": url_for("login", _external=True),
            "logout": url_for("logout", _external=True),
            "userinfo": url_for("me", _external=True),
            "accounts": url_for("accounts", _external=True),
        }
    })

@app.route("/login")
def login():
    redirect_uri = url_for("auth_callback", _external=True)
    return oauth.cyclos.authorize_redirect(redirect_uri)

@app.route(REDIRECT_PATH, methods=["GET"])
def auth_callback():
    # Exchanges the authorization code for tokens (handles PKCE automatically)
    token = oauth.cyclos.authorize_access_token()
    session["token"] = token
    #
    token = oauth.cyclos.authorize_access_token()
    print("granted scopes:", token.get("scope"))  # e.g., "openid profile email account_status"
    session["token"] = token

    # sanity: call userinfo to be sure the token works at all
    userinfo = oauth.cyclos.userinfo(token=token)
    print("userinfo ok:", userinfo.get("sub"))
    session["user"] = userinfo
    
    # Fetch OIDC userinfo
    userinfo = oauth.cyclos.userinfo(token=token)
    session["user"] = userinfo
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/me")
def me():
    if "token" not in session:
        return redirect(url_for("login"))
    # Return cached userinfo (you can also call UserInfo again)
    return jsonify(session.get("user"))

@app.route("/accounts")
def accounts():
    """
    Example REST call using the access token.
    Cyclos docs: include 'Authorization: Bearer <ACCESS_TOKEN>' and request
    account scopes in consent (account_status/account_history). 
    """
    if "token" not in session:
        return redirect(url_for("login"))
    access_token = session["token"]["access_token"]
    
    

    # Depending on your setup, the accounts endpoint may be /api/self/accounts
    # (owner=self). Adjust to your instance paths / version as needed.
    url = f"{CYCLOS_BASE}/api/self/accounts"
    resp = requests.get(url, headers={"Authorization": f"Bearer {access_token}"}, timeout=20)
    return jsonify({
        "status_code": resp.status_code,
        "data": resp.json() if resp.headers.get("content-type","").startswith("application/json") else resp.text
    })

if __name__ == "__main__":
    # e.g., flask run --port 5000
    app.run(debug=True, port=5000)
