import vacation_booking
import time
import argparse
import re

# --------------------------------------------------------------------
# FORMATTER
# --------------------------------------------------------------------
def printer(test_name, result, status, execution_time, actual=None, expected=None):
    print(f"==============================")
    print(f"TEST RESULT: {status}")
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

def assert_equals(actual, expected, test_name, execution_time):
    if actual == expected:
        printer(test_name, actual, "SUCCESS", execution_time, actual, expected)
    elif expected is None:
        # Handle error cases when no expected value is provided
        printer(test_name, actual, "ERROR", execution_time)
    else:
        # Failure case when actual does not match expected
        printer(test_name, actual, "FAIL", execution_time, actual, expected)

# --------------------------------------------------------------------
# SUCCESS
# --------------------------------------------------------------------
def test_calculate_cost_BeachResort_with_surfing_success():
    try:
        vacation = vacation_booking.do_BeachResort("Maldives", 100, 7, True)
        start_time = time.perf_counter()

        actual_cost = vacation_booking.call(vacation, "calculate_cost")
        expected_cost = 700 + 100  # 7 days * 100 per day + 100 for surfing

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, "Beach Resort with Surfing", execution_time)
    except Exception as e:
        assert_equals(None, None, "Beach Resort with Surfing", 0)  # In case of unexpected errors

# --------------------------------------------------------------------
# FAILURE
# --------------------------------------------------------------------
def test_calculate_cost_BeachResort_with_surfing_failure():
    try:
        vacation = vacation_booking.do_BeachResort("Maldives", 100, 7, False)
        start_time = time.perf_counter()


        actual_cost = vacation_booking.call(vacation, "calculate_cost")
        expected_cost = 800  # Wrong expectation deliberately

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, "BeachResort Failure", execution_time)
    except Exception as e:
        assert_equals(e, None, "BeachResort Failure", 0)

# --------------------------------------------------------------------
# ERROR
# --------------------------------------------------------------------
def test_calculate_cost_BeachResort_with_surfing_error():
    try:
        vacation = vacation_booking.do_BeachResort("Maldives", 100, 7) # Deliberately missing the surfing argument
        start_time = time.perf_counter()


        actual_cost = vacation_booking.call(vacation, "calculate_cost")
        expected_cost = 700  # 7 days * 100 per day

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, "BeachResort Success", execution_time)
    except Exception as e:
        assert_equals(e, None, "BeachResort Error-Failure", 0)

# --------------------------------------------------------------------
# SUCCESS
# --------------------------------------------------------------------
def test_calculate_cost_AdventureTrip_hard_success():
    try:
        vacation = vacation_booking.do_AdventureTrip("Maldives", 100, 7, "hard")
        start_time = time.perf_counter()

        actual_cost = vacation_booking.call(vacation, "calculate_cost")
        expected_cost = (700)*2 

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, "AdventureTrip Success", execution_time)
    except Exception as e:
        assert_equals(None, None, "Adventure trip hard", 0)  # In case of unexpected errors

# --------------------------------------------------------------------
# FAILURE
# --------------------------------------------------------------------
def test_calculate_cost_AdventureTrip_hard_failure():
    try:
        vacation = vacation_booking.do_AdventureTrip("Maldives", 100, 7, "easy")
        start_time = time.perf_counter()


        actual_cost = vacation_booking.call(vacation, "calculate_cost")
        expected_cost = 1400  # Wrong expectation deliberately

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, "AdventureTrip Failure", execution_time)
    except Exception as e:
        assert_equals(e, None, "AdventureTrip Failure", 0)

# --------------------------------------------------------------------
# ERROR
# --------------------------------------------------------------------
def test_calculate_cost_AdventureTrip_hard_error():
    try:
        vacation = vacation_booking.do_AdventureTrip("Maldives", 100, 7) # Deliberately missing the surfing argument
        start_time = time.perf_counter()


        actual_cost = vacation_booking.call(vacation, "calculate_cost")
        expected_cost = 700 

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, "AdventureTrip Success", execution_time)
    except Exception as e:
        assert_equals(e, None, "AdventureTrip Error-Failure", 0)


# --------------------------------------------------------------------
# SUCCESS
# --------------------------------------------------------------------
def test_calculate_cost_LuxuryCruise_has_private_suite_success():
    try:
        vacation = vacation_booking.do_LuxuryCruise("Maldives", 100, 7, True)
        start_time = time.perf_counter()

        actual_cost = vacation_booking.call(vacation, "calculate_cost")
        expected_cost = 700*1.5

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, "Luxury Cruise with private suite", execution_time)
    except Exception as e:
        assert_equals(None, None, "Luxury Cruise with private suite", 0)  # In case of unexpected errors

# --------------------------------------------------------------------
# FAILURE
# --------------------------------------------------------------------
def test_calculate_cost_LuxuryCruise_has_private_suite_failure():
    try:
        vacation = vacation_booking.do_LuxuryCruise("Maldives", 100, 7, False)
        start_time = time.perf_counter()


        actual_cost = vacation_booking.call(vacation, "calculate_cost")
        expected_cost = 800  # Wrong expectation deliberately

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, "LuxuryCruise Failure", execution_time)
    except Exception as e:
        assert_equals(e, None, "LuxuryCruise Failure", 0)

# --------------------------------------------------------------------
# ERROR
# --------------------------------------------------------------------
def test_calculate_cost_LuxuryCruise_has_private_suite_error():
    try:
        vacation = vacation_booking.do_LuxuryCruise("Maldives", 100, 7) # Deliberately missing the surfing argument
        start_time = time.perf_counter()


        actual_cost = vacation_booking.call(vacation, "calculate_cost")
        expected_cost = 700 

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        assert_equals(actual_cost, expected_cost, "LuxuryCruise Success", execution_time)
    except Exception as e:
        assert_equals(e, None, "LuxuryCruise Error-Failure", 0)


# --------------------------------------------------------------------
# UTILITY FUNCTIONS
# --------------------------------------------------------------------
def run_tests(pattern=None):
    
    print(f"Finding and executing selected tests with the patten {pattern}...\n" if pattern else "Running all tests...\n")
    
    regex = re.compile(pattern, re.IGNORECASE) if pattern else None
    
    tests_executed = False  # Flag to track if any tests were executed

    # Iterate over all global variables to find tests
    for name, func in globals().items():
        if callable(func) and name.startswith("test"):
            # If a pattern is provided, check if the function name matches the pattern
            if regex and not regex.search(name):
                continue  # Skip tests that do not match the pattern
            func()  # Call the test function
            tests_executed = True  # At least one test has been executed

    # Check if any tests were executed
    if not tests_executed:
        raise ValueError(f"No tests found matching the pattern: {pattern}")
    else:
        print("Selected tests executed." if pattern else "All tests executed.")      



def parse_arguments():
    parser = argparse.ArgumentParser(description="Run a sleection of vacation package tests.")
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
            
# --------------------------------------------------------------------
# --------------------------------------------------------------------

def main():
    args = parse_arguments()
    run_tests(pattern=args)

if __name__ == "__main__":
    main()