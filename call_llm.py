from google import genai
from dotenv import load_dotenv
import os
load_dotenv()


client = genai.Client(api_key=os.getenv("key"))


def call_llm(prompt):

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    return response.text


