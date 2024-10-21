from vacation_booking import call, make, find_method, VacationPackage, BeachResort, AdventureTrip, LuxuryCruise, VacationBookingSummary
from time import perf_counter
import inspect, argparse, re

# --------------------------------------------------------------------
# FORMATTER
# --------------------------------------------------------------------
def pretty_printer(test_name, result, status, execution_time, actual=None, expected=None):
    print(f"==============================")

    # Print the test result in color
    if status == "SUCCESS":
        print(f"TEST RESULT: {'\033[92m'}{status}{'\033[0m'}")
    elif status == "FAIL":
        print(f"TEST RESULT: {'\033[91m'}{status}{'\033[0m'}")
    elif status == "ERROR":
        print(f"TEST RESULT: {'\033[94m'}{status}{'\033[0m'}")

    print(f"TEST NAME: {test_name}")
    print(f"Execution time: {execution_time:.6f} seconds")   
    if status == "SUCCESS":
        print(f"Actual: {actual}")
        print(f"Expected: {expected}")

    if status == "ERROR":
        print(f"An error occurred: {result}")

    if status == "FAIL":
        print(f"Expected: {expected}, but got: {actual}")    
    print(f"==============================\n")

def assert_equals(actual, expected, test_name, execution_time, error=False):
    if error:
        pretty_printer(test_name, actual, "ERROR", execution_time, actual, expected)
    elif actual == expected:
        pretty_printer(test_name, actual, "SUCCESS", execution_time, actual, expected)
    else:
        pretty_printer(test_name, actual, "FAIL", execution_time, actual, expected)

# --------------------------------------------------------------------
# SUCCESSES
# --------------------------------------------------------------------
def test_calculate_cost_BeachResort_with_surfing():
    test_name = inspect.currentframe().f_code.co_name
    try:
        clear_mydict()
        vacation = make(BeachResort, "Maldives", 100, 7, True)
        start_time = perf_counter()

        actual_cost = call(vacation, "calculate_cost")
        expected_cost = 700 + 100  # 7 days * 100 per day + 100 for surfing

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, test_name, execution_time)
    except Exception as e:
        assert_equals(e, None, test_name, 0, error=True)  # In case of unexpected errors

def test_calculate_cost_BeachResort_without_surfing():
    test_name = inspect.currentframe().f_code.co_name
    try:
        clear_mydict()
        vacation = make(BeachResort, "Maldives", 100, 7, False)
        start_time = perf_counter()

        actual_cost = call(vacation, "calculate_cost")
        expected_cost = 700  # 7 days * 100 per day + 100 for surfing

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, test_name, execution_time)
    except Exception as e:
        assert_equals(e, None, test_name, 0, error=True)  # In case of unexpected errors

def test_BeachResort_missing_argument():
    test_name = inspect.currentframe().f_code.co_name
    try:
        clear_mydict()
        vacation = make(BeachResort, "Maldives", 100, 7) # Deliberately missing the surfing argument
        start_time = perf_counter()

        actual_cost = call(vacation, "calculate_cost")
        expected_cost = 700  # 7 days * 100 per day

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, test_name, execution_time)

    # We expect a ValueError to be raised, this means that the function is working as expected
    except ValueError as e:
        assert_equals(e, e, test_name, 0)

    # In case of unexpected errors, we want to flag the test as ERROR
    except Exception as e:
        assert_equals(None, None, test_name, 0, error=True)

def test_calculate_cost_AdventureTrip_hard():
    test_name = inspect.currentframe().f_code.co_name
    try:
        clear_mydict()
        vacation = make(AdventureTrip, "Maldives", 100, 7, "hard")
        start_time = perf_counter()

        actual_cost = call(vacation, "calculate_cost")
        expected_cost = (700)*2 

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, test_name, execution_time)
    except Exception as e:
        assert_equals(e, None, test_name, 0, error=True)  # In case of unexpected errors

def test_calculate_cost_AdventureTrip_easy():
    test_name = inspect.currentframe().f_code.co_name
    try:
        clear_mydict()
        vacation = make(AdventureTrip, "Maldives", 100, 7, "easy")
        start_time = perf_counter()

        actual_cost = call(vacation, "calculate_cost")
        expected_cost = 700

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, test_name, execution_time)
    except Exception as e:
        assert_equals(e, None, test_name, 0, error=True)  # In case of unexpected errors

def test_AdventureTrip_missing_argument():
    test_name = inspect.currentframe().f_code.co_name
    try:
        clear_mydict()
        vacation = make(AdventureTrip, "Maldives", 100, 7) # Deliberately missing the surfing argument
        start_time = perf_counter()

        actual_cost = call(vacation, "calculate_cost")
        expected_cost = 700  # 7 days * 100 per day

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, test_name, execution_time)

    # We expect a ValueError to be raised, this means that the function is working as expected
    except ValueError as e:
        assert_equals(e, e, test_name, 0)

    # In case of unexpected errors, we want to flag the test as ERROR
    except Exception as e:
        assert_equals(None, None, test_name, 0, error=True)

def test_calculate_cost_LuxuryCruise_has_private_suite():
    test_name = inspect.currentframe().f_code.co_name
    try:
        clear_mydict()
        vacation = make(LuxuryCruise, "Maldives", 100, 7, True)
        start_time = perf_counter()

        actual_cost = call(vacation, "calculate_cost")
        expected_cost = 700*1.5

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, test_name, execution_time)
    except Exception as e:
        assert_equals(e, None, test_name, 0, error=True)  # In case of unexpected errors

def test_calculate_cost_LuxuryCruise_no_private_suite():
    test_name = inspect.currentframe().f_code.co_name
    try:
        clear_mydict()
        vacation = make(LuxuryCruise, "Maldives", 100, 7, False)
        start_time = perf_counter()

        actual_cost = call(vacation, "calculate_cost")
        expected_cost = 700

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, test_name, execution_time)
    except Exception as e:
        assert_equals(e, None, test_name, 0, error=True)  # In case of unexpected errors

def test_LuxuryCruise_missing_argument():
    test_name = inspect.currentframe().f_code.co_name
    try:
        clear_mydict()
        vacation = make(LuxuryCruise, "Maldives", 100, 7) # Deliberately missing the surfing argument
        start_time = perf_counter()

        actual_cost = call(vacation, "calculate_cost")
        expected_cost = 700  # 7 days * 100 per day

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, test_name, execution_time)

    # We expect a ValueError to be raised, this means that the function is working as expected
    except ValueError as e:
        assert_equals(e, e, test_name, 0)

    # In case of unexpected errors, we want to flag the test as ERROR
    except Exception as e:
        assert_equals(None, None, test_name, 0, error=True)

def test_calculate_VacationBookingSummary():
    test_name = inspect.currentframe().f_code.co_name
    try:
        start_time = perf_counter()
        clear_mydict()

        vacation1 = make(BeachResort, "Maldives", 100, 7, True)
        vacation2 = make(AdventureTrip, "Greece", 120, 4, "hard")
        vacation3 = make(LuxuryCruise, "Caribbean", 150, 10, False)
        
        # Assuming VacationBookingSummary takes a list of vacations
        vacations_summary = make(VacationBookingSummary, "summary")

        actual_cost = call(vacations_summary, 'calculate_cost')        
        expected_cost = (100*7 + 100) + ((120*2)*4) + (150*10)

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, test_name, execution_time)
    except Exception as e:
        assert_equals(e, None, test_name, 0, error=True)  # In case of unexpected errors

# # --------------------------------------------------------------------
# # FAILURES
# # --------------------------------------------------------------------

# We are failing this test ON PURPOSE to demonstrate the test failure output

def test_calculate_cost_LuxuryCruise_has_private_suite_failure():
    test_name = inspect.currentframe().f_code.co_name
    try:
        start_time = perf_counter()
        clear_mydict()
        vacation = make(LuxuryCruise, "Maldives", 100, 7, False)
        


        actual_cost = call(vacation, "calculate_cost")
        expected_cost = 800  # Wrong expectation deliberately

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, test_name, execution_time)
    except Exception as e:
        assert_equals(e, None, test_name, 0)

def test_calculate_cost_AdventureTrip_easy_failure():
    test_name = inspect.currentframe().f_code.co_name
    try:
        start_time = perf_counter()
        clear_mydict()
        vacation = make(AdventureTrip, "Maldives", 100, 7, "easy")

        actual_cost = call(vacation, "calculate_cost")
        expected_cost = 1400  # Counted times 2 even though it is not hard

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, test_name, execution_time)
    except Exception as e:
        assert_equals(e, None, test_name, 0, error = True)

def test_calculate_cost_BeachResort_with_no_surfing_failure():
    test_name = inspect.currentframe().f_code.co_name
    try:
        start_time = perf_counter()
        clear_mydict()
        vacation = make(BeachResort, "Spain", 50, 6, False)

        actual_cost = call(vacation, "calculate_cost")
        expected_cost = 400  # Counted as if there would be surfing

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, test_name, execution_time)
    except Exception as e:
        assert_equals(e, None, test_name, 0, error=True)

def test_calculate_VacationBookingSummarys_failure():
    test_name = inspect.currentframe().f_code.co_name
    try:
        start_time = perf_counter()
        clear_mydict()

        vacation1 = make(BeachResort, "Maldives", 100, 7, True)
        vacation2 = make(AdventureTrip, "Greece", 120, 4, "hard")
        vacation3 = make(LuxuryCruise, "Caribbean", 150, 10, True)   
        vacations_summary = make(VacationBookingSummary, "summary", 'Tibet')
        
        actual_cost = call(vacations_summary, 'calculate_cost')
        expected_cost = (100*7 + 100) #just took the first vacation

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, test_name, execution_time)
    except Exception as e:
        assert_equals(None, None, test_name, 0, error = True)

# # --------------------------------------------------------------------
# # ERRORS
# # --------------------------------------------------------------------

# We are triggering errors ON PURPOSE to demonstrate the show the error-state output

def test_make_AdventureTrip_medium_error():
    test_name = inspect.currentframe().f_code.co_name
    try:
        clear_mydict()
        vacation = make(AdventureTrip, "Alps", 200, 7, "medium") # Invalid argument
        start_time = perf_counter()

        actual_description = call(vacation, "describe_package")
        expected_description = None 

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_description, expected_description, test_name, execution_time)

    except Exception as e:
        assert_equals(e, None, test_name, 0, error=True)

def test_calculate_cost_with_invalid_days():
    test_name = inspect.currentframe().f_code.co_name
    try:
        clear_mydict()
        vacation = make(AdventureTrip, "Bern", 150, -5, "easy") # Invalid number of vacation days
        start_time = perf_counter()

        actual_cost = call(vacation, "calculate_cost") 
        expected_cost = None #no output should be returned

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, test_name, execution_time)
 
    except Exception as e:
        assert_equals(e, None, test_name, 0, error=True)  # In case of unexpected errors

def test_calculate_VacationBookingSummary_without_vacations_made():
    test_name = inspect.currentframe().f_code.co_name
    try:
        start_time = perf_counter()
        clear_mydict()

        vacation1 = make(BeachResort, "Maldives", 100, 7, True)
        vacation2 = make(AdventureTrip, "Greece", 120, 4, "hard")
        vacation3 = make(LuxuryCruise, "Caribbean", 150, 10, True)   
        vacation4 = make(InventedVacation, "Nowhere", 1000, 3, False)
        vacations_summary = make(VacationBookingSummary, "summary")

        actual_cost = call(vacations_summary, 'calculate_cost')        
        expected_cost = None

        end_time = perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, test_name, execution_time)

    except Exception as e:
        assert_equals(e, None, test_name, 0, error=True)  # In case of unexpected errors

# --------------------------------------------------------------------
# UTILITY FUNCTIONS
# --------------------------------------------------------------------
def run_tests(pattern=None):
    
    print(f"Finding and executing selected tests with the patten {pattern}...\n" if pattern else "Running all tests...\n")
    
    regex = re.compile(pattern, re.IGNORECASE) if pattern else None
    
    tests_executed = False  # Flag to track if any tests were executed
    total_tests = 0  # Total number of tests
    actual_tests = 0  # Number of tests actually executed

    # Iterate over all global variables to find tests
    for name, func in globals().items():
        if callable(func) and name.startswith("test"):

            total_tests += 1

            # If a pattern is provided, check if the function name matches the pattern
            if regex and not regex.search(name):
                continue  # Skip tests that do not match the pattern
            func()  # Call the test function
            tests_executed = True  # At least one test has been executed
            actual_tests += 1  # Increment the number of tests executed

    # Check if any tests were executed
    if not tests_executed:
        raise ValueError(f"No tests found matching the pattern: {pattern}")
    else:
        print(f"Selected tests executed ({actual_tests}/{total_tests})." if pattern else f"All tests executed. ({actual_tests}/{total_tests}).")      

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run a selection of vacation package tests.")
    parser.add_argument(
        '--select',
        type=str,
        # Prints a message to show with inputs are valid.
        help='Pattern to select specific tests to run (e.g., "Beach", "Cruise")'
    )
    args = parser.parse_args()
    
    if args.select:
        pattern = str(args.select).strip()  # Make sure it's a clean string
    else:
        pattern = None
    return pattern

def clear_mydict():
    mydict = find_method(VacationPackage, 'mydict')
    mydict.clear() 

# --------------------------------------------------------------------
# --------------------------------------------------------------------

def main():
    args = parse_arguments()
    run_tests(pattern=args)

if __name__ == "__main__":
    main()