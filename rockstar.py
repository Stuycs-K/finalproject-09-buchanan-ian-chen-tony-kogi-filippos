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

def find_quotes_in_expression(expression):
    quotes = []
    i = 0
    while expression.find("\"", i) != -1:
        quotes.append(expression.find("\"", i))
        i += expression.find("\"", i) + 1
    return quotes

def find_words_in_expression(expression, words):
    locs = []
    i = 0
    #use regex search and change the expression in a loop way
    while expression.find("\"", i) != -1:
        quotes.append(expression.find("\"", i))
        i += expression.find("\"", i) + 1
    return quotes

def contains(string, list):
    for i in list:
        if string.find(i) != -1:
            return True

def handle_expression(expression):
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
            if expression.count("\"") > 2:
                quotes = find_quotes_in_expression(expression)
                pairs_quotes = [[quotes[i], quotes[i+1]] for i in range(0, len(quotes) - 1)]
            elif contains(expression, ("+", "with", "plus")):
                d = {"action":"add", "value":[i.strip() for i in re.split("\+|(with)|(plus)", expression) if i is not None and not (i in ('with', 'plus'))]}
                for i in range(len(d["value"])):
                    d["value"][i] = handle_expression(d["value"][i])
                return d
            elif contains(expression, ("-", "minus", "without")):
                d = {"action":"minus", "value":[i.strip() for i in re.split("\-|(minus)|(without)", expression) if i is not None and not (i in ('minus', 'without'))]}
                for i in range(len(d["value"])):
                    d["value"][i] = handle_expression(d["value"][i])
                return d
            elif contains(expression, ("*", "times", "of")):
                d = {"action":"multiply", "value":[i.strip() for i in re.split("\*|(times)|(of)", expression) if i is not None and not (i in ('times', 'of'))]}
                for i in range(len(d["value"])):
                    d["value"][i] = handle_expression(d["value"][i])
                return d
            elif contains(expression, ("/", "over", "between")):
                d = {"action":"divide", "value":[i.strip() for i in re.split("\/|(over)|(between)", expression) if i is not None and not (i in ('over', 'between'))]}
                for i in range(len(d["value"])):
                    d["value"][i] = handle_expression(d["value"][i])
                return d

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
    #     d = {"action":"assign_variable", "value":["var_name", "value"]}
    #     i += len(word) + 1

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

# print(find_quotes_in_expression("\"donkey\" \"doop"))
# print(re.split("\*|(times)|(of)","1 * 2 times 3"))
print(handle_expression("1 * 2 times 3 + 5 / 3 - 10"))
