import sys, json, pprint
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

##############################################
################ OPERATIONS ##################
##############################################

def do_add(args, metadata):
    assert len(args) == 2
    left = do(args[0], metadata)
    right = do(args[1], metadata)
    return left + right

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

##############################################
############ GETTERS AND SETTERS #############
##############################################

def do_call(args, metadata: dict):
    assert len(args) >= 1, "Expected at least 1 argument: function name"
    assert isinstance(args[0], str), f"Function name must be a string, got {type(args[0])}"

    func_name = args[0]
    args = args[1:]
    assert func_name in metadata['functions'], f"Function {func_name} not defined in the global scope."
    func_data = metadata['functions'][func_name]
    
    # Ensure the number of passed arguments matches the function definition
    assert len(args) == len(func_data['params']), "Incorrect number of arguments passed to function."

    # Set up a new local scope (fresh scope for each call)
    new_local_scope = {}
    metadata['functions'][func_name]['scope'] = metadata['functions'][func_name]['scope'].new_child(new_local_scope)

    # Set up the function parameters in the new local scope
    for param_name, arg_value in zip(func_data['params'], args):
        metadata['functions'][func_name]['scope'][param_name] = do(arg_value, metadata)

    # Execute the function body
    result = do(func_data['body'], metadata)

    # Discard the local scope after execution
    metadata['functions'][func_name]['scope'] = metadata['functions'][func_name]['scope'].parents

    return result


def do_set(args, metadata: dict):
    assert len(args) == 2, "Expected exactly 2 arguments: key and value"
    assert isinstance(args[0], str), f"Variable name must be a string, got {type(args[0])}"

    name, value = args  # ["function", ["a", "b"], [ ... ] ]   OR   ["x", "2"]
    
    # Handle function definition
    if isinstance(value, list) and value[0] == 'function':
        params = value[1]  # Function parameters
        if isinstance(params, str):
            params = [params]
        body = value[2]    # Function body

        # Prepare the function's scope (whether it's global or nested in another function)
        if metadata['in_function'] and metadata['in_function'] not in OPS:
            func_name = metadata['in_function']
            outer_func_scope = metadata['functions'][func_name]['scope']

            # Layer inner function scope over outer function scope
            metadata['functions'][name] = {
                'params': params,
                'body': body,
                'scope': outer_func_scope.new_child()
            }

        else:
            # This is a global function, layer it over the global scope
            metadata['functions'][name] = {
                'params': params,
                'body': body,
                'scope': ChainMap({}),  # Initialize with an empty scope
            }

        return metadata['functions'][name]

    # For variable assignments
    value = do(value, metadata)

    # Assign to the function's local scope or globally if not inside a function
    if metadata['in_function']:
        func_name = metadata['in_function']
        # Ensure the function has a scope, initialize if missing
        if 'scope' not in metadata['functions'][func_name]:
            metadata['functions'][func_name]['scope'] = ChainMap({})

        # Assign variable to the current function's local scope
        metadata['functions'][func_name]['scope'][name] = value
    else:
        metadata['globals'][name] = value  # Assign globally if outside any function

    return value



def do_get(args, metadata: dict):
    assert len(args) == 1, "Expected exactly 1 argument: key"
    key = args[0]
    locals = metadata['locals']
    globals = metadata['globals']

    print(key, locals, globals)

    # Check in locals first
    if key in locals:
        return locals[key]

    # If inside a function, check in its scope
    if metadata['in_function'] and metadata['in_function'] not in OPS:
        func_name = metadata['in_function']
        func_scope = metadata['functions'][func_name]['scope']
        print(f"outer scope: {func_scope}")
        if key in func_scope:
            return func_scope[key]

    # Check globals
    if key in globals:
        return globals[key]

    raise KeyError(f"Variable {key} not found in locals, globals, or function scope")


def do(expr, metadata):
    # If the expression is an integer or base case, return it directly
    if isinstance(expr, int):
        return expr
    
    # Ensure that the expression is a list and not something else
    assert isinstance(expr, list), f"Expression must be a list, got {type(expr)}"
    
    # Check if the first item is a valid operation (it must be a string)
    operation = expr[0]
    assert isinstance(operation, str), f"First element of the expression must be a string operation, got {type(operation)}: {operation}"
    assert operation in OPS, f"Unknown operation {operation}"

    # Delegate to the correct operation handler
    enter_function(operation, metadata)
    res = OPS[operation](expr[1:], metadata)
    exit_function(metadata)
    return res


def enter_function(func_name, metadata):
    metadata['in_function'] = func_name
    if func_name not in metadata['functions']:
        metadata['functions'][func_name] = {}

def exit_function(metadata):
    # Clear the local scope after function execution
    if metadata['in_function'] and metadata['in_function'] not in OPS:
        func_name = metadata['in_function']
        # Remove the local scope for this function
        metadata['functions'][func_name]['scope'] = metadata['functions'][func_name]['scope'].parents

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

    #print(json.dumps(program, indent=2))

    metadata = {
        'in_function': None,
        'globals': {},  # True global variables
        'functions': {},  # Function-specific scopes
        'locals': {},  # Local variables
    }
    print("=======BEFORE========")
    pprint.pprint(metadata)
    result = do(program, metadata)
    print("=======AFTER========")
    print("Result: {}".format(result))

    pprint.pprint(metadata)



if __name__ == "__main__":
    main()