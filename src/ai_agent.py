import pandas as pd
from ollama import chat

from analysis import (
    get_financial_analysis,
    get_best_product,
    get_best_city,
    get_worst_product,
    get_profit_per_product,
    get_data_summary
)


# Beschikbare AI-tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_financial_analysis",
            "description": "Geeft totale omzet, kosten en winst uit de Excel-data.",
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
            "name": "get_best_product",
            "description": "Geeft het product met de hoogste omzet.",
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
            "name": "get_best_city",
            "description": "Geeft de stad met de hoogste omzet.",
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
            "name": "get_worst_product",
            "description": "Geeft het product met de laagste omzet.",
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
            "name": "get_profit_per_product",
            "description": "Geeft de totale winst per product.",
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
            "name": "get_data_summary",
            "description": "Geeft een algemeen overzicht van de Excel-data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


available_functions = {
    "get_financial_analysis": get_financial_analysis,
    "get_best_product": get_best_product,
    "get_best_city": get_best_city,
    "get_worst_product": get_worst_product,
    "get_profit_per_product": get_profit_per_product,
    "get_data_summary": get_data_summary
}


def ask_ai(question, df):

    messages = [
        {
            "role": "system",
            "content": (
                "Je bent ExcelInsight AI, een data-analyseassistent. "
                "Beantwoord vragen uitsluitend op basis van de meegegeven Excel-data. "
                "Gebruik altijd een beschikbare tool wanneer exacte cijfers nodig zijn. "
                "Verzin nooit cijfers. "
                "Als de vraag niet uit de data kan worden beantwoord, zeg dat duidelijk. "
                "Geef korte, duidelijke antwoorden in het Nederlands."
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

    if response.message.tool_calls:

        for tool_call in response.message.tool_calls:

            function_name = tool_call.function.name
            function_to_call = available_functions.get(function_name)

            if function_to_call:
                result = function_to_call(df)

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": function_name,
                        "content": str(result)
                    }
                )

        final_response = chat(
            model="llama3.2:3b",
            messages=messages,
            tools=tools
        )

        return final_response.message.content

    return response.message.content