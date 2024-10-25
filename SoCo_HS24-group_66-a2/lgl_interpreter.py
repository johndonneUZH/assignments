import sys, json, pprint

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

def createFunctionObject(params, body, parent=None):
    return {
        'params': params,
        'body': body,
        'scope': Scope(parent),
        'callable': True
    }

def do_set(args, metadata):
    assert len(args) == 2, "Expected exactly 2 arguments: name and value"
    assert isinstance(args[0], str), f"Variable name must be a string, got {type(args[0])}"

    keyword, value = args

    if isinstance(value, list) and value[0] == 'function':
        params = value[1]
        if isinstance(params, str):
            params = [params]
        body = value[2]

        metadata['functions'][keyword] = createFunctionObject(params, body)
        return metadata['functions'][keyword]

    value = do(value, metadata)
    # If inside a function, set the variable in the function's scope
    if metadata['in_function']:
        func_name = metadata['in_function']
        metadata['functions'][func_name]['scope'].set(keyword, value)
    else:
        # Set the variable in the global scope
        metadata['globals'].set(keyword, value)
    return value

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

    caller_func = None
    if metadata['in_function'] != func_name:
        caller_func = metadata['in_function']

    enter_function(func_name, metadata)
    result = do(body, metadata)
    exit_function(metadata)

    if caller_func:
        metadata['in_function'] = caller_func

    # Restore the original scope after execution
    func_data['scope'] = original_scope
    return result

def enter_function(func_name, metadata):
    metadata['in_function'] = func_name

def exit_function(metadata):
    metadata['in_function'] = None

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

    assert isinstance(expr, list)
    operation = expr[0]
    assert operation in OPS, f"Unknown operation {operation}"

    return OPS[operation](expr[1:], metadata)

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

def do_power(args, metadata):
    assert len(args) == 2
    num = do(args[0], metadata)
    power = do(args[1], metadata)
    return num ** power

OPS = {
    name.replace('do_', ''): func 
    for name, func in globals().items() 
    if name.startswith('do_')
}

def main():
    assert len(sys.argv) == 2   # Usage: python lgl_interpreter.py code.gsc
    with open(sys.argv[1]) as source:
        program = json.load(source)

    pprint.pprint(OPS)

    metadata = {
        'in_function': None,
        'globals': GLOBAL_SCOPE,
        'functions': {},
    }

    result = do(program, metadata)
    print('===============================\n')
    print("Result:", result)
    print('===============================\n')
    pprint.pprint(metadata)
    print('===============================\n')


if __name__ == "__main__":
    main()