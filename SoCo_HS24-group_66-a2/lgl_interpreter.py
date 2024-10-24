import sys, json, re, ast, operator
from collections import ChainMap
# Idea of lexicographic scoping is:
# --> We have 2 globals
#       1. The first one is the actual globals() dictionary
#       2. The second one is a pseudo-global dictionary with func_names as keys and the values defined within those funcs as values
#          This way if we define a function inside a function we copy the outer func dictionary and add on top

# ['set', 'get_n_power', 
#     ['function', ['x'], 
#         [
#             'set', 'n', 5, 
#             'set', 'result', 0, 
#             'set', 'calculate',
#                 ['function',
#                     [
#                         'set', 'result', ['power', ['get', 'x'], ['get', 'n']]
#                     ]
#                 ],
#             ["call","calculate"]
#         ]
#     ]
# ]

# def get_n_power(x):
#     n = 5
#     result = 0
#     def calculate():
#         result = x**n
#     return result

# pseudo_globals = {
#     'add': {'x': 1, 'y': 2},
#     'calculate': {'x': 1, 'y': 2, 'result': 1**2},
# }
def convert_value(val):
    try:
        return int(val) # First, try to convert the value to an integer
    except ValueError:
        try:
            inner = val.strip()[1:-1].strip()
            if inner.startswith("'") and inner.endswith("'"):
                inner_str = inner[1:-1]
                result = [inner_str]
                return result #Tries to see if it is a list
            else:
                try:
                    result = ast.literal_eval(val)
                    if isinstance(result, list):
                        return result #Tries to see if it is a list
                    else:
                       raise ValueError(f"'{val}' is neither a number nor a list.")
                except:
                    pass
        except (ValueError, SyntaxError):
            raise ValueError(f"'{val}' is neither a number nor a list.")
            
def solve_expression(args, operation, metadata):
    assert len(args) == 2, f"Expected two arguments, got {len(args)}"
    left = do(convert_value(args[0]), metadata)     # Convert the arguments to values (numbers or nested expressions)
    right = do(convert_value(args[1]), metadata)
    #We do it this way to avoid using eval() and avoiding else if statements
    OPERATORS = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.floordiv, # to avoid having floats, and thene error because of that
        'and': operator.and_,
        'or': operator.or_,
        'xor': operator.xor,
    }
    op_func = OPERATORS.get(operation.lower())
    if op_func is None:
        raise ValueError(f"Unsupported operator: {operation}")
    return op_func(left, right)

def evaluate_expression(expr, metadata):
    match = re.search(r'([+\-*/]|and|or|xor)', expr, re.IGNORECASE) # gets the expression
    assert match, f"Not a valid expression: {expr}" # if there is not valid expression then error
    operation = match.group(0) # gets the exact expression that he got
    index = expr.find(operation)
    left = expr[:index].strip()
    right = expr[index + 1:].strip()
    args = [left, right]
    # use search
    return solve_expression(args, operation, metadata)


def do_add(args, metadata):
    assert len(args) == 2
    left = do(args[0], metadata)
    right = do(args[1], metadata)
    return left + right

def do_substract(args, metadata):
    assert len(args) == 2
    left = do(args[0], metadata)
    right = do(args[1], metadata)
    return left - right

def do_multiplication(args, metadata):
    assert len(args) == 2
    left = do(args[0], metadata)
    right = do(args[1], metadata)
    return left * right

def do_divition(args, metadata):
    assert len(args) == 2
    left = do(args[0], metadata)
    right = do(args[1], metadata)
    assert right != 0, "Error: divition by 0"
    return left / right

def do_or(args, metadata):
    assert len(args) == 2
    left = do(args[0], metadata)
    right = do(args[1], metadata)
    return left or right

def do_and(args, metadata):
    assert len(args) == 2
    left = do(args[0], metadata)
    right = do(args[1], metadata)
    return left and right

def do_xor(args, metadata):
    assert len(args) == 2
    left = do(args[0], metadata)
    right = do(args[1], metadata)
    return left ^ right

def do_absolute(args, metadata):
    assert len(args) == 1
    val = do(args[0], metadata)
    return abs(val)

def do_sequence(args, metadata):
    assert len(args) > 0
    result = None
    for expr in args:
        result = do(expr, metadata)
    return result

def do_call(args, metadata: dict):
    assert len(args) >= 1, "Expected at least 1 argument: function name"
    assert isinstance(args[0], str), f"Function name must be a string, got {type(args[0])}"

    func_name = args[0]
    args = args[1:]

    enter_function(func_name, metadata)

    func_data = metadata['functions'][func_name]
    params = func_data['params']
    body = func_data['body']

    for param_name, arg_value in zip(params, args):
        metadata['locals'][param_name] = do(arg_value, metadata)

    result = do(body, metadata)
    exit_function(metadata)
    return result


def do_set(args, metadata: dict):
    assert len(args) == 2, "Expected exactly 2 arguments: name and value"
    assert isinstance(args[0], str), f"Variable name must be a string, got {type(args[0])}"

    name, value = args  # ["function", ["a", "b"], [ ... ] ]   OR   ["x", "2"]

    # Handle function definition
    if isinstance(value, list) and value[0] == 'function':
        params = value[1]  # Function parameters
        body = value[2]    # Function body

        metadata['functions'][name] = {
            'params': params,
            'body': body,
            'func_scope': {} 
        }
        return metadata['functions'][name]

    value = do(value, metadata)

    if metadata['in_function']:
        func_name = metadata['in_function']
        metadata['functions'][func_name]['scope'][name] = value
    else:
        metadata['globals'][name] = value
    
    return value

def do(expr, metadata):
    if isinstance(expr, int):
        return expr

    if isinstance(expr, str):
        return evaluate_expression(expr, metadata)

    assert isinstance(expr, list), f"Expected expr to be a list, got {type(expr)}: {expr}"

    if len(expr) == 1 and isinstance(expr[0], str):
        return evaluate_expression(expr[0], metadata)
    
    operation = expr[0]
    print(operation)
    if operation in OPS:
        return OPS[operation](expr[1:], metadata)
    else:
        raise ValueError(f"Unknown operation: {operation}")
        

    
def enter_function(func_name, metadata):
    metadata['in_function'] = func_name
    if func_name not in metadata['functions']:
        metadata['functions'][func_name] = {}

def exit_function(metadata):
    metadata['locals'] = {}
    metadata['in_function'] = False

# Dynamically find and name all operations we support in our language
OPS = {
    name.replace("do_", ""): func
    for (name, func) in globals().items()
    if name.startswith("do_")
}

def main():
    assert len(sys.argv) == 2   # Usage: python lgl_interpreter.py code.gsc
    with open(sys.argv[1]) as source:
        program = json.load(source)



    metadata = {
        'in_function': None,
        'globals': {},  # True global variables
        'functions': {},  # Function-specific scopes
        'locals': {},  # Local variables
    }

    result = do(program, metadata)
    
    print(result)
    print(metadata)




if __name__ == "__main__":
    main()