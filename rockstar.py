import re

def process_program(program):
    trees = []
    program = re.sub(r"(?![A-Z]\.)(([a-zA-Z\.]{1,})(\.|\?|\!|\;|\n))",r"\2\n", program)
    for i in program.split("\n"):
        if i == "":
            continue
        i = i.strip()
        trees.append(generate_trees(i))
    return trees

def check_for_ops_in_expression(expression):
    quotes = []
    i = 0
    while expression.find("\"", i) != -1:
        quotes.append(expression.find("\"", i))
        i = expression.find("\"", i) + 1
    return quotes

def handle_print_expression(expression):
    if expression.count("\"") == 2:
        return expression[1:-1]
    elif expression in ('true','right','ok','yes'):
        return True
    elif expression in ('wrong','no','lies','false'):
        return False
    elif expression in ("nothing", "nowhere", "nobody", "gone", "null"):
        return None
    elif expression in ("empty", "silence"):
        return ""
    else:
        try: 
            return float(expression)
        except ValueError:
            pass
            # if ops in expression:
                # do stuff
            # else:
                # print("handle poetic numbers")

def get_word(statement, index):
    statement = statement[index:]
    end = statement.find(" ")
    return statement[:end]

# def get_next_word(statement, index, currWordLength): 

def generate_trees(statement):
    i = 0
    word = get_word(statement, i).lower()

    if word in ('print', 'say', 'shout', 'scream', 'whisper'): 
        d = {"action":"print", "value":""}

        i += len(word) + 1

        if statement[i:][0] == "\"":
            endquote = statement[i+1:].find("\"")
            d["value"] = statement[i+1: i+1+endquote]
        else:
            e = {"action":"get_variable", "value": statement[i:]}
            d["value"] = e
        return d

    quotes = check_for_ops_in_expression(statement)
    if word in ('put'):
        d = {"action":"assign_variable", "value":["var_name", "value"]}
        i += len(word) + 1
        word = get_word(statement, i) 
        if statement[i] == "\"":
            endquote = quotes[quotes.index(i) + 1]  
            d["value"][1] = statement[i+1:endquote]
        elif word in ('true','right','ok','yes'):
            d["value"][1] = True
        elif word in ('wrong','no','lies','false'):
            d["value"][1] = False
        elif word in ("nothing", "nowhere", "nobody", "gone", "null"):
            d["value"][1] = None
        elif word in ("empty", "silence"):
            d["value"][1] = ""
        else:
            try: 
                d["value"][1] = float(word)
            except ValueError:
                print("handle poetic numbers")
        i += len(word) + 1 
        word = get_word(statement, i) 
        if word not in ('into'): 
            print("into expected as next word") 
        i += len(word) + 1 
        word = statement[i:]  
        d["value"][0] = word 
        return d 
        
    #     expression_end = statement.find("into")
    #     expression = statement[i:expression_end]

    #     if statement[i] == "\"":
    #         endquote = statement[i+1:].find("\"")
    #         d["value"][1] = statement[i:endquote]
    #     elif word in ('true','right','ok','yes'):
    #         d["value"][1] = True
    #     elif word in ('wrong','no','lies','false'):
    #         d["value"][1] = False
    #     elif word in ("nothing", "nowhere", "nobody", "gone", "null"):
    #         d["value"][1] = None
    #     elif word in ("empty", "silence"):
    #         d["value"][1] = ""
    #     else:
    #         try: 
    #             d["value"][1] = float(word)
    #         except ValueError:
    #             print("handle poetic numbers")
    #     return d

    elif (word == "let"):
        i = len(word) + 1
        arg = ""
        word = get_word(statement,i)
        while (word != "be"):
            arg += word
            i += len(word) + 1
        i += len(word) + 1
        val = get_word(statement,i)
        d = {"action":"assign_variable", "value":[arg, val]}
        return d
        
    else: #variable assignment / FUNCTION ASSIGNMENT LATER
        if "is" in statement or "are" in statement or "am" in statement or "was" in statement or "were" in statement or "'s" in statement or "'re" in statement: 
            if word in ("a", "an", "the", "my", "your", "our"):
                i += len(word) + 1
            
            word = get_word(statement, i)

            d = {"action":"assign_variable", "value":[word[:-3] if word[-3:] in ("'re", "'s") else word, "value"]}

            i += len(word) + 1

            word = get_word(statement, i)

            i += len(word) + 1
            if statement[i] == "\"":
                d["value"][1] = statement[i:][1:-1]
            elif statement[i:] in ('true','right','ok','yes'):
                d["value"][1] = True
            elif statement[i:] in ('wrong','no','lies','false'):
                d["value"][1] = False
            elif statement[i:] in ("nothing", "nowhere", "nobody", "gone", "null"):
                d["value"][1] = None
            elif statement[i:] in ("empty", "silence"):
                d["value"][1] = ""
            else:
                try: 
                    d["value"][1] = float(statement[i:])
                except ValueError:
                    print("handle poetic numbers")
                
            return d


# print(process_program("print cheese. b is empty"))
# float("sada")

# print(check_for_ops_in_expression("\"donkey\" \"dick"))

d = generate_trees("put true into my var")
print(d) 
