import openai
import os
from dotenv import load_dotenv
import signal


load_dotenv()
token = os.getenv("GITHUB_TOKEN")
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"
client = openai.OpenAI(
    base_url=endpoint,
    api_key=token,
)
messages = []
with open("context.txt", "r+") as file:
    for line in file:
        if line != "":
            role = line.split(":")[0]
            content = line.split(":")[1][:-1]
            messages += [{"role": role, "content": content}]
if messages == []:
    messages += [{"role": "system", "content": "You are a helpful assistant."}]


def signal_handler(messages):
    print("Okay see ya!")
    context = ""
    for message in messages:
        context += f"{message[role]}:{message[content]}\n"
    file.write(context)
    file.close()
    exit(0)


signal.signal(signal.SIGINT, signal_handler)

print("Assistant: Hello! What's on your mind?")
while True:
    user_message = input("User: ")
    messages += [{"role": "user", "content": user_message}]
    response = client.chat.completions.create(
        messages=messages,
        temperature=1.0,
        top_p=1.0,
        max_tokens=1000,
        model=model_name,
    )
    print(f"Assistant: {response.choices[0].message.content}")
    messages += [response.choices[0].message]
