from groq import Groq

keys = {
    "Key 1 (new)": " ",
    "Key 2 (old)": " "
}

for name, key in keys.items():
    print(f"\nTesting {name}:")
    print(f"Key: {key[:20]}...{key[-10:]}")
    try:
        client = Groq(api_key=key)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Say hi"}],
            temperature=0.2
        )
        print(f"✅ SUCCESS! Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ FAILED! Error: {e}")