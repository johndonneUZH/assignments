import sys
import re

def program_reader():
    assert len(sys.argv) == 2, "usage: python interpreter.py code.tll"
    with open(sys.argv[1], 'r') as file:
        program = file.readlines
    return program

def evaluate_expression(expr, env):
    pass

def do_addieren(env, args):
    assert len(args) == 2
    left = do(env, args[0])
    right = do(env, args[1])
    return left + right
def do_subtrahieren(env, args):
    assert len(args) == 2
    left = do(env, args[0])
    right = do(env, args[1])
    return left - right

def do_multiplizieren(env, args):
    assert len(args) == 2
    left = do(env, args[0])
    right = do(env, args[1])
    return left * right

def do_dividieren(env, args):
    assert len(args) == 2
    left = do(env, args[0])
    right = do(env, args[1])
    assert right != 0, "Error: división por cero"
    return left / right

def do_betrag(env, args):
    assert len(args) == 1
    val = do(env, args[0])
    return abs(val)

def do_setzen(env, args):
    assert len(args) == 2
    assert isinstance(args[0], str)
    var_name = args[0]
    value = do(env, args[1])
    env[var_name] = value
    return value

def do_bekommen(env, args):
    assert len(args) == 1
    assert isinstance(args[0], str)
    assert args[0] in env, f"Variable name {args[0]} not found"
    value = env[args[0]]
    return value

def do_sequenz(env, args):
    assert len(args) > 0
    result = None
    for expr in args:
        result = do(env, expr)
    return result


OPERATIONS =  {
    "addieren": do_addieren,
    "substraieren": do_subtrahieren,
    "multiplizieren": do_multiplizieren,
    "dividieren": do_dividieren,
    "betrag": do_betrag,
    "setzen": do_setzen,
    "bekommen": do_bekommen,
    "sequenz": do_sequenz
}
    
def do(env, expr):
    if isinstance(expr, list):
        operation = expr[0]
        assert operation in OPERATIONS, f"Operation {operation} not implemented"
        return OPERATIONS[operation](env, expr[1:])
    
    

def main():
    env = {} #empty enviroment
    program = program_reader() 
    result = do(env, program)
    print(result)
    
    
if __name__ == "__main__":
    main()