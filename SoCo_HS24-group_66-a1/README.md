# **Vacation Booking System - Group 66**
---
## Overview
This project implements a vacation booking system using Python dictionaries to model single inheritance between a parent class and multiple child classes. In the
image below a UML Class Diagram shows the overall structure of our system

![image](https://github.com/user-attachments/assets/34b955b6-b807-4f58-a1e0-50f31afa130c)

## Libraries
In this section we explain which libraries we used and why:
- **re** | regex helped us develop features like *--select* & *searchTerm*, for example the user is allowed to type words like 'bea', 'beach', 'BEACH', 'bEAc' and this
will mactch all the objects of the class BeachResort
- **argparse** | argparse module is used to handle command-line arguments. It provides a way to define what arguments the program requires, parse those arguments, and automatically generate help and usage messages
- **inspect** | used to get the current function name for logging and debugging purposes
- **collections** | more specifically we are using *defaultdict()* to provide default values for dictionary keys that do not exist. This can simplify the code by avoiding the need to check if a key exists before accessing or modifying its value.

## Script : vacation_booking.py
### Abstract Class
**describe_package()**
- Subclasses can extend this description by appending their specific details (e.g., "includes surfing" for BeachResort). This is achieved by calling the parent class’s describe_package method from within the child class.
- This design allows subclasses to reuse the parent class’s description logic while still being able to customize it.

**calculate_cost()**
- Why NotImplementedError? Since VacationPackage is a general template, it doesn’t have enough specific details to compute the cost. Attempting to call this method directly will raise a NotImplementedError.
- This design enforces subclasses to provide their own implementation.

**mydict**
- In OOP, if we want to keep track of all the different children we created, the easiest way is to use a data structure in the parent class. This is what we also did.
- We refused to use a global dict, even if it was the easiest way, and thought that all vacations shared a common feature: the parent class.
- Given that all of them have access to this dict through inheritance, when we create a chilc vacation we can directly keep track of it by inserting it in the dict

### Children Classes
**do_*ChildClass*()** (We are referring to them generally, because all of them work exactly the same)
- We agreed on the convention that all the builders will be built by a 'do_' followed by the name of the specific class in camel case:
> do_BeachResort, do_LuxuryCruise, do_AdventureTrip, do_VacationSummary

**_description**
- We realized that the children descriptions have very little difference between them. We added a new parameter in the class definition that gives additional information about the specific class.
- This way we reuse the parent's logic to avoid code duplication, and extend the description with child-class-specific details.
- The find_method function ensures that if the parent class is changed, the child class will automatically adapt. The convention we are using is that we substitute the word *vacation* with *_description*, thus if we want to change the parent class we would need to keep this in mind

### Vacation Summaries
**do_VacationBookingSummary()**
- This is a utility function that creates a summary dictionary for a vacation booking and adheres to the same convention as the other children classes.
- **_objectName** is the name we want to give to our collection, it can be seen as the equivalent of a *destination* for a normal Child class
- **_searchTerm** is the optional search term of our Vacation Summary object. This way we can have different objects at the same time, tailored for different search words. If no search term is provided, the default value will be None and we will return ALL the created vacations.

**findSearchTerm()**
- This function searches for a specific vacation type based on a search term from the vacation dictionary.
- It extracts the search term from the vacation dictionary (_searchTerm), then retrieves all vacation summaries using find_method(VacationPackage, 'mydict').
- Afterwards we use regular expressions to match the search term (case-insensitive) with vacation type names.
- If a match is found, the function returns the matching vacation type. If no match is found, it returns None.

**calculate_total_cost()**
- We retrieve the parent's dictionary using find_method(VacationPackage, 'mydict')
- We then use it to check for vacations (depending if there is a search term or not) and we iterate trough them, using *call()* with the 'calculate_cost' function to calculate for each vacation object their cost.
- The total cost is returned as a float with two decimal places.

**extract_total_vacation_summary()**
- The logic works very similarly to calculate_total_cost, but we just call the 'describe_package' on each vacation instead
- The function also prints the total cost of the vacation (even if there’s only one vacation found).

**add_to_vacation_summaries()**
- We use the find_method to get the current vacation summaries and append the new vacation to the relevant list within the summaries.
- This function is used in *make()*, whenever a vacation is created

TO FINISH HERE
### Utility Function
**call()**
- It retrieves methods by name rather than calling them directly, enabling more flexibility.
Defensive Programming: The function validates input types to ensure robustness.
Exception Handling: It catches all exceptions and wraps them in a RuntimeError for consistent error messages.
Pros:
Flexible design: Allows adding or changing methods without altering the core logic.
Centralized error handling: Makes debugging easier.
Cons:
Performance impact: Reflection-like behavior (dynamic calls) can be slower than direct method invocations.
Limited static analysis: IDEs and linters may not detect errors in method names at compile time.


---

## Tests : test_vacation_booking.py

### Description
TODO
### Usage
TODO
