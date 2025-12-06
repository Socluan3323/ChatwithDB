from google import genai
from dotenv import load_dotenv
import os
load_dotenv


client = genai.Client(api_key=os.getenv("key"))


def call_llm(prompt):

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    return response.text


def build_prompt(text):
    return f"""
    
    phân loại các sản phẩm trong List sau: 
    {text}
    này thành một danh sách tương ứng , thuộc type_id như sau:
    - 1.VEGETABLES
    - 2.FRUITS
    - 3.GRAINS_LEGUMES
    - 4.DAIRY_EGGS
    - 5.MEAT_SEAFOOD
    format:
    ```yaml
    prouduct_id: type_id
    ```
    example :
    ```yaml
    1:2
    2:1
    3:5
    4:5
    5:5
    6:2
    7:1
    ```
    
    trả về chinh xac câu trúc YML như trên:
    """
