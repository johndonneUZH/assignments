---
# Lexical Scoping in LGL

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
#### args
- `args[0]` is the variable name (or function name, if a function is being defined).
- `args[1]` is the value or function definition.

#### metadata
- A dictionary that tracks the current state of global and local variables, functions, and scope context.

### Breakdown:
1. **Input Validation**: Ensures that exactly two arguments are provided and that the variable name is a string.
2. **Argument Extraction**: Extracts keyword (variable name) and value from `args`.
3. **Function Definition Check**:
   - Checks if `value` is a list and starts with the keyword 'function', indicating a function definition.
   - Retrieves `params` (parameters) and `body` from `value`.
   - If `params` is a single string instead of a list, it wraps `params` in a list, ensuring consistency in parameter structure. This standardization enables `do_get()` to expect a list of parameters consistently.

   **Function Creation and Storage**: Calls `createFunctionObject` with `params` and `body` and assigns it to `metadata['functions']` under the keyword. 
4. **Evaluating the Value (If Not a Function)**:
   - If `value` is not a function, it is evaluated using `do()` to handle any expressions.
   
5. **Variable Assignment**:
   - Determines the scope (function’s scope or global scope) where the variable should be stored based on the `in_function` flag in `metadata`:
   - If `metadata['in_function']` is set, the variable is stored in that function’s local scope by accessing the specific `Scope()` object in `metadata['functions']`.
   - If `in_function` is not set, assigns `value` to the global scope (`metadata['globals']`).

### **do_call()**
The `do_call` function manages function invocation and scope handling during calls. It ensures that the correct parameters are passed, creates an isolated scope for each call, and switches back to the previous scope upon completion.

### Breakdown:
1. **Input Validation**: Ensures the function name is provided and that it is a string, preventing potential errors from misformatted calls or nonexistent functions.
2. **Function Lookup and Metadata Retrieval**: Looks up the function in `metadata['functions']` and retrieves the function’s parameters (`params`) and body (`body`). 
3. **Parameter Count Verification**: Compares the number of provided arguments to the function’s expected parameters. This is especially important to prevent execution issues in complex or nested function calls.
4. **Scope Creation for the Function Call**:
   - A new `Scope` object (`call_scope`) is created specifically for the function call, with its parent set to the function’s original scope, preserving lexical scoping:
      - This ensures that the function’s variables are isolated within this call, avoiding conflicts with variables outside the function.
      - **Function Calls**: When calling `foo()` from within `bar()`, the implementation supports passing variables from `bar()` to `foo()`, allowing shared access when necessary. The local `call_scope` for `foo()` is a child of `foo`'s original scope, maintaining independence while enabling variable inheritance if required.
      - **Nested Function Calls**: If `bar()` is a nested within `foo()` then this process will be redundant (because `bar()`'s scope is already `foo()`'s scopes's child, because of the implementation of the do_set() function) but still corrent, we will still pass the arguments in the call (if they're needed) and `bar()` will have access both to `call_scope` and `call_scope.parent`
5. **Argument Assignment in Local Scope**: Iterates through `params` and `arguments`, evaluating each argument using `do()`, and sets it in `call_scope`. By placing parameters in `call_scope`, the function isolates arguments from both global variables and other function-level variables, ensuring encapsulation.
6. **Temporary Scope Switch**:
   - Temporarily assigns `call_scope` to `func_data['scope']`, so that variable lookups within this function use this specific scope. This temporary switch:
      - Ensures the function operates within its unique scope during execution, maintaining proper isolation.
      - Allows nested functions within the body to reference local variables or, if necessary, to fall back on their parent scope according to lexical scoping rules.
7. **Caller Tracking and State Preservation**:
   - Tracks the active caller in `metadata['in_function']`. When calling a new function, `metadata['in_function']` is updated to the current function name, preserving the call stack. After the function call, `metadata['in_function']` reverts to the previous caller or to a global state if returning from a top-level call.
8. **Executing the Function Body**:
   - Calls `do()` to evaluate the function body, using `metadata` to manage any active states or context-dependent behavior. This setup lets the interpreter run the body with the correct lexical context and access to local variables.
9. **Scope Restoration**:
   - After execution, the function’s original scope is restored to `func_data['scope']`, ensuring any state or variable changes are kept within the function’s isolated call scope. This restoration prevents residual state leakage between different calls or recursive instances, allowing each function to execute independently.


### **do_get()**
The `do_get` function retrieves variables from the appropriate scope by checking the current function’s scope first. If the variable is not found, it falls back to the global scope. This process ensures efficient scope resolution, following typical lexical scoping rules.
