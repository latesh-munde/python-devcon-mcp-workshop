# server.py

import os
import time
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse, PlainTextResponse
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

APS_CLIENT_ID = os.getenv("APS_CLIENT_ID")
APS_CLIENT_SECRET = os.getenv("APS_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:3001/auth/callback"

if not APS_CLIENT_ID or not APS_CLIENT_SECRET:
    raise Exception("Missing APS_CLIENT_ID or APS_CLIENT_SECRET")

# -------------------------
# Globals (same as JS)
# -------------------------
cached_token = None
token_expires_at = 0
user_access_token = None

# -------------------------
# Token (2-legged OAuth)
# -------------------------
async def get_token():
    global cached_token, token_expires_at

    if cached_token and time.time() < token_expires_at - 60:
        return cached_token

    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://developer.api.autodesk.com/authentication/v2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": APS_CLIENT_ID,
                "client_secret": APS_CLIENT_SECRET,
                "scope": "data:read data:write bucket:read bucket:create",
            },
        )

        data = res.json()
        cached_token = data["access_token"]
        token_expires_at = time.time() + data["expires_in"]

        print("APS token refreshed")
        return cached_token


# -------------------------
# OSS Client (helper)
# -------------------------
async def get_headers():
    token = await get_token()
    return {"Authorization": f"Bearer {token}"}


# -------------------------
# MCP Server
# -------------------------
mcp = FastMCP("devcon-aps-server")


# -------------------------
# Tool 1: List Buckets
# -------------------------
@mcp.tool()
async def list_buckets(region: str):
    """Lists all OSS buckets"""

    headers = await get_headers()

    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://developer.api.autodesk.com/oss/v2/buckets",
            headers=headers,
            params={"region": region},
        )

        data = res.json()
        items = data.get("items", [])

        if not items:
            return "No buckets found. Create one first."

        lines = [
            f"{b['bucketKey']} ({b['policyKey']}, created: {b['createdDate']})"
            for b in items
        ]

        return "\n".join(lines)


# -------------------------
# Tool 2: Create Bucket
# -------------------------
@mcp.tool()
async def create_bucket(bucket_key: str, policy: str, region: str):
    """Creates a new OSS bucket"""

    headers = await get_headers()

    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"https://developer.api.autodesk.com/oss/v2/buckets",
                headers=headers,
                json={
                    "bucketKey": bucket_key,
                    "policyKey": policy,
                },
                params={"region": region},
            )

            return f"Bucket '{bucket_key}' created with policy '{policy}'"

        except Exception as e:
            return f"Error: {str(e)}"


# -------------------------
# Tool 3: Get User Info (3-legged OAuth)
# -------------------------
@mcp.tool()
async def get_user_info():
    """Returns Autodesk user profile"""

    global user_access_token

    if not user_access_token:
        return "Not authenticated. Open http://localhost:3001/auth/login"

    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.userprofile.autodesk.com/userinfo",
            headers={"Authorization": f"Bearer {user_access_token}"},
        )

        if res.status_code != 200:
            return f"Error: {res.status_code}"

        user = res.json()

        return f"Name: {user['name']}\nEmail: {user['email']}\nID: {user['sub']}"


# -------------------------
# FastAPI App (HTTP Layer)
# -------------------------
app = FastAPI()


# -------------------------
# Route 1: Login
# -------------------------
@app.get("/auth/login")
async def login():
    url = (
        "https://developer.api.autodesk.com/authentication/v2/authorize"
        f"?response_type=code"
        f"&client_id={APS_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=data:read"
    )

    return RedirectResponse(url)


# -------------------------
# Route 2: Callback
# -------------------------
@app.get("/auth/callback")
async def callback(request: Request):
    global user_access_token

    code = request.query_params.get("code")

    if not code:
        return PlainTextResponse("Missing code", status_code=400)

    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://developer.api.autodesk.com/authentication/v2/token",
            data={
                "grant_type": "authorization_code",
                "client_id": APS_CLIENT_ID,
                "client_secret": APS_CLIENT_SECRET,
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
        )

        data = res.json()
        user_access_token = data["access_token"]

    return HTMLResponse("<h1>Login successful. You can close this tab.</h1>")


# -------------------------
# Route 3: MCP Endpoint
# -------------------------
@app.post("/mcp")
async def mcp_handler(request: Request):
    return await mcp.handle(request)


# -------------------------
# Run Server
# -------------------------
if __name__ == "__main__":
    import uvicorn

    print("MCP Server: http://localhost:3001/mcp")
    print("Login at: http://localhost:3001/auth/login")

    uvicorn.run(app, host="0.0.0.0", port=3001)