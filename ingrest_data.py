from typing import Dict, List

from crud import *
from clean_data import convert_list_to_dict,convert_string_to_dict,convert_string_to_list
from call_llm import call_llm
from yaml import safe_load


init_schema()

productype_id_to_name = {
    "FP" : "thuc pham",
    "DR" : "do uong",
    "HG" : "do gia dung",
    "EL" : "thiet bi dien tu",
    "CS" : "my pham"
}
productype_name_to_id = {
    "thuc pham" : "FP",
    "do uong" : "DR",
    "do gia dung" : "HG",
    "thiet bi dien tu" : "EL",
    "my pham" : "CS"
}

prompt_classify = """ 

Bạn là trợ lý hỗ trợ phân loại cặp product_id: product_name thành các cặp:
- product_type_id: product_type_name
{list_product_type_name}

Example:
input:
- hk: banh mi
- gh: iphone

output với format sau:

'''yaml
hk: FP
gh: EL
''' 
hiện tại input là :
{list_pair_product_id_name}

hãy trả về output như ví dụ trên.



"""


def format_dictionary_to_string(dictionary: Dict[str,str]) -> str:
    product_id = dictionary.get("product_id",None)
    name = dictionary.get("name", None)
    return f"{product_id}: {name}"
    """
    {'product_id': 'EL035',
  'name': 'Day HDMI 3m',
  'price': '120000',
  'quantity': '110'}
  
    output :
    
      "-EL035: Day HDMI 3m"
    """
    
    
def create_format_list_product_id_name(t: List[Dict[str,str]])->str:
    return "\n".join(format_dictionary_to_string(item) for item in t)
      
    """
    INPUT:
    [{'product_id': 'FP001',
  'name': 'Gao thom ST25',
  'price': '18000',
  'quantity': '120'},
  ...
  ]
    
    
    
    output:
    "-FP001: Gao thom ST25
    - ...
    - ... 
    - ..."

    
    """
    

for type_id,type_name in productype_id_to_name.items():
    a = ProductType(id= type_id,name= type_name)
    insert_one_productType(a)
    
    
with open("newdata.txt","r") as f:
    data_rows = f.readlines()
    
    
clean_data = [convert_list_to_dict(x) for x in data_rows if convert_list_to_dict(x)]

list_product_type_name = "\n".join(f"-{a[0]}: {a[1]}" for a in productype_id_to_name.items())
complete_prompt = prompt_classify.format(list_pair_product_id_name = create_format_list_product_id_name(clean_data), list_product_type_name = list_product_type_name)


result = call_llm(complete_prompt)
product_id_to_type_id = safe_load(result.split("```yaml")[1].split("```")[0])

lists_product = []
for item in clean_data:
    lists_product.append(Product(id = item.get("product_id"), 
        name = item.get("name"),
        price = item.get("price"),
        quantity = item.get("quantity"),
        type_id = product_id_to_type_id.get(item.get("product_id"))))
    
insert_list_products(lists_product)