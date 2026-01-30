from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

print("=" * 60)
print("TESTING OPENAI API KEY")
print("=" * 60)
print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
print()

try:
    client = OpenAI(api_key=api_key)

    print("Sending test request to OpenAI...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, the API key is working!'"}
        ],
        temperature=0.2
    )

    result = response.choices[0].message.content
    print()
    print("SUCCESS! OpenAI API is working!")
    print()
    print("Response:", result)
    print()
    print("=" * 60)

except Exception as e:
    print()
    print("ERROR! OpenAI API key is not working")
    print()
    print("Error:", str(e))
    print()
    print("=" * 60)