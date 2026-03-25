"""LLM-powered intent router with tool calling."""

import json
import sys
from openai import OpenAI
from config import Config
from services.lms_api import LmsApiClient


SYSTEM_PROMPT = """\
You are a helpful university lab assistant bot. You help students and instructors \
get information about labs, scores, students, and course analytics.

When the user asks a question, use the available tools to fetch data from the backend. \
Always use tools when the question is about labs, scores, students, groups, or course data. \
After receiving tool results, summarize the data clearly and concisely for the user.

If the user's message is a greeting, respond friendly and mention what you can help with. \
If the message is unclear or gibberish, respond helpfully and list what you can do. \
If the message is ambiguous (like just "lab 4"), ask what they'd like to know about it.

Available data: labs list, per-task pass rates, score distributions, timelines, \
group performance, top learners, completion rates, and student enrollment info.\
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get the list of all labs and tasks in the course",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get all enrolled students and their groups",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submission timeline (submissions per day) for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group performance scores and student counts for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return, default 5"},
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL data sync to refresh data from the autochecker",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

# Map tool names to API client methods
TOOL_DISPATCH = {
    "get_items": lambda args: LmsApiClient.get_items(),
    "get_learners": lambda args: LmsApiClient.get_learners(),
    "get_scores": lambda args: LmsApiClient.get_scores(args["lab"]),
    "get_pass_rates": lambda args: LmsApiClient.get_pass_rates(args["lab"]),
    "get_timeline": lambda args: LmsApiClient.get_timeline(args["lab"]),
    "get_groups": lambda args: LmsApiClient.get_groups(args["lab"]),
    "get_top_learners": lambda args: LmsApiClient.get_top_learners(args["lab"], args.get("limit", 5)),
    "get_completion_rate": lambda args: LmsApiClient.get_completion_rate(args["lab"]),
    "trigger_sync": lambda args: LmsApiClient.trigger_sync(),
}


def _execute_tool(name: str, arguments: dict) -> str:
    """Execute a tool call and return the result as a JSON string."""
    try:
        fn = TOOL_DISPATCH.get(name)
        if not fn:
            return json.dumps({"error": f"Unknown tool: {name}"})
        result = fn(arguments)
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


def _get_client() -> OpenAI:
    return OpenAI(
        api_key=Config.LLM_API_KEY or "dummy",
        base_url=Config.LLM_API_BASE_URL,
    )


def route(user_message: str) -> str:
    """Route a natural language message through the LLM with tool calling."""
    client = _get_client()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    max_iterations = 10
    for _ in range(max_iterations):
        try:
            response = client.chat.completions.create(
                model=Config.LLM_API_MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
        except Exception as e:
            return f"LLM error: {e}"

        choice = response.choices[0]

        # If the LLM returned a text response (no tool calls), we're done
        if choice.finish_reason != "tool_calls" and not choice.message.tool_calls:
            return choice.message.content or "I couldn't generate a response."

        # Process tool calls
        messages.append(choice.message)

        tool_calls = choice.message.tool_calls or []
        print(f"[summary] Processing {len(tool_calls)} tool call(s)", file=sys.stderr)

        for tc in tool_calls:
            fn_name = tc.function.name
            try:
                fn_args = json.loads(tc.function.arguments) if tc.function.arguments else {}
            except json.JSONDecodeError:
                fn_args = {}

            print(f"[tool] LLM called: {fn_name}({json.dumps(fn_args)})", file=sys.stderr)
            result = _execute_tool(fn_name, fn_args)
            print(f"[tool] Result: {result[:100]}{'...' if len(result) > 100 else ''}", file=sys.stderr)

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

        print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)

    return "I ran out of steps trying to answer your question. Please try a simpler query."
