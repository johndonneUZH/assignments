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

def make(vacation_class: dict, destination: str, cost_per_day: int, duration_in_days: int, *args):
    dict_packages = {name.strip('do_'): func for name, func in globals().items() if name.startswith('do_')}
    
    # Defensive programming
    if not isinstance(vacation_class, dict):
        raise ValueError("Invalid vacation package class")
    if not isinstance(destination, str):
        raise ValueError("Invalid destination")
    if not isinstance(cost_per_day, int) or cost_per_day < 0:
        raise ValueError("Invalid cost per day")
    if not isinstance(duration_in_days, int) or duration_in_days < 0:
        raise ValueError("Invalid duration in days")

    # Get the vacation type
    vacation_type = vacation_class['_classname']

    # Start checks for input validation:
    # Get the vacation class's constructor function from the global functions
    constructor_func = None
    if vacation_type in dict_packages:
        constructor_func = dict_packages[vacation_type]
    else:
        raise ValueError(f"Invalid vacation package type: {vacation_type}")
    
    # Bools includes_surfing or has_private_suit are not passed into make()
    match vacation_type:
        case "BeachResort" | "LuxuryCruise":
            if len(args) != 1 or not isinstance(args[0], bool):
                raise ValueError(f"{vacation_type} requires only 1 additional argument")
        case "AdventureTrip":
            if len(args) != 1:
                raise ValueError(f"{vacation_type} requires 1 additional argument")
            if args[0] not in ("easy", "hard")  or not isinstance(args[0], str):
                raise ValueError(f"{vacation_type} is either easy or hard")
        case _:
            pass

    return constructor_func(destination, cost_per_day, duration_in_days, *args)


# --------------------------------------------------------------------
# GLOBAL VARIABLES
# --------------------------------------------------------------------
vacation_summaries = {name.strip('do_'): [] for name, func in globals().items() if name.startswith('do_')}

def add_to_vacation_summaries(vacation_type: str, destination: str, cost_per_day: int, duration_in_days: int, *args):
    global vacation_summaries
    if vacation_type in vacation_summaries:
        vacation_summaries[vacation_type].append(
            {
                "destination": destination,
                "cost_per_day": cost_per_day,
                "duration_in_days": duration_in_days,
                "args": list(args)
            }
        )

# --------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------

def main():
    print(vacation_summaries)
    beach_resort = make(BeachResort, "Maldives", 100, 7, True)
    print(call(beach_resort, "describe_package"))
    print(call(beach_resort, "calculate_cost"))

    adventure_trip = make(AdventureTrip, "Macchu Picchu", 50, 8, "hard")
    print(call(adventure_trip, "describe_package"))
    print(call(adventure_trip, "calculate_cost"))

    luxury_cruise = make(LuxuryCruise, "Malta", 200, 14, True)
    print(call(luxury_cruise, "describe_package"))
    print(call(luxury_cruise, "calculate_cost"))

    print(vacation_summaries)


if __name__ == "__main__":
    main()

