from fastmcp import FastMCP
from typing import Literal
import httpx
from fastapi import FastAPI, Request
import uvicorn

mcp = FastMCP("devcon-workshop-server")


# -------------------------
# Tool 1: Add Numbers
# -------------------------
@mcp.tool()
async def add(a: float, b: float):
    """Adds two numbers together"""
    return f"Result: {a + b}"


# -------------------------
# Tool 2: Greet
# -------------------------
@mcp.tool()
async def greet(name: str, language: Literal["english", "french", "spanish"]):
    """Returns a greeting in the chosen language"""

    greetings = {
        "english": f"Hello, {name}! Welcome to the DevCon MCP Workshop.",
        "french": f"Bonjour, {name}! Bienvenue au Workshop MCP DevCon.",
        "spanish": f"¡Hola, {name}! Bienvenido al Workshop MCP de DevCon.",
    }

    return greetings[language]


# -------------------------
# Tool 3: Estimate Cost
# -------------------------
@mcp.tool()
async def estimate_cost(
    VConcrete: float,
    VSteel: float,
    VTimber: float,
    VGlass: float
):
    """Returns estimate cost of given materials"""

    cost = (
        VConcrete * 150
        + VSteel * 950
        + VTimber * 400
        + VGlass * 1200
    )

    return f"Result: {cost}"


# -------------------------
# Tool 4: Weather API
# -------------------------
@mcp.tool()
async def get_weather(city: str):
    """Returns current weather for a city"""

    async with httpx.AsyncClient() as client:

        # Step 1: Geocoding
        geo_res = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
        )
        geo_data = geo_res.json()

        if not geo_data.get("results"):
            return f"City not found: {city}"

        loc = geo_data["results"][0]
        latitude = loc["latitude"]
        longitude = loc["longitude"]

        # Step 2: Weather
        weather_res = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": True,
            },
        )

        data = weather_res.json()["current_weather"]

        return f"Weather in {city}: {data['temperature']}°C, wind {data['windspeed']} km/h"


# -------------------------
# Run Server (HTTP mode)
# -------------------------


app = FastAPI()

@app.post("/mcp")
async def handle_mcp(request: Request):
    return await mcp.handle(request)

if __name__ == "__main__":
    print("Workshop MCP running at http://localhost:3000/mcp")
    uvicorn.run(app, host="0.0.0.0", port=3000)