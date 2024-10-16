import re
from collections import defaultdict
# Authors: SoCo_HS24-group_66-a1

# --------------------------------------------------------------------
# Parent class: VACATION PACKAGE
# --------------------------------------------------------------------

# Abstract methods for subclasses to implement
def calculate_cost(vacation_package: dict):
    return NotImplementedError("Abstract Class: This method must be implemented by a subclass")

# Given that only the child classes have a description, we can use this to determine if a vacation package is a child class or not.
# If the vacation package has a description, then it's a child class and we can return it. Else, we throw an error.
# Furthermore, all the descriptions start the same way, so we can just append the rest of the description to the call of the parent class's describe_package method.
def describe_package(vacation_package: dict):
    return f'The {vacation_package["duration_in_days"]} day long vacation in {vacation_package["destination"]}'

# Parent class: VacationPackage
VacationPackage = {
    "calculate_cost": calculate_cost,
    "describe_package": describe_package,
    "mydict": defaultdict(list),
    "_classname":"VacationPackage",
    "_parent": None
}

# Constructor for a new vacation package
def ab_VacationPackage(destination: str, cost_per_day: int, duration_in_days: int) -> dict:
    return {
        "destination": destination,
        "cost_per_day": cost_per_day,
        "duration_in_days": duration_in_days,
        "_class": VacationPackage
    }

# --------------------------------------------------------------------
# Child class: BEACH RESORT
# --------------------------------------------------------------------

def calculate_cost_BeachResort(vacation_package: dict):
    total_cost = vacation_package['cost_per_day'] * vacation_package['duration_in_days']
    if vacation_package['includes_surfing']:
        total_cost += 100
    return total_cost

def describe_package_BeachResort(vacation_package: dict):
    description = find_method(vacation_package['_class']['_parent'], 'describe_package')(vacation_package)
    description = description.replace("vacation", vacation_package["_class"]["_description"])
    if vacation_package['includes_surfing']:
        description += " includes surfing"
    else:
        description += " does not include surfing"
    return description

BeachResort = {
    'calculate_cost': calculate_cost_BeachResort,
    'describe_package': describe_package_BeachResort,
    "_description": "Beach Resort vacation",
    "_classname": "BeachResort",
    "_parent": VacationPackage
}

def do_BeachResort(destination: str, cost_per_day: int, duration_in_days: int, includes_surfing: bool) -> dict:
    return {
        "destination": destination,
        "cost_per_day": cost_per_day,
        "duration_in_days" : duration_in_days,
        "includes_surfing" : includes_surfing,
        "_class": BeachResort
    }

# --------------------------------------------------------------------
# Child class: ADVENTURE TRIP
# --------------------------------------------------------------------

def calculate_cost_AdventureTrip(vacation_package: dict):
    total_cost = vacation_package['cost_per_day'] * vacation_package['duration_in_days']
    if vacation_package['difficulty_level'] == "hard":
        total_cost *= 2
    return total_cost

def describe_package_AdventureTrip(vacation_package: dict):
    description = find_method(vacation_package['_class']['_parent'], 'describe_package')(vacation_package)
    description = description.replace("vacation", vacation_package["_class"]["_description"])
    if vacation_package['difficulty_level'] == "hard":
        description += " is considered hard."
    else:
        description += " is considered easy."
    return description

AdventureTrip = {
    'calculate_cost': calculate_cost_AdventureTrip,
    'describe_package': describe_package_AdventureTrip,
    "_description": "Adventure trip",
    "_classname": "AdventureTrip",
    "_parent": VacationPackage
}

def do_AdventureTrip(destination: str, cost_per_day: int, duration_in_days: int, difficulty_level: str) -> dict:
    return {
        "destination": destination,
        "cost_per_day": cost_per_day,
        "duration_in_days" : duration_in_days,
        "difficulty_level" : difficulty_level,
        "_class": AdventureTrip
    }

# -------------------------------------------------------------------
# Child class: LUXURY CRUISE
# --------------------------------------------------------------------

def calculate_cost_LuxuryCruise(vacation_package: dict):
    total_cost = vacation_package['cost_per_day'] * vacation_package['duration_in_days']
    if vacation_package['has_private_suite']:
        total_cost = total_cost*1.5
    return total_cost

def describe_package_LuxuryCruise(vacation_package: dict):
    description = find_method(vacation_package['_class']['_parent'], 'describe_package')(vacation_package)
    description = description.replace("vacation", vacation_package["_class"]["_description"])
    if vacation_package['has_private_suite']:
        return description + " does include a private suite."
    return description + " does not include a private suite."

LuxuryCruise = {
    'calculate_cost' : calculate_cost_LuxuryCruise,
    'describe_package': describe_package_LuxuryCruise,
    "_description": "Luxury Cruise",
    "_classname": "LuxuryCruise",
    "_parent": VacationPackage
}

def do_LuxuryCruise(destination: str, cost_per_day: int, duration_in_days: int, has_private_suite: bool) -> dict:
    return {
        "destination": destination,
        "cost_per_day": cost_per_day,
        "duration_in_days" : duration_in_days,
        "has_private_suite" : has_private_suite,
        "_class": LuxuryCruise
    }

# --------------------------------------------------------------------
# Child class: VACATION BOOKING SUMMARIES
# --------------------------------------------------------------------

def findSearchTerm(vacation: dict) -> str:
    searchTerm = vacation['_searchTerm']
    vacation_summaries = find_method(VacationPackage, 'mydict')  

    vacation_type = None
    for type in vacation_summaries.keys():
        regex = re.compile(searchTerm, re.IGNORECASE)
        if regex.search(type):
            vacation_type = type
            break

    if not vacation_type:
        return None
    
    return vacation_type

def do_VacationBookingSummary(searchTerm=None) -> dict:
    return {
        "_class": VacationBookingSummary,
        "_searchTerm": searchTerm
    }

def calculate_total_cost(vacation: dict):
    if not isinstance(vacation, dict):
        raise ValueError("Invalid vacation package")

    try:
        total_cost = 0
        vacation_summaries = find_method(VacationPackage, 'mydict')
        searchTerm = vacation['_searchTerm']

        # Calculate the total cost of all vacations if no search term is provided
        if not searchTerm:
            for vacation_type, vacations in vacation_summaries.items():
                for vacation in vacations:
                    total_cost += call(vacation, 'calculate_cost')
        
        # Find the vacation type based on the search term
        else:
            vacation_type = findSearchTerm(vacation)        
            if not vacation_type:
                return "No vacation type found for the search term"
            
            for vacation in vacation_summaries[vacation_type]:
                total_cost += call(vacation, 'calculate_cost')        
        return f'Total cost of all vacations: {total_cost}'
    
    except Exception as e:
        raise RuntimeError(f"Error when calculating total cost: {e}")

def extract_total_vacation_summary(vacation: dict) -> str:
    if not isinstance(vacation, dict):
        raise ValueError("Invalid vacation package")

    try:
        vacation_summaries = find_method(VacationPackage, 'mydict')
        searchTerm = vacation['_searchTerm']

        # Pretty print the vacation summaries
        separator_title = '=' * 20
        separator_normal = '-' * 20

        # Initialize the result list
        result = []
        result.append('\n{}VACATION SUMMARIES{}\n'.format(separator_title, separator_title))
                
        # Loop through the vacation summaries if no search term is provided
        if not searchTerm:
            for vacation_type, vacations in vacation_summaries.items():
                result.append(f"{separator_normal}{vacation_type.upper()}S{separator_normal}")
                for vacation in vacations:
                    result.append(call(vacation, 'describe_package'))
                result.append('\n')

        else:
            # Find the vacation type based on the search term
            vacation_type = findSearchTerm(vacation)
            
            if not vacation_type:
                return "No vacation type found for the search term"

            result.append(f"{separator_normal}{vacation_type.upper()}S{separator_normal}")
            for vacation in vacation_summaries[vacation_type]:
                result.append(call(vacation, 'describe_package'))
            result.append('\n')    

        return '\n'.join(result)
    
    except Exception as e:
        raise RuntimeError(f"Error when extracting vacation summary: {e}")

VacationBookingSummary = {
    'calculate_cost': calculate_total_cost,
    'describe_package': extract_total_vacation_summary,
    "_classname": "VacationBookingSummary",
    "_parent": VacationPackage
}

def add_to_vacation_summaries(vacation: dict):
    vacation_type = vacation['_class']['_classname']
    vacation_summaries = find_method(vacation['_class'], 'mydict')
    vacation_summaries[vacation_type].append(vacation)

def remove_from_vacation_summaries(vacation: dict):
    vacation_type = vacation['_class']['_classname']
    vacation_summaries = find_method(vacation['_class'], 'mydict')
    vacation_summaries[vacation_type].remove(vacation)

# --------------------------------------------------------------------
# UTILITY FUNCTIONS
# --------------------------------------------------------------------

def call(vacation_package: dict, method_name: str):
    # Defensive programming
    if not isinstance(vacation_package, dict):
        raise ValueError("Invalid vacation package")
    
    if not isinstance(method_name, str):
        raise ValueError("Invalid method name")
    
    try:
        method = find_method(vacation_package['_class'], method_name)
        return method(vacation_package)
    except Exception as e:
        raise RuntimeError(f"Error when calling {method_name} on {vacation_package['_class']['_classname']}: {e}")

def find_method(cls: dict, method_name: str):
    if method_name in cls:
        return cls[method_name]
    if cls['_parent']:
        return find_method(cls['_parent'], method_name)
    raise NotImplementedError(f'Invalid method: {method_name}')

def make(vacation_class: dict, destination: str, *args):
    dict_packages = {name.strip('do_'): func for name, func in globals().items() if name.startswith('do_')}

    # Defensive programming
    if not isinstance(vacation_class, dict):
        raise ValueError("Invalid vacation package class")
    if not isinstance(destination, str):
        raise ValueError("Invalid destination")

    # Get the vacation type
    vacation_type = vacation_class['_classname']

    # Handle VacationBookingSummary (no need for cost_per_day or duration_in_days)
    if vacation_type == 'VacationBookingSummary':
        if len(args) > 1:
            raise ValueError(f"{vacation_type} requires 0 or 1 additional arguments")
        searchTerm = args[0] if len(args) == 1 else None
        constructor_func = dict_packages[vacation_type]
        return constructor_func(searchTerm)

    # Check for valid number of arguments based on vacation type
    constructor_func = dict_packages.get(vacation_type)
    if constructor_func is None:
        raise ValueError(f"Invalid vacation package type: {vacation_type}")

    # Handle different vacation types and their required arguments
    match vacation_type:
        case "BeachResort" | "LuxuryCruise":
            if len(args) != 3 or not isinstance(args[2], bool):
                raise ValueError(f"{vacation_type} requires exactly 3 arguments: destination, cost_per_day, duration_in_days, and a boolean flag")
            cost_per_day, duration_in_days, includes_surfing_or_private_suite = args
        case "AdventureTrip":
            if len(args) != 3 or args[2] not in ("easy", "hard"):
                raise ValueError(f"{vacation_type} requires exactly 3 arguments: destination, cost_per_day, duration_in_days, and difficulty ('easy' or 'hard')")
            cost_per_day, duration_in_days, difficulty = args
        case _:
            raise KeyError(f"Invalid vacation type: {vacation_type}")

    # Perform common validation
    if not isinstance(cost_per_day, int) or cost_per_day < 0:
        raise ValueError("Invalid cost per day")
    if not isinstance(duration_in_days, int) or duration_in_days < 0:
        raise ValueError("Invalid duration in days")

    # Create the vacation object and add to summaries, we're passing also *args[2:] for two main reasons:
    # 1) We want to pass the boolean flag or the difficulty level to the constructor function
    # 2) If we want to add more arguments in the future, we can easily do so without changing the call
    # we will only need to add some input validation for the new arguments and it's done.
    vacation = constructor_func(destination, cost_per_day, duration_in_days, *args[2:])
    add_to_vacation_summaries(vacation)
    
    return vacation



# --------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------

def main():
    beach_resort = make(BeachResort, "Maldives", 100, 7, True)
    # print(call(beach_resort, "describe_package"))
    # print(call(beach_resort, "calculate_cost"))

    adventure_trip = make(AdventureTrip, "Macchu Picchu", 50, 8, "hard")
    # print(call(adventure_trip, "describe_package"))
    # print(call(adventure_trip, "calculate_cost"))

    luxury_cruise = make(LuxuryCruise, "Malta", 200, 14, True)
    luxury_cruise2 = make(LuxuryCruise, "Greece", 400, 4, False)
    # print(call(luxury_cruise, "describe_package"))
    # print(call(luxury_cruise, "calculate_cost"))
    vacation_summaries = make(VacationBookingSummary, "VacationBookingSummary", 'bea')
    print(vacation_summaries['_searchTerm'])

    print(call(vacation_summaries, "describe_package"))
    print(call(vacation_summaries, "calculate_cost"))

    beach_resort3 = make(BeachResort, "Art", 110, 9, False)

    print(call(vacation_summaries, "describe_package"))
    print(call(vacation_summaries, "calculate_cost"))



if __name__ == "__main__":
    main()

