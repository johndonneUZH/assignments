import vacation_booking
import time
import argparse
import re


# Helper function to assert results and print results
def assert_equals(actual, expected, test_name, execution_time):
    if actual == expected:
        print(f"PASS: {test_name} (Execution time: {execution_time:.6f} seconds)")
    else:
        print(f"FAIL: {test_name} - Expected {expected}, but got {actual} (Execution time: {execution_time:.6f} seconds)")
        

def test_Calculate_cost_BeachResort():
# Test case 1: Beach resort with surffing included
    beach_resort_with_surfing = vacation_booking.do_BeachResort("Maldives", 100, 7, True)
    start_time = time.perf_counter()
    cost_with_surfing = vacation_booking.call(beach_resort_with_surfing, "calculate_cost")
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    expected_cost = 700 + 100  # 7 days * 100 per day + 100 for surfing
    assert_equals(cost_with_surfing, expected_cost, "Beach Resort with Surfing", execution_time)

    # Test Case 2: Beach Resort without surfing
    beach_resort_without_surfing = vacation_booking.do_BeachResort("Maldives", 100, 7, False)
    start_time = time.perf_counter()
    cost_without_surfing = vacation_booking.call(beach_resort_without_surfing, "calculate_cost")
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    expected_cost = 700  # 7 days * 100 per day, no surfing surcharge
    assert_equals(cost_without_surfing, expected_cost, "Beach Resort without Surfing", execution_time)   

def run_tests(pattern=None):
    
    print(f"Running selected tests with the patten {pattern}...\n" if pattern else "Running all tests...\n")
    
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
        print("No tests found matching the pattern." if pattern else "No tests found.")
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
            
    
def main():
    args = parse_arguments()
    run_tests(pattern=args)

if __name__ == "__main__":
    main()