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

---
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
