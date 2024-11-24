from mistralai import Mistral
from dotenv import load_dotenv
import os


load_dotenv()

async def generate(content):
    s = Mistral(
        api_key=os.getenv('AI_TOKEN'),
    )
    res = await s.chat.complete_async(model="mistral-small-latest", messages=[
        {
            "content": content,
            "role": "user",
        },
    ])
    return res

