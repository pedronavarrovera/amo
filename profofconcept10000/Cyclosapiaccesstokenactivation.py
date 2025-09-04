# Cyclos Access Clients
# An admin enables Access clients for your users and you (or the user) create an access client in Cyclos, which gives a 4-digit activation code.
# Your backend activates it once via: POST /api/clients/activate?code=XXXX using HTTP Basic (the user’s username+password)
# The response returns an access client token. Store it securely
# Use that token on every API call via header Access-Client-Token: <token> (optionally also the Channel header)
# Token stays valid until the access client is blocked/disabled
# One-time activation script (run once to mint the token)
# Endpoint, Basic auth, and return value (the token) are exactly per the docs. 
# You’ll pass this token in the Access-Client-Token header later. 
# Tokens remain valid until revoked. You can also add a prefix query param (e.g., a device ID) to bind the token to a known identifier.
# Use the token to call the REST API (balance + transactions)

import os
import requests
from getpass import getpass

BASE = "https://communities.cyclos.org"           # no trailing /api
NETWORK_PATH = "/amo"                                   # e.g. "/your-network" or "" if default
CODE = input("Enter the 4-digit access client activation code: ").strip()
myusername = os.environ["CYCLOS_ACCESS_USERNAME"]
mypassword = os.environ["CYCLOS_ACCESS_PASSWORD"]
USERNAME = input(myusername).strip()
PASSWORD = getpass(mypassword)

# POST /api/clients/activate?code=XXXX (optionally &prefix=DEVICEID)
url = f"{BASE}{NETWORK_PATH}/api/clients/activate"
resp = requests.post(url, params={"code": CODE}, auth=(USERNAME, PASSWORD), timeout=20)
resp.raise_for_status()

token = resp.text.strip()  # server returns the token as text
print("✅ Access client token (store securely!):", token)
# Save to env / secrets manager; do NOT hardcode in source.

