from groq import Groq
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)
def get_llm_response(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        raise