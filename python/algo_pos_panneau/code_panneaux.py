
code_back = {
    "B14": "A00",
    "B1" : "A00",     # à metttre à jour quand la classification contiendra ces informations (lire le csv panodico.csv)
}

def is_code_face(code):
    #return code in code_back.keys()
    return code != "A00"

def is_code_back(code):
    #return code in code_back.values()
    return code == "A00"

def get_code_back(code):
    #return code_back[code]
    return "A00"


if __name__ == "__main__":
    code = "B14"
    print(is_code_face(code), is_code_back(code))
