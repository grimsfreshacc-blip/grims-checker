from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Load environment variables
EPIC_CLIENT_ID = os.environ.get("EPIC_CLIENT_ID")
EPIC_SECRET = os.environ.get("EPIC_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")

if not EPIC_CLIENT_ID or not REDIRECT_URI:
    raise ValueError("ERROR: EPIC_CLIENT_ID and REDIRECT_URI must be set in environment variables.")

# ------------------------------
# Fortnite OAuth Redirect URL
# ------------------------------
@app.route("/")
def home():
    return {
        "status": "online",
        "oauth_url": f"https://www.epicgames.com/id/authorize?"
                     f"client_id={EPIC_CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"
    }

# ------------------------------
# OAuth Callback
# ------------------------------
@app.route("/callback")
def callback():
    code = request.args.get("code")

    if not code:
        return {"error": "Missing ?code="}, 400

    token_url = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": EPIC_CLIENT_ID,
        "client_secret": EPIC_SECRET
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    token_res = requests.post(token_url, data=data, headers=headers)

    if token_res.status_code != 200:
        return {"error": "Failed to fetch token", "details": token_res.text}, 400

    token_json = token_res.json()

    access_token = token_json["access_token"]
    account_id = token_json["account_id"]

    # Fetch owned skins
    cosmetics_url = f"https://fortnite-api.com/v2/cosmetics/br"
    owned_url = f"https://fortnite-api.com/v2/stats/br/v2/{account_id}"

    skins = requests.get(owned_url).json()

    return {
        "account_id": account_id,
        "skins": skins
    }

# ------------------------------
# Start Server
# ------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
