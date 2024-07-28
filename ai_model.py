from openai import OpenAI

OPENAI_API_KEY = "sk-proj-mhHVqwhz49vadko1SClPT3BlbkFJR9klPbxKLXDgWfGPYZZl"
client = OpenAI(api_key=OPENAI_API_KEY)

def prepare_openai_messages(messages):
    openai_messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for message in reversed(messages):  # Reverse to go from oldest to newest
        role = "user" if message[2] == "user" else "assistant"
        openai_messages.append({"role": role, "content": message[3]})
    return openai_messages

def get_openai_response(messages):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response["choices"][0]["message"]["content"]
