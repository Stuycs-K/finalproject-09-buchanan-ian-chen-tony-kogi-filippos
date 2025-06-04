import math
import re
import itertools
import sys

FLOW_CONTROL = ("if", "while", "until")
FALSY = ("wrong", "no", "lies", "false","nothing", "nowhere", "nobody", "gone", "null", "mysterious", 0, "", None) #everything else is truthy
NUMBERS = ["1","2","3","4","5","6","7","8","9"]

def isNumber(word):
    for i in range(len(word)):
        if word[i] not in NUMBERS:
            return False
    return True

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

def handle_variable_names(variable, ctx):
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
        return {"action":"get_array", "value":[variable, []]} #MAKE THIS WORK 
    return {"action":"get_array", "value":[handle_variable_names(variable[:variable.find(" at ")], ctx), handle_array(variable[variable.find(" at ") + 1:])]}

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

def conditionalToArray(statement, i, ctx):
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
            elif word in ctx:
                tokens.append([word])
            else: 
                if word[0] == "\"" and word[-1] == "\"": 
                    tokens.append(word)
                elif word.lower() == "true": 
                    tokens.append(True) 
                elif word.lower() == "false": 
                    tokens.append(False) 
                else: 
                    tokens.append(int(word)) 
    return tokens

def comparisonEval(value1, queued, next): 
    #print(value1, queued, next) 
    value = value1 
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
            value = (value == next)
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
    return value 
        

# OR, AND, STRICTEQ, INEQ, LEQ, GEQ, LT, GT
#if either value is string, they are coerced to string, if both are numerical they are compared as that
def parseConditionalArray(tokens, ctx):
    value = tokens[0]
    next = None
    queued = None
    #print(len(tokens)) 
    #print(value, queued, next)
    for i in range(1, len(tokens)):
        if queued != None:
            if type(tokens[i]) == list:
                var = tokens[i][0]
                next = ctx[var]
                #print(var) 
                #print(next) 
            else:
                next = tokens[i]
            value = comparisonEval(value, queued, next)
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
        #print(value, queued, next)
    return value



# def get_next_word(statement, index, currWordLength):

def generate_trees(statement, ctx):
    i = 0
    word = get_word(statement, i).lower()
    word = word.replace(",", "")

    if word in ('print', 'say', 'shout', 'scream', 'whisper'):
        d = {"action":"print", "value":""}

        i += len(word) + 1
        if " at " in statement:
            e = handle_array(statement[i:])
            e["action"] = "print_array"
        else:
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
        d["value"][0] = handle_variable_names(word, ctx)
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
        d = {"action":"assign_variable", "value":[handle_variable_names(var_name, ctx), handle_expression(exp, ctx)]}
        return d

    elif word in ("if", "when"):
        d = {"action": "if", "value": "expression"}
        i += len(word) + 1
        tokens = conditionalToArray(statement, i, ctx) # statement is spliced expression
        next_d = parseConditionalArray(tokens, ctx)
        d["value"] = next_d
        return d
    
    elif word in ("else", "otherwise"): 
        i += len(word) + 1 
        d = {"action": "else", "value": generate_trees(statement[i:])} 
        return d 

    elif word in ("while", "until"):
        d = {"action": "loop", "value": [word, "expression"]}
        i += len(word) + 1
        tokens = conditionalToArray(statement, i, ctx)
        next_d = parseConditionalArray(tokens, ctx)
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
            return {"action":"assign_variable", "value":[handle_variable_names(var_name, ctx), handle_expression(statement[pos+1:], ctx)]}
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
            return d["value"][0]
        
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
                d = {"action":"assign_variable", "value":[handle_variable_names(statement[:pos.start()], ctx), "value"]}

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
            d = {"action":"assign_variable", "value":[handle_variable_names(statement[:pos], ctx), "value"]}
            i = pos

            word = get_word(statement, i)
            i +=len(word) +1
            d["value"][1] = handle_expression(statement[i:], ctx)
            return d
        if contains(statement, ("says", "said")):
            start = re.search("( says)|( said)",statement).start()
            end = re.search("( says)|( said)",statement).end()
            str = statement[end+1:] if statement[end] == " " else statement[end:]
            return {"action":"assign_variable", "value":[handle_variable_names(statement[:start].strip(), ctx), handle_expression('"' + str + '"', ctx)]}
        if contains(statement, ("holds")):
            start = re.search("( holds)",statement).start()
            d = {"action":"assign_variable", "value":[handle_variable_names(statement[:start], ctx), "value"]}
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

def create_list(index):
    dict = {}
    curr = dict
    for i in index: 
        if type(i) is float or type(i) is int:
            i = int(i)
            for j in range(i+1):
                curr[j] = {}
        else:
            curr[i] = {}
        curr = curr[i]
    return dict

def list_to_string(dict):
    out = "["
    if dict == {}:
        return "null, "
    if type(dict) is int or type(dict) is float:
        return str(dict) + ", "
    if type(dict) is bool:
        return str(dict).lower() + ", "
    if type(dict) is str:
        return dict + ", "
    if dict is None:
        return "null, "
    b = [i for i in list(dict.keys()) if type(i) is int]
    b.sort()
    for i in b:
        out += list_to_string(dict[i])
    for i in [i for i in list(dict.keys()) if type(i) is not int]:
        out += f"\"{i}\":" + list_to_string(dict[i]) + ", "
    out += "]"
    return out

def get_dict(dict, index, ctx):
    dict = ctx[dict]
    for i in index:
        dict = dict[int(i)]
    return dict

def interpret_dict(dict, ctx):
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
        if list_to_string(ctx[dict["value"]["value"]])[-1] == ",":
            print(list_to_string(ctx[dict["value"]["value"]]))
        else:
            print(interpret_dict(dict["value"], ctx))
    if dict["action"] == "print_array":
        # print(get_dict(dict["value"][0], dict["value"][1], ctx))
        return list_to_string(get_dict(dict["value"][0], dict["value"][1], ctx))
    if dict["action"] == "get_array":
        if not (dict["value"][0] in ctx.keys()):
            ctx[dict["value"][0]] = create_list(dict["value"][1])
        return dict["value"][0], dict["value"][1]
    if dict["action"] == "append":
        a, b = interpret_dict(dict["value"][0], ctx)
        d = get_dict(a, b, ctx)
        k = [i for i in list(dict.keys()) if type(i) is int]
        if len(k) == 0: n = 0 
        else: n = max(k) + 1
        d[n] = interpret_dict(dict["value"][1], ctx)
    if dict["action"] == "inplace":
        a, b = interpret_dict(dict["value"][0], ctx)
        d = get_dict(a, b[:-1], ctx)
        if type(b[-1]) is float:
            b[-1] = int(b[-1])
        d[b[-1]] = interpret_dict(dict["value"][1], ctx)
    if dict["action"] == "if": 
        exp = dict["value"] 
        return ["if", exp]
    if dict["action"] == "else": 
        tree = dict["value"] 
        return ["else", tree] 
    if dict["action"] == "end flow": 
        count = dict["value"][1] 
        return ["end flow", count]


def run_program(li, ctx={"cheese":5}):
    # if statement run parameters 
    else_run = False 
    run = None
    if_counter = 0 

    # process dictionaries 
    for i in li:
        if (if_counter != 0 and run == True) or if_counter == 0: 
            output = interpret_dict(i, ctx)
        elif (if_counter != 0 and run == False): 
            else_run = True 
            if_counter = if_counter - 1

        # flow control processing 
        if type(output) == list and output[0] == "else": 
            if else_run == True: 
                tree = output[1] 
                interpret_dict(tree, ctx)
        if type(output) == list and output[0] == "if": 
            if_counter += 1 
            if output[1] in FALSY: 
                run = False 
            else: 
                run = True 
            if_counter += 1 
        if type(output) == list and output[0] == "end flow": 
            count = output[1] 
            if_counter = max(if_counter - count, 0) 

out = ""
with open(sys.argv[1], "r") as f:
    out = f.read()


ctx = {}
run_program(process_program(out, ctx), ctx)

