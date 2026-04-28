# client.py

import asyncio
import httpx


# -------------------------
# MCP Client (Generic)
# -------------------------
class MCPClient:
    def __init__(self, url: str, name: str):
        self.url = url
        self.name = name
        self.client = httpx.AsyncClient()

    async def list_tools(self):
        payload = {
            "type": "list_tools"
        }
        res = await self.client.post(self.url, json=payload)
        return res.json()

    async def call_tool(self, name: str, arguments: dict):
        payload = {
            "type": "call_tool",
            "name": name,
            "arguments": arguments,
        }
        res = await self.client.post(self.url, json=payload)
        return res.json()

    async def close(self):
        await self.client.aclose()


# -------------------------
# Main Flow
# -------------------------
async def main():

    # Connect to server
    workshop = MCPClient("http://localhost:3000/mcp", "workshop-client")
    print("Connected to workshop MCP server.")

    # Connect to APS server
    aps = MCPClient("http://localhost:3001/mcp", "aps-client")
    print("Connected to APS MCP server.")

    # -------------------------
    # List Tools
    # -------------------------
    workshop_tools = await workshop.list_tools()
    aps_tools = await aps.list_tools()

    all_tools = workshop_tools.get("tools", []) + aps_tools.get("tools", [])

    print("\nAvailable tools:")
    for tool in all_tools:
        print(f"  - {tool['name']}: {tool.get('description')}")

    # -------------------------
    # Tool Calls
    # -------------------------

    # add
    add_result = await workshop.call_tool(
        "add", {"a": 12, "b": 30}
    )
    print("\nadd(12, 30):", add_result["content"][0]["text"])

    # greet
    greet_result = await workshop.call_tool(
        "greet", {"name": "Nabil", "language": "spanish"}
    )
    print("greet():", greet_result["content"][0]["text"])

    # weather
    weather_result = await workshop.call_tool(
        "get_weather", {"city": "Amsterdam"}
    )
    print("get_weather():", weather_result["content"][0]["text"])

    # -------------------------
    # APS Tools
    # -------------------------

    # list buckets US
    buckets_us = await aps.call_tool(
        "list_buckets", {"region": "US"}
    )
    print("\nlist_buckets (US):\n", buckets_us["content"][0]["text"])

    # list buckets EMEA
    buckets_emea = await aps.call_tool(
        "list_buckets", {"region": "EMEA"}
    )
    print("\nlist_buckets (EMEA):\n", buckets_emea["content"][0]["text"])

    # -------------------------
    # Close
    # -------------------------
    await workshop.close()
    await aps.close()


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    asyncio.run(main())