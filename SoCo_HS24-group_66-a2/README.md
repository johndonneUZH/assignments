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
