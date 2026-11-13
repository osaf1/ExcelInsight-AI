
import json
from ollama import chat

from analysis import (
    get_data_summary,
    calculate_column,
    group_column
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_data_summary",
            "description": "Toon kolommen, voorbeelddata en statistieken van het Excel-bestand.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_column",
            "description": "Bereken som, gemiddelde, minimum, maximum of aantal van een numerieke kolom.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {"type": "string"},
                    "operation": {
                        "type": "string",
                        "enum": ["sum", "mean", "min", "max", "count"]
                    }
                },
                "required": ["column", "operation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "group_column",
            "description": "Bereken waarden per groep, bijvoorbeeld omzet per stad of gemiddelde cijfers per klas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "group_by": {"type": "string"},
                    "value_column": {"type": "string"},
                    "operation": {
                        "type": "string",
                        "enum": ["sum", "mean", "count", "min", "max"]
                    }
                },
                "required": ["group_by", "value_column", "operation"]
            }
        }
    }
]


available_functions = {
    "get_data_summary": get_data_summary,
    "calculate_column": calculate_column,
    "group_column": group_column
}


def ask_ai(question, df):

    if df.empty:
        return "Het Excel-bestand bevat geen gegevens."

    columns = list(df.columns)

    messages = [
        {
            "role": "system",
            "content": (
                "Je bent ExcelInsight AI. "
                "Je analyseert verschillende Excel-bestanden. "
                f"Beschikbare kolommen: {json.dumps(columns, ensure_ascii=False)}. "
                "Gebruik exact deze kolomnamen. "
                "Gebruik de tools voor berekeningen. "
                "Verzin nooit gegevens of cijfers. "
                "Als gegevens ontbreken, zeg dat duidelijk. "
                "Antwoord in eenvoudig Nederlands."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    response = chat(
        model="llama3.2:3b",
        messages=messages,
        tools=tools
    )

    messages.append(response.message)

    if not response.message.tool_calls:
        return (
            "Ik kan deze vraag niet betrouwbaar berekenen. "
            "Probeer je vraag specifieker te stellen."
        )

    for tool_call in response.message.tool_calls:
        name = tool_call.function.name
        arguments = tool_call.function.arguments or {}

        function = available_functions.get(name)

        if function is None:
            result = {"error": "Onbekende functie."}
        else:
            try:
                result = function(df, **arguments)
            except (TypeError, ValueError, KeyError) as error:
                result = {"error": str(error)}

        messages.append({
            "role": "tool",
            "tool_name": name,
            "content": json.dumps(
                result, ensure_ascii=False, default=str
            )
        })

    final_response = chat(
        model="llama3.2:3b",
        messages=messages
    )

    return final_response.message.content
