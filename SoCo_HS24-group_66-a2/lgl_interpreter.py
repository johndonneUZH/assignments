import sys
import re

def program_reader():
    assert len(sys.argv) == 2, "usage: python interpreter.py code.tll"
    with open(sys.argv[1], 'r') as file:
        program = file.readlines
    return program

def evaluate_expression(expr, env):
    pass

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