# Parent class: VacationPackage
VacationPackage = {
    "_classname":"VacationPackage",
    "_parent": None
}

# Constructor for a new vacation package
def do_VacationPackage(destination: str, cost_per_day: int, duration_in_days: int) -> dict:
    return {
        "destination": destination,
        "cost_per_day": cost_per_day,
        "duration_in_days": duration_in_days,
        "_class": VacationPackage
    }

# Abstract methods for subclasses to implement
def calculate_cost(vacation_package: dict):
    return NotImplementedError("Subclasses should implement the calculate_cost() method")

def describe_package(vacation_package: dict):
    return NotImplementedError("Subclasses should implement the describe_package() method")

# --------------------------------------------------------------------
# Child class: BeachResort
BeachResort = {
    "_classname":"BeachResort",
    "_parent":VacationPackage
}

def do_BeachResort(destination: str, cost_per_day: int, duration_in_days: int, includes_surfing: bool) -> dict:
    return {
        "destination": destination,
        "cost_per_day": cost_per_day,
        "duration_in_days" : duration_in_days,
        "includes_surfing" : includes_surfing,
        "_class": BeachResort
    }

def calculate_cost_BeachResort(vacation_package: dict):
    total_cost = vacation_package['cost_per_day'] * vacation_package['duration_in_days']
    if vacation_package['includes_surfing']:
        total_cost += 100
    return total_cost

def describe_package_BeachResort(vacation_package: dict):
    return f"The {vacation_package['duration_in_days']} day long to {vacation_package['destination']} costs {calculate_cost_BeachResort(vacation_package)}"
    

# --------------------------------------------------------------------
# Child class: AdventrureTrip
# TODO














# --------------------------------------------------------------------
# Child class: LuxuryCruise 
# TODO





















# --------------------------------------------------------------------

# Utility functions
def call(vacation_package: dict, method_name: str):
    method = find_method(vacation_package['_class'], method)
    return method(vacation_package)

def find_method(cls: dict, method_name: str):
    if method_name in cls:
        return cls[method_name]
    if cls['_parent']:
        return find_method(cls['_parent'], method_name)
    raise NotImplementedError(f'Invalid method: {method_name}')

# --------------------------------------------------------------------
