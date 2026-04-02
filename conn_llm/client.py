import os
import json
from dotenv import load_dotenv
import litellm

from conn_llm.system_prompt import SYSTEM_PROMPT
from conn_llm.mcp_config import TOOLS
from ragy_extractor.client import list_collections, extract_relevant_days
from conn_tavily.client import client as tavily_client

load_dotenv()

MODEL = os.getenv("LLM_MODEL", "gemini/gemini-2.5-flash-lite")


def execute_list_collections() -> str:
    collections = list_collections()
    return json.dumps({"collections": collections})


def execute_ragy_extractor(query: str, collection_name: str, top_k: int = 10) -> str:
    results = extract_relevant_days(query, collection_name, top_k)
    return json.dumps({"results": results})


def execute_tavily_search(query: str) -> str:
    response = tavily_client.search(query)
    results = response.get('results', [])
    formatted = [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", "")
        }
        for r in results[:5]
    ]
    return json.dumps({"results": formatted})


def generate_response(prompt: str, messages: list[dict] | None = None) -> tuple[str, list[dict]]:
    if messages is None:
        print("[DEBUG] Starting new conversation")
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    else:
        print(f"[DEBUG] Continuing conversation (history: {len(messages)} messages)")

    messages.append({"role": "user", "content": prompt})
    print(f"[DEBUG] User: {prompt}")

    max_iterations = 20
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n[DEBUG] --- Iteration {iteration} ---")
        print(f"[DEBUG] Messages count: {len(messages)}")

        response = litellm.completion(
            model=MODEL,
            messages=messages,
            tools=TOOLS
        )

        assistant_message = response.choices[0].message
        print(f"[DEBUG] Response - has_content: {bool(assistant_message.content)}, has_tools: {bool(assistant_message.tool_calls)}")

        if bool(assistant_message.content) and not bool(assistant_message.tool_calls):
            final_response = assistant_message.content or "No response generated"
            print(f"[DEBUG] Final response: {final_response[:100]}...")
            return (final_response, messages)
        
        if not bool(assistant_message.content) and not bool(assistant_message.tool_calls):
            print("[DEBUG] No content and no tool calls detected, ending conversation.")
            messages.append({"role": "user", "content": 'try again to respond...'})
            continue


        print(f"[DEBUG] Tool calls detected: {len(assistant_message.tool_calls)}")

        tool_calls_dict = [
            {
                "id": tc.id,
                "type": tc.type,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            }
            for tc in assistant_message.tool_calls
        ]

        messages.append({
            "role": "assistant",
            "content": assistant_message.content or "",
            "tool_calls": tool_calls_dict
        })

        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"[DEBUG] Executing tool: {function_name}({arguments})")

            if function_name == "list_collections":
                result = execute_list_collections()
            elif function_name == "ragy_extractor":
                result = execute_ragy_extractor(**arguments)
            elif function_name == "tavily_search":
                result = execute_tavily_search(**arguments)
            else:
                result = json.dumps({"error": f"Unknown tool: {function_name}"})

            print(f"[DEBUG] Tool result: {result[:150]}...")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

    print("[DEBUG] Max iterations reached!")
    return ("Max iterations reached", messages)
