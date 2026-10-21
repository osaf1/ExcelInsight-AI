from ollama import chat


response = chat(
    model="llama3.2:3b",
    messages=[
        {
            "role": "user",
            "content": "Leg in één zin uit wat Pandas in Python is."
        }
    ]
)

print(response.message.content)