def preprocess(code):
    return code.replace("\n", " ") + " "

def get_word(code, index):
    code = code[index:]
    end = code.find(" ")
    return code[index:end]

def generate_tokens(code):
    tokens = [] # example token {"action":"define var", "value":["cheese", 1]}
    i = 0
    while i < len(code):
        word= get_word(code, i)
        # if word == "something":
            # do something with potentially next word

	# booleans
    if word in ('true','right','ok','yes'):
        tokens.append({"action":"boolean", "value":"true"})
        i += len(word)
    if word in ('wrong','no','lies','false'):
        tokens.append({"action":"boolean", "value":"false"})
        i += len(word)
	# functions


	# null
    if word in ("nothing", "nowhere", "nobody", "gone", "null"):
        tokens.append({"action":"nullType", "value":"null"}) 
        i += len(word)


    return tokens
