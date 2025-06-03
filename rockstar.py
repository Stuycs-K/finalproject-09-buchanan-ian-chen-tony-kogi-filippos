import re
import itertools

FLOW_CONTROL = ("if", "while", "until")
FALSY = ("wrong", "no", "lies", "false","nothing", "nowhere", "nobody", "gone", "null", "mysterious", 0, "", None) #everything else is truthy
NUMBERS = ["1","2","3","4","5","6","7","8","9"]

def get_word(statement, index):
    statement = statement[index:]
    end = statement.find(" ")
    if end == -1:
       return statement
    return statement[:end]

def process_program(program):
    trees = []
    program = re.sub("(\.|\?|\!|\;|\n)","\n", program)
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
        i = expression.find("\"", i) + 1
    return quotes

# def find_words_in_expression(expression, words):
#     locs = []
#     i = 0
#     #use regex search and change the expression in a loop way
#     while expression.find("\"", i) != -1:
#         locs.append(expression.find("\"", i))
#         i += expression.find("\"", i) + 1
#     return locs

def contains(string, list):
    for i in list:
        if string.find(i) != -1:
            return True

def handle_variable_names(variable):
    if " at " in variable:
        return handle_array(variable)
    if variable in ("it", "he", "she", "him", "her", "they", "them", "ze", "hir", "zie", "zir", "xe", "xem", "ve", "ver"):
        return {"action":"pronoun", "value":"variable"}
    if len(variable.split(" ")) == 3 or (len(variable.split(" ")) == 2 and not contains(variable, ("a", "an", "the", "my", "your", "our"))):
        return " ".join([i[0] + i[1:].lower() for i in variable.split(" ")])
    return variable.lower()

def handle_array(variable):
    if variable[:3] == "at ":
        return [handle_expression(i.strip()) for i in variable.split("at ") if i != ""]
    if " at " not in variable:
        return {"action":"get_array", "value":[variable, []]}
    return {"action":"get_array", "value":[handle_variable_names(variable[:variable.find(" at ")]), handle_array(variable[variable.find(" at ") + 1:])]}

def handle_expression(expression, ctx=["cheese", "the total", "the price", "the tax"]):
    if len(re.findall('((?<!")"(?!"))|((?<="")")', expression)) == 2 and expression[0] == '"' and expression[-1] == '"':
        return re.sub("\"\"", "\"", expression[1:-1])
    elif "," in expression:
        return [handle_expression(i.strip()) for i in re.split(" *,", expression) if i is not None and i not in (",", " ,")]
    elif get_word(expression, 0) in ("so", "like"):
        word = get_word(expression, 0)
        return float("".join(list(itertools.chain.from_iterable([[str(len(i.replace("'", "").replace(".", "")) % 10), "."] if "." in i else str(len(i.replace("'", "")) % 10) for i in expression[len(word) + 1:].split(" ")]))))
    elif get_word(expression, 0) in ("holds"):
        return chr(int(str(("".join([str(len(i.replace("'", "")) % 10) for i in expression[5 + 1:].split(" ")])))))
    elif expression in ('true','right','ok','yes'):
        return True
    elif expression in ('wrong','no','lies','false'):
        return False
    elif expression in ("nothing", "nowhere", "nobody", "gone", "null"):
        return None
    elif expression in ("empty", "silence"):
        return ""
    elif expression in ("it", "he", "she", "him", "her", "they", "them", "ze", "hir", "zie", "zir", "xe", "xem", "ve", "ver"):
        return {"action":"pronoun", "value":"value"}
    else:
        try:
            return float(expression)
        except ValueError:
            if contains(expression, ("+", "with", "plus")):
                d = {"action":"add", "value":[i.strip() for i in re.split("\+|(with)|(plus)", expression) if i is not None and i != "" and not (i in ('with', 'plus'))]}
                for i in range(len(d["value"])):
                    d["value"][i] = handle_expression(d["value"][i])
                return d
            elif contains(expression, ("-", "minus", "without")):
                d = {"action":"minus", "value":[i.strip() for i in re.split("\-|(minus)|(without)", expression) if i is not None and i != "" and not (i in ('minus', 'without'))]}
                for i in range(len(d["value"])):
                    d["value"][i] = handle_expression(d["value"][i])
                return d
            elif contains(expression, ("*", "times", "of")):
                d = {"action":"multiply", "value":[i.strip() for i in re.split("\*|(times)|(of)", expression) if i is not None and i != "" and not (i in ('times', 'of'))]}
                for i in range(len(d["value"])):
                    d["value"][i] = handle_expression(d["value"][i])
                return d
            elif contains(expression, ("/", "over", "between", "divided by")):
                d = {"action":"divide", "value":[i.strip() for i in re.split("\/|(over)|(between)", expression) if i is not None and i != "" and not (i in ('over', 'between'))]}
                for i in range(len(d["value"])):
                    d["value"][i] = handle_expression(d["value"][i])
                return d
            elif expression in ctx:
                return {"action":"get_variable", "value":expression}
            else:
                return "".join(list(itertools.chain.from_iterable([[str(len(i.replace("'", "").replace(".", "")) % 10), "."] if "." in i else str(len(i.replace("'", "")) % 10) for i in expression.split(" ")])))

def booleanParse(word):
    if word in FALSY:
        return False
    else:
        return True

def conditionalToArray(statement, i):
    tokens = []
    while i < len(statement):
        word = get_word(statement, i)
        i += len(word) + 1
        if word in FALSY:
            tokens.append(False)
        elif word in ("not"):
            word = get_word(statement, i)
            i += len(word) + 1
            tokens.append(not booleanParse(word))
        elif word[:3] == "non":
            nonList = word.split("-")
            if nonList[-1] != "non":
                eval = nonList[-1]
                nonList = nonList[:-1]
                if len(nonList) % 2 == 0:
                    tokens.append(booleanParse(eval))
                else:
                    tokens.append(not booleanParse(eval))
            else:
                word = get_word(statement, i)
                i += len(word) + 1
                if len(nonList) % 2 == 0:
                    tokens.append(booleanParse(eval))
                else:
                    tokens.append(not booleanParse(eval))
        ### binary operators
        elif word == "or":
            tokens.append("OR")
        elif word == "and":
            tokens.append("AND")
        elif word in ("is", "was", "are", "were"):
            word = get_word(statement, i)
            i += len(word) + 1
            if word in ("exactly", "really", "actually", "totally"):
                tokens.append("STRICTEQ")
            elif word in ("higher", "greater", "bigger", "stronger"):
                word = get_word(statement, i)
                i += len(word) + 1
                if word == "than":
                    tokens.append("GT")
                else:
                    print("THAN expected in comparison")
            elif word in ("lower", "less", "smaller", "weaker"):
                word = get_word(statement, i)
                i += len(word) + 1
                if word == "than":
                    tokens.append("LT")
                else:
                    print("THAN expected in comparison")
            elif word == "as":
                word = get_word(statement, i)
                i += len(word) + 1
                if word in ("high", "great", "big", "strong"):
                    word = get_word(statement, i)
                    i += len(word) + 1
                    if word == "as":
                        tokens.append("GEQ")
                    else:
                        print("AS expected in comparison")
                if word in ("low", "little", "small", "weak"):
                    word = get_word(statement, i)
                    i += len(word) + 1
                    if word == "as":
                        tokens.append("LEQ")
                    else:
                        print("AS expected in comparison")
            else:
                tokens.append("EQ")
                if len(tokens) != 0 and type(tokens[-1]) == list:
                    x = tokens[-1]
                    s = x[0]
                    s += " " + word
                    x[0] = s
                    tokens[-1] = x
                else:
                    tokens.append([word])
        elif word in ("isn't", "ain't"):
            tokens.append("INEQ")
        else:
            if len(tokens) != 0 and type(tokens[-1]) == list:
                x = tokens[-1]
                s = x[0]
                s += " " + word
                x[0] = s
                tokens[-1] = x
            else:
                tokens.append([word])
    return tokens

# OR, AND, STRICTEQ, INEQ, LEQ, GEQ, LT, GT
#if either value is string, they are coerced to string, if both are numerical they are compared as that
def parseConditionalArray(tokens, ctx={"bigI": "1", "mega": 2}):
    value = tokens[0]
    next = None
    queued = None
    for i in range(1, len(tokens)):
        if queued != None:
            # extract next variable
            if type(tokens[i]) == list:
                var = tokens[i][0]
                next = ctx[var]
            else:
                next = tokens[i]

            # check for string coercion between variables
            string_coercion = False
            if type(value) == str or type(next) == str:
                string_coercion = True

            # begin to evaluate based on queued action
            if queued == "OR":
                if value in FALSY:
                    value = next
            elif queued == "AND":
                if value not in FALSY:
                    value = next
            elif queued == "STRICTEQ":
                value = (value == next)
            elif queued in ("EQ", "INEQ"):
                # check for type coerction (bool and string)
                if type(value) == bool or type(next) == bool:
                    value = booleanParse(value)
                    next = booleanParse(next)
                elif string_coercion:
                    value = str(value)
                    next = str(next)
                #evaluate
                if queued == "EQ":
                    value == (value == next)
                else:
                    value = (value != next)

            # comparison
            else:
                # check for type coercion
                if string_coercion:
                    value = str(value)
                    next = str(value)
                else:
                    if value == True:
                        value = 1
                    elif value == False or value == None:
                        value = 0
                    if next == True:
                        next = 1
                    elif next == False or next == None:
                        next = 0
                #evaluate
                if queued == "LEQ":
                    value = (value <= next)
                elif queued == "GEQ":
                    value = (value >= next)
                elif queued == "LT":
                    value = (value < next)
                elif queued == "GT":
                    value = (value > next)
            # reset action queue and next variable
            next = None
            queued = None
        # no action in queue
        else:
            if type(tokens[i]) == list:
                var = tokens[i][0]
                next = var
            elif type(tokens[i]) == bool:
                next = tokens[i]
            else:
                queued = tokens[i]
    return value



# def get_next_word(statement, index, currWordLength):

def generate_trees(statement):
    i = 0
    word = get_word(statement, i).lower()
    word = word.replace(",", "")

    if word in ('print', 'say', 'shout', 'scream', 'whisper'):
        d = {"action":"print", "value":""}

        i += len(word) + 1
        e = handle_expression(statement[i:], {"cheese":4})
        d["value"] = e
        return d

    if word in ('put'):
        d = {"action":"assign_variable", "value":["var_name", "value"]}
        i += len(word) + 1

        # replace with handle_expression()
        d["value"][1] = handle_expression(statement[i:statement.find(" into")])

        i = statement.find("into")
        word = get_word(statement, i)
        i += len(word) + 1
        word = statement[i:]
        d["value"][0] = handle_variable_names(word)
        return d

    elif (word == "let"):
        i = len(word) + 1
        var_name = statement[i:statement.find(" be")]
        # print(word)
        i = statement.find("be")
        word = get_word(statement, i)
        i += len(word) + 1
            # print(word,i)
        exp = statement[i:]
        # print(word)
        print(exp)
        d = {"action":"assign_variable", "value":[handle_variable_names(var_name), handle_expression(exp)]}
        return d

    elif word == "if":
        d = {"action": "if", "value": "expression"}
        i += len(word) + 1

        # regex to search for end of "expression" -> find action words that are after the "if"
        # re.search() returns match object that can return start and end indexes to splice expression
        # update i to be after expression

        tokens = conditionalToArray(statement, i) # statement is spliced expression
        next_d = parseConditionalArray(tokens)
        d["value"] = next_d
        return d
    elif word in ("while", "until"):
        d = {"action": "loop", "value": [word, "expression", "trees"]}
        i += len(word) + 1
        tokens = conditionalToArray(statement, i)
        next_d = parseConditionalArray(tokens)
        d["value"][1] = next_d
        return d

    elif word[-2:] == "oh":
        i += len(word) + 1
        d = {"action": "end flow", "value": [word, "count"]}
        d["value"][1] = len(word) - 2
        return d
    elif word in ("yeah", "baby"):
        i += len(word) + 1
        d = {"action":"end flow", "value": [word, 1]}
        return d

    elif word in ["rock"]:
        if " like " in statement:
            pos = statement.find(" like ")
            var_name = statement[5:pos]
            return {"action":"assign_variable", "value":[handle_variable_names(var_name), handle_expression(statement[pos+1:])]}
        pos = re.search("(?<=(rock )).*(at ([0-9]|.*))*(?=(( using)|( with)))", statement)
        arr_name = statement[5:pos.end() if pos is not None else len(statement)]
        d = {"action":"", "value":[handle_array(arr_name)]}
        if " using " in statement:
            d["action"] = "replace" #makes the stuff into a list and replaces at that level
            d["value"].append(handle_expression(statement[statement.find(" using ") + 7:]))
        if " with " in statement:
            d["action"] = "append"
            d["value"].append(handle_expression(statement[statement.find(" with ") + 6:]))
        else:
            d["action"] = "assign_array"
        return d

    elif word in ["rock"]:
        if contains(statement, "at"):
            arr_name = ""
            d = [{"action":"assign array", "value": ""}]
            i += len(word) + 1
            word = get_word(statement,i)
            while word != "at" and i < len(statement):
                if (len(arr_name) != 0):
                    arr_name += " "
                arr_name += word
                print(word)
                i += len(word) + 1
                word = get_word(statement,i)
            if word == "at":
                i += len(word) + 1
                word = get_word(statement,i)
                # while (word != is and i < len(statement)):.

                # if word in NUMBERS:
                    # index = word
                    # i += len(word) + 1
                    # word = get_word(statement,i)
                    #
                # else:
                     # raise Exception("index or key is required for array assignment")
            else:
                d[0]["value"] = [arr_name]
            return d
        else:
            pass
            #FILIPPOS WRITE HERE

    elif " at " in statement:
        d = {}
        arr_name = ""
        arr_name += word
        # print(word)
        i += len(word) + 1
        word = get_word(statement,i)
        while word != "at" and i < len(statement):
            arr_name += " " + word
            # print(word)
            i += len(word) + 1
            word = get_word(statement,i)
        if word == "at":
            return d

        # i += len(word) + 1
        # word = get_word(statement,i)
        # print(word)
        # index = word
        # i += len(word) + 1
        # word = get_word(statement,i)
        if word == "is":
            i += len(word) + 1
            val = statement[i:]
        else:
            raise Exception("\'is\' is required when using \'at\'")

        d = {"action":"assign array", "value":[arr_name,index,val]}
        return d

    else:
        if " is " in statement or " are " in statement or " am " in statement or " was " in statement or " were " in statement:
            pos = re.search("( is)|( are)|( am)|( was)|( were)",statement)
            d = {"action":"assign_variable", "value":[handle_variable_names(statement[:pos.start()]), "value"]}

            i = pos.end()

            word = get_word(statement, i)

            i += len(word) + 1
            d["value"][1] = handle_expression(statement[i:])
            return d
        if "'s" in statement or "'re" in statement:
            pos = re.search("('s)|('re)",statement).start()
            d = {"action":"assign_variable", "value":[handle_variable_names(statement[:pos]), "value"]}
            i = pos

            word = get_word(statement, i)
            i +=len(word) +1
            d["value"][1] = handle_expression(statement[i:])
            return d
        if contains(statement, ("says", "said")):
            start = re.search("( says)|( said)",statement).start()
            end = re.search("( says)|( said)",statement).end()
            str = statement[end+1:] if statement[end] == " " else statement[end:]
            return {"action":"assign_variable", "value":[handle_variable_names(statement[:start].strip()), handle_expression('"' + str + '"')]}
        if contains(statement, ("holds")):
            start = re.search("( holds)",statement).start()
            d = {"action":"assign_variable", "value":[handle_variable_names(statement[:start]), "value"]}
            d["value"][1] = handle_expression(statement[start + 1:])
            return d


# print(process_program("print cheese. b is empty"))
# float("sada")

# print(check_for_ops_in_expression("\"donkey\" \"doop"))

# print(generate_trees("M at 0 is me"))

# print(get_word("let him be me", 11))
# d = generate_trees("put true into my var")
# print(d)
# print(find_quotes_in_expression("\"donkey\" \"doop"))
# print(re.split("\*|(times)|(of)","1 * 2 times 3"))
# print(generate_trees("put 1 * 2 times 3 + 5 / 3 - 10 into the b"))
# print(generate_trees("the b's 1 * 2 times 3 + 5 / 3 - 10"))
# print(generate_trees("let the b be 1 * 2 times 3 + 5 / 3 - 10"))
# print(generate_trees("let Jonny Cheese be 1 * 2 times 3 + 5 / 3 - 10"))
# print(generate_trees("let the STICKY B be cheese * 2 times 3 + 5 / 3 - 10"))
# print(generate_trees("Let the total be the price + the tax"))
# print(generate_trees("he holds a gun"))

tokens = conditionalToArray("bigI and bigI or mega", 0)
print(parseConditionalArray(tokens, {"bigI": "1", "mega": 2}))
print(generate_trees("rock jimmy at 3 using 1,2, \"cheese\""))
print(generate_trees("rock jimmy at 3 with 1,2, \"cheese\""))
print(generate_trees("jimmy is dying"))
# print(handle_array("jimmy"))
# print(conditionalToArray("me and you or my dream", 0))
