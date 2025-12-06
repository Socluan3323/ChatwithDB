from typing import List,Dict
import os 

from config import FILE_PATH


 
def convert_string_to_list(one_line: str , seperate_by: str = None) ->List[str]: 
    """
    Chuyển dòng từ file text thành 1 list của string.
    Example:
    Input:
    one_line = 'FP001,Gao thom ST25,18000,120' , seperate_by = ','
    Output:
    ['FP001','Gao thom ST25','18000','120']

    
    """
    
    
    # clean_row = []
    # name = ""
    # for element in one_line:
    #     if element.isnumeric():
    #         clean_row.append(int(element))
    #     else:
    #         name = name + " "  + element
            
    # name = name.strip()
    # clean_row.insert(1, name)
    # return clean_row
    return [x.strip() for x in one_line.split(seperate_by)]

def convert_list_to_dict (rows: List[List[str]]) -> Dict[str,str]:
    """
    input
    ['FP001','Gao thom ST25','18000','120']
    output
    {
        'product_id': 'FP001'
        'name': 'Gao thom ST25'
        'price':'18000'
        'quantity': '120'
    }
    
    """
    try:
        if not len(rows) == 4:
            raise IndexError("Mảng phải đủ 4 phần tử")

        return {

            'product_id' : rows[0],
            'name': rows[1],
            'price': rows[2],
            'quantity': rows[3]

                }
    except Exception as e:
        print(e,rows)

if __name__ == '__main__':
    # convert_string_to_list(FILE_PATH)
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH,'r') as f :
            data_rows = f.readlines()
        one_row = data_rows[2]
        clean_data= []
        for idx, value in enumerate(data_rows):
            if value.strip() == '':
                continue
            clean_rows = convert_string_to_list(value,',')
            clean_data = convert_list_to_dict(clean_rows)
            print(clean_data)
        # print(one_row)
        # loop through each row and turn it into a list of string.  
    else: 
        print("file dont exist")