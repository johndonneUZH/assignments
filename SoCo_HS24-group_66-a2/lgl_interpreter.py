import argparse, json, re, ast, operator, csv
from datetime import datetime
import secrets

##############################################
################## SCOPES ####################
##############################################

class GlobalScope:
    def __init__(self):
        self.globals = {}

    def get(self, name):
        if name in self.globals:
            return self.globals[name]
        else:
            raise NameError(f"Variable {name} not found in the global scope")

    def set(self, name, value):
        self.globals[name] = value

    def __str__(self):
        return str(self.globals)

GLOBAL_SCOPE = GlobalScope()

class Scope:
    def __init__(self, parent=None):
        self.locals = {}
        self.parent = parent if parent else GLOBAL_SCOPE

    def get(self, name):
        if name in self.locals:
            return self.locals[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise NameError(f"Variable {name} not found")

    def set(self, name, value):
        self.locals[name] = value

    def __str__(self):
        return str(self.locals)

##############################################
############### DECORATOR ####################
##############################################

def trace(func):
    def wrapper(args, metadata):
        func_name = args[0]  # Get the specific function name from arguments

        # If trace file is provided, write the function call event to the file
        if metadata['trace_file']:
            call_id = secrets.token_hex(3) # Generate a unique call ID for each function call
            start_time = datetime.now() # Get the current timestamp
            # Write the function call event to the trace file
            with open(metadata['trace_file'], mode="a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([call_id, start_time, func_name, "start"])

        # Call the function and get the result
        result = func(args, metadata)

        if metadata['trace_file']:
            end_time = datetime.now() # Get the current timestamp
            with open(metadata['trace_file'], mode="a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([call_id, end_time, func_name, "stop"])
        # Return the result of the function call
        return result
    # Return the wrapper function
    return wrapper

##############################################
############# UTILITY FUNCTIONS ##############
##############################################

def do_set(args, metadata):
    assert len(args) == 2, "Expected exactly 2 arguments: name and value"
    assert isinstance(args[0], str), f"Variable name must be a string, got {type(args[0])}"

    keyword, value = args

    # Check if the value is a function definition
    if isinstance(value, list) and value[0] == 'function':
        params = value[1]
        if isinstance(params, str):
            params = [params]
        body = value[2]

        # If we're already inside a function, create a nested function
        if metadata['in_function']:
            parent_func = metadata['in_function']
            child_func = createFunctionObject(params, body, metadata['functions'][parent_func]['scope'])
        # Otherwise, create a global function
        else:
            child_func = createFunctionObject(params, body)

        # Store the function in the metadata
        metadata['functions'][keyword] = child_func
        return metadata['functions'][keyword]

    # Evaluate the value if it's an expression
    value = do(value, metadata)
    
    # If inside a function, set the variable in the function's scope
    if metadata['in_function']:
        func_name = metadata['in_function']
        metadata['functions'][func_name]['scope'].set(keyword, value)
    # Else we set the variable in the global scope
    else:
        metadata['globals'].set(keyword, value)
    return value

@trace
def do_call(args, metadata):
    assert len(args) >= 1, "Expected at least one argument"
    assert isinstance(args[0], str), "First argument must be the function name"

    func_name = args[0]
    arguments = args[1:] if len(args) > 1 else []

    if func_name not in metadata['functions']:
        raise NameError(f"Function {func_name} not found")

    func_data = metadata['functions'][func_name]
    params = func_data['params']
    body = func_data['body']

    if len(params) != len(arguments):
        raise TypeError(f"Function {func_name} expects {len(params)} arguments but got {len(arguments)}")

    # Create a new scope for the function call with the caller's scope as its parent
    call_scope = Scope(func_data['scope'])

    # Set function arguments in this new local scope
    for param_name, arg_value in zip(params, arguments):
        evaluated_arg = do(arg_value, metadata)
        call_scope.set(param_name, evaluated_arg)

    # Temporarily switch the function’s scope to this new scope
    original_scope = func_data['scope']
    func_data['scope'] = call_scope

    # If the function is called from another function, update the caller function name
    caller_func = None
    if metadata['in_function'] != func_name:
        caller_func = metadata['in_function']

    enter_function(func_name, metadata) # Enter the function
    result = do(body, metadata) # Execute the function body
    exit_function(metadata) # Exit the function

    if caller_func: # Restore the caller function name in metadata
        metadata['in_function'] = caller_func

    # Restore the original scope after execution
    func_data['scope'] = original_scope
    return result

def do_get(args, metadata):
    assert len(args) == 1, "Expected exactly 1 argument: name"
    assert isinstance(args[0], str), f"Variable name must be a string, got {type(args[0])}"
    keyword = args[0]

    # Check active function scope first, then global
    if metadata['in_function']:
        active_func = metadata['in_function']
        active_scope = metadata['functions'][active_func]['scope']
        try:
            return active_scope.get(keyword)
        except NameError:
            pass
    
    return metadata['globals'].get(keyword)

def do(expr, metadata):
    if isinstance(expr, int):
        return expr

    if isinstance(expr, str):
        return evaluate_expression(expr, metadata)

    assert isinstance(expr, list), f"Expected expr to be a list, got {type(expr)}: {expr}"


    if len(expr) == 1 and isinstance(expr[0], str):
        return evaluate_expression(expr[0], metadata)
    
    operation = expr[0]
    if operation in OPS:
        return OPS[operation](expr[1:], metadata)
    else:
        raise ValueError(f"Unknown operation: {operation}")
    
##############################################
############# HELPER FUNCTIONS ###############
##############################################

def createFunctionObject(params, body, parent=None):
    return {
        'params': params,
        'body': body,
        'scope': Scope(parent),
    }

def enter_function(func_name, metadata):
    metadata['in_function'] = func_name
 
def exit_function(metadata):
    metadata['in_function'] = None

def evaluate_gets_in_expression(expr, metadata):
    pattern = re.compile(r'\[\s*\'get\'\s*,\s*\'([^\']+)\'\s*\]')
    while True:
        match = pattern.search(expr)
        if not match:
            break
        var_name = match.group(1)
        value = do_get([var_name], metadata)
        # Replace the 'get' expression with its value in the expression
        expr = expr[:match.start()] + str(value) + expr[match.end():]
    return expr


def convert_value(val):
    try:
        return int(val) # First, try to convert the value to an integer
    except ValueError:
        try:            
            inner = val.strip()[1:-1].strip()
            if inner.startswith("'") and inner.endswith("'"): # Checks if the string is inside a list and turns into a string so can be further analyzed
                inner_str = inner[1:-1] 
                result = [inner_str]
                return result # Tries to see if it is a list inside a string and turns into a list so can be further analyzed
            else: # Checks if the list is already in list format.
                try:
                    result = ast.literal_eval(val)
                    if isinstance(result, list):
                        return result #Tries to see if it is a list
                    else:
                        raise ValueError(f"'{val}' is neither a number nor a list.")
                except:
                    raise ValueError(f"'{val}' is neither a number nor a list.")
        except (ValueError, SyntaxError):
            raise ValueError(f"'{val}' is neither a number nor a list.")


def solve_expression(args, operation, metadata):
    assert len(args) == 2, f"Expected two arguments, got {len(args)}"
    left = do(convert_value(args[0]), metadata) # Convert the arguments to values (numbers or nested expressions)
    right = do(convert_value(args[1]), metadata)

    # We do it this way to avoid using eval() and avoiding else if statements
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
    # Check if the operator is supported
    if op_func is None:
        raise ValueError(f"Unsupported operator: {operation}")
    return op_func(left, right)

def evaluate_expression(expr, metadata):
    expr = evaluate_gets_in_expression(expr, metadata)
    
    def find_bracket_ranges(expr): # Function to find nested [] if they are in the left side of the operator.
        stack = []  
        ranges = []
        for i, char in enumerate(expr):
            if char == '[':
                stack.append(i) # We decided to use a stack inspired by pushdowns automatas, to check if im inside a nested []
            elif char == ']':
                start = stack.pop()
                ranges.append((start, i))
        return ranges

    def is_inside_brackets(index, ranges):
        for start, end in ranges:
            if start < index < end:
                return True
        return False
    
    bracket_ranges = find_bracket_ranges(expr) # Return the indixes of the [] to check if the operator is inside or if it is okey to do the funciton.
    pattern = re.compile(r'([+\-*/]|and|or|xor)', re.IGNORECASE) # look for operators.

    for match in pattern.finditer(expr): # Look for operators outside the []
        op = match.group(0) # Get the operator
        index = match.start() # Get the index of the operator
        if not is_inside_brackets(index, bracket_ranges): # Cheecks that the operator is outside the []
            left = expr[:index].strip()
            right = expr[index + len(op):].strip()
            args = [left, right]
            return solve_expression(args, op, metadata)


##############################################
############## OPERATIONS ####################
##############################################

def do_sequence(args, metadata):
    assert len(args) > 0
    result = None
    for expr in args:
        result = do(expr, metadata)
    return result

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

def do_division(args, metadata):
    assert len(args) == 2
    left = do(args[0], metadata)
    right = do(args[1], metadata)
    assert right != 0, "Error: division by 0"
    return left // right

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

def do_power(args, metadata):
    assert len(args) == 2
    num = do(args[0], metadata)
    power = do(args[1], metadata)
    return num ** power

# RETRIEVE OPERATIONS DINAMICALLY AND STORE THEM IN A DICTIONARY
# {operation_name: function}
OPS = {
    name.replace("do_", ""): func
    for (name, func) in globals().items()
    if name.startswith("do_")
}

##############################################
############## MAIN FUNCTION #################
##############################################

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Process a code file and an optional trace log file.',
        epilog='Example usage: python lgl_interpreter.py code.gsc --trace trace_file.log',
        usage='lgl_interpreter.py code_file [-h] [--trace TRACE_FILE]'
    )
    parser.add_argument('code_file', help='Path to the code file (e.g., code.gsc)')
    parser.add_argument(
        '--trace', dest='trace_file', help='Path to the optional trace log file (e.g., trace_file.log)'
    )

    args = parser.parse_args()
    
    # Check if the trace file is provided
    trace_file = args.trace_file
    if trace_file:
        with open(trace_file, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'timestamp', 'function_name', 'event'])
    
    with open(args.code_file) as source:
        program = json.load(source)
    
    # Initialize metadata
    metadata = {
        'in_function': None,
        'globals': GLOBAL_SCOPE,
        'functions': {},
        'trace_file': trace_file
    }

    print('BUILT-IN FUNCTIONS | ' + ', '.join(OPS.keys()))
    result = do(program, metadata)
    print('USER-DEFINED FUNCTIONS | ' + ', '.join(metadata['functions'].keys()))
    print('RESULT |', result)

if __name__ == "__main__":
    main()
