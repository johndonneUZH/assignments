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
Scope:

### Scope:
- Represents local scopes, each with its own locals dictionary.
- Supports nested scoping by allowing each Scope to have a parent scope, enabling the retrieval of variables from outer scopes if not found locally.


## Utility Functions
### **do_set()**
The function is designed to set a variable’s value within the appropriate scope (global or local) or define a new function. This function updates the program’s metadata dictionary to handle both standard variables and function definitions.
### Parameters:
#### args
- args[0] is the variable name (or function name, if a function is being defined).
- args[1] is the value or function definition.
#### metadata
- Dictionary holding the current state of global and local variables, functions, and scope context.

### Breakdown:
1. **Input Validation:** Ensures exactly two arguments are provided and that the variable name is a string.
2. **Argument Extraction:** Extracts keyword (variable name) and value from args.
3. **Function Definition Check:**
   - Checks if value is a list and starts with the keyword 'function', indicating a function definition.
   - Retrieves params (parameters) and body from value.
   - If params is a single string instead of a list, wraps it in a list, making the parameter structure uniform and consistent. This way when using do_get(), we will always expect a _list_ of parameters
   
   **Function Creation and Storage:** Calls createFunctionObject with params, body, and assigns it to metadata['functions'] under the name keyword. 
4. **Evaluating the Value (If Not a Function)**
5. **Variable Assignment:**
   Determines the scope (function’s scope or global scope) where the variable should be stored based on the in_function flag in metadata:
   - If metadata['in_function'] is set (indicating that the code is currently within a function), assigns value to keyword in that function’s local scope by accessing the specific Scope() object in metadata['functions'] dictionary.
   - If in_function is not set, assigns value to keyword in the global scope (metadata['globals']).


## **do_set()**
