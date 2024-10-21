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

**remove_from_vacation_summaries()**
- We use the find_method to get the current vacation summaries and remove the selected vacation from any vacation type in the relevant list within the object vacation_summaries.
- The function relies on defaultdict structure so it can safely access the list of vacations by type without needing to check for the existence of a list. 

  
### Utility Functions
**call()**
- It retrieves methods by name rather than calling them directly, enabling more flexibility.
Defensive Programming: The function validates input types to ensure robustness.
Exception Handling: It catches all exceptions and wraps them in a RuntimeError for consistent error messages.

   - Pros:
     
        Flexible design: Allows adding or changing methods without altering the core logic.  
        Centralized error handling: Makes debugging easier.  

   - Cons:
     
        Performance impact: Reflection-like behavior (dynamic calls) can be slower than direct method invocations.  
        Limited static analysis: IDEs and linters may not detect errors in method names at compile time.


**find_method()**
- It recursively retrieves a method from a class by searching its hierarchy, so if the method is not found in the current class, it looks for the method in the parent class.
  Defensive Programming: The function ensures that method names are searched across the parent-child relationship, avoiding potential issues where methods might be missed due to class inheritance.
  Exception Handling: If the method is not found after traversing the entire class hierarchy, it raises a NotImplementedError.
  
   - Pros:
     
        Supports class hierarchy: By looking into the parent's classes, it ensures that even the inherited methods can be accessed and makes it easier to retrieve methods from subclasses without explicitly navigating the hierarchy.  

   - Cons:
     
        Performance impact: The fact that it traverses the class hierarchy recursively, introduces performance costs.
  
**make()**
- This function serves as the creator, that dynamically creates instances of different vacation types (eg. BeachResort, LuxuryCruise). It uses the provided vacation type information to construct the object with the given parameters and adds it to the vacation summaries.
  Defensive Programming:  It validates both the class of the vacation package and the input parameters, ensuring that invalid input or incorrect types are caught.
  Exception Handling: The function checks for invalid argument counts and incorrect vacation types, raising informative ValueError exceptions.
   - Pros:
     
        The creator pattern: It is intuitive and easy to have just one big make() function that allows different vacation types to be created through a single interface. It is also done so that it can be easily extended for new vacation types.   

   - Cons:
     
        Rigid checks for functions and errors: If the signature of vacation constructures changes, it may require to modify the function make(), also the strict validation might lead to extensive exception handling code, which could become harder to maintain if more vacation types are added.
---

## Tests : test_vacation_booking.py

### Description

- test_calculate_cost_BeachResort_with_surfing()
  - Description: This test verifies that the cost calculation for a BeachResort vacation includes the additional cost of surfing when the includes_surfing argument is set to True. It checks whether the total cost is correctly calculated by multiplying the daily rate by the duration and adding the surfing cost.
  - Relevance: This test ensures that additional activities, like surfing, are factored into the cost calculation for beach vacations. It verifies the correctness of how extra features affect the overall vacation cost.


- test_calculate_cost_BeachResort_without_surfing ()

  - Description: This test is verfies the cost calculation for a BeachResort vacation that does not include surfing. It checks if the programm still calculates the costs correctly if includes_surfing argument is set to False. It should simply calculate the cost by multiplying the duration of the vacation by the daily rate.
  - Relevance: This test ensures that the code runs smoothly for BeachResort vacations that do not include surfing. Like the test above, it confirms the correctnes of cost calculation of BeachResort.


- test_calculate_cost_BeachResort_missing_argument()
  - Description: This test is designed to check how the system handles the case where a required argument (includes_surfing) is missing when creating a BeachResort vacation. It expects the test to raise a ValueError since the input is incomplete.
  - Relevance: Ensures robust error handling by verifying that the system throws an appropriate error when required arguments are missing, preventing unexpected behavior or crashes.


- test_calculate_cost_AdventureTrip_hard()
  - Description: This test checks the cost calculation for an AdventureTrip vacation when the difficulty_level is set to "hard". It verifies that the cost is doubled for harder trips, as specified by the business rules.
  - Relevance: This test ensures that difficulty levels are correctly applied to the cost calculation, validating the system’s ability to handle pricing adjustments based on vacation difficulty.


- test_calculate_cost_AdventureTrip_easy():
  - Description: This test controls if the calculation with difficulty_level "easy" is computed correctly for an AdeventureTrip. The cost should simply be computed by multiplying the duration of the vacation and the cost per day rate.
  - Relevance: This test ensures that the difficulty level "easy" is also correctly apllied. This makes sure that our programm handles different levels of difficulty as it should.


- test_AdventureTrip_missing_argument():
  - Description: This test is designed to ensure that the cost calculations for AdventureTrip are not computed, if  the difficulty_level argument is not provided. It demonstrates us that an Error Message is outputed correctly.
  - Relevcance: It demonstrates that the programm realises that there is an input missing and gives an accurate Error response. Together with the two tests before, it concludes that the cost calculation for AdventureTrip is accurately computed, given the arguments are provided correctily.


- test_calculate_cost_LuxuryCruise_has_private_suite()
  - Description: This test verifies that the cost calculation for a LuxuryCruise vacation correctly includes the surcharge for having a private suite. The test checks whether the total cost is increased by 1.5x when has_private_suite is set to True.
  - Relevance: It ensures that luxury options, such as private suites, are properly factored into the cost calculation, providing correctness in pricing for premium offerings.


- test_calculate_cost_LuxuryCruise_no_private_suite() 
  - Description: This test ensures that when has_private_suite is set to False the calculation for a LuxuryCruise vacation is adjusted correspondingly. The cost should only be computed with the duration of the vacation and rate per day.
  - Relevance: It checks that the cost is computed correctly, even when the has_private_suite argument is set to False, ensuring that without a private suite, the costs are not increased.


- test_LuxuryCruise_missing_argument()
  - Description: This test demonstrates how the cost computation for a LuxuryCruise behaves when the argument has_private_suite is forgotten. The output should give us an error mesage.
  - Relevance: Together with the two test before, it is ensured that the cost for a LuxuryCruise is always computed correctly, as the programm outputs a ValueError if the argument is missing.


- test_calculate_VacationBookingSummary
  - Description: This test checks the functionality of the VacationBookingSummary class by creating a summary of multiple vacation types (BeachResort, AdventureTrip, and LuxuryCruise). It verifies that the total cost of all vacations is calculated correctly.
  - Relevance: Ensures that the system can handle multiple vacation packages at once and provides a correct aggregate cost. This is important for summarizing and calculating the total cost of vacations across various types and to prove the functionality of the function summary.

- test_calculate_cost_LuxuryCruise_has_private_suite_failure()
  - Description: It checks if the the tests above do not run wich a "SUCCESS" output with any given integer. The solution has to be correct. This test is designed to fail.
  - Relevance: This test is an addition to the the tests of the LuxuryCruise above given, as it demonstrates that not any integer given is taken as correct, it does indeed have to match the calculations. This insures that not any costs for LuxuryCruise are computed correctly.


- test_calculate_cost_AdventureTrip_easy_failure()
  - Description: This checks if the output given from running the cost function on an AdventureTrip vacation does not simply output any integer. This test should fail.
  - Relevance: Similarly to the test above, it ensures that the tests that were executed on cost computation of an AdventureTrip vacation do not compute correct for any given integer. Furthermore, it ensures that cost are not falsely doubled since the difficulty_level attribute is set to "easy".


- test_calculate_cost_BeachResort_with_no_surfing_failure()
  - Description: This test demonstrates that when the cost is calculated for a BeachResort vacation, it gives us a correct integer and not just any. The ouput here should be "FAIL".
  - Relevance: As the two test did before this one, it ensures that the tests that were perfomed on the cost calculation of a BeachResort vacation do not simply accept any integer as true. In addition to this, it checks that the cost was not falsely computed for vacation including surfing.


- test_calculate_VacationBookingSummarys_failure()
  - Description: Here we ensure that the test given do not just compute just the fist vacation given but all of them. Furthermore we prove that the tests above did not just access the test as successfull for any integer given.
  - Relevance: This test makes sure that the test executed above is not just passed for any integer. It demonstrates us that the calculation for the cost of all vacations together is runs smoothly.


- test_make_AdventureTrip_medium_error()
  - Description: Here we ensure that an error mesage is ouputed if an arbitrary difficulty_level is given.
  - Relevance: This test is very important, as it demonstrates that an AdventureTrip is not made and therefore not described if an argument is not given in the defined way.


- test_calculate_cost_with_invalid_days()
  - Description: In this test we demonstrate that the cost of a vacation is not calculated if the number of vacation days is negative. This test should have the output in form of "ERROR".
  - Relevance: This shows, that the the programm does not execute for inputs that do not make sense, here in the example of a negative vacation duration.


- test_calculate_VacationBookingSummary_not_existent_vacationtype()
  - Description: This test ensures that no cost is calculated for the summary of vacations, whilst one of them is faulty. This is due to the fact that a vacation is not made with an inexistent vacation type. This test should have an error as output.
  - Relevance: This shows us that functions like calculate_cost() and make() do not run if the vacation_class attribut is not correctly defined.


### Utility Functions

**pretty_printer()**
  - This function formats and prints the results of each test, including details such as test name, status (SUCCESS, FAIL, ERROR), actual vs expected output, and execution time.

**assert_equals()**
  - assert_equals() compares the actual output of a test with the expected output. If they match, the test is marked as a success; otherwise, it's marked as a failure or error. It also tracks the time taken to run the test. Error is marked when an exception occurs during the test.

**clear_mydict()**
  - Given that all the children classes share the same parent dictionary, when we create vacations the test they are getting added to 'mydict'
  - This utility function clears the vacation summaries (mydict) before each test to ensure that previous tests don’t affect the current test, especially for tests regarding VacationBookingSummary

**run_tests()**
  - This function identifies and runs all test functions in the script. It can also run a subset of tests based on a pattern, making it flexible for targeted testing.
  - It was built so that all tests could run without calling them one by one, it will run by main when compiled.
  - It requires a pattern to find the tests, but if no pattern is provided it will take that value as none and will execute all tests.
  - It will count how many tests were run, if no tests are run it asserts an error because it would mean that the pattern was not found and no tests were executed.
  - The library re is imported to be able to run tests even if the pattern is not 100% exact. For example: "Bea" would run all the tests with "beach". 

**parse_arguments()**
  - This function parses command-line arguments to determine if a specific test pattern is provided by the user. If a pattern is provided, the value is saved and will be then sent to the function run_tests()
  - When python -h is called, a description of how to use the command line is shown to help the users who are not familiar with the usage.
  - The pattern is then stripped and turned into a string so it can be easily worked with.
  - Example of how to use the command line: python test_script.py --select Beach

---

## General Remarks
### Project Structure
- While setting up the repository on GitLab, we discovered the option to mirror a repository from GitHub. Since we were already familiar with GitHub, we chose to leverage that experience and focus on building a basic CI/CD pipeline. This approach allowed us to simulate a typical coding workflow in a professional environment. As a result, both our GitHub and GitLab usernames are visible in this repository.
- Our workflow follows these steps:
1. Pull the latest changes from the main branch locally.
2. Create a new branch to work on a feature or task.
3. Commit the changes to the feature branch.
4. Submit a merge request to integrate the feature into the main branch.
5. Peer review: Another team member reviews the merge request, providing feedback if necessary (with the option to approve or reject).
6. Merge and deploy: Once approved, the feature is merged and successfully integrated.

## AI Integration
- We leveraged GitHub Copilot's autocomplete feature to generate detailed code comments. This allowed us to maintain clear, comprehensive documentation within the codebase while streamlining our development process.
