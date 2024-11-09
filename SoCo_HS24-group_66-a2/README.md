---
# Lexical Scoping in GSC

This project implements Lexical Scoping using Python to manage function calls, scoping, and metadata handling. Our approach closely follows the lecture structure by creating a dictionary-based structure to pass and track metadata, which we represent through Python classes for added flexibility and organization.

## Structure of Metadata
The structure of our _Metadata_ dictionary is shown in the UML Diagram below, providing an overview of how function calls, scope, and variables are managed.

![image](https://github.com/user-attachments/assets/d618d13a-93d5-4499-9866-3bd169ab771f)

## Choosing Classes for Scoping
Given that we had no restrictions on data structures, we utilized Python classes to represent both global and local scopes. This choice makes it easier to manage nested scopes and provides clear advantages, such as encapsulation and ease of access.
1. **Encapsulation**: Each scope is isolated and can only access variables within its own or its parent scope.
2. **Clear Scope Resolution**: By defining get and set methods, variables are located efficiently either within the local scope or its parent.
3. **Readability and Maintainability**: Using classes, the scope hierarchy is more intuitive, and modifications are easier to manage.
   
## How It Works
### GlobalScope:
- Manages all global variables accessible by all function calls.
- Has get() and set() methods to retrieve and store variables.

### Scope:
- Represents local scopes, each with its own locals dictionary.
- Supports nested scoping by allowing each Scope to have a parent scope, enabling the retrieval of variables from outer scopes if not found locally.

## Utility Functions
### **do_set()**
The `do_set` function handles variable assignment and function definition within the correct scope (global or local). It also updates the program’s metadata dictionary to track variables and function definitions effectively.

### Parameters:
- `args[0]` is the variable name (or function name, if a function is being defined).
- `args[1]` is the value or function definition.
- `metadata` is the dictionary that tracks the current state of global and local variables, functions, and scope context.

### Breakdown:
1. **Input Validation**: Ensures that exactly two arguments are provided and that the variable name is a string.
2. **Argument Extraction**: Extracts keyword (variable name) and value from `args`.
3. **Function Definition Check**:
   - Checks if `value` is a list and starts with the keyword 'function', indicating a function definition.
   - Retrieves `params` (parameters) and `body` from `value`.
   - If `params` is a single string instead of a list, it wraps `params` in a list, ensuring consistency in parameter structure. This standardization enables `do_get()` to expect a list of parameters consistently.
      ```python
       if isinstance(value, list) and value[0] == 'function':
           params = value[1]
           if isinstance(params, str):
               params = [params]
           body = value[2]
   **Function Creation and Storage**:
   Calls `createFunctionObject` with `params` and `body` and assigns it to `metadata['functions']` under the keyword. If we are currently in a function call, this means that we're dealing with a nested function, so we link these two with a parent-child relation
      ```python
        if metadata['in_function']:
            parent_func = metadata['in_function']
            child_func = createFunctionObject(params, body, metadata['functions'][parent_func]['scope'])
        else:
            child_func = createFunctionObject(params, body)

        metadata['functions'][keyword] = child_func
        return metadata['functions'][keyword]
5. **Evaluating the Value (If Not a Function)**:
   - If `value` is not a function, it is evaluated using `do()` to handle any expressions.
   
6. **Variable Assignment**:
   - Determines the scope (function’s scope or global scope) where the variable should be stored based on the `in_function` flag in `metadata`:
   - If `metadata['in_function']` is set, the variable is stored in that function’s local scope by accessing the specific `Scope()` object in `metadata['functions']`.
   - If `in_function` is not set, assigns `value` to the global scope (`metadata['globals']`).
     ```python
       if metadata['in_function']:
           func_name = metadata['in_function']
           metadata['functions'][func_name]['scope'].set(keyword, value)
       else:
           # Set the variable in the global scope
           metadata['globals'].set(keyword, value)
       return value

### **do_call()**
The `do_call` function manages function invocation and scope handling during calls. It ensures that the correct parameters are passed, creates an isolated scope for each call, and switches back to the previous scope upon completion.

### Parameters:
- `args[0]` is the function name 
- `args[1:]` are the different arguments, separated by a comma
> Notation remark for GSC: when we _call_ a function with no arguments, we call only the name (e.g. `["call", "foo"]`) while when we _set_ a function with no arguments we pass an empty list of arguments (e.g. `["set", "foo", ["function", [], [ ... ] ] ]`
- `metadata` is the dictionary that tracks the current state of global and local variables, functions, and scope context.

### Breakdown:
1. **Input Validation**: Ensures the function name is provided and that it is a string, preventing potential errors from misformatted calls or nonexistent functions.

2. **Function Lookup and Metadata Retrieval**: Looks up the function in `metadata['functions']` and retrieves the function’s parameters (`params`) and body (`body`). 
3. **Parameter Count Verification**: Compares the number of provided arguments to the function’s expected parameters. This is especially important to prevent execution issues in complex or nested function calls.
4. **Scope Creation for the Function Call**:
   - A new `Scope` object (`call_scope`) is created specifically for the function call, with its parent set to the function’s original scope, preserving lexical scoping:
      - This ensures that the function’s variables are isolated within this call, avoiding conflicts with variables outside the function.
      - **Function Calls**: When calling `foo()` from within `bar()`, the implementation supports passing variables from `bar()` to `foo()`, allowing shared access when necessary. The local `call_scope` for `foo()` is a child of `foo`'s original scope, maintaining independence while enabling variable inheritance if required.
      - **Nested Function Calls**: If `bar()` is a nested within `foo()` then this process will be redundant (`bar()`'s scope is already `foo()`'s scopes's child, because of the implementation of the do_set() function) but still corrent, we will still pass the arguments in the call (if they're needed) and `bar()` will have access both to `call_scope` and `call_scope.parent`.
   ```python
       call_scope = Scope(func_data['scope'])

5. **Argument Assignment in Local Scope**: Iterates through `params` and `arguments`, evaluating each argument using `do()`, and sets it in `call_scope`.
   ```python
    for param_name, arg_value in zip(params, arguments):
        evaluated_arg = do(arg_value, metadata)
        call_scope.set(param_name, evaluated_arg)
6. **Temporary Scope Switch**:
   - Temporarily assigns `call_scope` to `func_data['scope']`, so that variable lookups within this function use this specific scope. 
      - **Function Calls**: When calling `foo()` from within `bar()` we can have access to variables defined in `bar()` if they are passed as arguments in the call to `foo()`. This ensures the function operates within its unique scope during execution, maintaining proper isolation.
      - **Nested Function Calls**: Allows nested functions within the body to reference local variables or, if necessary, to fall back on their parent scope according to lexical scoping rules.
   ```python
    original_scope = func_data['scope']
    func_data['scope'] = call_scope

7. **Caller Tracking and State Preservation**:
   - When calling a new function, if we're already in one, we extract the caller and store it, then we change `metadata['in_function']` to make it updated to the current function name, and then we run it. After the function call, `metadata['in_function']` reverts to the previous caller or to a global state if returning from a top-level call. This make sure we're preserving the call stack
   ```python
    caller_func = None
    if metadata['in_function'] != func_name:
        caller_func = metadata['in_function']

    enter_function(func_name, metadata)
    result = do(body, metadata)
    exit_function(metadata)

8. **Scope Restoration**:
   - After execution, the function’s original scope is restored to `func_data['scope']`, ensuring any state or variable changes are kept within the function’s isolated call scope. This restoration prevents residual state leakage between different calls or recursive instances, allowing each function to execute independently.
   ```python
    if caller_func:
        metadata['in_function'] = caller_func

    # Restore the original scope after execution
    func_data['scope'] = original_scope
    return result

### **do_get()**
The `do_get` function retrieves variables from the appropriate scope by checking the current function’s scope first. If the variable is not found, it falls first back to the parent scope (only if it's a nested function) else to the global scope. This process ensures efficient scope resolution, following typical lexical scoping rules.

## Helper Functions
### Helper Functions Explanation

1. **createFunctionObject**
   - **Purpose**: This function creates a new function object, encapsulating details necessary for the interpreter to manage each function’s parameters, body, and scope.
   - **Returns**: A dictionary representing the function object, containing:
     - `'params'`: The function's parameters.
     - `'body'`: The function’s body to execute.
     - `'scope'`: A `Scope` instance initialized with the `parent` scope (if provided), which preserves lexical scoping by linking this function’s scope to its parent (only if it's a nested function) else the parent will be the global scope.

2. **enter_function**:
   - **Purpose**: Updates the interpreter’s metadata to mark the start of a function execution.
   - **Behavior**: Sets `metadata['in_function']` to `func_name`, indicating the interpreter is actively executing this function.
   - **Usage**: Used at the beginning of a function call to track the active function, aiding in managing function nesting and lexical scoping.

3. **exit_function**:
   - **Purpose**: Clears the active function state in `metadata`, marking the end of a function call.
   - **Behavior**: Sets `metadata['in_function']` to `None`, indicating the interpreter has exited the current function context.
   - **Usage**: Called at the end of a function execution, ensuring the interpreter correctly resets its state, supporting seamless transitions between function calls.

---
# Infix Operations in GSC

Our languge can "call" functions using two forms, the first one is inside a dictionay stating the name of the function to call and the parameters or by giving a string that contains a special character that indicates an arimetical operation such as '+', '-' and so on. Both types of calls are evaluated with the `do()` recursively.

### **do()**
The `do()` function is the main evaluation function, based on the type of the argument `expr`: integers, str, lists.

### Parameters:
- `expr` is the function to ve evaluates, can be in "any" form as long it is lexically correct.
- `metadata` is the dictionary that tracks the current state of global and local variables, functions, and scope context.

### Breakdown:
1. **Input Validation**: Ensures that the `expr` is eaither a number, a string, a list of one value (which is a string) or a list with the first value as a string but with more values. 

2. **Returnign values with if conditions**: Checks the type of `expr`:
     - if `expr` is an int, it is the base case and returs the same number.
     - if `expr` is a string, it returns the value after `expr` is evaluated with `evaluate_expression()`
     - if `expr` is a list, has a length of 1 and that value is a string then  `expr` is evaluated with `evaluate_expression()`, this is important for nested expressions and decides the order it is decomposed.
     - if `expr` is a list, and the first value is a str, then the operation is found and it is evaluated with the help of the OPS dictionary that contains all the functions that are called in the traditional way.
      
3. **Defencing codign**:
      - if `expr` is not an int nor a str nor a list, it raises an error.
      - if the operation is not in OPS raises an error as a not known operation.

### `OPS` and `do()_` functions:

We decide to have a dictionary OPS so the functions can be called dynamically and it is easy to scale. 

### Breakdown:

1. **Creation of OPS**: OPS is a dictionary comprehension that loops through the global variables looking for the functions that start with do_. The keys are the name without the "do_" so it is easier to call in the LGL and the value is the function itself.
   
2. **`do_()` functions**.
      - These functions take arguments and metadata as arguments. Depending on the function first asserts the number of arguments, if different it raises an error.
        ```python
         def do_multiplication(args, metadata):
              assert len(args) == 2

      - Then separate the left and the right values as left and right by setting variables inside the `do()_` functions. However it is not set that easily, instead of just setting the variables with the value, it calls the `do()` function with the value, this is the recursive part, as it allows nested expressions and will just return a value when all the operations inside the left or right are computed.
        ```python
        left = do(args[0], metadata)
        right = do(args[1], metadata)
        
      - Finally, it returns the result of the expression with the left and the right value.
        ```python
        return left * right

### `evaluate_expression()` :

### Breakdown:

A general view of this function and its helpers are: 
    - First: tries to turn to get a value calling  `evaluate_gets_in_expression()`, which at the same time calls `do_get()`
    - Second: looks for the operators inside the expression, but if the operator is inside a list (brackets) it ignores it with the help of the in-defined function `find_bracket_ranges()`, so the operations are executed in the right order. 
    - Third: if the operator is not inside brackets, the expression will be divided into three, a right part a left part, and the operator. The arguments are put in a list and the `solve_expression()` function is called.


- #### `def evaluate_gets_in_expression()`:
   -    Breakdown: This function scans through a complex expression to identify and replace any instances of `['get', 'variable_name']` with the actual value of that variable. It’s useful for substituting variables within an expression before performing further evaluation. It gets the value by looking at a pattern that includes the word get and if there is one it uses the `do_get` to obtain the value of the variable.
   -    Parameters: it receives an expression `expr` and the `metadata` dictionary, where the variable will be found.
   -    Output: It returns a modified version of `expr` with the corresponding value.
- #### `find_bracket_ranges()`:
     - Breakdown: This function identifies ranges of characters within an expression that are enclosed in brackets `([])`. It’s designed to locate nested or standalone brackets and return their start and end positions, which is useful for determining if parts of an expression are inside brackets or not. It is inspired by pushdown automata. A "stack" is used to track the positions of opening brackets.
     - Internal workflow logic: For each character, if it’s an opening bracket ([), its index is pushed onto the stack. If it’s a closing bracket (]), the last opening bracket index is popped from the stack and paired with the current index to form a tuple representing the range of the bracketed section.
     - Parameters: It receives one parameter `expr`, which is a string representing the expression in which we want to find bracket ranges.
     - Output: It returns a list of tuples `ranges`, where each tuple contains the start and end indices of a bracketed segment in expr. For example, an output of `[(2, 5), (10, 15)]` means there are two bracketed sections: one from index 2 to 5 and another from 10 to 15.
- #### `is_inside_brackets()`:
     - Breakdown: This function checks whether a given index is located within any of the bracketed ranges in an expression.
     - Parameters:
         - `index`: An integer representing the position in the expression we want to check.
         - `ranges`: A list of tuples where each tuple contains the start and end indices of bracketed sections, as returned by `find_bracket_ranges()`.
      - Output: It returns `True` if `index` is within any of the provided ranges, meaning it’s inside a set of brackets. Otherwise, it returns False.

### `solve_expression()` and helper functions:

### Breakdown:
The `solve_expression()` function is designed to solve arithmetical expressions by applying a specified operator to two arguments. This is particularly useful for handling operations within an expression after the main parts (left, operator, right) have been identified with the `evaluate_expressio()`.

   - Convert and Evaluate Arguments: It converts the two arguments (left and right) from a potential string format to their actual values using `convert_value()`. Then, it evaluates each argument by calling `do()` recursively so if the left or right part is rather a list it will be evaluated first and the result would be commutative until it returns a number.
   - Operator Lookup: It uses a dictionary of operators `OPERATORS`, which maps operation symbols (like +, -, *, etc.) to their corresponding functions from Python’s operator module, it could not be done dynamically since special characters such as '+' cannot be used in functions names.
   - Operation Execution: Using OPERATORS, it applies the correct operator function to the left and right arguments.
   - Return Result: It returns the result of the operation if the operator is valid. Otherwise, it raises an error for unsupported operators.
   - Parameters:
      - `args`: A list containing two arguments representing the left and right sides of the binary expression that can be either a number, a string, or a list with a string inside.
      - `operation`: A string indicating the operation to be performed (e.g., '+', '-', '*', etc.).
      - `metadata`: The dictionary holding the current state, including variables and scopes.
   - Output:
It returns an integer after applying `operation` to the evaluated left and right arguments.
   
   - #### `convert_value()`:
      - Breakdown: This helper function converts a string value into an integer or a list, depending on its format. It’s useful for handling arguments that may need to be evaluated as numbers or lists.
      - Parameters:
         - val: A string representing the value to be converted. It can potentially represent an integer, a string wrapped in a list format, or an actual list in string form.
      - Output:
         - Returns an integer if `val` can be converted to one.
         - Returns a list if `val` represents a single string element within a list or if it’s a list structure that ast.literal_eval can parse. Useful for recursivity as it will be called by `do()`
         - Raises a ValueError if `val` cannot be interpreted as either an integer or a list.

# Tracing in GSC

First we check in main() if there is a need for a trace_file. If needed, one is created and a csv header with column names are written. The file path is kept in the metadata. This enables tracing based on depending on the availability of a trace_file.

This project implements a tracing system that when a function is called, it logs the calls and their timing and entry and exit points. It is implemented with Python's decorator, here with "@trace".

### **trace()**
In the trace function we use a wrapper. If there exists a trace_file, an unique call_id is created. The uniqueness is guaranteed with the funcation secrets.token_hex(3). It records the entry time. with datetime.now(), as to guarantee high-precision timing. The event "start" is logged. Next, the input function is executed. The exit time is recorded and the event "stop" is logged.


---
# Reporting.py
This file analyzes trace logs generated from the LGL interpreter. It produces a summary report of each function and its' performance.

### **summary_stats()**
    This function reads the csv trace file from the lgl_interpreter and organzises the data by their function name. A dictionary is initialized. It distincts the different calls through their call ID, matching start and stop events in the trace logs. If the trace file is faulty, a ValueError is raised.

### **calculate_stats()**
    The function calculate_stats() processes the collected data of summary_stats(). It caluclates the number of calls per function, total execution time in millieseconde and the average exection per call. As to not have duplicates, a list of tuples is returned with the calculated statistics.

### **display()**
    This function displays the statistics that were caluclated in calculate_stats. THe output is fomatted with the use of PrettyTable.
