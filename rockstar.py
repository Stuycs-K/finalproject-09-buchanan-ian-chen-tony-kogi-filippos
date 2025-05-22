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

def get_word(statement, index):
    statement = statement[index:]
    end = statement.find(" ")
    return statement[index:end]

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
    # if word in ('put'):
        
    else: #variable assignment / FUNCTION ASSIGNMENT LATER
        if "is" in statement or "are" in statement or "am" in statement or "was" in statement or "were" in statement or "'s" in statement or "'re" in statement: 
            if word in ("a", "an", "the", "my", "your", "our"):
                i += len(word) + 1
            
            word = get_word(statement, i)

            d = {"action":"assign_variable", "value":[word[:-3] if word[-3:] in ("'re", "'s") else word, "value"]}

            i += len(word) + 1

            i += len(word) + 2
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


print(process_program("print cheese. b is empty"))
# float("sada")