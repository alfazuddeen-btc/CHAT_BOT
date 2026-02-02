from groq import Groq

keys = {
    "Key 1 (new)": "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",
    "Key 2 (old)": "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"
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