# agent.py

import os
import asyncio
import httpx
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# -------------------------
# MCP Client (same as before)
# -------------------------
class MCPClient:
    def __init__(self, url):
        self.url = url
        self.client = httpx.AsyncClient()

    async def list_tools(self):
        res = await self.client.post(self.url, json={"type": "list_tools"})
        return res.json()

    async def call_tool(self, name, arguments):
        res = await self.client.post(
            self.url,
            json={
                "type": "call_tool",
                "name": name,
                "arguments": arguments,
            },
        )
        return res.json()

    async def close(self):
        await self.client.aclose()


# -------------------------
# Connect to MCP Servers
# -------------------------
async def setup_clients():
    workshop = MCPClient("http://localhost:3000/mcp")
    aps = MCPClient("http://localhost:3001/mcp")

    workshop_tools = await workshop.list_tools()
    aps_tools = await aps.list_tools()

    workshop_tools = workshop_tools.get("tools", [])
    aps_tools = aps_tools.get("tools", [])

    all_tools = workshop_tools + aps_tools

    # tool → client mapping
    tool_client_map = {}
    for t in workshop_tools:
        tool_client_map[t["name"]] = workshop

    for t in aps_tools:
        tool_client_map[t["name"]] = aps

    print(f"Connected. {len(all_tools)} tools available:")
    for t in all_tools:
        print(f"  - {t['name']}: {t.get('description')}")

    return workshop, aps, all_tools, tool_client_map


# -------------------------
# Convert MCP tools → Gemini format
# -------------------------
def build_gemini_tools(all_tools):
    return [{
        "function_declarations": [
            {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get("inputSchema", {}),
            }
            for t in all_tools
        ]
    }]


# -------------------------
# Agent Loop
# -------------------------
async def ask(prompt, model, tools, tool_map):
    print("\n" + "=" * 60)
    print(f"User: {prompt}\n")

    messages = [{"role": "user", "parts": [{"text": prompt}]}]

    while True:
        response = model.generate_content(
            contents=messages,
            tools=tools,
            generation_config={"temperature": 0},
        )

        candidate = response.candidates[0].content

        # extract tool calls
        tool_calls = [
            p.function_call for p in candidate.parts if hasattr(p, "function_call")
        ]

        # FINAL ANSWER
        if not tool_calls:
            final_text = "".join([p.text or "" for p in candidate.parts])
            print(f"Agent: {final_text}")
            return final_text

        tool_results = []

        # EXECUTE TOOLS
        for call in tool_calls:
            name = call.name
            args = dict(call.args)

            print(f"  → Calling tool: {name}({args})")

            result = await tool_map[name].call_tool(name, args)

            result_text = "\n".join(
                [c.get("text", "") for c in result.get("content", [])]
            )

            print(f"  ← Result: {result_text[:120]}...")

            tool_results.append({
                "function_response": {
                    "name": name,
                    "response": {"output": result_text},
                }
            })

        # Append conversation
        messages.append({"role": "model", "parts": candidate.parts})
        messages.append({"role": "user", "parts": tool_results})


# -------------------------
# MAIN
# -------------------------
async def main():
    workshop, aps, all_tools, tool_map = await setup_clients()

    gemini_tools = build_gemini_tools(all_tools)

    model = genai.GenerativeModel("gemini-2.5-flash")

    await ask(
        "Create a new OSS bucket called 'latesh-devcon-test2' with a persistent policy in the US region, then list my US buckets to confirm it was created.",
        model,
        gemini_tools,
        tool_map
    )

    await workshop.close()
    await aps.close()


if __name__ == "__main__":
    asyncio.run(main())