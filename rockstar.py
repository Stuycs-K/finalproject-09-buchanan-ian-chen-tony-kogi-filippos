import math
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

def process_program(program, ctx):
    trees = []
    program = re.sub("(\.|\?|\!|\;|\n)","\n", program)
    for i in program.split("\n"):
        if i == "":
            continue
        i = i.strip()
        trees.append(generate_trees(i, ctx))
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

def handle_variable_names(variable, ctx=[]  ):
    if variable in ctx:
        return handle_expression(variable)
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
        return {"action":"get_array", "value":[handle_expression(variable), []]} #MAKE THIS WORK 
    return {"action":"get_array", "value":[handle_expression(handle_variable_names(variable[:variable.find(" at ")])), handle_array(variable[variable.find(" at ") + 1:])]}

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
            if contains(expression, ("+", "with ", "plus")):
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
            # elif expression in ctx:
            #     return {"action":"get_variable", "value":expression}
            else:
                return {"action":"get/poetic", "value":expression}
                # return "".join(list(itertools.chain.from_iterable([[str(len(i.replace("'", "").replace(".", "")) % 10), "."] if "." in i else str(len(i.replace("'", "")) % 10) for i in expression.split(" ")])))

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

def generate_trees(statement, ctx):
    i = 0
    word = get_word(statement, i).lower()
    word = word.replace(",", "")

    if word in ('print', 'say', 'shout', 'scream', 'whisper'):
        d = {"action":"print", "value":""}

        i += len(word) + 1
        e = handle_expression(statement[i:], ctx)
        d["value"] = e
        return d

    if word in ('put'):
        d = {"action":"assign_variable", "value":["var_name", "value"]}
        i += len(word) + 1

        # replace with handle_expression()
        d["value"][1] = handle_expression(statement[i:statement.find(" into")], ctx)

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
        # print(exp)
        d = {"action":"assign_variable", "value":[handle_variable_names(var_name), handle_expression(exp, ctx)]}
        return d

    elif word in ("if", "while", "until"):
        d = {"action":"flow control", "value": [word, "expression"  ]}
        i += len(word) + 1
        tokens = conditionalToArray(statement, i)
        next_d = parseConditionalArray(tokens)
        d["value"][1] = next_d
        return d

    elif word in ("oh", "yeah", "baby"):
        d = {"action":"end flow", "value": word}
        return d

    elif word in ["rock"]:
        if " like " in statement:
            pos = statement.find(" like ")
            var_name = statement[5:pos]
            return {"action":"assign_variable", "value":[handle_variable_names(var_name), handle_expression(statement[pos+1:], ctx)]}
        pos = re.search("(?<=(rock )).*(at ([0-9]|.*))*(?=(( using)|( with)))", statement)
        arr_name = statement[5:pos.end() if pos is not None else len(statement)]
        d = {"action":"", "value":[handle_array(arr_name)]}
        if " using " in statement:
            d["action"] = "replace" #makes the stuff into a list and replaces at that level 
            d["value"].append(handle_expression(statement[statement.find(" using ") + 7:], ctx))
        if " with " in statement:
            d["action"] = "append"
            d["value"].append(handle_expression(statement[statement.find(" with ") + 6:], ctx))
        else: 
            d["action"] = "assign_array"
        return d
    # elif " at " in statement:
    #     d = {}
    #     arr_name = ""
    #     arr_name += word
    #     # print(word)
    #     i += len(word) + 1
    #     word = get_word(statement,i)
    #     while word != "at" and i < len(statement):
    #         arr_name += " " + word
    #         # print(word)
    #         i += len(word) + 1
    #         word = get_word(statement,i)
    #     if word == "at":
    #         return d

        # i += len(word) + 1
        # word = get_word(statement,i)
        # print(word)
        # index = word
        # i += len(word) + 1
        # word = get_word(statement,i)
        # if word == "is":
        #     i += len(word) + 1
        #     val = statement[i:]
        # else:
        #     raise Exception("\'is\' is required when using \'at\'")

        # d = {"action":"assign array", "value":[arr_name,index,val]}
        # return d

    else:
        if " is " in statement or " are " in statement or " am " in statement or " was " in statement or " were " in statement:
            if " at " not in statement:
                pos = re.search("( is)|( are)|( am)|( was)|( were)",statement)
                d = {"action":"assign_variable", "value":[handle_variable_names(statement[:pos.start()]), "value"]}

                i = pos.end()

                word = get_word(statement, i)

                i += len(word) + 1
                d["value"][1] = handle_expression(statement[i:], ctx)
                return d
            else: 
                pos = statement.find(" is ")
                arr_name = statement[:pos]
                d = {"action":"inplace", "value":[handle_array(arr_name)]}
                d["value"].append(handle_expression(statement[pos + 4:], ctx))
                return d
        if "'s" in statement or "'re" in statement:
            pos = re.search("('s)|('re)",statement).start()
            d = {"action":"assign_variable", "value":[handle_variable_names(statement[:pos]), "value"]}
            i = pos

            word = get_word(statement, i)
            i +=len(word) +1
            d["value"][1] = handle_expression(statement[i:], ctx)
            return d
        if contains(statement, ("says", "said")):
            start = re.search("( says)|( said)",statement).start()
            end = re.search("( says)|( said)",statement).end()
            str = statement[end+1:] if statement[end] == " " else statement[end:]
            return {"action":"assign_variable", "value":[handle_variable_names(statement[:start].strip()), handle_expression('"' + str + '"', ctx)]}
        if contains(statement, ("holds")):
            start = re.search("( holds)",statement).start()
            d = {"action":"assign_variable", "value":[handle_variable_names(statement[:start]), "value"]}
            d["value"][1] = handle_expression(statement[start + 1:], ctx)
            return d



def add(a, b):
    if type(a) is dict:
        a = interpret_dict(a)
    if type(b) is dict:
        b = interpret_dict(b)
    if type(a) is float:
            try: 
                a = int(a)
            except:
                pass
    if type(b) is float:
        try: 
            b = int(b)
        except:
            pass
    if type(a) is str or type(b) is str:
        if a == True and not type(a) is int and not type(a) is float: a = "true"
        if a == False and not type(a) is int and not type(a) is float: a = "false"
        if b == True and not type(b) is int and not type(b) is float: b = "true"
        if b == False and not type(b) is int and not type(b) is float: b = "false"
        if a == None: a = "null"
        if b == None: b = "null"   
        return str(a) + str(b)
    if a == None: a = 0
    if b == None: b = 0
    if a == True and not type(b) is int and not type(b) is float: a = 1
    if b == False and not type(b) is int and not type(b) is float: b = 0
    return a + b

def minus(a, b):
    if type(a) is dict:
        a = interpret_dict(a)
    if type(b) is dict:
        b = interpret_dict(b)
    if type(a) is float:
            try: 
                a = int(a)
            except:
                pass
    if type(b) is float:
        try: 
            b = int(b)
        except:
            pass
    if (type(a) is int or type(a) is float) and (type(b) is int or type(b) is float):
        return a - b
    if type(a) is str or type(b) is str: 
        if a == True and not type(a) is int and not type(a) is float: a = "true"
        if a == False and not type(a) is int and not type(a) is float: a = "false"
        if b == True and not type(b) is int and not type(b) is float: b = "true"
        if b == False and not type(b) is int and not type(b) is float: b = "false"
        a = str(a)
        b = str(b)
        index = len(b)
        if a[-1 * index:] == b:
            return a[:-1*index]
        if a == "true":
            return True
        if a == "false":
            return False
    if (type(a) is bool or a is None) or (type(b) is bool or b is None):
        if a == True: a = 1
        if a == False or a == None: b = 0
        if b == True: b = 1
        if b == False or b == None: b = 0
        return a - b
    
def mult(a, b):
    if type(a) is dict:
        a = interpret_dict(a)
    if type(b) is dict:
        b = interpret_dict(b)
    if a is None or (a == False and type(a) is bool): 
        a = 0
    if b is None or (b == False and type(b) is bool): 
        b = 0
    if (type(a) is float or type(a) is int) and (type(b) is float or type(b) is int):
        return a * b
    if type(a) is str:
        if b < 0:
            a = a[::-1]
            b *= -1
        whole = math.floor(b)
        remainder = b - whole
        out = a * whole
        index = math.ceil(len(a) * remainder)
        return out + a[index:]
    if type(b) is str: 
        if a < 0:
            b = b[::-1]
            a *= -1
        whole = math.floor(a)
        remainder = a - whole
        out = b * whole
        index = math.ceil(len(b) * remainder)
        return out + b[index:]

def div(a, b):
    if type(a) is dict:
        a = interpret_dict(a)
    if type(b) is dict:
        b = interpret_dict(b)
    if type(b) is bool and b == True:
        b = 1
    if type(b) is str:
        if a == True and not type(a) is int and not type(a) is float: a = "true"
        if a == False and not type(a) is int and not type(a) is float: a = "false"
        if b == True and not type(b) is int and not type(b) is float: b = "true"
        if b == False and not type(b) is int and not type(b) is float: b = "false"
        a = str(a)
        count = 0
        for i in range(len(a)):
            if a[i:i+len(b)] == b:
                count += 1
        return count
    if type(b) is float or type(b) is int:
        if a is None or (type(a) is bool and a == False):
            a = 0
        if type(a) is bool and a == True:
            a = 1
        if type(a) is bool:
            return a / (b * 1.)
        if type(a) is str:
            return mult(a, 1/(b * 1.))



def compute(li, func):
    out = li[0]
    for i in range(1, len(li)):
        out = func(out, li[i])
    return out

def interpret_dict(dict, ctx={"cheese":5}):
    if type(dict) is float or type(dict) is int or type(dict) is str:
        if type(dict) is float: 
            try: 
                dict = int(dict)
            except: 
                pass
        return dict
    if dict["action"] == "get/poetic":
        if dict["value"] in ctx:
            return ctx[dict["value"]]
        return "".join(list(itertools.chain.from_iterable([[str(len(i.replace("'", "").replace(".", "")) % 10), "."] if "." in i else str(len(i.replace("'", "")) % 10) for i in dict["value"].split(" ")])))
    if dict["action"] == "assign_variable":
        value = interpret_dict(dict["value"][1], ctx)
        # print(value, 1)
        var = dict["value"][0]
        if var in ctx: 
            if type(value) is str:
                if value[0] == "+":
                    # print(add(ctx[var], handle_expression(value[1:])))
                    ctx[var] = add(ctx[var], handle_expression(value[1:]))
                if value[0] == "-":
                    ctx[var] = minus(ctx[var], handle_expression(value[1:]))
                if value[0] == "*":
                    ctx[var] = mult(ctx[var], handle_expression(value[1:]))
                if value[0] == "/":
                    ctx[var] = div(ctx[var], handle_expression(value[1:]))
                return
        ctx[dict["value"][0]] = value
    if dict["action"] == "add":
        if len(dict["value"]) == 1:
            return "+" + str(dict["value"][0])
        return compute(dict["value"], add)
    if dict["action"] == "minus":
        if len(dict["value"]) == 1:
            return "-" + str(dict["value"][0])
        return compute(dict["value"], minus)
    if dict["action"] == "multiply":
        if len(dict["value"]) == 1:
            return "*" + str(dict["value"][0])
        return compute(dict["value"], mult)
    if dict["action"] == "divide":
        if len(dict["value"]) == 1:
            return "/" + str(dict["value"][0])
        return compute(dict["value"], div)
    if dict["action"] == "print":
        print(interpret_dict(dict["value"], ctx))
    
def run_program(li, ctx={"cheese":5}):
    for i in li:
        interpret_dict(i, ctx)
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

# tokens = conditionalToArray("bigI and bigI or mega", 0)
# print(parseConditionalArray(tokens, {"bigI": "1", "mega": 2}))
# print(generate_trees("rock jimmy at 3 using 1,2, \"cheese\""))
# print(generate_trees("rock jimmy at 3 with 1,2, \"cheese\""))
# print(generate_trees("jimmy is dying"))

# print(process_program("print \"cheese\". cheese is 5. rock cheese. fries is 5 + 5 + 2"))
# print(interpret_dict({"action":"add", "value":[None, 1, 2.0, "cheese", True]}))
# print(generate_trees("he is over 5"))
# print(interpret_dict({"action":"multiply", "value":["cheese", 1/-0.24]}))
# print(interpret_dict({"action":"divide", "value":["cheese", 0.24]}))
ctx = {}
# run_program(process_program("rock cheese like aces. cheese is with 4. print cheese.", ctx))
# print(process_program("john at 4 is 1", ctx))
print(generate_trees("tim at 1 is 5", ctx))
#test more ROCK, FIX AT 
# print(process_program("rock cheese like aces. cheese is with 4. print cheese.", ctx))

# print(parseConditionalArray(conditionalToArray("bigI and \"cheese\"", 0)))
#MAKE CHEESE CALL THE VARIABLE
# print(handle_array("jimmy"))
# print(conditionalToArray("me and you or my dream", 0))