
from groq import Groq
import os

# client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
client = Groq(api_key="<your_api_key>")

class LLMInterface:
    def __init__(self):
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"
        self.last_guest_word_total = 0

    def generate_followups(self, context, buffer):
        print("\n🧠 [TRANSCRIPT BUFFER]")
        for entry in buffer:
            print(f"- {entry['speaker'].upper()}: {entry['text']}")

        guest_texts = [entry["text"] for entry in buffer if entry["speaker"].lower() == "guest"]
        all_guest_words = sum(len(text.split()) for text in guest_texts)
        new_words = all_guest_words - self.last_guest_word_total

        print(f"\n🧮 Guest word stats: Total={all_guest_words}, Last={self.last_guest_word_total}, New={new_words}")

        if new_words < 50:
            print(f"[⏳] Guest has spoken only {new_words} new words since last generation. Waiting for 50+.")
            return []

        self.last_guest_word_total = all_guest_words

        last_units = buffer[-3:]
        quotes = "\n".join([f"{entry['speaker']}: {entry['text']}" for entry in last_units])

        print("\n📋 [Last 3 Conversation Entries Passed to LLM]")
        print(quotes)

        system_prompt = """
You are an AI assistant for a podcast host. Your job is to help the host keep the conversation flowing by generating short, punchy follow-up questions in real-time.

Instructions:
- Focus ONLY on the latest guest reply, with awareness of the previous 2 turns.
- Follow-up questions should be:
    - Short (2–5 words max)
    - Specific to the latest guest response
    - No full sentences or vague generics
    - No repetitive or filler questions
- Return at most 3 questions formatted as:

Follow-Up Questions for Unit [X]:
1. <question>
2. <question>
3. <question>
"""

        user_prompt = f"""
Podcast Metadata:
- Topic: {context.get('podcast_topic', '')}
- Guest Bio: {context.get('guest_bio', '')}
- Goal: {context.get('podcast_goal', '')}

Conversation:
{quotes}

Generate up to 3 short follow-up questions based on the guest’s last reply only.
"""

        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=300,
            top_p=1.0,
            stream=False,
        )

        full_response = completion.choices[0].message.content.strip()
        print("\n[📤] Raw LLM Output:", repr(full_response))

        followups = []
        for line in full_response.splitlines():
            if '?' in line:
                cleaned = line.strip("1234567890.- ").strip()
                if cleaned:
                    followups.append(cleaned)

        return followups[:3]
