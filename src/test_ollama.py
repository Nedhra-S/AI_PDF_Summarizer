import ollama

response = ollama.chat(
    model="qwen2.5:3b",
    messages=[
        {
            "role": "user",
            "content": "Give me 3 short points about lecture notes."
        }
    ]
)

print(response["message"]["content"])