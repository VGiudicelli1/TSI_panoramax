
code_back = {
    "B14": "A00",
    "B1" : "A00",
}

def is_code_face(code):
    return code in code_back.keys()

def is_code_back(code):
    return code in code_back.values()

def get_code_back(code):
    return code_back[code]


if __name__ == "__main__":
    code = "B14"
    print(is_code_face(code), is_code_back(code))
