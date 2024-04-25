import re

def get_location_id(input:str)->str:
    pattern = r'(\d{9})'
    matches = re.findall(pattern, input)
    for match in matches:
        return match
    return "101010100"